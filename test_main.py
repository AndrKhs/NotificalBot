import unittest
from unittest.mock import patch, Mock
import asyncio


from main import send_message, send_photo, schedule_notifications


class TestMain(unittest.TestCase):
    @patch('main.bot.send_message')
    def test_send_message(self, mock_bot_send_message):
        chat_id = 123456789
        text = "Test Message"
        asyncio.run(send_message(chat_id, text))
        mock_bot_send_message.assert_called_once_with(chat_id, text, reply_markup=None)

    @patch('main.bot.send_photo')
    def test_send_photo(self, mock_bot_send_photo):
        chat_id = 123456789
        img = "test.jpg"
        asyncio.run(send_photo(chat_id, img))
        mock_bot_send_photo.assert_called_once_with(chat_id, img, reply_markup=None)

    @patch('main.send_message')
    @patch('main.send_photo')
    @patch('main.datetime')
    @patch('main.sqlite3')
    async def test_schedule_notifications(self, mock_sqlite3, mock_datetime, mock_send_message):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite3.connect.return_value = mock_conn

        mock_now = Mock()
        mock_now.strftime.return_value = "09:00"
        mock_datetime.datetime.now.return_value = mock_now

        mock_sleep = Mock()
        asyncio.sleep = mock_sleep

        mock_cursor.execute.side_effect = [
            [("123456789",)],
            [("Test Event", "Test Description", "01.01.2022")]
        ]

        await schedule_notifications()

        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_with("SELECT userID FROM users")
        mock_send_message.assert_called_with("123456789", "Сегодняшние события:")
        mock_send_message.assert_called_with("123456789", "Название: Test Event")
