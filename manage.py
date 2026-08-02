#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kundalik.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Даун скачай джанго"
            "Как можно забыть включить "
            "венв?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
