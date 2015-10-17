# Intro
Muddery is an online text game (like MUD) framework in Python. It is licensed under 3-clause BSD license. Muddery bases on [Evennia](https://github.com/evennia/evennia) which is a MUD/MU* creation system.

Our website is http://www.muddery.org.


#Features
Muddery is still under construction. It will have following features. 

1. It is in Python, so it can run on multiple platforms. Users can install it in just several minutes.

1. It uses webpage as client. The data between server and client are in JSON. The client is responsible for display, so users can customize the display style by modifying the webpage. Muddery can support simple images and sounds, but it does not support Telnet and other common MUD clients. We may build native app client for it in the future.

1. It will provide a series of modules, such as battle system, skill system, equipment system, etc. Users can use these modules to build their own game. 

1. It can load the all game world from a series of tables. Game designers who know little about programing also can use Muddery to build their games.


# Installation
First, install [Python](https://www.python.org/)(2.7.x), [pip](https://pypi.python.org/pypi/pip/), [virtualenv](https://pypi.python.org/pypi/virtualenv) and [Git](http://git-scm.com/).

Activate virtualenv. Go to the place where you want to place Muddery and run
```
git clone https://github.com/muddery/muddery.git
```
If you have a Github account, you can also run
```
git clone git@github.com:muddery/muddery.git
```
This will download Muddery to your current place.

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

It will install Muddery and its dependent libs into your virtual environment.


# Create your game
Move to the place where you want to place your game. It should be outside of your Muddery folder. Then run
```
muddery --init your_game_name
```

This will create a new game project in folder "your_game_name".

Move into the game folder and run
```
muddery -i start
```

This will setup the database and create superuser account first, then the Muddery server will be running.

Open your web browser and point to ```http://localhost:8000```, you can see the game's web page. The game's webclient is on ```http://localhost:8000/webclient```.

You can use
```
muddery -i start
muddery reload
muddery stop
```
to start, reload or stop the server.


# Game example
This example is developed from Evennia's tutorial world.

Move to the place where you want to place the game example. It should be outside of your Muddery folder. Then run
```
muddery --init your_game_name example
```

Move into the game folder and run
```
muddery -i start
```

The game example will be built when the server is initiating.
