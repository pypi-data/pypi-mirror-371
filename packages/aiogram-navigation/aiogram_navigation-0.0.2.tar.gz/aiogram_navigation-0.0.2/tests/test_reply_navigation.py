import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, User, Chat

from aiogram_navigation.reply import ReplyMenu, ReplyButton, ReplyNavigation


class TestReplyNavigation(unittest.TestCase):
    def setUp(self):
        self.bot = MagicMock()
        self.bot.id = 123456789
        self.user = User(id=1, is_bot=False, first_name="Test")
        self.chat = Chat(id=1, type="private")

        self.storage = MemoryStorage()
        self.state = FSMContext(storage=self.storage, key=StorageKey(
            chat_id=self.chat.id,
            user_id=self.user.id,
            bot_id=self.bot.id,
        ))

        self.menu1 = ReplyMenu(
            menu_id="main",
            text="Main Menu",
            buttons=[
                [
                    ReplyButton(text="Go to Menu 2", navigate_to="menu2"),
                    ReplyButton(text="Action", handler=self.action_handler)
                ]
            ]
        )
        self.menu2 = ReplyMenu(
            menu_id="menu2",
            text="Menu 2",
            buttons=[[ReplyButton(text="Back", navigate_to="main")]]
        )

        self.navigation = ReplyNavigation(self.menu1, self.menu2)

    async def action_handler(self, message: Message, state: FSMContext):
        pass  # This is a mock handler

    def test_initialization(self):
        self.assertEqual(len(self.navigation.menus), 2)
        self.assertIn("main", self.navigation._id_menu_map)
        self.assertIn("menu2", self.navigation._id_menu_map)
        self.assertEqual(self.navigation._id_menu_map["main"], self.menu1)
        self.assertEqual(self.navigation._id_menu_map["menu2"], self.menu2)

    @patch('aiogram_navigation.reply.replymenu.ReplyMenu.start', new_callable=AsyncMock)
    def test_start_navigation(self, mock_menu_start):
        async def run_test():
            message = Message(message_id=1, date=1, chat=self.chat, from_user=self.user, text="/start")
            await self.navigation.start("main", message, self.state)
            mock_menu_start.assert_called_once_with(message, self.state, text=None)

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
