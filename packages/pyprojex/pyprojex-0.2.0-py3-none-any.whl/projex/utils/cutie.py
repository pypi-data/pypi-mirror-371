# This file is for cute prints and stuff
import os
import sys
from datetime import datetime as dt
from typing import Union, Literal
import shutil


class ANSIColors:
    RESET = "\033[0m"

    # Styles
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    REVERSED = "\033[7m"

    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    @staticmethod
    def colored(text, color):
        return f"{color}{text}{ANSIColors.RESET}"


def check_for_logfile() -> Union[bool, str]:
    for arg in sys.argv:
        if arg.startswith("--log"):
            return arg.lstrip("--log=")
    if logfile := os.getenv("LOG_FILE"):
        return logfile
    return False


def p(
    msg,
    level: Union[
        Literal["info"], Literal["warning"], Literal["error"], Literal["fatal"]
    ] = "info",
):
    date = dt.now().strftime("%H:%M:%S")

    match level:
        case "info":
            pre = ANSIColors.WHITE
        case "warning":
            pre = ANSIColors.YELLOW
        case "error":
            pre = ANSIColors.RED
        case "fatal":
            pre = ANSIColors.BOLD + ANSIColors.UNDERLINE + ANSIColors.BRIGHT_RED
        case _:
            pre = ANSIColors.BOLD + ANSIColors.BRIGHT_RED
            msg = "Error in backend, developer misused logging."

    print(ANSIColors.BLUE + date + ANSIColors.RESET, "-", pre + msg + ANSIColors.RESET)
    if logfile := check_for_logfile():
        with open(logfile, "+a", encoding="utf-8") as fp:
            fp.write(f"{date} - {msg}")
    if level == "fatal":
        sys.exit(1)


def line(title: str = None, color: str = ANSIColors.WHITE):
    width, _ = shutil.get_terminal_size()
    lw = width // 2
    if len(title) + 2 >= width:
        print(f"{color}[{title}]{ANSIColors.RESET}")
        return
    if title:
        lw -= (len(title) + 2) // 2
    rw = width - lw - len(title) - 2
    final_string = f'{color}{"-"*lw}[{title}]{"-"*rw}{ANSIColors.RESET}\n'
    print(final_string)
