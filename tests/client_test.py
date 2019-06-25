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
        self.credentials = Credentials(
            consumer_key=os.environ.get('tw_consumer_key'),
            consumer_secret=os.environ.get('tw_consumer_secret'),
            access_token_key=os.environ.get('tw_access_token_key'),
            access_token_secret=os.environ.get('tw_access_token_secret')
        )

    def test_init(self):
        client = Client(self.credentials)
        self.assertIsNotNone(client)

    def test_status_update_and_delete(self):
        client = Client(self.credentials)
        res = client.status_update(self.TEST_CTX, media=self.TEST_IMG)
        self.assertIsNotNone(res)
        self.assertTrue(res.text.startswith(self.TEST_CTX))
        self.assertEqual(res.entities.hashtags[0], self.TEST_HT)
        self.assertIsNotNone(res.entities.media[0])

        res = res.delete()
        self.assertIsNotNone(res)

    def test_status(self):
        client = Client(self.credentials)
        res = client.status_update(self.TEST_CTX)
        self.assertIsNotNone(res)
        rec = client.status(res.id)
        self.assertEqual(res.text, rec.text)
        rec.delete()


if __name__ == '__main__':
    unittest.main()