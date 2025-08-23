import os
import sys
import argparse
import logging
from cli_logging_moxad import setup_cli_logging

# check for options --debug and --nocolor
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", 
                    help="Enable debug logging")
parser.add_argument("-n", "--nocolor", action="store_false", 
                    help="disable color output")
args = parser.parse_args()

setup_cli_logging(debug=args.debug,
                    progname=os.path.basename( sys.argv[0]),
                    use_color=args.nocolor,
)

logging.debug("Debug message")
logging.info("Info message")
logging.warning("This is a warning!")
logging.error("This is an ERROR!")
logging.critical("Critical issue!!!")

sys.exit(0)
