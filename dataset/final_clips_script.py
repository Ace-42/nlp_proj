import os
import re
import srt
import pandas as pd
from datetime import timedelta
from moviepy.editor import VideoFileClip

# Paths
base_dir = r"C:\Users\akash\Downloads\NLP Project"
clips_dir = os.path.join(base_dir, "output", "clips")
srt_dir = base_dir
utterance_output_base = os.path.join(base_dir, "output", "utterances")
utterance_csv_path = os.path.join(base_dir, "output", "utterances.csv")
final_csv_path = os.path.join(base_dir, "output", "final.csv")

# Read the real timestamp ranges
final_df = pd.read_csv(final_csv_path)
clip_to_range = {
    row['video_name'].replace('.mp4', ''): row['timestamp_range'] for _, row in final_df.iterrows()
}

# Ensure output dir exists
os.makedirs(utterance_output_base, exist_ok=True)
utterance_data = []

def td_to_sec(td):
    return td.total_seconds()

def timestamp_to_seconds(ts):
    h, m, s_ms = ts.split(":")
    s, ms = s_ms.split(",")
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

# Iterate through each clip
for clip_file in sorted(os.listdir(clips_dir)):
    if not clip_file.endswith(".mp4"):
        continue

    match = re.match(r"(\d+)-(\d+)\.mp4", clip_file)
    if not match:
        print(f"Skipping: {clip_file}")
        continue

    video_id, clip_id = match.groups()
    clip_key = f"{video_id}-{clip_id}"
    srt_path = os.path.join(srt_dir, f"subtitles{video_id}.srt")
    clip_path = os.path.join(clips_dir, clip_file)

    if not os.path.exists(srt_path):
        print(f"Missing SRT for {clip_file}")
        continue

    # Get the original video timestamp range from final.csv
    if clip_key not in clip_to_range:
        print(f"No timestamp for {clip_key} in final.csv")
        continue

    try:
        range_str = clip_to_range[clip_key]
        start_str, end_str = [s.strip() for s in range_str.split("-->")]
        start_sec = timestamp_to_seconds(start_str)
        end_sec = timestamp_to_seconds(end_str)
    except Exception as e:
        print(f"Failed to parse timestamp range for {clip_key}: {e}")
        continue

    # Parse subtitles
    with open(srt_path, "r", encoding="utf-8-sig") as f:
        srt_content = f.read()
        subs = list(srt.parse(srt_content))

    # Load full clip
    try:
        full_clip = VideoFileClip(clip_path)
    except Exception as e:
        print(f"Failed to load clip {clip_file}: {e}")
        continue

    # Output folder
    clip_output_folder = os.path.join(utterance_output_base, clip_key)
    os.makedirs(clip_output_folder, exist_ok=True)

    utterance_idx = 1
    for sub in subs:
        sub_start = td_to_sec(sub.start)
        sub_end = td_to_sec(sub.end)

        if sub_start >= start_sec and sub_end <= end_sec:
            try:
                # Offset within the clip
                clip_sub_start = sub_start - start_sec
                clip_sub_end = sub_end - start_sec

                subclip = full_clip.subclip(clip_sub_start, clip_sub_end)
                subclip_name = f"{clip_key}-{utterance_idx:03d}.mp4"
                subclip_path = os.path.join(clip_output_folder, subclip_name)
                subclip.write_videofile(subclip_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

                utterance_data.append([
                    subclip_name,
                    clip_file,
                    f"{video_id}.mp4",
                    sub.content.replace('\n', ' '),
                    f"{sub.start} --> {sub.end}"
                ])

                utterance_idx += 1

            except Exception as e:
                print(f"Failed to process utterance in {clip_file}: {e}")

    full_clip.close()

# Save final CSV
df = pd.DataFrame(utterance_data, columns=[
    "subclip_name", "parent_clip", "original_video", "utterance_text", "utterance_timestamp"
])
df.to_csv(utterance_csv_path, index=False)
print(f"✅ Done! Final utterances.csv saved at: {utterance_csv_path}")
