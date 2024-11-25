import os
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

TRANSCRIPTION_CHECKPOINT_PATH = '/mnt/mmlab2024nas/visedit/AIC2024/code/Backend/ASR/transcription_checkpoint/batch1_1.txt'
CHECKPOINT_PATH = '/mnt/mmlab2024nas/visedit/AIC2024/code/Backend/ASR/checkpoints/batch1.txt'
START_LINE_INDEX = 17644  # Thay đổi giá trị này nếu cần bắt đầu từ dòng khác
END_LINE_INDEX = 250000  # Đặt giá trị None nếu muốn đọc đến hết file hoặc chỉ định số dòng kết thúc

# Load Whisper model và processor
processor = WhisperProcessor.from_pretrained("openai/whisper-large-v2")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v2").to('cuda:0')
model.config.forced_decoder_ids = None

# Định nghĩa hàm đọc file âm thanh và chuyển thành mảng
def map_to_array(audio_path: str):
    audio, sampling_rate = librosa.load(audio_path, sr=16000)
    return audio

# Transcribe một file âm thanh (.wav) thành văn bản tiếng Việt
def transcribe(audio_path: str):
    audio = map_to_array(audio_path)
    # Tokenize
    input_features = processor(audio, sampling_rate=16000, return_tensors="pt").input_features.to('cuda:0')
    # Sử dụng model để generate kết quả
    predicted_ids = model.generate(input_features)
    # Decode output thành text
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    
    return transcription[0]

# Đọc danh sách file từ file checkpoint
with open(CHECKPOINT_PATH, 'r') as checkpoint_file:
    checkpoint_lines = checkpoint_file.readlines()[START_LINE_INDEX:END_LINE_INDEX]

# Mở file checkpoint để ghi kết quả
with open(TRANSCRIPTION_CHECKPOINT_PATH, 'a') as f:
    for audio_path in checkpoint_lines:
        audio_path = audio_path.strip()  # Xoá các ký tự trắng thừa và xuống dòng

        try:
            # Thực hiện chuyển đổi âm thanh thành văn bản
            transcription = transcribe(audio_path)

            # Kiểm tra xem kết quả transcription có hợp lệ không và ít nhất có 40 ký tự
            if transcription and len(transcription) >= 40:
                # Ghi vào file kết quả theo định dạng mong muốn
                line = f"{audio_path}\t{transcription}\n"
                f.write(line)
                f.flush()  # Đảm bảo buffer được cập nhật liên tục

                print(f"Đã chuyển đổi: {audio_path}")
        except Exception as e:
            # In ra lỗi và bỏ qua file lỗi
            print(f"Lỗi khi chuyển đổi {audio_path}: {e}")
