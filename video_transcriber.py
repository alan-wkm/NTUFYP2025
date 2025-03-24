import time
import ffmpeg
import os
from faster_whisper import WhisperModel


def extract_audio(input_video):
    base_name = os.path.splitext(input_video)[0]
    extracted_audio = base_name + "." + "wav"
    # extracted_audio = input_video.replace(".mp4", ".wav")
    stream = ffmpeg.input(input_video)
    stream = ffmpeg.output(stream, extracted_audio)
    ffmpeg.run(stream, overwrite_output=True)
    return extracted_audio


def transcribe_video(input_video):
    extracted_audio = extract_audio(input_video)

    model = WhisperModel("medium")
    segments, info = model.transcribe(extracted_audio, word_timestamps=True)

    word_timestamp_file = os.path.join(
        os.path.dirname(input_video), "word_timestamps.txt")

    # Write word-level timestamps to a separate file
    with open(word_timestamp_file, 'w') as word_file:
        for segment in segments:
            # Check if word-level timestamps are available
            if segment.words:
                for word in segment.words:
                    word_line = ("[%.2fs -> %.2fs] %s" %
                                 (word.start, word.end, word.word))
                    word_file.write(f"{word_line}\n")

    return word_timestamp_file
