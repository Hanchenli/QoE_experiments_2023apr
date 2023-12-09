import os
import shutil
from datetime import datetime, timedelta

source_folder = '/dataheart/hanchen/llmqoe/video_qoe/QoE_experiments_2023apr/results'
destination_folder = '/dataheart/hanchen/llmqoe/video_qoe/QoE_experiments_2023apr/results_stall'

# Create the destination folder if it does not exist
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Get the current date and time
now = datetime.now()

# Define the age criteria (1 week in this case)
week_ago = now - timedelta(days=7)

# Loop through the files in the source folder
for filename in os.listdir(source_folder):
    file_path = os.path.join(source_folder, filename)

    # Check if it's a file (not a directory)
    if os.path.isfile(file_path):
        # Get the last modified time of the file
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))

        # Check if the file is older than a week
        if file_modified_time < week_ago:
            # Move the file
            shutil.move(file_path, os.path.join(destination_folder, filename))
            print(f"Moved: {filename}")
