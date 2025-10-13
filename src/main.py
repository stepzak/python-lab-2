import logging
from src.command_line_session import CommandLineSession
import src.constants as cst

def main():
    logging.basicConfig(
        level=cst.LOGGING_LEVEL,
        filename=cst.LOG_FILE,
        format=cst.FORMAT
    )
    session = CommandLineSession()
    session.start_session()


if __name__ == "__main__":
    main()
