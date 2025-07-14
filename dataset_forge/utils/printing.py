from .color import Mocha
from .audio_utils import play_error_sound


def print_header(title, char="#", color=Mocha.mauve):
    print(color + Mocha.bold + char * 50 + Mocha.reset)
    print(color + Mocha.bold + f"{title.center(50)}" + Mocha.reset)
    print(color + Mocha.bold + char * 50 + Mocha.reset)


def print_section(title, char="-", color=Mocha.sapphire):
    print(color + char * 40 + Mocha.reset)
    print(color + Mocha.bold + f"{title.center(40)}" + Mocha.reset)
    print(color + char * 40 + Mocha.reset)


def print_success(msg):
    print(Mocha.green + Mocha.bold + "  " + msg + Mocha.reset)


def print_warning(msg):
    print(Mocha.peach + Mocha.bold + "! " + msg + Mocha.reset)


def print_error(msg):
    play_error_sound(block=False)
    print(Mocha.red + Mocha.bold + "  " + msg + Mocha.reset)


def print_info(msg):
    print(Mocha.sky + msg + Mocha.reset)


def print_prompt(msg):
    print(Mocha.yellow + msg + Mocha.reset, end="")
