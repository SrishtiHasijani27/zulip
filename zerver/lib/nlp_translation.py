import torch
import fasttext.util
from transformers import MarianMTModel, MarianTokenizer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import nltk
import numpy as np
from translate import Translator  # Make sure you have the translate module in the same directory
import fasttext  # Install fasttext using `pip install fasttext`
import matplotlib.pyplot as plt  # Importing matplotlib for plotting

# Function for translation
def translate(input_sentence, model_name="Helsinki-NLP/opus-mt-en-fr"):
    # Load the MarianMTModel and MarianTokenizer
    model, tokenizer = load_marianmt_model(model_name)

    # Tokenize the input sentence
    input_ids = tokenizer(input_sentence, return_tensors="pt").input_ids

    # Translate the input sentence
    translated_ids = model.generate(input_ids)
    translated_sentence = tokenizer.decode(translated_ids[0], skip_special_tokens=True)

    return translated_sentence

# Function for loading the MarianMTModel
def load_marianmt_model(model_name="Helsinki-NLP/opus-mt-en-fr"):
    # Download the tokenizer and model
    nltk.download("punkt")
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)

    return model, tokenizer

# Function for calculating BLEU score and average embedding similarity
def evaluate_translation(reference, translated, word_embeddings):
    # Calculate BLEU score using NLTK
    bleu_score = sentence_bleu([reference.split()], translated.split(), smoothing_function=SmoothingFunction().method7)

    # Calculate average embedding similarity
    embeddings_ref = [word_embeddings.get(token, np.zeros(300)) for token in reference.split()]
    embeddings_trans = [word_embeddings.get(token, np.zeros(300)) for token in translated.split()]

    # Calculate cosine similarity and handle zero vectors
    similarity_scores = []
    for emb_ref, emb_trans in zip(embeddings_ref, embeddings_trans):
        if np.all(emb_ref == 0) or np.all(emb_trans == 0):
            similarity_scores.append(0)
        else:
            similarity_scores.append(np.dot(emb_ref, emb_trans) / (np.linalg.norm(emb_ref) * np.linalg.norm(emb_trans)))
    avg_embedding_similarity = np.mean(similarity_scores)

    return bleu_score, avg_embedding_similarity

if __name__ == "__main__":
    input_sentence = "Hello, how are you?"
    reference_translation = "Bonjour, comment ça va ?"

    # Load Google Translate using translate.py
    translator = Translator(to_lang="fr")

    # Translate using the NLP Translation Library
    translated_nlp_lib = translate(input_sentence)
    print("Input Sentence:", input_sentence)
    print("Translated Sentence (NLP Translation Library):", translated_nlp_lib)

    # Translate using Google Translate (translate.py)
    translated_google_translate = translator.translate(input_sentence)
    print("Translated Sentence (Google Translate):", translated_google_translate)

    # Load the pre-trained FastText model
    fasttext.util.download_model('fr', if_exists='ignore')
    fasttext_model = fasttext.load_model('cc.fr.300.bin')

    # Tokenize sentences and retrieve word embeddings
    reference_tokens = nltk.word_tokenize(reference_translation)
    translated_tokens = nltk.word_tokenize(translated_nlp_lib)

    word_embeddings = {}
    for token in set(reference_tokens + translated_tokens):
        word_embeddings[token] = fasttext_model.get_word_vector(token)

    # Print word embeddings for tokens
    print("Word Embeddings:")
    for token, embedding in word_embeddings.items():
        print(token, ":", embedding)

    # Calculate BLEU score and average embedding similarity
    bleu_score_nlp_lib, avg_embedding_similarity_nlp_lib = evaluate_translation(
        reference_translation, translated_nlp_lib, word_embeddings
    )

    bleu_score_google_translate, avg_embedding_similarity_google_translate = evaluate_translation(
        reference_translation, translated_google_translate, word_embeddings
    )

    # Print evaluation results
    print("BLEU Score (NLP Translation Library):", bleu_score_nlp_lib)
    print("BLEU Score (Google Translate):", bleu_score_google_translate)
    print("Average Embedding Similarity (NLP Translation Library):", avg_embedding_similarity_nlp_lib)
    print("Average Embedding Similarity (Google Translate):", avg_embedding_similarity_google_translate)

    # Plot word embedding graph
    tokens = list(word_embeddings.keys())
    embeddings = np.array(list(word_embeddings.values()))

    plt.figure(figsize=(10, 8))
    plt.scatter(embeddings[:, 0], embeddings[:, 1], alpha=0.5)
    for i, token in enumerate(tokens):
        plt.annotate(token, (embeddings[i, 0], embeddings[i, 1]), fontsize=8)
    plt.title("Word Embedding Visualization")
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    plt.show()
