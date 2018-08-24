# FacebookWebBot
A simple library to automatize facebook without the official API
All the functions are made scraping and parsing mbasic.facebook.com

## Available functions:
    Login
    Logout
	Get post in a facebook group
	Get the members of a facebook group
	Get all post from a profile/fanpage
	Get number of likes and coments in a post

## Basic usage example:
```
from FacebookWebBot import *
bot=FacebookBot()
bot.set_page_load_timeout(10)
bot.login("your@email.com","yourpassword")
allpost=bot.getPostInProfile("https://mbasic.facebook.com/profile.php?fref=pb",deep=50)
for p in allpost:
	print(p)
```

## Know issues:
    * Images
    * Video

## Dependencies:
    * Python 3.4
    * Selenium 
    * Webdriver
