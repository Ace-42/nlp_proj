import os
import pandas as pd
import re
from pathlib import Path

# === Helper functions ===
def timestamp_to_seconds(ts: str) -> float:
    h, m, s_ms = ts.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def parse_srt(srt_path):
    entries = []
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    blocks = re.split(r"\n\n+", content)
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) >= 3:
            try:
                time_range = lines[1]
                start_str, end_str = time_range.split(" --> ")
                start_sec = timestamp_to_seconds(start_str.strip())
                end_sec = timestamp_to_seconds(end_str.strip())
                text = " ".join(lines[2:]).strip()
                entries.append((start_sec, end_sec, text))
            except:
                continue
    return entries

# === Paths ===
utterances_dir = Path(r"C:\Users\akash\Downloads\NLP Project\output\utterances")
final_csv_path = Path(r"C:\Users\akash\Downloads\NLP Project\output\final.csv")
subclip_pairs_path = utterances_dir / "subclip_pairs.csv"
subtitles_dir = Path(r"C:\Users\akash\Downloads\NLP Project")

# === Load data ===
final_df = pd.read_csv(final_csv_path)
subclip_pairs = pd.read_csv(subclip_pairs_path)

# === Build lookup set of (start_utt, end_utt) from final.csv and SRTs ===
start_end_pairs = set()

for _, row in final_df.iterrows():
    video_num = row['video_name'].split("-")[0]  # e.g. "1" from "1-001.mp4"
    srt_path = subtitles_dir / f"subtitles{video_num}.srt"
    if not srt_path.exists():
        continue

    entries = parse_srt(srt_path)
    timestamp_range = row['timestamp_range']
    start_str, end_str = map(str.strip, timestamp_range.split("-->"))
    start_sec = timestamp_to_seconds(start_str)
    end_sec = timestamp_to_seconds(end_str)

    start_utt = end_utt = None

    for entry_start, entry_end, text in entries:
        if abs(entry_start - start_sec) < 0.01:
            start_utt = text
        if abs(entry_end - end_sec) < 0.01:
            end_utt = text

    if start_utt and end_utt:
        start_end_pairs.add((start_utt, end_utt))

# === Label subclip pairs ===
def label_row(row):
    return 1 if (row['utterance_text_1'], row['utterance_text_2']) in start_end_pairs else 0

subclip_pairs['class'] = subclip_pairs.apply(label_row, axis=1)

# === Save result ===
output_path = utterances_dir / "subclip_pairs_labeled.csv"
subclip_pairs.to_csv(output_path, index=False)
print(f"Saved labeled pairs to {output_path}")
