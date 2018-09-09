# FacebookWebBot
A simple library to collect data from facebook without the official API
All the functions are made scraping and parsing mbasic.facebook.com

Made to work with facebook language set to english. 

Tested with Chrome webdriver. 

## Available functions:
    Login
    Logout
    Set facebook language to english
    Check if facebook language is set to english
	Get short versions of text of posts in profile/fanpage/group, includes images and like count
	Get full version of a post or story and some of the comments, includes images and like count
    Get links to all profiles that has liked a post
    Get members of a group

## Basic usage example:
```
from FacebookWebBot import *
bot=FacebookBot()
bot.set_page_load_timeout(10)
bot.login("your@email.com","yourpassword")
group_posts = bot.getShortPosts(url=https://www.facebook.com/groups/<facebookgroup_id>/, deep=10)
posts_and_comments = []
for post in group_posts:
    if('story.php?story_fbid=' in post.linkToMore or '/groups/' in post.linkToMore):
        posts_and_comments = posts_and_comments+bot.getFullPostWithComments(url=post.linkToMore)
postsToJsonFile(posts_and_comments, filename=('posts_and_comments', path='folder')
```

## Know issues:
    * Timeout on pages where images won't load.
    * Not getting date from all posts
    * Full posts: Story, from who, to who, text sometimes gone. 

## Dependencies:
    * Python 3.4
    * Selenium 
    * Webdriver
