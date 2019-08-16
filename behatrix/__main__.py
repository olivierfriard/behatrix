#!python3

import sys

from behatrix import cli, main

if len(sys.argv) > 1:
    cli()
else:
    main()
