import re
import random
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def extractive_summary(text, num_sentences=5):
    """Extract key sentences from text"""
    # Get sentences
    sentences = sent_tokenize(text)
    
    if len(sentences) <= num_sentences:
        return " ".join(sentences)
    
    # Simple scoring - longer sentences with important words tend to be more informative
    word_frequencies = {}
    for sentence in sentences:
        for word in sentence.lower().split():
            if word not in word_frequencies:
                word_frequencies[word] = 0
            word_frequencies[word] += 1
    
    # Calculate sentence scores
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        sentence_scores[i] = 0
        words = sentence.lower().split()
        if len(words) > 3:  # Ignore very short sentences
            for word in words:
                if word in word_frequencies:
                    sentence_scores[i] += word_frequencies[word]
            sentence_scores[i] = sentence_scores[i] / len(words)
    
    # Get top sentences
    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    top_indices.sort()  # Maintain original order
    
    return " ".join([sentences[i] for i in top_indices])

def abstractive_summary(text, max_length=150):
    """Simple abstractive summary without deep learning models"""
    # This is a simplified version without T5
    sentences = sent_tokenize(text)
    
    # Get first few sentences as the most important info is often at the beginning
    if not sentences:
        return ""
        
    first_sentence = sentences[0]
    
    # Get a few key sentences from the middle and end if available
    selected_sentences = [first_sentence]
    if len(sentences) > 2:
        mid_idx = len(sentences) // 2
        selected_sentences.append(sentences[mid_idx])
    if len(sentences) > 4:
        selected_sentences.append(sentences[-2])
    
    summary = " ".join(selected_sentences)
    
    # Truncate if too long
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