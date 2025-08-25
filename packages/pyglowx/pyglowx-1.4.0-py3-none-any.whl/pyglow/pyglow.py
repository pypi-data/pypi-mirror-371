from .parser import PyGlowParser
from .mapping import ANSI_RESET


class Glow:

    @staticmethod
    def parse(text: str) -> str:
        parsed_text, _ = PyGlowParser.parse_recursively(text)
        return parsed_text

    @staticmethod
    def print(text: str):
        print(Glow.parse(text))

    @staticmethod
    def prints(text: str, style: str):
        Glow.print(f"[{style}]{text}[/]")

    @staticmethod
    def printc(text: str):
        print(f"{text}{ANSI_RESET}")
