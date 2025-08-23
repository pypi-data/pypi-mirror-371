import os
import sys
try:
    import logging
    import argparse
    import colorlog
except ModuleNotFoundError as e:
    prog = sys.argv[0]
    sys.stderr.write(f"{prog}: error during import: {e}\n")
    sys.exit(1)

_VERSION = '0.5.0'


class MaxLevelFilter(logging.Filter):
    """Only allow records with levelno <= max_level."""
    def __init__(self, max_level):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.levelno <= self.max_level


def setup_cli_logging(debug: bool = False, progname: str | None = None,
                      use_color: bool = True ):
    """Configure CLI logging with split streams, colors
    Setup logging:
        - DEBUG/INFO -> stdout
        - WARNING/ERROR/CRITICAL -> stderr
        - Colors are only applied if the stream is a terminal
    Arguments:
        1) debug=False
            If debug is True, then logging.debug() is enabled
        2) progname=None
            If progname is given, the message is prepended with it
        3) use_color=True
            By default, use colors in the message level (ERROR, etc)
    Returns:
        None
    """

    level = logging.DEBUG if debug else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    base_fmt = "%(levelname)s: %(message)s"
    if progname:
        base_fmt = f"{progname}: {base_fmt}"

    # Build colored and plain formatters
    def make_formatter(stream):
        color_flag = stream.isatty() if use_color else False
        if color_flag:
            # %(log_color)s … %(reset)s will color the WHOLE line per level
            fmt = f"%(log_color)s{base_fmt}%(reset)s"
            return colorlog.ColoredFormatter(
                fmt,
                log_colors={
                    'DEBUG':    'cyan',
                    'INFO':     'green',
                    'WARNING':  'yellow',
                    'ERROR':    'red',
                    'CRITICAL': 'bold_red',
                },
                style='%'   # we're using %-style formatting
            )
        else:
            return logging.Formatter(base_fmt)

    # stdout: DEBUG/INFO
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(MaxLevelFilter(logging.INFO))
    stdout_handler.setFormatter(make_formatter(sys.stdout))

    # stderr: WARNING+
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(make_formatter(sys.stderr))

    root.addHandler(stdout_handler)
    root.addHandler(stderr_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", 
                        help="Enable debug logging")
    parser.add_argument("-n", "--nocolor", action="store_false", 
                        help="disable color output")
    args = parser.parse_args()

    setup_cli_logging(debug=args.debug,
                      progname=os.path.basename(sys.argv[0]),
                      use_color=args.nocolor,
    )

    logging.debug("Debug message")
    logging.info("Info message")
    logging.warning("This is a warning!")
    logging.error("This is an ERROR!")
    logging.critical("Critical issue!!!")

    sys.exit(0)
