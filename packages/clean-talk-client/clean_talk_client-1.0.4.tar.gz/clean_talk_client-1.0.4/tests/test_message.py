import unittest
from clean_talk_client.message import Message
from clean_talk_client.exception.clean_talk_exception import CleanTalkException

class TestMessage(unittest.TestCase):
    def test_valid_message(self):
        msg = Message('id123', 'Hello world')
        self.assertEqual(msg.get_message_id(), 'id123')
        self.assertEqual(msg.get_text(), 'Hello world')

    def test_empty_message_id(self):
        with self.assertRaises(CleanTalkException):
            Message('', 'Hello world')

    def test_whitespace_message_id(self):
        # Should raise exception for whitespace-only message_id
        with self.assertRaises(CleanTalkException):
            Message('   ', 'Hello')

    def test_empty_text(self):
        with self.assertRaises(CleanTalkException):
            Message('id123', '')

    def test_whitespace_text(self):
        # Should raise exception for whitespace-only text
        with self.assertRaises(CleanTalkException):
            Message('id123', '   ')

if __name__ == '__main__':
    unittest.main()
