# coding: utf-8
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import json
import datetime
import urllib.parse as urlparse
from urllib.parse import urlencode

selfProfile = "https://mbasic.facebook.com/profile.php?fref=pb"

def mfacebookToBasic(url):
    """Reformat a url to load mbasic facebook instead of regular facebook, return the same string if
    the url don't contains facebook"""

    if "m.facebook.com" in url:
        return url.replace("m.facebook.com", "mbasic.facebook.com")
    elif "www.facebook.com" in url:
        return url.replace("www.facebook.com", "mbasic.facebook.com")
    else:
        return url

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
        self.__str__()

class Post():
    """Class to contain information about a post"""

    def __init__(self):
        self.posterName = ""
        self.text = ""
        self.numLikes = 0
        self.time = ""
        self.privacy = ""
        self.posterLink = ""
        self.linkToComment = ""
        self.linkToLike = ""
        self.linkToLikers = ""
        self.linkToReport = ""
        self.groupLink = ""
        self.linkToShare = ""
        self.linkToMore = ""
        self.numComents = 0
        self.postId = 0
        self.commentId = 0
        self.subCommentId = 0
        self.pageId = 0

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
        return json.dumps(self.toDict())

    def __str__(self):
        s = "\nPost by " + self.posterName + ": "
        s += self.text + "\n"
        s += "Likes: " + str(self.numLikes) + " - "
        s += "Comments: " + str(self.numComents) + " - "
        s += self.time + " "
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
        # seems to be not working

        url = "https://mbasic.facebook.com/logout.php?h=AffSEUYT5RsM6bkY&t=1446949608&ref_component=mbasic_footer&ref_page=%2Fwap%2Fhome.php&refid=7"
        try:
            self.get(url)
            return True
        except Exception as e:
            print("Failed to log out ->\n", e)
            return False

    def getPostInGroup(self, url, deep=2, moreText="Visa fler"):
        """Get a list of posts (list:Post) in group url(str) iterating deep(int) times in the group
        pass moreText depending of your language, i couldn't find a elegant solution for this"""

        self.get(url)
        posts = []
        for n in range(deep):
            print("Searching, deep ",n)
            post = Post()
            articles = self.find_elements_by_xpath("//div[@role='article']")
            for article in articles:
                print(articles.index(article))
                post = Post()
                p = article
                #print(p.text)
                a = p.find_elements_by_tag_name("a")
                post.posterName = a[0].text
                try:
                    #post.numLikes = int(a[3].text.split(" ")[0])
                    post.numLikes = p.find_element_by_xpath("//a[contains(@aria-label, 'reaktioner, inklusive')]").text
                except ValueError:
                    post.numLikes = 0
                try: 
                    post.text = p.find_element_by_tag_name("p").text
                except NoSuchElementException:
                    post.text = ''
                try:
                    post.time = p.find_element_by_tag_name("abbr").text
                except NoSuchElementException:
                    post.time = '' 
                # p.text.split("· ")[1].split("\n")[0]
                post.privacy = self.title
                post.posterLink = a[0].get_attribute('href')
                # p.find_element_by_class_name("du").get_attribute('href')
                post.linkToComment = a[2].get_attribute('href')
                try:
                    post.linkToLike = a[4].get_attribute('href')
                except IndexError: 
                    post.linkToLike = ''
                try:
                    post.numComents = int(a[5].text.split(" ")[0])
                except ValueError:
                    post.numComents = 0
                except IndexError: 
                    post.numComents = 0
                # post.linkToShare = a[5].get_attribute('href')
                post.linkToLikers = a[1].get_attribute('href')
                try:
                    #post.linkToMore = a[6].get_attribute('href') 
                    post.linkToMore = p.find_element_by_link_text('Visa hela händelsen').get_attribute("href")
                except IndexError:
                    post.linkToMore = ''
                except NoSuchElementException:
                    # prob a shared post inside another post... 
                    post.linkToMore = ''
                    continue
                if post not in posts:
                    posts.append(post)
            try:
                more = self.find_element_by_partial_link_text(
                    moreText).get_attribute('href')
                self.get(more)
            # self.find_element_by_partial_link_text(moreText)
            except Exception as e:
                print(e)
                print(" Can't get more posts")
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
        """Return a list of Posts in a profile/fanpage , setup the "moreText" using your language, theres not elegant way to handle that"""
        posts = []

        #url = '{}?v=timeline'.format(profileURL)
        params = {'v':'timeline'}
        url_parts = list(urlparse.urlparse(profileURL))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query)
        url = urlparse.urlunparse(url_parts)

        self.get(url)

        for d in range(deep):
            try:
                articles = self.find_elements_by_xpath("//div[@role='article']")
                for p in articles:
                    post = Post()
                    try:
                        a = p.find_elements_by_tag_name("a")
                        post.posterName = a[0].text
                        try:
                            post.numLikes = int(a[4].text.split(" ")[0])
                        except ValueError:
                            post.numLikes = 0
                        except IndexError:
                            post.numLikes = 0
                        try: 
                            post.text = p.find_element_by_tag_name("p").text
                        except NoSuchElementException:
                            post.text = ''
                        try:
                            post.time = p.find_element_by_tag_name("abbr").text
                        except NoSuchElementException:
                            post.time = '' 
                        # p.text.split("· ")[1].split("\n")[0]
                        post.privacy = self.title
                        post.posterLink = a[0].get_attribute('href')
                        # p.find_element_by_class_name("du").get_attribute('href')
                        try:
                            post.linkToComment = a[2].get_attribute('href')
                        except IndexError:
                            post.linkToComment = ''
                        try:
                            post.linkToLike = a[4].get_attribute('href')
                        except IndexError: 
                            post.linkToLike = ''
                        try:
                            post.numComents = int(a[5].text.split(" ")[0])
                        except ValueError:
                            post.numComents = 0
                        except IndexError: 
                            post.numComents = 0
                        # post.linkToShare = a[5].get_attribute('href')
                        post.linkToLikers = a[1].get_attribute('href')
                        try:
                            post.linkToMore = a[6].get_attribute('href')
                        except IndexError:
                            post.linkToMore = ''
                        if post not in posts:
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

    def getCommentsOnPost(self, url, deep=3, moreText="Visa fler svar"):
        """ Get all Comments on a post returned as a list of posts """
        self.get(url)

        main_story_element = self.find_element_by_xpath("//div[contains(@class, 'z ba')]")
        main_post_info = main_story_element.get_attribute("data-ft")
        main_story_data = json.loads(main_post_info)
        main_story_poster = main_story_element.find_element_by_xpath("//h3")


        posts_collected = []

        post = Post()
        post.postId = main_story_data['top_level_post_id']
        post.pageId = main_story_data['page_id']

        unix_time = main_story_data['page_insights'][str(main_story_data['page_id'])]['post_context']['publish_time']
        post.time  = datetime.datetime.fromtimestamp(
                int(unix_time)
            ).strftime('%Y-%m-%d %H:%M:%S')
        post.poster = main_story_element.find_element_by_xpath("//h3").text
        post.posterLink = main_story_element.find_element_by_xpath("//h3")\
                .find_element_by_tag_name("a").get_attribute("href")
        post.text = main_story_element.text
        posts_collected.append(post)

        # Comments
        #comment_elements = self.find_elements_by_class_name("dv")
        comment_elements = []
        number_ids = self.find_elements_by_xpath("//div[@id]")

        for e in number_ids:
            try:
                ep = int(e.get_attribute('id'))
                print(ep, "seems like a comment!")
                comment_elements.append(e)
            except ValueError: 
                #print("thats not a comment element, not an int -- continue")
                continue

        for comment in comment_elements: 
            post = Post()
            post.pageId = main_story_data['page_id']
            post.postId = main_story_data['top_level_post_id']
            post.commentId = comment.get_attribute("id")
            try: 
                post.posterName = comment.find_element_by_tag_name("h3").text
                post.posterLink = comment.find_element_by_tag_name("h3").find_element_by_tag_name("a").get_attribute("href")
            except NoSuchElementException:
                # Has no h3 => is prob a subcomment
                continue
            try: 
                post.time = comment.find_element_by_tag_name("abbr").text
            except NoSuchElementException:
                continue
            post.text = comment.text
            posts_collected.append(post)

        # TODO: Click show more answers button
        # looks like => id="see_next_1845692485515656"

        return posts_collected

    def getProfilesFromPosts(self, posts):
        """ Get unique profiles from a list of posts """
        profiles = []
        for post in posts:
            profile = Profile()
            profile.name = post.posterName
            profile.profileLink = post.posterLink
            if(profile not in profiles):
                profiles.append(profile)
        return profiles
