import os
import zipfile

folder = "data/ransomware"

for file in os.listdir(folder):
    if file.endswith(".zip"):
        path = os.path.join(folder, file)
        try:
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(folder)
            print(f"Extracted: {file}")
        except Exception as e:
            print(f"Error with {file}: {e}")