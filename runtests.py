#!/usr/bin/env python

import sys
import warnings

from django.core.management import execute_from_command_line

warnings.simplefilter("error")

try:
    from psycopg2cffi import compat

    compat.register()
except ImportError:
    pass


def runtests():
    argv = sys.argv[:1] + ["test", "--settings=tests.settings", "--noinput"]
    execute_from_command_line(argv)


if __name__ == "__main__":
    runtests()
