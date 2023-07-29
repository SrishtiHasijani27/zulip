import re
import emoji
from translate import Translator


def extract_emojis(text):
    return ''.join(c for c in text if c in emoji.UNICODE_EMOJI)


def translate_message(text, target_language_code):
    # Extract emojis from the original text
    emojis = extract_emojis(text)

    # Remove emojis from the text
    text_without_emojis = ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)

    # Translate the text without emojis
    translator = Translator(to_lang=target_language_code)
    translated_text = translator.translate(text_without_emojis)

    # Reinsert emojis into the translated text
    translated_message = ''.join(
        [a + b if b in emoji.UNICODE_EMOJI else a for a, b in zip(translated_text, emojis)])

    return translated_message
