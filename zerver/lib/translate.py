import re
from translate import Translator


def extract_emojis(text):
    emoji_pattern = r'[^\u0000-\u007F]+'
    return ''.join(c for c in text if re.match(emoji_pattern, c))


def remove_links(message):
    link_pattern = r'http[s]?://\S+'
    return re.sub(link_pattern, '', message)


def translate_message(message, target_language):
    # Extract emojis from the message
    emojis = extract_emojis(message)

    # Remove links from the message and replace them with placeholders
    message_without_links = remove_links(message)
    links = re.findall(r'http[s]?://\S+', message)
    for link in links:
        message_without_links = message_without_links.replace(link, f'<link_placeholder_{links.index(link)}>')

    # Remove <p> tags from the message and replace them with placeholders
    message_without_p_tags = message_without_links.replace('<p>', '').replace('</p>', '<p_placeholder>')

    # Translate the message without <p> tags using the translate module
    translator = Translator(to_lang=target_language)
    translated_message_without_p_tags = translator.translate(message_without_p_tags)

    # Restore the <p> tags in the translated message
    translated_message = translated_message_without_p_tags.replace('<p_placeholder>', '<p>')

    # Reinsert emojis back into the translated message
    for i, emoji_char in enumerate(emojis):
        translated_message = translated_message.replace(f'<emoji_placeholder_{i}>', emoji_char)

    # Replace the placeholders with the original links
    for i, link in enumerate(links):
        translated_message = translated_message.replace(f'<link_placeholder_{i}>', link)

    return translated_message
