import os
import pandas as pd

# Paths
utterances_dir = r"C:\Users\akash\Downloads\NLP Project\output\utterances"
utterances_csv_path = r"C:\Users\akash\Downloads\NLP Project\output\utterances.csv"
output_pairs_path = os.path.join(utterances_dir, "subclip_pairs.csv")

# Load utterance text CSV
utterance_df = pd.read_csv(utterances_csv_path)
utterance_text_lookup = dict(zip(utterance_df['subclip_name'], utterance_df['utterance_text']))

# Collect all pairs
all_pairs = []

for folder_name in sorted(os.listdir(utterances_dir)):
    folder_path = os.path.join(utterances_dir, folder_name)

    if os.path.isdir(folder_path):
        subclips = sorted([
            f for f in os.listdir(folder_path)
            if f.endswith('.mp4')
        ])

        for i in range(len(subclips)):
            for j in range(i+1, len(subclips)):
                clip1 = subclips[i]
                clip2 = subclips[j]

                text1 = utterance_text_lookup.get(clip1, "")
                text2 = utterance_text_lookup.get(clip2, "")

                all_pairs.append([
                    clip1, text1,
                    clip2, text2,
                    folder_name
                ])

# Save to CSV
df = pd.DataFrame(all_pairs, columns=[
    "clip_1", "utterance_text_1",
    "clip_2", "utterance_text_2",
    "parent_folder"
])
df.to_csv(output_pairs_path, index=False)
print(f"✅ Subclip pairs with texts saved to: {output_pairs_path}")
