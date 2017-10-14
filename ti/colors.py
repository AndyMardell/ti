from colorama import Fore
import re


class TiColorText(object):
    def __init__(self, use_colors):
        self.use_colors = use_colors

    def color_string(self, color, text):
        if self.use_colors:
            return color + text + Fore.RESET
        else:
            return text


color_regex = re.compile("(\x9B|\x1B\\[)[0-?]*[ -\/]*[@-~]")


def strip_color(str):
    """Strip color from string."""
    return color_regex.sub("", str)


def len_color(str):
    """Compute how long the color escape sequences in the string are."""
    return len(str) - len(strip_color(str))


def ljust_with_color(str, n):
    """ljust string that might contain color."""
    return str.ljust(n + len_color(str))
