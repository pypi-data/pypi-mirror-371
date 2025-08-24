import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User, Chat

from aiogram_navigation.reply import ReplyMenu, ReplyButton


class TestReplyMenu(unittest.TestCase):
    def setUp(self):
        self.bot = MagicMock()
        self.chat = Chat(id=1, type="private")
        self.message = Message(message_id=1, date=1, chat=self.chat,
                               from_user=User(id=1, is_bot=False, first_name="Test"))
        self.state = FSMContext(storage=MagicMock(), key=MagicMock())
        self.state.update_data = AsyncMock()

    def test_reply_button_initialization(self):
        button = ReplyButton(text="Test", navigate_to="next_menu")
        self.assertEqual(button.text, "Test")
        self.assertEqual(button.navigate_to_menu_id, "next_menu")
        self.assertIsNone(button.handler)

    def test_reply_menu_initialization(self):
        button = ReplyButton(text="Test", navigate_to="next_menu")
        menu = ReplyMenu(menu_id="main", text="Main Menu", buttons=[[button]])
        self.assertEqual(menu.menu_id, "main")
        self.assertEqual(menu.text, "Main Menu")
        self.assertEqual(menu.buttons, [[button]])

    def test_reply_menu_callable_text(self):
        def dynamic_text(message: Message, state: FSMContext):
            return f"Hello, {message.from_user.first_name}!"

        button = ReplyButton(text="Test", navigate_to="next_menu")
        menu = ReplyMenu(menu_id="main", text=dynamic_text, buttons=[[button]])
        self.assertEqual(menu.text, dynamic_text)

    @patch('aiogram.types.Message.answer', new_callable=AsyncMock)
    def test_start_menu_with_string_text(self, mock_answer):
        async def run_test():
            button = ReplyButton(text="Test", navigate_to="next_menu")
            menu = ReplyMenu(menu_id="main", text="Main Menu", buttons=[[button]])
            await menu.start(self.message, self.state)

            self.state.update_data.assert_called_once_with(menu_id="main")
            mock_answer.assert_called_once()
            self.assertIn("Main Menu", mock_answer.call_args[0])

        asyncio.run(run_test())

    @patch('aiogram.types.Message.answer', new_callable=AsyncMock)
    def test_start_menu_with_callable_text(self, mock_answer):
        async def run_test():
            def dynamic_text(message: Message, **kwargs):
                return f"Hello, {message.from_user.first_name}!"

            button = ReplyButton(text="Test", navigate_to="next_menu")
            menu = ReplyMenu(menu_id="main", text=dynamic_text, buttons=[[button]])
            await menu.start(self.message, self.state)

            self.state.update_data.assert_called_once_with(menu_id="main")
            mock_answer.assert_called_once()
            self.assertIn("Hello, Test!", mock_answer.call_args[0])

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
