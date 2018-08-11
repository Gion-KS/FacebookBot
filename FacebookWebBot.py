# coding: utf-8
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import json

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

class Person():
    """Basic class for people's profiles"""

    def __init__(self):
        self.name = ""
        self.profileLink = ""
        self.addLink = ""

    def __str__(self):
        s = ""
        s += self.name + ":\n"
        s += "Profile Link: " + self.profileLink
        if self.addLink != "":
            s += "Addlink ->: " + self.addLink
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
        if(debug is False):
            options.add_argument('headless')
        webdriver.Chrome.__init__(self, executable_path=pathToWebdriver, chrome_options=options)

    def get(self, url):
        """The make the driver go to the url but reformat the url if is for facebook page"""
        super().get(mfacebookToBasic(url))

    def login(self, email, password):
        """Log to facebook using email (str) and password (str)"""

        url = "https://mbasic.facebook.com"
        self.get(url)
        email_element = self.find_element_by_name("email")
        email_element.send_keys(email)
        pass_element = self.find_element_by_name("pass")
        pass_element.send_keys(password)
        pass_element.send_keys(Keys.ENTER)
        if self.find_element_by_class_name("bi"):
            self.find_element_by_class_name("bp").click();
        try:
            self.find_element_by_name("xc_message")
            print("Logged in")
            return True
        except NoSuchElementException as e:
            print("Fail to login")
            return False

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

    def getPostInGroup(self, url, deep=2, moreText="Visa fler inlägg"):
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
                post.posterName = a[1].text
                try:
                    post.numLikes = int(a[3].text.split(" ")[0])
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
                    post.linkToMore = a[6].get_attribute('href')
                except IndexError:
                    post.linkToMore = 0
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
        """Return a list of members of a group(url) as a list:Person iterat deep(int) times"""

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
                person = Person()
                h3 = b.find_elements_by_tag_name("h3")
                person.name = h3[0].text
                person.profileLink = h3[0].find_element_by_tag_name(
                    "a").get_attribute('href')
                try:
                    person.addLink = b.find_elements_by_tag_name(
                        "a")[1].get_attribute('href')  # puede haber error
                except Exception:
                    # print("No Addlink")
                    pass
                members.append(person)
                # more = self.find_element_by_id("m_more_item").find_element_by_tag_name("a").get_attribute('href')
                # self.get(more)
                # print(more)
        # print(len(members))
        return members

    def getPostInProfile(self, profileURL, deep=3, moreText="Visa fler inlägg"):
        """Return a list of Posts in a profile/fanpage , setup the "moreText" using your language, theres not elegant way to handle that"""
        posts_list = []
        url = '{}?v=timeline'.format(profileURL)
        self.get(url)

        #years_elements = self.find_elements_by_xpath("//div[@class='h']/a[contains(., '20')]")
        years_elements = self.find_elements_by_xpath("//div[@class='bu gc']/a[contains(., '20')]")
        years = [y.text for y in years_elements]
        years.append('9999')  # append one dummy year for the extraction of the last year in the list
        more_button_exists = True
        for year in years:
            while more_button_exists:
                for d in range(deep):
                    try:
                        articles = self.find_elements_by_xpath("//div[@role='article']")
                        for p in articles:
                            post = Post()
                            try:
                                #post.text=str(article.text)
                                #posts_list.append(post)
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
                                post.privacy = bot.title
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
                                #posts_list.append(str(article.text))
                            except Exception as e:
                                print("1p ERROR: " + str(e))
                        # press more if more button exists
                        try:
                            show_more_link_element = self.find_element_by_partial_link_text(moreText)
                            show_more_link = show_more_link_element.get_attribute('href')
                            self.get(show_more_link)
                        except NoSuchElementException:
                            # if more button does not exist go to the next year
                            more_button_exists = False
                            if year is not '9999':
                                year_link_element = self.find_element_by_xpath("//div[@class='h']/a[text()='{}']".format(year))
                                year_link = year_link_element.get_attribute('href')
                                self.get(year_link)

                    except TimeoutError as e:
                        print("2p Timeout:", str(e))
                        time.sleep(1)
                    except BaseException as e:
                        print("3p ERROR:", str(e))

            return posts_list
