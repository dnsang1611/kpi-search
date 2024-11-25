import os
import soundfile as sf
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

TRANSCRIPTION_CHECKPOINT_PATH = '/mnt/mmlabworkspace/Students/visedit/AIC2024/Backend/ASR/transcription_checkpoint/batch1.txt'
CHECKPOINT_PATH = '/mnt/mmlabworkspace/Students/visedit/AIC2024/Backend/ASR/checkpoints/batch1.txt'
START_LINE_INDEX = 59864  # Change this to the desired starting line index

# Load model and tokenizer
processor = Wav2Vec2Processor.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h", sampling_rate=16000)
model = Wav2Vec2ForCTC.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h").to('cuda:0')

# Define function to read in sound file
def map_to_array(batch: dict):
    speech, _ = sf.read(batch["file"])
    batch["speech"] = speech
    return batch

# Transcribe an audio (.wav) file into Vietnamese transcription
def transcribe(audio_path: str):
    ds = map_to_array({"file": audio_path})
    # Tokenize
    input_values = processor(ds["speech"], return_tensors="pt", padding="longest", sampling_rate=16000).input_values.to('cuda:0')  # Batch size 1
    # Retrieve logits
    logits = model(input_values).logits
    # Take argmax and use greedy decoding method
    predicted_ids = torch.argmax(logits, dim=-1)
    # Final output
    transcription = processor.batch_decode(predicted_ids)

    return transcription[0]

# Read the list of lines from the checkpoint file
with open(CHECKPOINT_PATH, 'r') as checkpoint_file:
    checkpoint_lines = checkpoint_file.readlines()[START_LINE_INDEX:]

# Open the transcription checkpoint file to write results
with open(TRANSCRIPTION_CHECKPOINT_PATH, 'a') as f:
    for audio_path in checkpoint_lines:
        audio_path = audio_path.strip()  # Remove leading/trailing whitespaces and newline characters

        try:
            # Attempt to transcribe audio
            transcription = transcribe(audio_path)

            # Check if the transcription is valid and has at least 20 characters
            if transcription and len(transcription) >= 20:
                # Write to the transcription file in the desired format
                line = f"{audio_path}\t{transcription}\n"
                f.write(line)
                f.flush()  # Flush the buffer to ensure real-time updates

                print(f"Transcribed: {audio_path}")
        except Exception as e:
            # Print the error and skip the current file
            print(f"Error transcribing {audio_path}: {e}")
