import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import get_unread_emails_count_by_sender, list_folders, mark_emails_as_read
from fastapi import HTTPException

class TestApp(unittest.TestCase):

    @patch('app.imaplib.IMAP4_SSL')
    def test_unread_count_by_sender(self, mock_imap):
        mock_mail = MagicMock()
        mock_mail.search.return_value = ("OK", [b'1 2 3'])
        mock_mail.fetch.side_effect = [
            ("OK", [(None, b'From: sender1@example.com')]),
            ("OK", [(None, b'From: sender2@example.com')]),
            ("OK", [(None, b'From: sender1@example.com')])
        ]
        mock_imap.return_value = mock_mail

        result = get_unread_emails_count_by_sender(mock_mail)
        self.assertEqual(result, {'sender1@example.com': 2, 'sender2@example.com': 1})

    @patch('app.imaplib.IMAP4_SSL')
    def test_unread_count_by_sender_failure(self, mock_imap):
        mock_mail = MagicMock()
        mock_mail.search.return_value = ("OK", [b'1 2 3'])
        mock_mail.fetch.side_effect = Exception("Failed to fetch email headers.")
        mock_imap.return_value = mock_mail

        with self.assertRaises(HTTPException):
            get_unread_emails_count_by_sender(mock_mail)

    @patch('app.imaplib.IMAP4_SSL')
    def test_list_folders(self, mock_imap):
        mock_mail = MagicMock()
        mock_mail.list.return_value = ("OK", [b'(\\HasNoChildren) "/" "INBOX"', b'(\\HasNoChildren) "/" "Sent"'])
        mock_imap.return_value = mock_mail

        result = list_folders(mock_mail)
        self.assertEqual(result, ['INBOX', 'Sent'])

    @patch('app.imaplib.IMAP4_SSL')
    def test_list_folders_failure(self, mock_imap):
        mock_mail = MagicMock()
        mock_mail.list.return_value = ("NO", [])
        mock_imap.return_value = mock_mail

        with self.assertRaises(HTTPException):
            list_folders(mock_mail)

    @patch('app.imaplib.IMAP4_SSL')
    def test_mark_emails_as_read(self, mock_imap):
        mock_mail = MagicMock()
        mock_mail.store.return_value = ("OK", [b'1', b'2', b'3'])
        mock_imap.return_value = mock_mail

        result = mark_emails_as_read(mock_mail, ['1', '2', '3'])
        self.assertEqual(result, 3)

if __name__ == '__main__':
    unittest.main()