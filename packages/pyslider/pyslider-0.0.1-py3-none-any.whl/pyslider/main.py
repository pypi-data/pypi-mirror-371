"""
main
"""

import sys
from pytconf import register_endpoint
from pytconf import register_main, config_arg_parse_and_launch
import pylogconf.core


from pyslider.static import DESCRIPTION, APP_NAME, VERSION_STR


@register_endpoint(
    configs=[],
    description="Say hello",
)
def hello() -> None:
    print("Hello")


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    pylogconf.core.setup()
    # make sure stdout is line buffered
    sys.stdout.reconfigure(line_buffering=True)
    config_arg_parse_and_launch()


if __name__ == "__main__":
    main()
