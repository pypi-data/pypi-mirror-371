import telebot.types # type: ignore
import telekit
import telekit.snapvault
import telekit.snapvault.snapvault

class User:
    names: telekit.Vault = telekit.Vault(
        path             = "data_base", 
        table_name       = "names", 
        key_field_name   = "user_id", 
        value_field_name = "name"
    )
    
    ages: telekit.Vault = telekit.Vault(
        path             = "data_base", 
        table_name       = "ages", 
        key_field_name   = "user_id", 
        value_field_name = "age"
    )
    
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    def get_name(self, default: str | None=None) -> str | None:
        return self.names.get(self.chat_id, default)

    def set_name(self, value: str):
        self.names[self.chat_id] = value

    def get_age(self, default: int | None=None) -> int | None:
        return self.ages.get(self.chat_id, default)

    def set_age(self, value: int):
        self.ages[self.chat_id] = value
    

class EntryHandler(telekit.Handler):

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the command handler.
        """
        @bot.message_handler(commands=['entry']) # type: ignore
        def handler(message: telebot.types.Message) -> None: # type: ignore
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self._user = User(self.message.chat.id)
        self.entry_name()

    def entry_name(self, message: telebot.types.Message | None=None) -> None:
        prompt: telekit.Chain = self.get_child()
        prompt.set_always_edit_previous_message(True)
         
        prompt.sender.set_title("⌨️ What`s your name?")
        prompt.sender.set_message("Please, send a text message")

        name = self._user.get_name(
            self.user.get_username()
        )
        
        if name:
            prompt.set_entry_suggestions([name])

        @prompt.entry_text(delete_user_response=True) # Text message only (User will not be abled to send photos, stickers, ...)
        def _(message: telebot.types.Message, name: str) -> None:
            received: telekit.Chain = self.get_child()

            received.sender.set_title(f"👋 Bonjour, {name}!")
            received.sender.set_message(f"Is that your name?")

            self._user.set_name(name)

            received.set_inline_keyboard(
                {
                    "« Change": prompt,
                    "Yes »": self.entry_age,
                }, row_width=2
            )

            received.send()

        prompt.send()

    def entry_age(self, message: telebot.types.Message) -> None:
        prompt: telekit.Chain = self.get_child() # Child of `entry_name.<locals>.received` (previous chain)
         
        prompt.sender.set_title("⏳ How old are you?")
        prompt.sender.set_message("Please, send a numeric message")

        @prompt.entry_text(                                 # Text message only (User will not be abled to send photos, stickers, ...)
            filter_message=lambda message, text: text.isdigit() and 0 < int(text) < 130, # Numeric message only
            delete_user_response=True)
        def _(message: telebot.types.Message, text: str) -> None:
            received: telekit.Chain = self.get_child()

            received.sender.set_title(f"😏 {text} years old?")
            received.sender.set_message(f"Noted. Now I know which memes are safe to show you")
            self._user.set_age(int(text))

            received.set_inline_keyboard(
                {
                    "« Change": prompt,
                    "Ok »": self.result,
                }, row_width=2
            )

            received.send()

        prompt.send()

    def result(self, message: telebot.types.Message) -> None:
        result: telekit.Chain = self.get_child() # Child of `entry_age.<locals>.received` (previous chain)
         
        result.sender.set_title("😏 Well well well")
        result.sender.set_message(f"So your name is {self._user.get_name()} and you're {self._user.get_age()}? Fancy!")

        result.set_inline_keyboard({"« Change": self.entry_name})

        result.send()