import logging
import re
from typing import Mapping, Any

FOREGROUND_COLOR_SEQ="\033[3{0}m{1}\033[0m"
BACKGROUND_COLOR_SEQ="\033[4{0}m{1}\033[49m"
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

def shortPrint(s: str, length: int = 50) -> str:
    if len(s) > length:
        max = int(length / 2)
        return f"{s[0:max]}...{s[-max:]}"
    else:
        return s

class ColorFormatter(logging.Formatter):
    classRe = re.compile("^[A-Z]{1}[A-z]+$") 
    moduleRe = re.compile("^(difd)(\.[a-z]+)+")

    def __init__(self, fmt: str | None = None, datefmt: str | None = None, style: str = "%", validate: bool = True, *, defaults: Mapping[str, Any] | None = None) -> None:
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        match level:
            case "DEBUG":
                # background yellow, foreground white   
                #record.levelname = FOREGROUND_COLOR_SEQ.format(CYAN, level)
                record.levelname = BACKGROUND_COLOR_SEQ.format(
                    YELLOW, FOREGROUND_COLOR_SEQ.format(BLACK, f" {level} ")
                ) + " "
            case "INFO":
                # background default, foreground green
                record.levelname = FOREGROUND_COLOR_SEQ.format(BLUE, level)
            case "WARNING":
                # background default, foreground yellow
                record.levelname = FOREGROUND_COLOR_SEQ.format(YELLOW, level)
            case "CRITICAL":
                # background default, foreground red
                record.levelname = FOREGROUND_COLOR_SEQ.format(RED, level)
            case "ERROR":
                # background red, foreground white
                record.levelname = BACKGROUND_COLOR_SEQ.format(
                    RED, FOREGROUND_COLOR_SEQ.format(BLACK, f" {level} ")
                ) + " "

        if self.classRe.search(record.name):
            record.name = FOREGROUND_COLOR_SEQ.format(GREEN, record.name)
        elif self.moduleRe.search(record.name):
            record.name = FOREGROUND_COLOR_SEQ.format(MAGENTA, record.name)

        return super().format(record)