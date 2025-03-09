import os
import shutil
from pydub import AudioSegment

# Define input and output directories
input_dir = "D:\Lexical analysis\Trimmed Audio"  # Change this
output_dir = "D:\Lexical analysis\Trimmed Audio Joined"     # Change this

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# List all files in the input directory
files = sorted(os.listdir(input_dir))

# Group files by number
audio_dict = {}

for file in files:
    if file.lower().endswith(".wav"):  # Case-insensitive extension check
        name, _ = os.path.splitext(file)
        if name.startswith("trimmed_P") and not name.startswith("trimmed_PP"):
            num = name[9:]  # Extract number after "trimmed_P"
            audio_dict.setdefault(num, {})["P"] = file
        elif name.startswith("trimmed_PP"):
            num = name[10:]  # Extract number after "trimmed_PP"
            audio_dict.setdefault(num, {})["PP"] = file

# Process files (merge if pair exists, copy if missing)
for num, pair in audio_dict.items():
    p_file = pair.get("P")
    pp_file = pair.get("PP")

    if p_file and pp_file:
        print(f"Merging: {p_file} + {pp_file}")
        audio1 = AudioSegment.from_file(os.path.join(input_dir, p_file))
        audio2 = AudioSegment.from_file(os.path.join(input_dir, pp_file))
        combined = audio1 + audio2  # Concatenate audio

        output_path = os.path.join(output_dir, f"Audio_P{num}.wav")
        combined.export(output_path, format="wav")
        print(f"Saved merged file: {output_path}")

    elif p_file:  # If only trimmed_P[number] exists, copy it
        shutil.copy(os.path.join(input_dir, p_file), os.path.join(output_dir, f"Audio_P{num}.wav"))
        print(f"Copied unpaired file: {p_file}")

    elif pp_file:  # If only trimmed_PP[number] exists, copy it
        shutil.copy(os.path.join(input_dir, pp_file), os.path.join(output_dir, f"Audio_P{num}.wav"))
        print(f"Copied unpaired file: {pp_file}")

print("Processing complete.")
