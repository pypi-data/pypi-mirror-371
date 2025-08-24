import inspect
from typing import Callable

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from aiogram_navigation.utils.handlerwrapper import HandlerWrapper


class ReplyButton:
    def __init__(
            self,
            text: str,
            handler: HandlerWrapper | Callable | None = None,
            navigate_to: str | None = None,
    ):
        """
        :param text: button text visible to user
        :param handler: aiogram message handler
        :param navigate_to: menu id to navigate to
        """
        self.text = text
        self.handler = handler
        self.navigate_to_menu_id = navigate_to

    def __call__(self, func):
        self.handler = func
        return func


class ReplyMenu:
    def __init__(
            self,
            menu_id: str,
            text: str | Callable,
            buttons: list[list[ReplyButton]]
    ):
        """
        :param menu_id: menu id
        :param text: menu text visible to user
        :param buttons: list of buttons
        """
        self.menu_id = menu_id
        self.text = text
        self.buttons = buttons

    async def start(self, message: Message, state: FSMContext, text: str | None = None, **kwargs):
        await state.update_data(
            menu_id=self.menu_id
        )
        await message.answer(
            _build_text(self.text, message, state, **kwargs) if text is None else text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=button.text
                        ) for button in column
                    ] for column in self.buttons
                ],
                resize_keyboard=True
            )
        )

def _build_text(text: str | Callable, message: Message, state: FSMContext, **kwargs):
    if isinstance(text, Callable):
        params = inspect.signature(text).parameters
        call_kwargs = {k: v for k, v in {**kwargs, "state": state}.items() if k in params}
        return text(message, **call_kwargs)
    return text