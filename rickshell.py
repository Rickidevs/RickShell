import sys

from interface.colors import Colors
from interface.console import ConsoleInterface


def main() -> None:
    console = ConsoleInterface()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        print(f"\n{Colors.warn('[*] Interrupted. Exiting RickShell.')}")
        sys.exit(0)


if __name__ == '__main__':
    main()