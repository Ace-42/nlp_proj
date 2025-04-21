import os
import pandas as pd
from moviepy.editor import VideoFileClip
import sys
import re

print(sys.executable)

# Base paths (update if needed)
base_dir = r"C:\Users\akash\Downloads\NLP Project"
videos_dir = os.path.join(base_dir, 'videos')
csvs_dir = os.path.join(base_dir, 'csvs')
output_clips_dir = os.path.join(base_dir, 'output', 'clips')
final_csv_path = os.path.join(base_dir, 'output', 'final.csv')

# Create output directories if not exist
os.makedirs(output_clips_dir, exist_ok=True)

# Final CSV data
final_data = []

# Iterate through each CSV
for csv_file in sorted(os.listdir(csvs_dir)):
    if csv_file.endswith('.csv') and csv_file.startswith('res'):
        # Extract number from resX.csv
        match = re.search(r'res(\d+)\.csv', csv_file)
        if not match:
            print(f"Filename doesn't match pattern: {csv_file}")
            continue
        number = match.group(1)
        video_name = number  # e.g., "1" for 1.mp4
        video_path = os.path.join(videos_dir, f"{video_name}.mp4")
        csv_path = os.path.join(csvs_dir, csv_file)

        # Load video
        try:
            video = VideoFileClip(video_path)
        except Exception as e:
            print(f"Failed to load video {video_path}: {e}")
            continue

        # Read CSV
        print(f"Processing {csv_file} with video {video_name}.mp4")
        df = pd.read_csv(csv_path)

        # Split video based on timestamp ranges
        for idx, row in df.iterrows():
            timestamp = row['timestamp_range']
            cause = row['cause_text']
            emotion = row['emotion_text']
            if emotion == 'LAUGHTER':
                continue

            try:
                # Convert timestamp to seconds
                start_str, end_str = timestamp.split(" --> ")

                def to_seconds(ts):
                    h, m, s = ts.split(":")
                    s, ms = s.split(",")
                    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

                start_sec = to_seconds(start_str.strip())
                end_sec = to_seconds(end_str.strip())

                # Clip video
                clip = video.subclip(start_sec, end_sec)

                # Name the clip
                clip_name = f"{video_name}-{idx+1:03d}.mp4"
                clip_path = os.path.join(output_clips_dir, clip_name)
                clip.write_videofile(clip_path, codec='libx264', audio_codec='aac', verbose=False, logger=None)

                # Append to final CSV data
                final_data.append([clip_name, cause, emotion, timestamp])

            except Exception as e:
                print(f"Error processing row {idx} in {csv_file}: {e}")

# Write final CSV
final_df = pd.DataFrame(final_data, columns=['video_name', 'cause_text', 'emotion_text', 'timestamp_range'])
final_df.to_csv(final_csv_path, index=False)
print(f"Done. Final CSV saved to {final_csv_path}")

