#!/usr/bin/env python
"""
MUDDERY SERVER LAUNCHER SCRIPT

This is the start point for running Muddery.

Sets the appropriate environmental variables and launches the server
and portal through the evennia_runner. Run without arguments to get a
menu. Run the script with the -h flag to see usage information.

"""


from evennia.server import evennia_launcher

def main():
    """
    Run the evennia main program.
    """
    evennia_launcher.main()


if __name__ == '__main__':
    # start Muddery from the command line
    main()
