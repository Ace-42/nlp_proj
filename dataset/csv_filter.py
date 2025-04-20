# import os
# import pandas as pd

# # Set the path to your folder of CSVs
# folder_path = r"C:\Users\akash\Downloads\NLP Project\csvs"

# # Loop through all files in the folder
# for filename in os.listdir(folder_path):
#     if filename.endswith('.csv'):
#         file_path = os.path.join(folder_path, filename)
        
#         # Read the CSV
#         df = pd.read_csv(file_path)
        
#         # Check if 'cause_text' column exists
#         if 'cause_text' in df.columns:
#             # Filter out rows where cause_text is "LAUGHTER"
#             df = df[df['cause_text'] != 'LAUGHTER']
            
#             # Save the cleaned CSV (overwrite original)
#             df.to_csv(file_path, index=False)
#             print(f"Processed: {filename}")
#         else:
#             print(f"'cause_text' column not found in: {filename}")
import os
import pandas as pd

# Set the path to your folder of CSVs
folder_path = r"C:\Users\akash\Downloads\NLP Project\csvs"
filename = 'res21.csv'

file_path = os.path.join(folder_path, filename)

# Check if the file exists
if os.path.exists(file_path):
    # Read the CSV
    df = pd.read_csv(file_path)
    
    # Check if 'cause_text' column exists
    if 'emotion_text' in df.columns:
        # Filter out rows where cause_text is "LAUGHTER"
        df = df[df['emotion_text'] != 'LAUGHTER']
        
        # Save the cleaned CSV (overwrite original)
        df.to_csv(file_path, index=False)
        print(f"Processed: {filename}")
    else:
        print(f"'cause_text' column not found in: {filename}")
else:
    print(f"{filename} not found in the specified directory.")
