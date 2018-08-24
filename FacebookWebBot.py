# coding: utf-8
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import json
import datetime
import urllib.parse as urlparse
from urllib.parse import urlencode
import urllib

selfProfile = "https://mbasic.facebook.com/profile.php?fref=pb"

def mfacebookToBasic(url):
    """Reformat a url to load mbasic facebook instead of regular facebook, 
    return the same string if the url don't contains facebook"""

    if "m.facebook.com" in url:
        return url.replace("m.facebook.com", "mbasic.facebook.com")
    elif "www.facebook.com" in url:
        return url.replace("www.facebook.com", "mbasic.facebook.com")
    else:
        return url

def facebookDateTimeConverter(date_string):
    """ Function to convert strings containing date from facebook and convert
    them to datetime format. 
    Function is language dependent and currently implemented for Swedish. 

    Does not cover : 
    * 1å (1 year), 
    * 10d (10 days)
    * 1 jan
    """
    now = datetime.datetime.now()
    # remove microseconds for compability with mysql
    now = now.replace(microsecond=0)
    months_of_the_year = ['januari','februari','mars','april','maj','juni',\
    'juli','augusti','september','oktober','november','december']


    if('tim' in date_string or ' h' in date_string):
        if(len(date_string.split(' ')) > 2):
            # longer format -- e.g. "för 6 timmar sedan"
            hours_ago = int(date_string.split(' ')[1])
        else:
            # short format -- eg. "6 tim" or "6 h"
            hours_ago = int(date_string.split(' ')[0])
        date = now-datetime.timedelta(hours=hours_ago)
    elif('Alldeles nyss' in date_string):
        date = now
    elif('min' in date_string):
        if(len(date_string.split(' ')) > 2):
            # longer format -- e.g. "för 6 timmar sedan"
            minutes_ago = int(date_string.split(' ')[1])
        else:
            # short format -- eg. 6 tim
            minutes_ago = int(date_string.split(' ')[0])
        date = now-datetime.timedelta(minutes=minutes_ago)
    elif("Igår" in date_string): 
        # Yesterday
        hour = int(date_string.split(' ')[2].split(':')[0])
        minute = int(date_string.split(' ')[2].split(':')[1])
        dateholder = datetime.datetime(year=now.year, month=now.month,\
        day=now.day, hour=hour, minute=minute )
        date = dateholder-datetime.timedelta(hours = 24)
    else:
        day = int(date_string.split(' ')[0])
        month = months_of_the_year.index(date_string.split(' ')[1])+1
        if(len(date_string.split(' ')) > 4): 
           # posts from other years than the current one have the year in 
           # the string
           year = int(date_string.split(' ')[2])
        else:
            # posts from this year does not have the year in the string
            year = now.year 
        time = date_string.split('kl. ')[1]
        hour = int(time.split(':')[0])
        minute = int(time.split(':')[1])
        date = datetime.datetime(year=year, month=month, day=day, hour=hour,\
        minute=minute)
    return date

class Profile():
    """Basic class for people's profiles"""

    def __init__(self):
        self.name = ""
        self.profileLink = ""

    def __str__(self):
        s = ""
        s += self.name + ":\n"
        s += "Profile Link: " + self.profileLink
        return s

    def __repr__(self):
        return self.__str__()

class Post():
    """Class to contain information about a post"""

    def __init__(self):
        self.posterName = ""
        self.text = ""
        self.numLikes = 0
        self.time = None
        # timetext for debugging
        self.timetext = ""
        self.privacy = ""
        self.posterLink = ""
        self.linkToComment = ""
        self.linkToLike = ""
        self.linkToLikers = ""
        self.linkToReport = ""
        self.groupLink = ""
        self.linkToShare = ""
        self.linkToMore = ""
        self.numComments = 0
        self.postId = 0
        self.commentId = 0
        self.subCommentId = 0
        self.pageId = 0
        self.images = []
        self.originalContentId = 0
        self.isShare = 0

        # possibly replace text with message and story
        self.message = ""
        self.story = ""

    def toDict(self):
        return self.__dict__.copy()

    def fromDict(self, d):
        self.__dict__ = d.copy()

    def from_json(self, j):
        self.fromDict(json.loads(j))

    def to_json(self):
        # "default = str" converts datetime in time to str. bc of serialzation
        return json.dumps(self.toDict(), default=str)

    def __str__(self):
        s = "\nPost by " + self.posterName + ": "
        s += " - Story: " + self.story + "\n-"
        s += self.text + "\n"
        s += "Likes: " + str(self.numLikes) + " - "
        s += "Comments: " + str(self.numComments) + " - "
        s += str(self.time) + " "
        s += " - Privacy: " + self.privacy + "\n-"
        s += "\n Comment -> " + self.linkToComment + "\n"
        return s

    def __repr__(self):
        return self.__str__()

class FacebookBot(webdriver.Chrome):
    """Main class for browsing facebook"""

    def __init__(self, pathToWebdriver='/usr/local/bin/chrome', debug=True):
        self.pathToWebdriver = pathToWebdriver
        options = webdriver.ChromeOptions()
        # cookies are stored in user-date
        options.add_argument("user-data-dir=selenium_cookies") 
        if(debug is False):
            # headless means no open chrome window
            options.add_argument('headless')
        webdriver.Chrome.__init__(self, executable_path=pathToWebdriver, chrome_options=options)

    def get(self, url):
        """The make the driver go to the url but reformat the url if is for facebook page"""
        super().get(mfacebookToBasic(url))

    def logged_in(self):
        try:
            self.find_element_by_name("xc_message")
            print("Logged in")
            return True
        except NoSuchElementException as e:
            print("Fail to login")
            return False

    def login(self, email, password):
        """Log to facebook using email (str) and password (str)"""
        url = "https://mbasic.facebook.com"
        self.get(url)
        if(self.logged_in()):
            print('Logged in with cookie!')
            return True
        else:
            email_element = self.find_element_by_name("email")
            email_element.send_keys(email)
            pass_element = self.find_element_by_name("pass")
            pass_element.send_keys(password)
            pass_element.send_keys(Keys.ENTER)
            if self.find_element_by_class_name("bi"):
                # bp is dont remember
                # bo is remember login in cookie
                self.find_element_by_class_name("bo").click()
                #self.find_element_by_class_name("bp").click()
            return logged_in()

    def logout(self):
        """Log out from Facebook"""
        #  TODO: seems to be not working

        url = "https://mbasic.facebook.com/logout.php?h=AffSEUYT5RsM6bkY&t=1446949608&ref_component=mbasic_footer&ref_page=%2Fwap%2Fhome.php&refid=7"
        try:
            self.get(url)
            return True
        except Exception as e:
            print("Failed to log out ->\n", e)
            return False

    def getPostInGroup(self, url, deep=2, moreText="Visa fler"):
        """Get a list of posts (list:Post) in group url(str) iterating 
        deep(int) times in the group
        pass moreText depending of your language, i couldn't find a elegant 
        solution for this"""

        self.get(url)
        posts = []
        for n in range(deep):
            print("Searching, deep ",n)
            articles = self.find_elements_by_xpath("//div[@role='article']")
            for article in articles:
                print("Debug: article index: ", articles.index(article))
                post = self.parseFacebookArticle(article)
                if(post is not None):
                    posts.append(post)
            try:
                more = self.find_element_by_partial_link_text(
                    moreText).get_attribute('href')
                self.get(more)
            # self.find_element_by_partial_link_text(moreText)
            except Exception as e:
                print(e)
                print("Can't get more posts")
        return posts

    def getGroupMembers(self, url, deep=3, start=0):
        """Return a list of members of a group(url) as a list:Profile iterat deep(int) times"""

        seeMembersUrl = url + "?view=members&amp;refid=18"
        groupId = url.split("groups/")[1]
        step = 28
        r = "https://mbasic.facebook.com/browse/group/members/?id=$GROUPID$&start=$n$"
        rg = r.replace("$GROUPID$", groupId)
        members = []
        for d in range(start, start + deep):
            url = rg.replace("$n$", str(d * 30))
            self.get(url)
            # print(self.current_url)
            p = self.find_elements_by_class_name("p")  # BK cada profile
            for b in p:
                Profile = Profile()
                h3 = b.find_elements_by_tag_name("h3")
                Profile.name = h3[0].text
                Profile.profileLink = h3[0].find_element_by_tag_name(
                    "a").get_attribute('href')
                try:
                    Profile.addLink = b.find_elements_by_tag_name(
                        "a")[1].get_attribute('href')  # puede haber error
                except Exception:
                    # print("No Addlink")
                    pass
                members.append(Profile)
                # more = self.find_element_by_id("m_more_item").find_element_by_tag_name("a").get_attribute('href')
                # self.get(more)
                # print(more)
        # print(len(members))
        return members

    def getPostInProfile(self, profileURL, deep=3, moreText="Visa fler inlägg"):
        """Return a list of Posts in a profile/fanpage , setup the "moreText" 
        using your language, theres not elegant way to handle that"""
        #url = '{}?v=timeline'.format(profileURL)
        params = {'v':'timeline'}
        url_parts = list(urlparse.urlparse(profileURL))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query)
        url = urlparse.urlunparse(url_parts)
        posts = []

        try: 
            self.get(url)
        except Exception as e:
            print(e.__doc__)
            print(e.message)
            print("""wtf exception is this TimeoutError? Catch it and remove 
                this except Exception as e to a explicit catch""")
            return posts

        for d in range(deep):
            try:
                articles = self.find_elements_by_xpath("//div[@role='article']")
                for article in articles:
                    try:
                        post = self.parseFacebookArticle(article)
                        if(post is not None):
                            posts.append(post)
                    except Exception as e:
                        print("1p ERROR: " + str(e))
                # press more if more button exists
                try:
                    show_more_link_element = self.find_element_by_partial_link_text(moreText)
                    show_more_link = show_more_link_element.get_attribute('href')
                    self.get(show_more_link)
                except NoSuchElementException:
                    print('no more button')
                    break

            except TimeoutError as e:
                print("2p Timeout:", str(e))
                time.sleep(1)
            except BaseException as e:
                print("3p ERROR:", str(e))

        return posts

    def getFullPostWithComments(self, url, deep=3, moreText="Visa fler svar",\
     likersText='lämnat reaktioner inklusive'):
        """ Get all Comments on a post returned as a list of posts """
        self.get(url)
        posts_collected = []
        try: 
            main_story_element = self.find_element_by_xpath(\
                "//div[contains(@class, 'z ba')]")
        except NoSuchElementException:
            return posts_collected

        post = self.parseDataft(main_story_element.get_attribute("data-ft"))   
        
        post.poster = main_story_element.find_element_by_xpath("//h3").text
        post.posterLink = main_story_element.find_element_by_xpath("//h3")\
                .find_element_by_tag_name("a").get_attribute("href")
        post.text = main_story_element.text
        # Part of the text string next to the likes link
        try: 
            like_link_element = self.find_element_by_xpath(
                "//a[./div/div[contains(@aria-label, '" + likersText + "')]]")
            post.linkToLikers  = like_link_element.get_attribute("href")
        except: 
            print("no link to likers")
            post.linkToLikers = ''

        posts_collected.append(post)

        # Comments
        #comment_elements = self.find_elements_by_class_name("dv")
        comment_elements = []
        number_ids = self.find_elements_by_xpath("//div[@id]")

        for e in number_ids:
            try:
                ep = int(e.get_attribute('id'))
                #print(ep, "seems like a comment!")
                comment_elements.append(e)
            except ValueError: 
                #print("thats not a comment element, not an int -- continue")
                continue

        for comment_element in comment_elements: 
            comment = Post()
            comment.pageId = post.pageId
            comment.postId = post.postId
            comment.commentId = comment_element.get_attribute("id")
            try: 
                comment.posterName = comment_element.find_element_by_tag_name("h3").text
                comment.posterLink = comment_element.find_element_by_tag_name("h3")\
                .find_element_by_tag_name("a").get_attribute("href")
            except NoSuchElementException:
                # Has no h3 => is prob a subcomment
                continue
            try: 
                comment.time = facebookDateTimeConverter(comment_element\
                    .find_element_by_tag_name("abbr").text)
                comment.timetext = comment_element.find_element_by_tag_name("abbr").text
            except NoSuchElementException:
                continue
            except ValueError:
                comment.time = None
            comment.text = comment_element.text
            posts_collected.append(comment)

        # TODO: Click show more answers button
        # looks like => id="see_next_1845692485515656"

        return posts_collected

    def getProfilesFromPosts(self, posts):
        """ Get unique (by name) Profiles from a list of Posts """
        posternames = [] # unique
        profiles = []
        for post in posts:
            if post.posterName not in posternames: 
                profile = Profile()
                profile.name = post.posterName
                profile.profileLink = post.posterLink
                profiles.append(profile)
                posternames.append(post.posterName)
        return profiles

    def getProfilesFromLikes(self, likes_url, moreText='Visa mer',\
        profiles=[]):
        """ 
        Get Profiles from a page where a Posts likes are listed. 
        Recusive method calls itself if there are more likes in more button
        """
        self.get(likes_url)
        profile_elements = self.find_elements_by_tag_name("li")

        for pe in profile_elements:
            profile = Profile()
            try:
                profile_link_element = pe.find_element_by_xpath(".//h3/a")
            except NoSuchElementException:
                # were at more button
                break
            profile.name = profile_link_element.text
            profile.profileLink = profile_link_element.get_attribute("href")
            profiles.append(profile)
        try: 
            more_link = self.find_element_by_link_text('Visa mer').get_attribute("href")
            par = urllib.parse.parse_qs(urlparse.urlparse(more_link).query)
            # set limit to the count
            params = {'limit':par['total_count'][0]}
            url_parts = list(urllib.parse.urlparse(more_link))
            query = dict(urllib.parse.parse_qsl(url_parts[4]))
            query.update(params)
            url_parts[4] = urllib.parse.urlencode(query)
            url_all_likes = urllib.parse.urlunparse(url_parts)
            return self.getProfilesFromLikes(likes_url=url_all_likes, profiles=profiles)
        except NoSuchElementException: 
            # no "show more" link / button
            print("no show more link / button when searching likes list")
            return profiles
        
    def parseFacebookArticle(self, article):
        """
        Parse a facebook article get a Post in return. 

        Takes:   Article, a selenium web object
        Returns: Post
        """
        dataft = article.get_attribute("data-ft")
        
        if(dataft is not None):
            post = self.parseDataft(dataft)
        else:
            # if no data-ft attribute is found this is probably an embedded
            # shared post in another post. both are articles and thereby 
            # passed through if iterated over articles. 
            return None

        if(post.time is None):
            try: 
                post.time = facebookDateTimeConverter(article\
                    .find_element_by_tag_name("abbr").text)
                post.timetext = article.find_element_by_tag_name("abbr").text
            except NoSuchElementException:
                post.time = None
            except ValueError:
                post.time = None

        post.story = article.find_elements_by_tag_name("h3")[0].text
        a = article.find_elements_by_tag_name("a")
        post.posterName = a[0].text
        try:
            post.numLikes = article.find_element_by_xpath(\
                "//a[contains(@aria-label, '" + 'reaktioner, inklusive'\
                + "')]").text
        except ValueError:
            post.numLikes = 0
        except IndexError:
            post.numLikes = 0
        except NoSuchElementException:
            post.numLikes = 0
            
        try: 
            post.text = article.find_element_by_tag_name("p").text
        except NoSuchElementException:
            post.text = ''
        #post.privacy = self.title
        post.posterLink = a[0].get_attribute('href')   
        try:
            post.linkToComment = a[2].get_attribute('href')
        except IndexError:
            post.linkToComment = ''
        try:
            post.linkToLike = a[4].get_attribute('href')
        except IndexError: 
            post.linkToLike = ''

        # TODO: comments count does not work
        try:
            post.numComments = int(a[5].text.split(" ")[0])
        except ValueError:
            post.numComments = 0
        except IndexError: 
            post.numComments = 0
        post.linkToLikers = a[1].get_attribute('href')
        try:
            post.linkToMore = article.find_element_by_link_text(\
                'Visa hela händelsen').get_attribute("href")
        except IndexError:
            post.linkToMore = ''

        # embedded article indicates shared post
        embedded_articles = article.find_elements_by_xpath(\
            ".//div[@role='article']")
        if(len(embedded_articles) > 0):
            # Add shared post contents
            post.text = post.text + 'Shared content:\n' + embedded_articles[0].text
            post.isShare = 1

        return post

    def parseDataft(self, dataft):
        """
        Parse datafield and return post filled with values from dataft.
        
        Takes:   data-ft attribute value (string)
        Returns: Post
        """
        post = Post()
        data = json.loads(dataft)

        if('top_level_post_id' in data):
            post.postId = data['top_level_post_id']

        if('page_id' in data):
            post.pageId = data['page_id']


        if('page_insights' in data):
            if('post_context' in data):
                unix_time = data['page_insights'][str(\
                    data['page_id'])]['post_context']['publish_time']
                post.time  = datetime.datetime.fromtimestamp(
                        int(unix_time)
                    ).strftime('%Y-%m-%d %H:%M:%S')
                post.timetext = unix_time
            post.isShare = data['page_insights'][str(\
                data['page_id'])]['dm']['isShare']

        if('photo_attachments_list' in data):
            post.images = data['photo_attachments_list']
        
        if('photo_id' in data):
            post.images.append(data['photo_id'])

        if('original_content_id' in data):
            post.originalContentId = data['original_content_id']

        return post
