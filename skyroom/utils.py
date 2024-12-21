"""
xblock helpers.
"""

import os
from html import unescape

from django.template import Context, Engine


def render_template(template_name, **context):
    """
    Render static resource using provided context.

    Returns: django.utils.safestring.SafeText
    """
    template_dirs = [os.path.join(os.path.dirname(__file__), "static/html")]
    libraries = {"clickaware_tags": "skyroom.templatetags"}
    engine = Engine(dirs=template_dirs, debug=True, libraries=libraries)
    html = engine.get_template(template_name)

    return unescape(html.render(Context(context)))
