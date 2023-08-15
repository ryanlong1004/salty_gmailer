"""Main execution"""

from pathlib import Path

from src.cli import get_cli_input, get_queue
from src.logger import get_logger
from src.mailer import Mailer
from src.rule import Rule


def main():
    """main execution"""
    logger = get_logger(__name__, "./gmailer.log")
    mailer = Mailer()

    paths = get_queue(get_cli_input().paths)
    for _path in paths:
        rule = Rule.from_path(Path(_path), mailer)
        logger.info(
            "executing %s: %s on %s messages",
            rule.name,
            rule.description,
            len(rule.messages.copy()),
        )
        rule()


if __name__ == "__main__":
    main()
