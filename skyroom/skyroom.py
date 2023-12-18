# -*- coding: utf-8 -*-
"""TO-DO: Write a description of what this XBlock is."""

import logging

import pkg_resources
import requests
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from web_fragments.fragment import Fragment
from xblock.completable import CompletableXBlockMixin, XBlockCompletionMode
from xblock.core import XBlock
from xblock.fields import Boolean, Integer, Scope, String
from xblock.utils.studio_editable import StudioEditableXBlockMixin

from .utils import render_template


logger = logging.getLogger(__name__)


@XBlock.wants("user")
@XBlock.needs("i18n")
class SkyRoomXBlock(XBlock, CompletableXBlockMixin, StudioEditableXBlockMixin):
    display_name = String(
        display_name=_("Component display name"),
        default=_("SkyRoom XBlock"),
        help=_("Title of the block. Course creators will see this name."),
        scope=Scope.content,
    )
    description = String(
        display_name=_("Block description"),
        help=_(
            "A description of the block. Usually guides the students on what this is about."
        ),
        default="To Enter the class, go ahead and click on the link below.",
        scope=Scope.content,
    )
    instance_url = String(
        display_name=_("Instance URL"),
        help=_("URL of the Skyroom instance. for example: https://www.skyroom.online"),
        default="https://www.skyroom.online",
        scope=Scope.content,
    )
    room_id = Integer(
        display_name=_("Room ID"),
        help=_("ID of the class room"),
        default=123456789,
        scope=Scope.content,
    )
    ttl = Integer(
        display_name=_("TTL"),
        help=_("Time To Live. How long the link is valid. in seconds."),
        default=3600,
        scope=Scope.content,
    )
    error_message = String(
        display_name=_("Error Message"),
        help=_("Error message to display to the user."),
        default=_("An error has occurred."),
        scope=Scope.content,
    )

    link_title = String(
        display_name=_("Link Title"),
        help=_("This will show up on the link which users will click on."),
        default=_("Enter class"),
        scope=Scope.content,
    )
    language = String(
        display_name=_("Language"),
        help=_("Skyroom will show to the students with the selected language"),
        default="en",
        scope=Scope.content,
        values=[
            {"display_name": "English", "value": "en"},
            {"display_name": "فارسی", "value": "fa"},
        ],
    )
    viewed = Boolean(default=False, scope=Scope.user_state_summary)

    editable_fields = (
        "display_name",
        "description",
        "instance_url",
        "room_id",
        "ttl",
        "link_title",
        "language",
        "error_message",
    )

    icon_class = "other"
    # Setting this attribute to standard means that this XBlock
    # takes part in completion tracking.
    completion_mode = XBlockCompletionMode.COMPLETABLE

    def has_custom_completion(self):
        """Return True if this XBlock uses custom completion criteria."""
        return True

    def get_user_data(self):
        user_service = self.runtime.service(self, "user")
        user = user_service.get_current_user()
        data = {
            "username": user.opt_attrs.get("edx-platform.username"),
            "full_name": user.full_name,
            "emails": user.emails,
            "is_staff": user.opt_attrs.get("edx-platform.user_is_staff"),
            "user_role": user.opt_attrs.get("edx-platform.user_role"),
        }
        return data

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_skyroom_api_key(self):
        return getattr(settings, "SKYROOM_API_KEY", None)

    def student_view(self, context=None):
        """
        The primary view of the SkyRoomXBlock, shown to students
        when viewing courses.
        """

        context = {
            "i18n_service": self.runtime.service(self, "i18n"),
            "display_name": self.display_name,
            "description": self.description,
            "link_title": self.link_title,
            "is_key_set": self.get_skyroom_api_key() is not None,
        }
        frag = Fragment()
        frag.content = render_template("skyroom.html", **context)
        frag.add_css(self.resource_string("static/css/skyroom.css"))
        frag.add_javascript(self.resource_string("static/js/src/skyroom.js"))
        frag.initialize_js("SkyRoomXBlock")
        return frag

    @XBlock.json_handler
    def mark_as_viewed(self, data, suffix=""):
        created, url = self.create_login_url(self.get_user_data())
        logger.debug(f"createLoginURL result: created:{created}, url:{url}")
        if not created:
            return {
                "result": "error",
                "message": str(self.error_message),
            }
        self.viewed = True
        self.runtime.publish(self, "completion", {"completion": 1.0})
        return {
            "result": "success",
            "url": url,
        }

    def create_login_url(self, user_data):
        base_url = "{instance_url}/skyroom/api/{key}".format(
            instance_url=self.instance_url,
            key=self.get_skyroom_api_key(),
        )
        full_name = user_data.get("full_name")
        username = user_data.get("username")
        payload = {
            "action": "createLoginUrl",
            "params": {
                "room_id": self.room_id,
                "user_id": username,
                "nickname": full_name if full_name else username,
                "access": 1
                if user_data.get("is_staff")
                or user_data.get("user_role") == "instructor"
                else 3,
                "concurrent": 1,
                "language": self.language,
                "ttl": self.ttl,
            },
        }

        response = requests.post(base_url, json=payload)
        if response.json().get("ok") == True:
            return True, response.json().get("result")
        logger.error(
            "Error creating login url: {}, payload: {}, endpoint: {}".format(
                response.json(),
                payload,
                self.instance_url,
            )
        )
        return False, "No URL"

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            (
                "SkyRoomXBlock",
                """<skyroom/>
             """,
            ),
            (
                "Multiple SkyRoomXBlock",
                """<vertical_demo>
                <skyroom/>
                <skyroom/>
                <skyroom/>
                </vertical_demo>
             """,
            ),
        ]
