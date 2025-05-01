import os
import sys
import subprocess
import whisper

def extract_audio(video_file, audio_file):
    """Extracts audio from a video file using ffmpeg."""
    command = [
        'ffmpeg', '-y',  # overwrite output file if exists
        '-i', video_file,
        '-vn',  # no video
        '-acodec', 'pcm_s16le',  # WAV format
        '-ar', '16000',  # 16kHz
        '-ac', '1',  # mono channel
        audio_file
    ]
    subprocess.run(command, check=True)

def transcribe_audio(audio_file, model_size="medium", language=None):
    """Transcribes audio to subtitles using whisper."""
    print(f"Loading Whisper model '{model_size}'...")
    model = whisper.load_model(model_size)

    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file, language=language, task="transcribe")

    return result['segments']

def save_as_srt(segments, output_srt):
    """Saves transcription segments as .srt file."""
    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    with open(output_srt, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            text = seg['text'].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

def main(video_file, target_language="en", model_size="medium"):
    base_name, _ = os.path.splitext(video_file)
    audio_file = base_name + ".wav"
    output_srt = f"{base_name}.{target_language}.srt"

    extract_audio(video_file, audio_file)
    segments = transcribe_audio(audio_file, model_size=model_size, language=target_language)
    save_as_srt(segments, output_srt)

    os.remove(audio_file)  # Clean up temporary audio
    print(f"Subtitle saved as: {output_srt}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_subtitle.py <video_file> <language_code>")
        sys.exit(1)

    video_file = sys.argv[1]
    language_code = sys.argv[2]
    main(video_file, language_code)
