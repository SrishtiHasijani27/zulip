import re
from translate import Translator
import langid


def extract_emojis(text):
    emoji_pattern = r'[^\u0000-\u007F]+'
    return ''.join(c for c in text if re.match(re.escape(emoji_pattern), c))


def remove_links(message):
    link_pattern = r'http[s]?://\S+'
    return re.sub(link_pattern, '', message)


def detect_source_language(message):
    detected_language, _ = langid.classify(message)
    print(f"Detected Language: {detected_language}")
    return detected_language


def translate_message(message, target_language):
    # Detect the source language of the message
    source_language = detect_source_language(message)

    # Extract emojis from the message
    emojis = extract_emojis(message)

    # Remove links from the message and replace them with placeholders
    message_without_links = remove_links(message)
    links = re.findall(r'http[s]?://\S+', message)
    for link in links:
        message_without_links = message_without_links.replace(link, f'<link_placeholder_{links.index(link)}>')

    # Remove <p> tags from the message and replace them with placeholders
    message_without_p_tags = message_without_links.replace('<p>', '').replace('</p>', '<p_placeholder>')

    try:
        # Translate the message without <p> tags using the translate module
        translator = Translator(from_lang=source_language, to_lang=target_language)

        # Split the message into smaller chunks (max 500 characters each)
        chunk_size = 500
        chunks = [message_without_p_tags[i:i + chunk_size] for i in
                  range(0, len(message_without_p_tags), chunk_size)]

        translated_chunks = []
        for chunk in chunks:
            translated_chunks.append(translator.translate(chunk))

        # Restore the <p> tags in the translated message
        translated_message = ''.join(translated_chunks).replace('<p_placeholder>', '<p>')

        # Reinsert emojis back into the translated message
        for i, emoji_char in enumerate(emojis):
            translated_message = translated_message.replace(f'<emoji_placeholder_{i}>', emoji_char)

        # Replace the placeholders with the original links
        for i, link in enumerate(links):
            translated_message = translated_message.replace(f'<link_placeholder_{i}>', link)

        # Add a line dynamically informing about the languages being translated
        info_line = f"Translating message from {source_language} to {target_language}:"
        translated_message = f"{info_line}<br>{translated_message}"

    except Exception as e:
        # If translation fails, post the original message
        print(f"Translation Error: {e}")
        translated_message = f"Message cannot be translated. Original message:\n{message}"

    return translated_message
