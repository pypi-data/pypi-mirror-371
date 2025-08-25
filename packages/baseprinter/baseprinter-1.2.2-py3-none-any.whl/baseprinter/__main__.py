from typing import Any

from . import cli

def main(args: Any = None) -> int:
    return cli.main(args)

if __name__ == "__main__":
    exit(main())
