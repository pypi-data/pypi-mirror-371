from typing import Callable, Optional


class HandlerWrapper:
    def __init__(self):
        self.handler: Optional[Callable] = None

    def __call__(self, func: Callable):
        self.handler = func
        return func
