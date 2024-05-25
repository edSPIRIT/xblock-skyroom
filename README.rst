Skyroom XBlock
##############

This is a simple xblock, connecting users to a classroom on `Skyroom <https://www.skyroom.online/>`__.

Installation
************

We need a ``SKYROOM_API_KEY`` to send a ``createLoginUrl`` request. if you're using tutor, create a new config variable called ``SKYROOM_API_KEY``:

.. code-block:: bash

  tutor config save -s SKYROOM_API_KEY="MY_SECRET_API_KEY"

then, create a tutor plugin called ``skyroom.py`` like below: 

.. code-block:: python

  from tutor import hooks
  import os
  
  
  hooks.Filters.ENV_PATCHES.add_item(
      (
          "openedx-common-settings",
          "SKYROOM_API_KEY = '{{ SKYROOM_API_KEY }}'"
      )
  )

This will patch ``SKYROOM_API_KEY`` to both lms and cms. That's it!
