from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class StateDataFilter(Filter):
    def __init__(self, data_key, data_value):
        self.data_key = data_key
        self.data_value = data_value

    async def __call__(
            self, message: Message, state: FSMContext, *args, **kwargs
    ):
        state_data = await state.get_data()
        return state_data.get(self.data_key) == self.data_value
