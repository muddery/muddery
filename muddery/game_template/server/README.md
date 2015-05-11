# server/ 

This directory holds files used by and configuring the Muddery server 
itself.

Out of all the subdirectories in the game directory, Muddery does
expect this directory to exist, so you should normally not delete,
rename or change its folder structure.

When running you will find four new files appear in this directory: 

 - `server.pid` and `portal.pid`: These hold the process IDs of the
   Portal and Server, so that they can be managed by the launcher. If
   Muddery is shut down uncleanly (e.g. by a crash or via a kill
   signal), these files might erroneously remain behind. If so Muddery
   will tell you they are "stale" and they can be deleted manually.
 - `server.restart` and `portal.restart`: These hold flags to tell the
   server processes if it should die or start again. You never need to
   modify those files.
 - `muddery.db3`: This will only appear if you are using the default
   SQLite3 database; it a binary file that holds the entire game
   database; deleting this file will effectively reset the game for
   you and you can start fresh with `muddery migrate` (useful during
   development).  

## server/conf/

This subdirectory holds the configuration modules for the server. With
them you can change how Muddery operates and also plug in your own
functionality to replace the default. You usually need to restart the
server to apply changes done here. The most importand file is the file
`settings.py´ which is the main configuration file of Muddery. 

## server/logs/

This subdirectory holds various log files created by the running
Muddery server. It is also the default location for storing any custom
log files you might want to output using Muddery's logging mechanisms.
