import re
import emoji
from translate import Translator


def extract_emojis(text):
    # Function to extract emojis from the text
    return ''.join(c for c in text if c in emoji.UNICODE_EMOJI)


def translate_messages(message, target_language):
    # Regular expression to identify links in the message
    link_pattern = r'http[s]?://\S+'

    # Find all links in the message and replace them with placeholders
    links = re.findall(link_pattern, message)
    for link in links:
        message = message.replace(link, f'<link_placeholder_{links.index(link)}>')

    # Extract emojis from the message
    emojis = extract_emojis(message)

    # Replace emojis with placeholders
    for emoji_char in emojis:
        message = message.replace(emoji_char, f'<emoji_placeholder_{emojis.index(emoji_char)}>')

    # Translate the message using the translate module
    translator = Translator(to_lang=target_language)
    translated_message = translator.translate(message)

    # Replace the placeholders with the original links and emojis
    for i, link in enumerate(links):
        translated_message = translated_message.replace(f'<link_placeholder_{i}>', link)

    for emoji_char in emojis:
        translated_message = translated_message.replace(f'<emoji_placeholder_{emojis.index(emoji_char)}>',
                                                        emoji_char)

    return translated_message



