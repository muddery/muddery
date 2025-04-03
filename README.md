**Due to changes in life and work, this project is suspended. Thank you for your support and encouragement.**

**由于生活和工作的变化，本项目暂停更新，感谢大家的支持和鼓励。**

# Intro
Muddery is an online text game (like MUD) framework in Python. It is licensed under 3-clause BSD license.

Our chinese website is https://www.muddery.org.
（欢迎访问中文网站：https://www.muddery.org ，可能需要翻墙。）


#Features
Muddery is still under construction. It will have the following features. 

1. It is in Python, so it can run on multiple platforms. Users can install it in just several minutes.

1. It uses webpage as client. The data between server and client are in JSON. The client is responsible for display, so users can customize the display style by modifying the webpage. Muddery can support simple images and sounds, but it does not support Telnet and other common MUD clients. We may build native app client for it in the future.

1. It will provide a series of modules, such as battle system, skill system, equipment system, etc. Users can use these modules to build their own game. 

1. It provides an online game editor. Game designers who know little about programing also can use Muddery to build their games.


# Installation
1. Install Python3.7+ and GIT. Start a Console/Terminal.
1. `cd` to some place you want to do your development. 
1. `git clone https://github.com/muddery/muddery`
1. `python -m venv mudenv`
1. `source mudenv/bin/activate` (Linux, Mac) or `mudenv\Scripts\activate` (Windows)
1. `pip install -e muddery`
1. `muddery --init mygame`
1. `cd mygame`
1. `muddery start`

Muddery should now be running and you can connect to it by pointing your web browser to http://localhost:8000.

If you want to stop the server, you can use `muddery stop`.
