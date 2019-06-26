import unittest
import os

from pytter import (
    Client, Credentials
)

class ClientTest(unittest.TestCase):
    
    TEST_IMG = 'https://proxy.duckduckgo.com/iu/?u=https%3A%2F%2Fblog.golang.org%2Fgophergala%2Ffancygopher.jpg'
    TEST_TXT = 'Hey, was geht ab!'
    TEST_HT  = 'justatestbo12738123123'
    TEST_CTX = '{} #{}'.format(TEST_TXT, TEST_HT)

    def setUp(self):
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
            try: 
                client.status_delete(t.id)
            except:
                pass

    def test_init(self):
        client = Client(self.credentials)
        self.assertIsNotNone(client)

    def test_status_update_and_delete(self):
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
        client = Client(self.credentials)
        res = client.status_update(self.TEST_CTX)
        self.assertIsNotNone(res)
        self.sent_tweets.append(res)
        rec = client.status(res.id)
        self.assertEqual(res.text, rec.text)

    def test_statuses(self):
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


if __name__ == '__main__':
    unittest.main()