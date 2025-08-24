from thonny import get_workbench
from thonny.workbench import SyntaxThemeSettings


def one_light() -> SyntaxThemeSettings:
    default_fg = "black"
    default_bg = "#fdfdfd"
    light_fg = "DarkGray"
    string_fg = "#50A14F"
    open_string_bg = "#FCEFED"
    gutter_foreground = "#999999"
    gutter_background = "#e0e0e0"

    return {
        "TEXT": {
            "foreground": default_fg,
            "insertbackground": default_fg,
            "background": default_bg,
        },
        "GUTTER": {
            "foreground": gutter_foreground,
            "background": gutter_background
        },
        "breakpoint": {"foreground": "crimson"},
        "current_line": {"background": "#f5f5f5"},
        "definition": {"foreground": "#2f5af3"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string_fg, "background": open_string_bg},
        "open_string3": {
            "foreground": string_fg,
            "background": open_string_bg,
        },
        'sel': {'foreground': "", 'background': "#E5E5E6"},
        "tab": {"background": "#EAEAEB"},
        "keyword": {"foreground": "#E45649"},
        "builtin": {"foreground": "#2f5af3"},
        "number": {"foreground": "#986801"},
        "comment": {"foreground": "#A0A1A7"},
        "function_call": {"foreground": "#0184BC"},
        "method_call": {"foreground": "#4078F2"},
        "class_definition": {"foreground": "#C18401"},
        "function_definition": {"foreground": "#0184BC"},
        "method_definition": {"foreground": "#4078F2"},
        "welcome": {"foreground": light_fg},
        "magic": {"foreground": light_fg},
        # shell
        "prompt": {"foreground": "#A626A4", "font": "BoldEditorFont"},
        "stdin": {"foreground": "Blue"},
        "stdout": {"foreground": "Black"},
        "stderr": {"foreground": "#ff0000"},
        "value": {"foreground": "DarkBlue"},
        "hyperlink": {"foreground": "#3A66DD", "underline": True},
        # paren matcher
        "surrounding_parens": {
            "foreground": "#4078F2",
            "background": "#E5E5E6",
            "font": "BoldEditorFont"
        },
        "unclosed_expression": {"background": "LightGray"},
        # find/replace
        "found": {
            "foreground": "",
            "background": "#D8DEFB",
            "underline": False
        },
        "current_found": {
            "foreground": "",
            "background": "#FBFBC8",
            "borderwidth": 1,
            "relief": "solid"
        },
        "matched_name": {"background": "#e6ecfe"},
        "local_name": {"font": "ItalicEditorFont"},
        # debugger
        "active_focus": {
            "background": "#F8FC9A",
            "borderwidth": 1,
            "relief": "solid"
        },
        "suspended_focus": {
            "background": "",
            "borderwidth": 1,
            "relief": "solid"
        },
        "completed_focus": {
            "background": "#BBEDB2",
            "borderwidth": 1,
            "relief": "flat"
        },
        "exception_focus": {
            "background": "#FFBFD6",
            "borderwidth": 1,
            "relief": "solid"
        },
        "expression_box": {"background": "#DCEDF2", "foreground": default_fg},
        "black_fg": {"foreground": "#2E3436"},
        "black_bg": {"background": "#2E3436"},
        "bright_black_fg": {"foreground": "#555753"},
        "bright_black_bg": {"background": "#555753"},
        "dim_black_fg": {"foreground": "#1E2224"},
        "dim_black_bg": {"background": "#1E2224"},
        "red_fg": {"foreground": "#CC0000"},
        "red_bg": {"background": "#CC0000"},
        "bright_red_fg": {"foreground": "#EF2929"},
        "bright_red_bg": {"background": "#EF2929"},
        "dim_red_fg": {"foreground": "#880000"},
        "dim_red_bg": {"background": "#880000"},
        "green_fg": {"foreground": "#4E9A06"},
        "green_bg": {"background": "#4E9A06"},
        "bright_green_fg": {"foreground": "#8AE234"},
        "bright_green_bg": {"background": "#8AE234"},
        "dim_green_fg": {"foreground": "#346704"},
        "dim_green_bg": {"background": "#346704"},
        "yellow_fg": {"foreground": "#C4A000"},
        "yellow_bg": {"background": "#C4A000"},
        "bright_yellow_fg": {"foreground": "#FCE94F"},
        "bright_yellow_bg": {"background": "#FCE94F"},
        "dim_yellow_fg": {"foreground": "#836B00"},
        "dim_yellow_bg": {"background": "#836B00"},
        "blue_fg": {"foreground": "#3465A4"},
        "blue_bg": {"background": "#3465A4"},
        "bright_blue_fg": {"foreground": "#729FCF"},
        "bright_blue_bg": {"background": "#729FCF"},
        "dim_blue_fg": {"foreground": "#22436D"},
        "dim_blue_bg": {"background": "#22436D"},
        "magenta_fg": {"foreground": "#75507B"},
        "magenta_bg": {"background": "#75507B"},
        "bright_magenta_fg": {"foreground": "#AD7FA8"},
        "bright_magenta_bg": {"background": "#AD7FA8"},
        "dim_magenta_fg": {"foreground": "#4E3552"},
        "dim_magenta_bg": {"background": "#4E3552"},
        "cyan_fg": {"foreground": "#06989A"},
        "cyan_bg": {"background": "#06989A"},
        "bright_cyan_fg": {"foreground": "#34E2E2"},
        "bright_cyan_bg": {"background": "#34E2E2"},
        "dim_cyan_fg": {"foreground": "#046567"},
        "dim_cyan_bg": {"background": "#046567"},
        "white_fg": {"foreground": "#D3D7CF"},
        "white_bg": {"background": "#D3D7CF"},
        "bright_white_fg": {"foreground": "#EEEEEC"},
        "bright_white_bg": {"background": "#EEEEEC"},
        "dim_white_fg": {"foreground": "#8D8F8A"},
        "dim_white_bg": {"background": "#8D8F8A"},
        "fore_fg": {"foreground": default_fg},
        "fore_bg": {"background": default_fg},
        "bright_fore_fg": {"foreground": "#000000"},
        "bright_fore_bg": {"background": "#000000"},
        "dim_fore_fg": {"foreground": "#222222"},
        "dim_fore_bg": {"background": "#222222"},
        "back_fg": {"foreground": default_bg},
        "back_bg": {"background": default_bg},
        "bright_back_fg": {"foreground": "#ffffff"},
        "bright_back_bg": {"background": "#ffffff"},
        "dim_back_fg": {"foreground": "#e0e0e0"},
        "dim_back_bg": {"background": "#e0e0e0"},
        "intense_io": {"font": "BoldIOFont"},
        "italic_io": {"font": "ItalicIOFont"},
        "intense_italic_io": {"font": "BoldItalicIOFont"},
        "underline": {"underline": True},
        "strikethrough": {"overstrike": True},
    }


def load_plugin() -> None:
    get_workbench().add_syntax_theme('One Light', 'Default Light', one_light)
