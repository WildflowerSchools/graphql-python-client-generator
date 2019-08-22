from unittest import TestCase

from mock import patch, MagicMock

from gqlpycgen import client

CLIENT_CREDS = {
    'token_uri': 'test.com',
    'audience': 'the queen',
    'client_id': 'foo',
    'client_secret': 'bar',
}



class ClientTest(TestCase):

    def test_client_init1(self):
        c = client.Client(uri='test.com', accessToken='ajkdsfjaksfh')

        self.assertEqual(c.uri, 'test.com')
        self.assertEqual(c.accessToken, 'ajkdsfjaksfh')
        self.assertEqual(c.headers["Authorization"], 'bearer ajkdsfjaksfh')
        self.assertIsNone(c.client_credentials)

    @patch('requests.post')
    def test_client_init2(self, post_mk):
        c = client.Client(uri='test.com', client_credentials=CLIENT_CREDS)

        post_mk.assert_called_once_with('test.com', {
            "audience": 'the queen',
            "grant_type": "client_credentials",
            "client_id": 'foo',
            "client_secret": 'bar',
        })

    @patch('requests.post')
    def test_client_init3(self, post_mk):
        c = client.Client(uri='test.com')
        post_mk.assert_not_called()

    @patch('requests.post', return_value=None)
    def test_client_init4(self, post_mk):
        with self.assertRaises(Exception):
            c = client.Client(uri='test.com', client_credentials=CLIENT_CREDS)

    @patch('requests.post')
    def test_client_init5(self, post_mk):
        post_mk.return_value.json = MagicMock()
        post_mk.return_value.json.return_value.get.return_value = None
        with self.assertRaises(Exception):
            c = client.Client(uri='test.com', client_credentials=CLIENT_CREDS)

    @patch('requests.post')
    def test_client_exec1(self, post_mk):
        c = client.Client(uri='test.com', client_credentials=CLIENT_CREDS)
        c.execute
