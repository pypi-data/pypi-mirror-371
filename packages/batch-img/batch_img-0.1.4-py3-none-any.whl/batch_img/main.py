"""class Main: the entry point of the tool
Copyright © 2025 John Liu
"""

import json
from pathlib import Path

from batch_img.border import Border
from batch_img.common import Common
from batch_img.const import PKG_NAME, REPLACE
from batch_img.log import Log, logger
from batch_img.resize import Resize
from batch_img.rotate import Rotate


class Main:
    @staticmethod
    def resize(options: dict) -> bool:
        """Resize the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        Log.init_log_file()
        logger.debug(f"{json.dumps(options, indent=2)}")
        in_path = Path(options["src_path"])
        length = options.get("length")
        if not length or length == 0:
            logger.error(f"No resize due to bad {length=}")
            return False
        output = options.get("output")
        out = Path(output) if output else REPLACE
        if in_path.is_file():
            ok, _ = Resize.resize_an_image((in_path, out, length))
        else:
            ok = Resize.resize_all_progress_bar(in_path, out, length)
        Common.check_latest_version(PKG_NAME)
        return ok

    @staticmethod
    def rotate(options: dict) -> bool:
        """Rotate the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        Log.init_log_file()
        logger.debug(f"{json.dumps(options, indent=2)}")
        in_path = Path(options["src_path"])
        angle = options.get("angle")
        if not angle or angle == 0:
            logger.error(f"No rotate due to bad {angle=}")
            return False
        output = options.get("output")
        out = Path(output) if output else REPLACE
        if in_path.is_file():
            ok, _ = Rotate.rotate_1_image((in_path, out, angle))
        else:
            ok = Rotate.rotate_all_in_dir(in_path, out, angle)
        Common.check_latest_version(PKG_NAME)
        return ok

    @staticmethod
    def border(options: dict) -> bool:
        """Add border to the image file(s)

        Args:
            options: input options dict

        Returns:
            bool: True - Success. False - Error
        """
        Log.init_log_file()
        logger.debug(f"{json.dumps(options, indent=2)}")
        in_path = Path(options["src_path"])
        bd_width = options.get("border_width")
        if not bd_width or bd_width == 0:
            logger.error(f"Bad border width: {bd_width=}")
            return False
        bd_color = options.get("border_color")
        if not bd_color:
            logger.error(f"Bad border color: {bd_color=}")
            return False
        output = options.get("output")
        out = Path(output) if output else REPLACE
        if in_path.is_file():
            ok, _ = Border.border_1_image((in_path, out, bd_width, bd_color))
        else:
            ok = Border.border_all_in_dir(in_path, out, bd_width, bd_color)
        Common.check_latest_version(PKG_NAME)
        return ok
