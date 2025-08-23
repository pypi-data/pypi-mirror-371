"""
All configurations for pyslider
"""


from pytconf import Config, ParamCreator


class ConfigOutput(Config):
    """
    Parameters to control output
    """
    terse = ParamCreator.create_bool(
        help_string="be terse?",
        default=False,
    )
    stats = ParamCreator.create_bool(
        help_string="show statistics are the end?",
        default=False,
    )
    output = ParamCreator.create_bool(
        help_string="show projects?",
        default=True,
    )
    print_not = ParamCreator.create_bool(
        help_string="print what the project is not",
        default=False,
    )
