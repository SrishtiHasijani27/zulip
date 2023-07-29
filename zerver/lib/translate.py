import re
from translate import Translator


def extract_links(text):
    # Regular expression to identify links in the text
    link_pattern = r'http[s]?://\S+'
    return re.findall(link_pattern, text)


def extract_emojis(text):
    # Regular expression to identify emojis in the text
    emoji_pattern = r'[^\w\s,]'
    return re.findall(emoji_pattern, text)


def replace_links_and_emojis_with_placeholders(text, links, emojis):
    # Replace links with placeholders
    for link in links:
        text = text.replace(link, f'<link_placeholder_{links.index(link)}>')

    # Replace emojis with placeholders
    for emoji in emojis:
        text = text.replace(emoji, f'<emoji_placeholder_{emojis.index(emoji)}>')

    return text


def restore_placeholders_with_links_and_emojis(translated_text, links, emojis):
    # Replace placeholders with links
    for i, link in enumerate(links):
        translated_text = translated_text.replace(f'<link_placeholder_{i}>', link)

    # Replace placeholders with emojis
    for i, emoji in enumerate(emojis):
        translated_text = translated_text.replace(f'<emoji_placeholder_{i}>', emoji)

    return translated_text


def translate_message(text, target_language_code):
    """
    Translates given text string to specified target language using chosen translation API.
    :param text: Input Text String (str)
    :param target_language_code: Target Language Code (e.g., 'es' for Spanish) (str)
    :return translated_text_string: Returns Translated Text String (str)
    """

    # Extract links and emojis from the input text
    links = extract_links(text)
    emojis = extract_emojis(text)

    # Replace links and emojis with placeholders
    text_with_placeholders = replace_links_and_emojis_with_placeholders(text, links, emojis)

    # Use The Chosen Translation API To Translate Message Text From Source To Target Language
    translator = Translator(to_lang=target_language_code)

    # Translate the text with placeholders using the specified target language code
    translated_text_with_placeholders = translator.translate(text_with_placeholders)

    # Restore the original links and emojis in the translated text
    translated_text = restore_placeholders_with_links_and_emojis(translated_text_with_placeholders, links,
                                                                 emojis)

    return translated_text
