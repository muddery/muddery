# Intro
Muddery is an online text game (like MUD) framework in Python. It is licensed under 3-clause BSD license. Muddery bases on [Evennia](https://github.com/evennia/evennia) which is a MUD/MU* creation system. It is developed from Evennia's game template.

Our website is http://www.muddery.org.

Muddery is still under construction. It will have following feathers. 

1. Muddery is in Python, so it can run on multiple platforms. Users can install it in just several minutes.

1. Muddery uses webpage as client. The data between server and client are in JSON. The client is responsible for display, so users can customize the display style by modifying the webpage. Muddery can support simple images and sounds, but it does not support Telnet and other common MUD clients. We may build native apps for it in the future.

1. Muddery will provide a series of modules, such as battle system, skill system, equipment system, etc. Users can use these modules to build their own game. 

1. Muddery can load the all game world from a series of tables. Game designers who know little about programing also can use Muddery to build their games.


# Installation
First, install [Python](https://www.python.org/)(2.7.x), [pip](https://pypi.python.org/pypi/pip/), [virtualenv](https://pypi.python.org/pypi/virtualenv) and [Git](http://git-scm.com/).

Activate virtualenv. Go to the place where you want to place Muddery and run
```
git clone https://github.com/muddery/muddery.git
```
or
```
git clone git@github.com:muddery/muddery.git
```

In the future, you can move into Muddery's folder and run
```
git pull
```
to get the latest version.

Move into Muddery's folder and run
```
pip install -e .
```
(note the period "." at the end)

It will install dependent libs and Muddery into your virtual environment.


# Create your game
Move to the place where you want to place your game. It should be outside of your Muddery folder. Then run
```
muddery --init game_name
```

This will create a new game project in folder "game_name".

Move into the game folder and run
```
muddery migrate
muddery -i start
```

This will setup the database and create superuser account first, then the muddery server will be running.

Open your web browser and point to ```http://localhost:8000```, you can see the game's web page. The game's webclient is on ```http://localhost:8000/webclient```.

You can use
```
muddery -i start
muddery reload
muddery stop
```
to start, reload or stop the server.


# Tutorial world
The tutorial world is developed from Evennia's tutorial world.

Move to the place where you want to place the tutorial world. It should be outside of your Muddery folder. Then run
```
muddery --init game_name
```

Copy ```muddery/examples/tutorial_world/worlddata``` to your game's folder, replace the current ```worlddata```.

Move into the game folder and run
```
muddery migrate
muddery -i start
```

Then login the game as superuser or builder. Run
```
@datainfo #2=limbo
@batchbld
```

The tutorial world will be loaded into the game.
