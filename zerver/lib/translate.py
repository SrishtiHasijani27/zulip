import re
import demoji
from translate import Translator


def extract_emojis(text):
    emojis = demoji.findall(text)
    return ''.join(emojis)


def translate_message(message, target_language):
    # Regular expression to identify links in the message
    link_pattern = r'http[s]?://\S+'

    # Find all links in the message and replace them with placeholders
    links = re.findall(link_pattern, message)
    for link in links:
        message = message.replace(link, f'<link_placeholder_{links.index(link)}>')

    # Extract emojis from the message
    emojis_in_text = extract_emojis(message)

    # Remove emojis from the message
    message_without_emojis = demoji.replace(message, '')

    # Translate the message without emojis using the translate module
    translator = Translator(to_lang=target_language)
    translated_message_without_emojis = translator.translate(message_without_emojis)

    # Reinsert emojis back into the translated message
    translated_message = demoji.replace(translated_message_without_emojis, emojis_in_text)

    # Replace the placeholders with the original links
    for i, link in enumerate(links):
        translated_message = translated_message.replace(f'<link_placeholder_{i}>', link)

    return translated_message
