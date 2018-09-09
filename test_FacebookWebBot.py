import unittest
import FacebookWebBot
import datetime

class TestFacebookWebBot(unittest.TestCase):

    def setUp(self):
        #self.bot = FacebookWebBot()
        pass

    def tearDown(self):
       pass

    def test_facebookDateTimeConverter(self):
        this_year = datetime.datetime.now().year
        self.assertEqual(FacebookWebBot.facebookDateTimeConverter('1 hrs'),
        datetime.datetime.now().replace(microsecond=0)-datetime.timedelta(hours=1))

        self.assertEqual(FacebookWebBot.facebookDateTimeConverter('1 hr'),
        datetime.datetime.now().replace(microsecond=0)-datetime.timedelta(hours=1))

        self.assertEqual(FacebookWebBot.facebookDateTimeConverter('11 mins'),
        datetime.datetime.now().replace(microsecond=0)-datetime.timedelta(minutes=11))

        self.assertEqual(FacebookWebBot.facebookDateTimeConverter('1 min'),
        datetime.datetime.now().replace(microsecond=0)-datetime.timedelta(minutes=1))

        self.assertEqual(\
            FacebookWebBot.facebookDateTimeConverter('June 16 at 11:16 AM'),\
            datetime.datetime(this_year, month = 6, \
            day=16, hour=11, minute=16))
            
        self.assertEqual(\
            FacebookWebBot.facebookDateTimeConverter('June 16 at 11:16 PM'),\
            datetime.datetime(this_year, month = 6, \
            day=16, hour=23, minute=16))

        #November 4, 2014 at 2:00 PM
        self.assertEqual(\
            FacebookWebBot.facebookDateTimeConverter('November 4, 2014 at 2:00 PM'),\
            datetime.datetime(year=2014, month = 11, \
            day=4, hour=14, minute=00))

        #Aug 22 at 1:55 PM        
        self.assertEqual(\
            FacebookWebBot.facebookDateTimeConverter('Aug 22 at 1:55 PM'),\
            datetime.datetime(year=this_year, month = 8, \
            day=22, hour=13, minute=55))
        # Aug 22, 2013 at 1:55 PM
        self.assertEqual(\
            FacebookWebBot.facebookDateTimeConverter('Aug 22, 2013 at 1:55 PM'),\
            datetime.datetime(year=2013, month = 8, \
            day=22, hour=13, minute=55))

        #Yesterday at 4:40 PM
        self.assertEqual(\
            FacebookWebBot.facebookDateTimeConverter('Yesterday at 4:40 PM'),\
            datetime.datetime.now().replace(hour=16, \
                minute=40, microsecond=0, second=0)-datetime.timedelta(days=1)\
            )


        # Sunday at 9:38 AM
        # Weekday only appears to be presented the day before yesterday
        """self.assertEqual(\
            FacebookWebBot.facebookDateTimeConverter('Sunday at 9:38 AM'),\
            datetime.datetime(year=2018, month = 8, \
                day=26, hour=9, minute=38))"""

        #Jun 9
        self.assertEqual(\
            FacebookWebBot.facebookDateTimeConverter('Jun 9'),\
            datetime.datetime(year=this_year, month = 6, \
            day=9, hour=0, minute=0))

        #Apr 13, 2014        
        # TODO: testcase

if __name__ == '__main__':
    unittest.main()

