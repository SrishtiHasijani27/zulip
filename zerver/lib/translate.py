import re
import emoji
from translate import Translator


def extract_emojis(text):
    emoji_pattern = r'[^\u0000-\u007F]+'
    return ''.join(c for c in text if re.match(emoji_pattern, c))


def translate_message(message, target_language):
    # Regular expression to identify links in the message
    link_pattern = r'http[s]?://\S+'

    # Find all links in the message and replace them with placeholders
    links = re.findall(link_pattern, message)
    for link in links:
        message = message.replace(link, f'<link_placeholder_{links.index(link)}>')

    # Extract and remove emojis from the message
    emojis = extract_emojis(message)
    message_without_emojis = message.encode('ascii', 'ignore').decode()

    # Translate the message without emojis using the translate module
    translator = Translator(to_lang=target_language)
    translated_message = translator.translate(message_without_emojis)

    # Reinsert the emojis back into the translated message (with lowercase)
    for emoji in emojis:
        translated_message += emoji.lower()

    # Replace the placeholders with the original links
    for i, link in enumerate(links):
        translated_message = translated_message.replace(f'<link_placeholder_{i}>', link)

    return translated_message
