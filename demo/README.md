# Welcome to Muddery!

This directory is your default game directory, set up to let you start
with your new game right away.

You can delete this readme file when you've read it and you can
re-arrange things in this game-directory to suit your own sense of
organisation (the only exception is the directory structure of the
server/ directory, which Muddery expects). If you change the structure
you must however also edit/add to your settings file to tell Muddery
where to look for things.

Your game's main configuration file is found in
`server/conf/settings.py` (but you don't need to change it to get
started). If you just created this directory, `cd` to this directory
then initialize a new database using

    muddery migrate

To start the server, `cd` to this directory and run

    muddery -i start

This will start the server so that it logs output to the console. Make
sure to create a superuser when asked. By default you can now connect
to your new game using a MUD client on localhost:4000.  You can also
log into the web client by pointing a browser to
http://localhost:8000.

# Getting started

It's highly recommended that you look up Muddery extensive
documentation found here: https://github.com/muddery/muddery/wiki.
