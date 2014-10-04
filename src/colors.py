def custom_foreground_color(n):
    return '\033[38;5;{}'.format(n)

def custom_background_color(n):
    return '\033[48;5;{}'.format(n)

colors = {
    'CUSTOM': custom_foreground_color,
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'ITALIC': '\033[3m',
    'UNDERLINE': '\033[4m',
    'BLINK': '\033[5m',
    'NEGATIVE': '\033[7m',
    'CROSSED': '\033[9m',
    'PRIMARY_FONT': '\033[10m',
    'RESET_BOLD': '\033[22m',
    'RESET_ITALIC': '\033[23m',
    'RESET_BLINK': '\033[25m',
    'RESET_COLORS': '\033[39m',

    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',

    'BACKGROUND': {
        'BLACK': '\033[40m',
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'YELLOW': '\033[43m',
        'BLUE': '\033[44m',
        'MAGENTA': '\033[45m',
        'CYAN': '\033[46m',
        'WHITE': '\033[47m',
        'RESET': '\033[49m',
        'CUSTOM': custom_background_color
    }
}
