# -*- encoding:utf-8 -*-
import time
import traceback
import sys

from . import init
import telebot # type: ignore

# ------------------------------------------
# Entry point
# ------------------------------------------
    
def polling_exception_msg(ex: Exception) -> None:
    tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
    print(f"- Polling cycle error: {ex}.", tb_str, sep="\n\n")

# ------------------------------------------
# Entry point
# ------------------------------------------

__all__ = ["Server"]

class Server:
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        init.init(bot)

    def polling(self):
        while True:
            print("Telekit server is starting polling...")

            try:
                self.bot.polling(none_stop=True)
            except Exception as ex:
                polling_exception_msg(ex)
            finally:
                time.sleep(10)

def example(token: str):
    import telekit.example as example

    example.example_server.run_example(token)