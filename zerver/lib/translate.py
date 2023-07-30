import re
from googletrans import Translator
import emoji

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
    message_without_emojis = ''.join(c for c in message if c not in emoji.UNICODE_EMOJI)

    # Translate the message without emojis using the Google Translate API
    translator = Translator()
    translated_message_without_emojis = translator.translate(message_without_emojis, dest=target_language).text

    # Reinsert emojis back into the translated message
    translated_message = ''.join([a + b if b in emoji.UNICODE_EMOJI else a for a, b in zip(translated_message_without_emojis, emojis)])

    # Replace the placeholders with the original links
    for i, link in enumerate(links):
        translated_message = translated_message.replace(f'<link_placeholder_{i}>', link)

    return translated_message

