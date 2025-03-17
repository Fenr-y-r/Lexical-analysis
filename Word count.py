import re
import csv
import os
from collections import Counter
from pydub import AudioSegment
import spacy
import string

nlp = spacy.load("en_core_web_sm")
os.chdir("D:/Lexical analysis")

# Define word categories
filler_words = {"uhm", "um", "uh"}  # Count these anywhere
sentence_start_words = {"basically", "like"}  # Only count these at sentence starts

# LIWC
Individual_Words = ["I", "me", "my", "mine", "myself", "I'd", "I'll", "I'm", "I've"]
Group_Words = ["we", "us", "our", "ours", "ourselves", "we'd", "we'll", "we're", "we've"]
They_Words = ["they", "them", "their", "theirs", "themselves", "they'd", "they'll", "they're", "they've"]
PosEmotion = ["hope", "improve", "kind", "love"]
NegEmotion = ["bad", "hate", "fool", "lose"]
Anxiety = ["anxious", "nervous", "panic", "stress", "tense", "worry", "worrying", "upset", "fear", "fearful", "scared", "scare", "scary", "afraid", "afraid", "anxiety", "anxieties", "nervousness", "panicking", "stressed", "tension", "tensions", "upsetting", "fears"]
Anger = ["angry", "anger", "angers", "annoy", "annoyed", "annoying", "annoyance", "annoyances", "irritate", "irritated", "irritating", "irritation", "irritations", "frustrate", "frustrated", "frustrating", "frustration", "frustrations", "bother", "disgust", "confront", "agitate"]
Sadness = ["sad", "sadness", "sadden", "saddened", "saddening", "saddens", "depress", "depressed", "depressing", "depression", "grieve", "grieved", "grieving", "grieves", "grief", "griefs"]
Cognitive = ["cause", "know", "learn", "notice", "teach", "taught", "make", "notice"]
Inhibition = ["refrain", "restrain", "prohibit", "restrained", "restraining", "restrains", "suppress", "suppressed", "prevent"]
Preceptual = ["see", "view", "watch", "observe", "expereince"]
Relativity = ["first", "huge", "new"]
Work = ["project", "study", "thesis", "university", "college", "academy", "assignment", "homework", "work", "job", "career", "profession", "employment", "occupation"]
Swear = ["shit", "fuck", "shitty"]
Articles = ["a", "an", "the"]
# Verbs
# Adverbs
# prepositions
# Conjunctions
Negations = ["no", "never", "none", "cannot", "can't", "don't", "do not", "could not", "couldn't"]
Quantifiers = ["all", "best", "bunch", "few", "ton", "unique"]

# Read the file
with open("D:/Lexical analysis/Complete Transcript.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Use regex to split by speakers
speaker_pattern = r"(P{1,2}\d+):"  # Matches speaker tags like P1:, P2:, etc.
speakers = re.split(speaker_pattern, text)[1:]  # Splitting while keeping data

# Organize into a dictionary
speaker_data = {}
LIWC = {}
for i in range(0, len(speakers), 2):
    speaker = speakers[i].strip()
    transcript = speakers[i+1].strip()  
    print(speaker)
    # Tokenize words (remove punctuation, convert to lowercase)
    words = re.findall(r"\b\w+\b", transcript.lower())
    
    # Count statistics
    total_words = len(words)
    unique_words = len(set(words))
    filler_count = sum(1 for word in words if word in filler_words)
    doc = nlp(transcript)
    
    # LIWC
    LIWC[speaker] = [           
            sum(1 for word in words if word in Individual_Words),
            sum(1 for word in words if word in Group_Words),
            sum(1 for word in words if word in They_Words),
            filler_count,
            sum(1 for word in words if word in PosEmotion),
            sum(1 for word in words if word in NegEmotion),
            sum(1 for word in words if word in Anxiety),
            sum(1 for word in words if word in Anger),
            sum(1 for word in words if word in Sadness),
            sum(1 for word in words if word in Cognitive),
            sum(1 for word in words if word in Inhibition),
            sum(1 for word in words if word in Preceptual),
            sum(1 for word in words if word in Relativity),
            sum(1 for word in words if word in Work),
            sum(1 for word in words if word in Swear),
            sum(1 for word in words if word in Articles),
            sum(1 for token in doc if token.pos_ == "VERB"),
            sum(1 for token in doc if token.pos_ == "ADV"),
            sum(1 for token in doc if token.pos_ == "ADP"),
            sum(1 for token in doc if token.pos_ in ["CCONJ", "SCONJ"]),
            sum(1 for word in words if word in Negations),
            sum(1 for word in words if word in Quantifiers),
            sum(1 for token in doc if token.pos_ == "NUM")+sum(1 for token in doc if re.match(r'\b\d+(st|nd|rd|th)\b', token.text)) + sum(1 for token in doc if "%" in token.text)]
    
    # Detect sentence-start words
    sentence_start_count = 0
    sentences = re.split(r"[.!?]", transcript)  # Split by sentence-ending punctuation
    for sentence in sentences:
        first_word_match = re.search(r"\b(\w+)\b", sentence.strip())  # Find first word
        if first_word_match:
            first_word = first_word_match.group(1).lower()
            if first_word in sentence_start_words:
                sentence_start_count += 1

    # Get audio duration
    audio_file = f"D:/Lexical analysis/Trimmed Audio/Trimmed_{speaker}.wav"  # Assuming WAV format
    if os.path.exists(audio_file):
        audio = AudioSegment.from_file(audio_file)
        duration_seconds = len(audio) / 1000  # Convert ms to seconds
    else:
        duration_seconds = 0  # Set to 0 if file not found to avoid NoneType errors
    filler_count = filler_count + sentence_start_count
    # Store results
    speaker_data[speaker] = [
        total_words, 
        unique_words, 
        filler_count,
        duration_seconds,
        round(total_words / duration_seconds, 2) if total_words > 0 else 0,
        round(unique_words / duration_seconds, 2) if unique_words > 0 else 0,
        round(filler_count / duration_seconds, 2) if filler_count > 0 else 0
    ]

# Write to CSV
csv_filename = "D:/Lexical analysis/speaker_statistics.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "Speaker", "Total Words", "Unique Words", "Filler Words",  
        "Audio Duration (s)", "Duration/Total Words", "Duration/Unique Words", "Duration/Filler Words"
    ])
    
    for speaker, stats in speaker_data.items():
        writer.writerow([speaker] + stats)
print(f"CSV file '{csv_filename}' created successfully!")

liwc_filename = "D:/Lexical analysis/LIWC.csv"
with open(liwc_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "Speaker",  "Individual", "We", "They", "Non-Fluences" ,"PosEmotion", "NegEmotion", "Anxiety", "Anger", "Sadness", "Cognitive", "Inhibition", "Preceptual", "Relativity", "Work", "Swear", "Articles", "Verbs", "Averbs", "Prepositions", "Conjunctions" ,"Negations", "Quantifiers", "Numbers"
    ])
    for speaker, stats in LIWC.items():
        writer.writerow([speaker] + stats)
    
