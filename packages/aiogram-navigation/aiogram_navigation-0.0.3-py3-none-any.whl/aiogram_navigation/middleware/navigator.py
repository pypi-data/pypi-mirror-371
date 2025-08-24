from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_navigation.reply import ReplyNavigation


class Navigator:
    def __init__(self, message: Message, state: FSMContext, navigation: ReplyNavigation):
        self._message = message
        self._state = state
        self._navigation = navigation

    async def start(self, menu_id: str, text: str | None = None):
        await self._navigation.start(menu_id, self._message, self._state, text=text)


class NavigatorMiddleware(BaseMiddleware):
    def __init__(self, navigation: ReplyNavigation):
        self._navigation = navigation

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        navigator = Navigator(event, data["state"], self._navigation)
        data["navigator"] = navigator
        return await handler(event, data)
