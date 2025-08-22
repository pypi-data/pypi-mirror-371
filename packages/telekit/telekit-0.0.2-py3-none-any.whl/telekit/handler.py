from typing import Callable

from telebot.types import Message # type: ignore
import telebot # type: ignore

from .chain import Chain
from .user import User


class Handler:
    
    bot: telebot.TeleBot

    # def __init__(self, message: telebot.types.Message):
    #     super().__init__(message)
    
    @classmethod
    def init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot

        for handler in cls.handlers:
            handler.init_handler(bot)

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the message handler
        """
        pass

    def __init__(self, message: Message):
        self.message: Message = message
        self.chain: Chain | None = None
        self.user = User(self.message.chat.id, self.message.from_user)
        self._chain_factory: Callable[[], Chain] = Chain.get_chain_factory(self.message.chat.id)
        self._children_factory: Callable[[Chain | None], Chain] = Chain.get_children_factory(self.message.chat.id)

    def get_chain(self) -> Chain:
        self.chain = self._chain_factory()
        return self.chain
    
    def get_child(self, parent: Chain | None = None) -> Chain:
        if parent is None:
            parent = self.chain

        self.chain = self._children_factory(self.chain)
        return self.chain

    handlers: list[type['Handler']] = []

    def __init_subclass__(cls, **kwargs): # type: ignore
        super().__init_subclass__(**kwargs)
        Handler.handlers.append(cls)