import re
import csv
import os
from collections import Counter
from pydub import AudioSegment

os.chdir("D:/Lexical analysis")

# Define word categories
filler_words = {"uhm", "um", "uh"}  # Count these anywhere
sentence_start_words = {"basically", "like"}  # Only count these at sentence starts

# Read the file
with open("D:/Lexical analysis/Cleaned_transcripts.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Use regex to split by speakers
speaker_pattern = r"(P\d+):"  # Matches speaker tags like P1:, P2:, etc.
speakers = re.split(speaker_pattern, text)[1:]  # Splitting while keeping data

# Organize into a dictionary
speaker_data = {}
for i in range(0, len(speakers), 2):
    speaker = speakers[i].strip()
    transcript = speakers[i+1].strip()
    
    # Tokenize words (remove punctuation, convert to lowercase)
    words = re.findall(r"\b\w+\b", transcript.lower())
    
    # Count statistics
    total_words = len(words)
    unique_words = len(set(words))
    filler_count = sum(1 for word in words if word in filler_words)
    
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
    audio_file = f"D:/Lexical analysis/Trimmed Audio Joined/Audio_{speaker}.wav"  # Assuming WAV format
    if os.path.exists(audio_file):
        audio = AudioSegment.from_file(audio_file)
        duration_seconds = len(audio) / 1000  # Convert ms to seconds
    else:
        duration_seconds = 0  # Set to 0 if file not found to avoid NoneType errors
    filler_count=filler_count+sentence_start_count
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
