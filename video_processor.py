import os
import json
import time
import re
from google import genai
from google.genai import types

# Ensure API key is set
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def parse_word_timestamps(word_timestamps_file):
    """Parses the word timestamps file and returns a list of word entries with start and end times."""
    word_entries = []
    timestamp_pattern = r"\[(\d+\.\d+)s\s*->\s*(\d+\.\d+)s\]\s*(\S.*)"

    with open(word_timestamps_file, "r", encoding="utf-8") as file:
        for line in file:
            match = re.match(timestamp_pattern, line.strip())
            if match:
                word_entries.append({
                    "word": match.group(3).strip(),
                    "start": float(match.group(1)),
                    "end": float(match.group(2))
                })
    return word_entries


def convert_to_seconds(timestamp):
    """Converts a timestamp in MM:SS or MM:SS.sss format to seconds."""
    minutes, seconds = timestamp.split(":")
    return int(minutes) * 60 + float(seconds)


def generate_segments(video_path, word_timestamps_file):
    """Generate segments from a video and return the path to the JSON file."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"The file '{video_path}' does not exist.")

    # Extract the filename for personalization
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_filename = f"{video_name}_segments.json"
    output_path = os.path.join("static/uploads", output_filename)

    # Upload the video file
    uploaded_file = client.files.upload(file=video_path)
    print(f"Uploaded file: {uploaded_file.name} (Waiting for activation...)")

    # Ensure the file is active before proceeding
    while True:
        file_info = client.files.get(name=uploaded_file.name)
        if file_info.state == "ACTIVE":
            print(f"File {uploaded_file.name} is now ACTIVE.")
            break
        time.sleep(1)  # Wait a bit before checking again

    model = "gemini-2.0-flash"

    # Generate segmentation prompt
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=uploaded_file.uri,
                    mime_type=uploaded_file.mime_type,
                ),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""Given this instructional video titled '{video_name}',
                segment it into logical instructional steps. For each segment, provide:
                1. **Title**
                2. **Timestamps**
                3. **Description**
                Output the result in a structured JSON format."""),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )

    print("\nGenerating segmentation...\n")

    segment_data = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        segment_data += chunk.text

    # Attempt to parse the response into JSON
    try:
        segments = json.loads(segment_data)
        words = parse_word_timestamps(word_timestamps_file)
        for segment in segments:
            start, end = map(convert_to_seconds, segment["Timestamps"].split("-"))
            segment_words = [entry["word"] for entry in words if start <= entry["start"] <= end]
            segment["Transcription"] = " ".join(segment_words)
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(segments, json_file, indent=4, ensure_ascii=False)
        print(f"\nSegmentation with transcription saved to {output_path}")
        return output_path
    except json.JSONDecodeError:
        raise ValueError("Failed to parse response as JSON.")


def generate_summary(video_path):
    """Generate a summary from a video and return the path to the JSON file."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"The file '{video_path}' does not exist.")

    # Extract the filename for personalization
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_filename = f"{video_name}_summary.json"
    output_path = os.path.join("static/uploads", output_filename)

    # Upload the video file
    uploaded_file = client.files.upload(file=video_path)
    print(f"Uploaded file: {uploaded_file.name} (Waiting for activation...)")

    # Ensure the file is active before proceeding
    while True:
        file_info = client.files.get(name=uploaded_file.name)
        if file_info.state == "ACTIVE":
            print(f"File {uploaded_file.name} is now ACTIVE.")
            break
        time.sleep(1)  # Wait a bit before checking again

    model = "gemini-2.0-flash"

    # Generate summary prompt
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=uploaded_file.uri,
                    mime_type=uploaded_file.mime_type,
                ),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""Create a comprehensive summary of this video titled '{video_name}'.
                Include the following in your JSON response:
                1. **Title** - A concise title for the video
                2. **Duration** - The approximate duration of the video
                3. **MainPoints** - An array of the key points covered
                4. **Summary** - A paragraph summarizing the content
                5. **Keywords** - An array of relevant keywords
                Output the result in a structured JSON format."""),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )

    print("\nGenerating summary...\n")

    summary_data = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        summary_data += chunk.text

    # Attempt to parse the response into JSON
    try:
        summary = json.loads(summary_data)
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(summary, json_file, indent=4, ensure_ascii=False)
        print(f"\nSummary saved to {output_path}")
        return output_path
    except json.JSONDecodeError:
        raise ValueError("Failed to parse response as JSON.")
