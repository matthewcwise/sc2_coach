import zipfile
import os

# Define paths
zip_dir = 'data/zip'
extract_dir = 'data/public_replays'

# Create the extract directory if it doesn't exist
os.makedirs(extract_dir, exist_ok=True)

# Function to get file size
def get_file_size(file_path):
    return os.path.getsize(file_path)

# Set of existing files and their sizes in the target directory
existing_files = {
    (filename, get_file_size(os.path.join(extract_dir, filename)))
    for filename in os.listdir(extract_dir)
}

# Iterate through all files in the zip directory
for zip_filename in os.listdir(zip_dir):
    if zip_filename.endswith('.zip'):
        zip_path = os.path.join(zip_dir, zip_filename)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                # Extract only files (not directories)
                if not file_info.is_dir():
                    # Determine the path to extract the file to
                    extracted_path = os.path.join(extract_dir, os.path.basename(file_info.filename))
                    
                    # Check for duplicates based on filename and size
                    if (os.path.basename(file_info.filename), file_info.file_size) in existing_files:
                        print(f"Skipping duplicate file: {file_info.filename}")
                    else:
                        # Extract the file to the target directory
                        with zip_ref.open(file_info.filename) as source, open(extracted_path, 'wb') as target:
                            target.write(source.read())
                        existing_files.add((os.path.basename(file_info.filename), file_info.file_size))
                        print(f"Extracted {file_info.filename} to {extract_dir}")

print("All zip files have been processed.")