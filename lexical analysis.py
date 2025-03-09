import assemblyai as aai
import os
import re
import time
import pandas as pd
from pydub import AudioSegment

class AudioTranscriber:
    def __init__(self, api_key, audio_path, output_file, speakers_expected=2):
        self.api_key = api_key
        self.audio_path = audio_path
        self.output_file = output_file
        self.speakers_expected = speakers_expected
        self.transcriptions = [None] * 200  # Preset size
        aai.settings.api_key = self.api_key
        self.config = aai.TranscriptionConfig(
            disfluencies=True,
            speaker_labels=True,
            speakers_expected=2
        )
        os.chdir(self.audio_path)
    
    def TrimAudio(transcript, file):
        audio=AudioSegment.from_wav(file)
        merged_audio=AudioSegment.empty()
        for utterance in transcript.utterances:
            if (utterance.speaker=="B"):
                StarterTime=utterance.start
                EndTime=utterance.end
                merged_audio+=audio[StarterTime:EndTime]
        output_path = f"D:/Lexical analysis/Trimmed Audio/trimmed_{file}"
        merged_audio.export(output_path, format="wav")
        print(f"Trimmed audio saved to {output_path}")        
            
    def extract_interview_number(self, file_name):
        match = re.search(r'\d+', file_name)
        return match.group() if match else None
    
    def process_audio_files(self):
        total_files = len([f for f in os.listdir() if f.endswith(".wav")])
        processed_count = 1      
        for file in os.listdir():
            if file.endswith(".wav"):
                interview_number = self.extract_interview_number(file)
                if interview_number is None:
                    continue
                
                interview_number = int(interview_number)
                audio_file_path = os.path.join(self.audio_path, file)
                current_time = time.strftime("[%M:%H:%d]")
                print(f"{current_time} Processing file: {file} ({processed_count} out of {total_files})")
                transcript = aai.Transcriber().transcribe(audio_file_path, self.config)
                AudioTranscriber.TrimAudio(transcript, file)
                processed_count += 1
                if self.transcriptions[interview_number] is None:
                    self.transcriptions[interview_number] = f"P{interview_number}: "              
                text = "".join(utterance.text for utterance in transcript.utterances if utterance.speaker == "B")
                self.transcriptions[interview_number] += text
    
    def save_transcriptions(self):
        final_text = "\n".join(text for text in self.transcriptions if text is not None)       
        with open(self.output_file, "w") as file:
            file.write(final_text)
        print("Transcription saved successfully.")
    def run(self):
        self.process_audio_files()
        self.save_transcriptions()

# Usage
if __name__ == "__main__":
    transcriber = AudioTranscriber(
        api_key="52e3e90185574153903f7fb2fb3bb81e",
        audio_path="D:/Lexical analysis/Audio",
        output_file="D:/Lexical analysis/Cleaned_transcripts.txt"
    )
    transcriber.run()