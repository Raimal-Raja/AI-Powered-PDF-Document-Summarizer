import re
import os
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_nltk_data():
    """Ensure NLTK data is installed and available, with explicit downloading."""
    nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    nltk.data.path.append(nltk_data_dir)
    
    required_resources = ['punkt', 'stopwords']
    
    for resource in required_resources:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
            logger.info(f"NLTK resource '{resource}' already available.")
        except LookupError:
            logger.info(f"Downloading NLTK resource '{resource}'...")
            try:
                nltk.download(resource, download_dir=nltk_data_dir, quiet=False)
                logger.info(f"NLTK resource '{resource}' downloaded successfully.")
            except Exception as e:
                logger.error(f"Failed to download NLTK resource '{resource}': {str(e)}")
                raise Exception(f"Failed to download NLTK resource '{resource}'. Please check your internet connection or run 'python -m nltk.downloader {resource}' manually.")

ensure_nltk_data()

def preprocess_text(text):
    """Clean text for summarization."""
    text = re.sub(r'\s+', ' ', text.strip())  # Normalize whitespace
    return text

def extractive_summary(text, num_sentences=5):
    """Improved extractive summary with stopword filtering."""
    text = preprocess_text(text)
    try:
        sentences = sent_tokenize(text)
    except Exception as e:
        logger.error(f"Sentence tokenization failed: {str(e)}")
        sentences = [s.strip() for s in text.split(".") if s.strip() and len(s.strip()) > 1]
    
    if not sentences or len(sentences) < 1:
        return "No valid sentences found to summarize."
    
    if len(sentences) <= num_sentences:
        return " ".join(sentences)
    
    stop_words = set(stopwords.words('english'))
    word_freq = defaultdict(int)
    for sentence in sentences:
        words = [w.lower() for w in re.split(r'\W+', sentence) if w]
        for word in words:
            if word not in stop_words and len(word) > 1:
                word_freq[word] += 1
    
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        words = [w.lower() for w in re.split(r'\W+', sentence) if w]
        if not words:
            sentence_scores[i] = 0
        else:
            score = sum(word_freq.get(word, 0) for word in words if word not in stop_words)
            sentence_scores[i] = score / max(len(words), 1)
    
    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    top_indices.sort()
    return " ".join(sentences[i] for i in top_indices)

def abstractive_summary(text, max_length=150):
    """Improved abstractive summary using key sentence selection."""
    text = preprocess_text(text)
    try:
        sentences = sent_tokenize(text)
    except Exception as e:
        logger.error(f"Sentence tokenization failed: {str(e)}")
        sentences = [s.strip() for s in text.split(".") if s.strip() and len(s.strip()) > 1]
    
    if not sentences:
        return "No valid sentences found to summarize."
    
    temp_summary = extractive_summary(text, num_sentences=3)
    summary = temp_summary
    
    if len(summary) > max_length:
        summary = summary[:max_length-3] + "..."
    
    return summary

def batch_summarization(texts, summary_type="extractive", num_sentences=5, max_length=150):
    """Process multiple texts."""
    summaries = {}
    for file_name, text in texts.items():
        if summary_type == "abstractive":
            summaries[file_name] = abstractive_summary(text, max_length)
        else:
            summaries[file_name] = extractive_summary(text, num_sentences)
    return summaries