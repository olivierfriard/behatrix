#!python3

import sys
from behatrix import main, cli

if len(sys.argv) > 1:
    cli()
else:
    main()



