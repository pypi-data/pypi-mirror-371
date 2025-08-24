# Aiogram Navigation

[![PyPI](https://img.shields.io/pypi/v/aiogram-navigation)](https://pypi.org/project/aiogram-navigation/)
[![Python Version](https://img.shields.io/pypi/pyversions/aiogram-navigation)](https://pypi.org/project/aiogram-navigation/)
[![License](https://img.shields.io/pypi/l/aiogram-navigation)](https://github.com/vladimir-batsura/aiogram-navigation/blob/main/LICENSE)

A simple and intuitive library for creating complex reply navigation menus in aiogram bots with minimal code.

## Features

- 🔄 Easy navigation between menus
- ⌨️ Simple button creation and handling
- 🧠 Built-in state management
- 🔧 Flexible handler binding
- 📦 Lightweight and easy to integrate

## Requirements

- Python >= 3.10
- aiogram >= 3.0.0

## Installation

```bash
pip install aiogram-navigation
```

## Quick Start

### Basic Concepts

The library provides three main classes:

- `ReplyNavigation` - Main class for managing navigation between menus
- `ReplyMenu` - Represents a menu with text and buttons
- `ReplyButton` - Individual buttons that can navigate to menus or bind to handlers

### Simple Example

```python
from aiogram_navigation.reply import ReplyNavigation, ReplyMenu, ReplyButton

# Create navigation with menus
navigation = ReplyNavigation(
    ReplyMenu(
        menu_id="main_menu",
        text="Welcome to Main Menu!",
        buttons=[
            [
                ReplyButton("Go to Profile", navigate_to="profile_menu"),
                ReplyButton("Settings", navigate_to="settings_menu"),
            ]
        ]
    ),
    ReplyMenu(
        menu_id="profile_menu",
        text=lambda message: f"Hello, {message.from_user.full_name}!",
        buttons=[
            [
                ReplyButton("Back", navigate_to="main_menu"),
            ]
        ]
    ),
    ReplyMenu(
        menu_id="settings_menu",
        text="Settings Menu",
        buttons=[
            [
                ReplyButton("Back", navigate_to="main_menu"),
            ]
        ]
    ),
)
```

## Usage Guide

### 1. Setting Up Navigation

First, create your menus and navigation:

```python
from aiogram_navigation.reply import ReplyNavigation, ReplyMenu, ReplyButton

# Create your menus
main_menu = ReplyMenu(
    menu_id="main",
    text="Main Menu",
    buttons=[
        [
            ReplyButton("Profile", navigate_to="profile"),
            ReplyButton("Settings", navigate_to="settings"),
        ]
    ]
)

profile_menu = ReplyMenu(
    menu_id="profile",
    text="Profile Menu",
    buttons=[
        [
            ReplyButton("Back", navigate_to="main"),
        ]
    ]
)

# Create navigation system
navigation = ReplyNavigation(main_menu, profile_menu)
```

### 2. Binding Handlers to Buttons

There are several ways to bind handlers to buttons:

#### Method 1: Using Button as Decorator

```python
from aiogram_navigation.utils import HandlerWrapper

# Create button
button = ReplyButton("Click Me")

# Use button as decorator
@button
async def my_handler(message):
    await message.answer("Button clicked!")
```

#### Method 2: Passing Handler Directly

```python
async def my_handler(message):
    await message.answer("Button clicked!")

button = ReplyButton("Click Me", handler=my_handler)
```

#### Method 3: Using HandlerWrapper as Decorator

```python
from aiogram_navigation.utils import HandlerWrapper

# Create handler wrapper
handler_wrapper = HandlerWrapper()

# Create button with wrapper
button = ReplyButton("Click Me", handler=handler_wrapper)

# Use wrapper as decorator
@handler_wrapper
async def my_handler(message):
    await message.answer("Button clicked!")
```

### 3. Integrating with Your Bot

```python
import asyncio
from os import environ
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_navigation.middleware import NavigatorMiddleware, Navigator
from aiogram_navigation.reply import ReplyNavigation, ReplyMenu, ReplyButton

TOKEN = environ.get("TOKEN")
dp = Dispatcher()

# Create your navigation
navigation = ReplyNavigation(
    ReplyMenu(
        menu_id="start",
        text=lambda message: f"Hi, {message.from_user.full_name}!",
        buttons=[
            [
                ReplyButton("Profile", navigate_to="profile")
            ]
        ]
    ),
    ReplyMenu(
        menu_id="profile",
        text="Profile Menu",
        buttons=[
            [
                ReplyButton("Back", navigate_to="start"),
            ]
        ]
    )
)

# Start command
@dp.message(Command("start"))
async def command_start_handler(
    message: Message,
    navigator: Navigator,  # Available through middleware
    state: FSMContext
) -> None:
    # Start navigation with navigator (recommended)
    await navigator.start("start")
    
    # Alternative ways:
    # await navigation.start("start", message, state)
    # await menu.start(message, state)

# Setup dispatcher
async def main() -> None:
    bot = Bot(token=TOKEN)
    dp.include_router(navigation.router)  # Include navigation router
    dp.message.middleware.register(NavigatorMiddleware(navigation))  # Required middleware
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Example

Here's a more comprehensive example showing profile management:

```python
from aiogram_navigation.reply import ReplyButton, ReplyMenu, ReplyNavigation
from aiogram_navigation.utils import HandlerWrapper

# Handler wrapper for profile functionality
fill_profile_handler = HandlerWrapper()

# Profile view button
view_profile = ReplyButton(text="View profile")

# Main menu
MAIN_MENU = ReplyMenu(
    menu_id="main",
    text="Bot Main menu",
    buttons=[
        [
            view_profile,
            ReplyButton(
                text="Edit profile",
                handler=fill_profile_handler
            ),
        ]
    ]
)

# Profile navigation
profile_navigation = ReplyNavigation(
    MAIN_MENU,
    ReplyMenu(
        menu_id="profile",
        text=lambda message: f"Profile of {message.from_user.full_name}",
        buttons=[
            [
                ReplyButton(
                    text="Back to menu",
                    navigate_to="main"
                )
            ]
        ]
    )
)

# Start menu
START_MENU = ReplyMenu(
    menu_id="start",
    text=lambda message: f"✋ {message.from_user.full_name}, welcome to the bot!",
    buttons=[
        [
            ReplyButton(
                text="Fill profile",
                handler=fill_profile_handler
            )
        ]
    ]
)

start_navigation = ReplyNavigation(START_MENU)
```

## Contributing

Contributions are welcome! Feel free to open issues and pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.