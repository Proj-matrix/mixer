# GPLv3 License
#
# Copyright (C) 2020 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Mixer addon entry point for Blender.

Register/unregister functions and logging setup.
"""

import atexit
import faulthandler
import logging
import os
from pathlib import Path

__version__ = "v0.20.0"  # Generated by inject_version.py
display_version = "v0.20.0"  # Generated by inject_version.py
version_date = "2021-01-22:13:23:12 UTC"  # Generated by inject_version.py

bl_info = {
    "name": "Mixer",
    "author": "Ubisoft Animation Studio",
    "description": "Collaborative 3D edition accross 3D software",
    "version": (0, 20, 0),  # Generated by inject_version.py
    "blender": (2, 83, 9),
    "location": "",
    "warning": "Experimental addon, can break your scenes",
    "wiki_url": "https://github.com/ubisoft/mixer",
    "tracker_url": "",
    "category": "Collaboration",
}

logger = logging.getLogger(__name__)
logger.propagate = False
MODULE_PATH = Path(__file__).parent.parent
_disable_fault_handler = False


def cleanup():
    from mixer.share_data import share_data

    try:
        if share_data.local_server_process:
            share_data.local_server_process.kill()
    except Exception:
        pass

    if _disable_fault_handler:
        faulthandler.disable()


def register():
    from mixer import bl_panels
    from mixer import bl_operators
    from mixer import bl_properties, bl_preferences
    from mixer.blender_data import debug_addon
    from mixer.log_utils import Formatter, get_log_file
    from mixer import config
    from mixer.utils import utils_ui_operators

    config.init_global_variables()

    if len(logger.handlers) == 0:
        # Add the pid to the log. Just enough for the tests, that merge the logs and need to distinguish
        # two Blender on the same machine. Pids might collide during regular networked operation
        old_factory = logging.getLogRecordFactory()
        pid = str(os.getpid())

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.custom_attribute = pid
            return record

        logging.setLogRecordFactory(record_factory)

        logger.setLevel(logging.WARNING)
        formatter = Formatter("{asctime} {custom_attribute:<6} {levelname[0]} {name:<36}  - {message:<80}", style="{")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        handler = logging.FileHandler(get_log_file())
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if not faulthandler.is_enabled():
        faulthandler.enable()
        global _disable_fault_handler
        _disable_fault_handler = True

    debug_addon.register()

    bl_preferences.register()
    bl_properties.register()
    bl_panels.register()
    bl_operators.register()
    utils_ui_operators.register()

    atexit.register(cleanup)


def unregister():
    from mixer import bl_panels
    from mixer import bl_operators
    from mixer import bl_properties, bl_preferences
    from mixer.blender_data import debug_addon
    from mixer import config
    from mixer.utils import utils_ui_operators

    cleanup()

    atexit.unregister(cleanup)

    utils_ui_operators.unregister()
    bl_operators.unregister()
    bl_panels.unregister()
    bl_properties.unregister()
    bl_preferences.unregister()

    debug_addon.unregister()

    config.release_global_variables()
