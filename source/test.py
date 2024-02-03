#@title <-- Rodar o whisper para transcrever:

import os
import whisper
from tqdm import tqdm
from whisper.utils import get_writer
import json

# Define the folder where the wav files are located

with open('config.json') as f:
    config=json.load(f)

print("Setting:")
print("Model: "+config["model"])
print("Folder in: "+config["in"])
print("Folder out: "+config["out"])
if config["language"]==None:
    print("language: auto")
else:
    print("language: " + config["language"])
print("Task "+config["task"])
print("Output format: ",end='')
print (*config["output_format"])
print("Fp16: ",end='')
print (config["fp16"])


root_folder=config['in']
exit_folder=config['out']

print("Loading whisper model...")
model = whisper.load_model(config['model'])
print("Whisper model complete.")

# Get the number of wav files in the root folder and its sub-folders
print("Getting number of files to transcribe...")
num_files = sum(1 for dirpath, dirnames, filenames in os.walk(root_folder) for filename in filenames if filename.endswith(".wav"))
print("Number of files: ", num_files)


# Transcribe the wav files and display a progress bar
with tqdm(total=num_files, desc="Transcribing Files") as pbar:
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".wav"):
                filepath = os.path.join(dirpath, filename)
                result = model.transcribe(filepath,language=config['language'], fp16=config["fp16"], verbose=False,task=config['task'])

                # Write transcription to text file
                filename_no_ext = os.path.splitext(filename)[0]
                for format in config["output_format"]:
                    writer = get_writer(format, exit_folder)
                    writer(result, filename_no_ext)

                pbar.update(1)