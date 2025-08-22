# TeleKit Library

## Overview

**TeleKit** is a Python library designed to simplify common tasks for developers working with Telegram bots or Python projects in general.  
It provides tools for:  

- Managing data with `Vault`, a lightweight interface for SQLite databases.  
- Organizing and processing text data using `chapters`, which allows converting `.txt` files into Python dictionaries for easy access.  
- Creating modular, reusable handlers and chains for structured code.  

The library is designed to reduce boilerplate code and make Python development more efficient.

---

## Quick Guide

Here is an example of defining a handler using TeleKit:

```python
import telebot.types
import telekit
import typing


class StartHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the message handler for the '/start' command.
        """
        @bot.message_handler(commands=['start'])
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        chain: telekit.Chain = self.get_chain()
         
        chain.sender.set_title("Hello")
        chain.sender.set_message("Welcome to the bot! Click the button below to start interacting.")
        chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")
        chain.sender.set_effect(chain.sender.Effect.PARTY)

        def counter_factory() -> typing.Callable[[int], int]:
            count = 0
            def counter(value: int=1) -> int:
                nonlocal count
                count += value
                return count
            return counter
        
        click_counter = counter_factory()

        @chain.inline_keyboard({"⊕": 1, "⊖": -1}, row_width=2)
        def _(message: telebot.types.Message, value: int) -> None:
            chain.sender.set_message(f"You clicked {click_counter(value)} times")
            chain.edit_previous_message()
            chain.send()

        chain.send()
```

---

## Chapters Example

TeleKit allows you to store large texts or structured information in `.txt` files and access them as Python dictionaries:

**`help.txt`**:

```txt
# intro
Welcome to TeleKit library. Here are the available commands:

# entry
/entry — Example command for handling input

# about
TeleKit is a general-purpose library for Python projects.
```

Usage in Python:

```python
import telekit

chapters: dict[str, str] = telekit.chapters.read("help.txt")

print(chapters["intro"])
# Output: "Welcome to TeleKit library. Here are the available commands:"

print(chapters["entry"])
# Output: "/entry — Example command for handling input"
```

This approach allows separating content from code and accessing text sections programmatically.

---

## Features

- Easy-to-use modular handlers and chains for structured project code.  
- `Vault` for persistent storage of Python data structures in SQLite.  
- `Chapters` for converting `.txt` files into Python dictionaries.  
- Lightweight and minimal dependencies, fully compatible with Python 3.12 and higher.

---

## Getting Started With Server / Main.py

```python

# Your server.py or main.py

import telebot
import telekit

from . import handlers # All your handlers

bot = telebot.TeleBot("TOKEN")
telekit.Server(bot).polling()
```

# Getting Started With Handlers

```python

# handlers/start.py

import telebot.types
import telekit
import typing


class StartHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the message handler for the '/start' command.
        """
        @bot.message_handler(commands=['start'])
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        chain: telekit.Chain = self.get_chain()
         
        chain.sender.set_title("Hello")
        chain.sender.set_message("Welcome to the bot! Click the button below to start interacting.")
        chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")
        chain.sender.set_effect(chain.sender.Effect.PARTY)

        def counter_factory() -> typing.Callable[[int], int]:
            count = 0
            def counter(value: int=1) -> int:
                nonlocal count
                count += value
                return count
            return counter
        
        click_counter = counter_factory()

        @chain.inline_keyboard({"⊕": 1, "⊖": -1}, row_width=2)
        def _(message: telebot.types.Message, value: int) -> None:
            chain.sender.set_message(f"You clicked {click_counter(value)} times")
            chain.edit_previous_message()
            chain.send()

        chain.send()
```

## Developer ##
Telegram: [@TeleKitLib](https://t.me/TeleKitLib) 