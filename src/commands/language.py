"""
Language command - Change transcription language
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.core.command import CallbackCommand


class LanguageCommand(CallbackCommand):
    """Handle /language command"""

    @property
    def name(self) -> str:
        return "language"

    @property
    def description(self) -> str:
        return "Change language"

    @property
    def menu_icon(self) -> str:
        return "🌐"

    def get_callback_patterns(self) -> list[str]:
        return ["lang_"]

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show language selection buttons"""
        current_lang = self.state.get_language()

        keyboard = [
            [
                InlineKeyboardButton(
                    "🇬🇧 English" + (" ✓" if current_lang == "en" else ""), callback_data="lang_en"
                )
            ],
            [
                InlineKeyboardButton(
                    "🇧🇬 Bulgarian" + (" ✓" if current_lang == "bg" else ""), callback_data="lang_bg"
                )
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🌐 Select transcription language:", reply_markup=reply_markup
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle language selection"""
        query = update.callback_query
        await query.answer()

        lang_code = query.data.replace("lang_", "")
        self.state.set_language(lang_code)

        lang_names = {"en": "English", "bg": "Bulgarian"}

        lang_name = lang_names.get(lang_code, lang_code)
        await query.edit_message_text(f"✅ Language set to: {lang_name}")
        self.logger.info(f"Language set to {lang_code}")
