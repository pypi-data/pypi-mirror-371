import inspect

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_navigation.filters.statedata import StateDataFilter
from aiogram_navigation.reply.replymenu import ReplyMenu, ReplyButton
from aiogram_navigation.utils.handlerwrapper import HandlerWrapper


class ReplyNavigation:
    """
    Library main class, used for creating reply keyboard aiogram_navigation menus.
    """

    def __init__(self, *menus: ReplyMenu):
        self.menus = menus

        self._id_menu_map: dict[str, ReplyMenu] = {}
        self._prepare_menus()

        self.router = Router()
        self._bind_router()

    async def start(self, menu_id: str, message: Message, state: FSMContext, text: str | None = None):
        await self._id_menu_map[menu_id].start(message, state, text=text)

    def _bind_router(self):
        for menu in self.menus:
            for column in menu.buttons:
                for button in column:
                    self.validate_button(button)
                    self._bind_button(menu, button)

    def validate_button(self, button: ReplyButton):
        if button.navigate_to_menu_id and button.navigate_to_menu_id not in self._id_menu_map:
            raise ValueError(f"Menu \"{button.navigate_to_menu_id}\" not found")

    def _bind_button(self, menu: ReplyMenu, button: ReplyButton):
        @self.router.message(
            F.text == button.text,
            StateDataFilter("menu_id", menu.menu_id)
        )
        async def _(message: Message, state: FSMContext, *args, **kwargs):
            if button.navigate_to_menu_id:
                await self._id_menu_map[button.navigate_to_menu_id].start(message, state)
            elif button.handler:
                handler = button.handler
                if isinstance(button.handler, HandlerWrapper):
                    handler = button.handler.handler
                params = inspect.signature(handler).parameters
                call_kwargs = {k: v for k, v in {**kwargs, "state": state}.items() if k in params}
                await handler(message, *args, **call_kwargs)
            else:
                raise ValueError("No handler or navigate_to_menu_id specified for button")

    def _prepare_menus(self):
        for menu in self.menus:
            self._id_menu_map[menu.menu_id] = menu
