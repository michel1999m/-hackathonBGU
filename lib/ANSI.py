# Color ANSI codes:
__red = "\u001b[31m"
__green = "\u001b[32m"
__yellow = "\u001b[33m"
__blue = "\u001b[34m"
__cyan = "\u001b[36m"
__white = "\u001b[37m"

# Reset the color to default.
__reset = "\u001b[0m"


def color_red():
    return __red


def color_green():
    return __green


def color_yellow():
    return __yellow


def color_blue():
    return __blue


def color_cyan():
    return __cyan


def color_white():
    return __white


def reset():
    return __reset


def bold():
    return "\033[1m"


def italic():
    return "\033[3m"


def print_error(error):
    print(__red + bold() +  str(error) + __reset)


def turn_on_colors():
    # set Windows console in virtual terminal so we can see all colors
    if __import__("platform").system() == "Windows":
        kernel32 = __import__("ctypes").windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        del kernel32
