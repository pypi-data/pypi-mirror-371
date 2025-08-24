import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_navigation.filters.statedata import StateDataFilter


class TestStateDataFilter(unittest.TestCase):
    def setUp(self):
        self.message = MagicMock(spec=Message)
        self.state = FSMContext(storage=MagicMock(), key=MagicMock())

    def test_filter_success(self):
        async def run_test():
            self.state.get_data = AsyncMock(return_value={"menu_id": "main"})
            filter_obj = StateDataFilter("menu_id", "main")
            result = await filter_obj(self.message, self.state)
            self.assertTrue(result)

        asyncio.run(run_test())

    def test_filter_failure_wrong_value(self):
        async def run_test():
            self.state.get_data = AsyncMock(return_value={"menu_id": "other_menu"})
            filter_obj = StateDataFilter("menu_id", "main")
            result = await filter_obj(self.message, self.state)
            self.assertFalse(result)

        asyncio.run(run_test())

    def test_filter_failure_key_not_in_state(self):
        async def run_test():
            self.state.get_data = AsyncMock(return_value={"other_key": "some_value"})
            filter_obj = StateDataFilter("menu_id", "main")
            result = await filter_obj(self.message, self.state)
            self.assertFalse(result)

        asyncio.run(run_test())

    def test_filter_failure_empty_state(self):
        async def run_test():
            self.state.get_data = AsyncMock(return_value={})
            filter_obj = StateDataFilter("menu_id", "main")
            result = await filter_obj(self.message, self.state)
            self.assertFalse(result)

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
