import re
from translate import Translator


def translate_message(message, target_language):
    # Regular expression to identify links in the message
    link_pattern = r'http[s]?://\S+'
    # Regular expression to identify emojis in the message
    emoji_pattern = r'[^\w\s,]'
    print(f"Original message is ", message)

    # Find all links in the message and replace them with placeholders
    links = re.findall(link_pattern, message)
    for link in links:
        message = message.replace(link, f'<link_placeholder_{links.index(link)}>')

    # Find all emojis in the message and replace them with placeholders
    emojis = re.findall(emoji_pattern, message)
    for emoji in emojis:
        message = message.replace(emoji, '')
        print(f"message after emoji is :",message)

    # Translate the message using the translate module
    translator = Translator(to_lang=target_language)
    translated_message = translator.translate(message)

    # Replace the placeholders with the original links and emojis
    for i, link in enumerate(links):
        translated_message = translated_message.replace(f'<link_placeholder_{i}>', link)

    return translated_message
