import os
import sys
import time
import unittest
from random import randint

from pytter import (
    Client, Credentials
)


def wait_rand():
    r = randint(0, 30)
    print('=== WAITING {} SECONDS BEFORE EXECUTING TEST ==='.format(r))
    time.sleep(r)

class ClientTest(unittest.TestCase):
    
    TEST_IMG            = 'https://proxy.duckduckgo.com/iu/?u=https%3A%2F%2Fblog.golang.org%2Fgophergala%2Ffancygopher.jpg'
    TEST_TXT            = 'Hey, was geht ab!'
    TEST_HT             = 'justatestbo12738123123'
    TEST_CTX            = '{} #{}'.format(TEST_TXT, TEST_HT)
    TEST_USER_NAME      = 'zekroTJA'
    TEST_USER_ID        = '2337066550'
    TEST_USER_SET_IDS   = ['2337066550', '1425765498']
    TEST_USER_SET_NAMES = ['luxtracon', 'h0denharald']

    def setUp(self):
        self.travis_mode = not not os.environ.get('travis_ci_mode')

        self.sent_tweets = []
        self.credentials = Credentials(
            consumer_key=os.environ.get('tw_consumer_key'),
            consumer_secret=os.environ.get('tw_consumer_secret'),
            access_token_key=os.environ.get('tw_access_token_key'),
            access_token_secret=os.environ.get('tw_access_token_secret')
        )

    def tearDown(self):
        client = Client(self.credentials)
        for t in self.sent_tweets:
            time.sleep(1)
            try: 
                client.status_delete(t.id)
            except:
                pass

    def test_init(self):
        if self.travis_mode: wait_rand()
        
        client = Client(self.credentials)
        self.assertIsNotNone(client)

    def test_status_update_and_delete(self):
        if self.travis_mode: wait_rand()

        client = Client(self.credentials)
        res = client.status_update(self.TEST_CTX, media=self.TEST_IMG)
        self.assertIsNotNone(res)
        self.sent_tweets.append(res)
        self.assertTrue(res.text.startswith(self.TEST_CTX))
        self.assertEqual(res.entities.hashtags[0], self.TEST_HT)
        self.assertIsNotNone(res.entities.media[0])

        res = res.delete()
        self.assertIsNotNone(res)

    def test_status(self):
        if self.travis_mode: wait_rand()

        client = Client(self.credentials)
        res = client.status_update(self.TEST_CTX)
        self.assertIsNotNone(res)
        self.sent_tweets.append(res)
        rec = client.status(res.id)
        self.assertEqual(res.text, rec.text)

    def test_statuses(self):
        if self.travis_mode: wait_rand()
        
        client = Client(self.credentials)
        res_t1 = client.status_update('my tweet 1')
        self.sent_tweets.append(res_t1)
        res_t2 = client.status_update('my tweet 2')
        self.sent_tweets.append(res_t2)
        rec = client.statuses((res_t1.id, res_t2.id, 1231231))
        print(res_t1.id, res_t2.id, rec)
        self.assertIsNotNone(rec)
        self.assertEqual(len(rec), 3)
        self.assertEqual(rec[res_t1.id_str].text, res_t1.text)
        self.assertEqual(rec[res_t2.id_str].text, res_t2.text)
        self.assertIsNone(rec['1231231'])

    def test_retweet_unretweet(self):
        if self.travis_mode: wait_rand()
        
        client = Client(self.credentials)
        o_t = client.status_update('this will be retweeted by me!')
        self.sent_tweets.append(o_t)
        rt = o_t.retweet()
        self.assertIsNotNone(rt)
        rt.un_retweet()
        self.assertIsNotNone(rt)

    def test_retweets(self):
        if self.travis_mode: wait_rand()
        
        client = Client(self.credentials)
        o_t = client.status_update('and this will also be retweeted by me!')
        self.sent_tweets.append(o_t)
        o_t.retweet()
        rts = o_t.retweets()
        self.assertIsNotNone(rts)
        self.assertEqual(len(rts), 1)
        # TODO: expand test

    def test_user(self):
        if self.travis_mode: wait_rand()

        client = Client(self.credentials)

        u_by_id = client.user(id=self.TEST_USER_ID)
        self.assertIsNotNone(u_by_id)
        u_by_name = client.user(screen_name=self.TEST_USER_NAME)
        self.assertIsNotNone(u_by_name)

        self.assertEqual(u_by_id.id_str, u_by_name.id_str)
        self.assertEqual(u_by_id.username, u_by_name.username)

    def test_users(self):
        if self.travis_mode: wait_rand()

        client = Client(self.credentials)

        users = client.users(
            ids=self.TEST_USER_SET_IDS)
        self.assertIsNotNone(users)
        u_1_id = self.TEST_USER_SET_IDS[0]
        u_2_id = self.TEST_USER_SET_IDS[1]
        self.assertEqual(users[u_1_id].id_str, u_1_id)
        self.assertEqual(users[u_1_id].id_str, u_1_id)
        self.assertEqual(users[u_2_id].id_str, u_2_id)
        self.assertEqual(users[u_2_id].id_str, u_2_id)

        users = client.users(
            screen_names=self.TEST_USER_SET_NAMES)
        self.assertIsNotNone(users)
        u_1_id = self.TEST_USER_SET_NAMES[0]
        u_2_id = self.TEST_USER_SET_NAMES[1]
        self.assertEqual(users[u_1_id].username, u_1_id)
        self.assertEqual(users[u_1_id].username, u_1_id)
        self.assertEqual(users[u_2_id].username, u_2_id)
        self.assertEqual(users[u_2_id].username, u_2_id)


if __name__ == '__main__':
    unittest.main()