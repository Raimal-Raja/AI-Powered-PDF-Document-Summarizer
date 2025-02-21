import re
import random
import nltk
import os

def ensure_nltk_data():
    """Ensure NLTK data is properly installed and uses the correct path."""
    nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)

    # Add to NLTK's data path
    nltk.data.path.append(nltk_data_dir)

    # Ensure 'punkt' is available
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK 'punkt' tokenizer...")
        nltk.download('punkt', download_dir=nltk_data_dir)
        print("NLTK 'punkt' tokenizer downloaded successfully.")

# Initialize NLTK data correctly
ensure_nltk_data()


from nltk.tokenize import sent_tokenize

def extractive_summary(text, num_sentences=5):
    """Extract key sentences from text."""
    try:
        sentences = sent_tokenize(text)
    except Exception as e:
        print(f"Sentence tokenization failed: {str(e)}")
        sentences = [s.strip() for s in text.split(".") if s.strip()]

    if not sentences:
        print("No meaningful text found to summarize.")
        return "No meaningful text found to summarize."

    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    word_frequencies = {}
    for sentence in sentences:
        for word in sentence.lower().split():
            if word not in word_frequencies:
                word_frequencies[word] = 0
            word_frequencies[word] += 1

    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        sentence_scores[i] = sum(word_frequencies.get(word, 0) for word in sentence.lower().split()) / len(sentence.split())

    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    top_indices.sort()

    return " ".join([sentences[i] for i in top_indices])

def abstractive_summary(text, max_length=150):
    """Simple abstractive summary without deep learning models."""
    try:
        sentences = sent_tokenize(text)
    except Exception as e:
        print(f"Sentence tokenization failed: {str(e)}")
        sentences = [s.strip() for s in text.split(".") if s.strip()]

    if not sentences:
        print("No meaningful text found to summarize.")
        return "No meaningful text found to summarize."

    first_sentence = sentences[0]
    selected_sentences = [first_sentence]

    if len(sentences) > 2:
        mid_idx = len(sentences) // 2
        selected_sentences.append(sentences[mid_idx])
    if len(sentences) > 4:
        selected_sentences.append(sentences[-2])

    summary = " ".join(selected_sentences)

    if len(summary) > max_length:
        summary = summary[:max_length-3] + "..."

    return summary

def batch_summarization(texts, summary_type="extractive", num_sentences=5, max_length=150):
    """Process multiple texts and return summaries"""
    summaries = {}
    for file_name, text in texts.items():
        if summary_type == "abstractive":
            summaries[file_name] = abstractive_summary(text, max_length)
        else:
            summaries[file_name] = extractive_summary(text, num_sentences)
    return summaries