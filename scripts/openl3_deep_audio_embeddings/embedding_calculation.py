import os
import numpy as np
import soundfile as sf
import openl3
from skimage.measure import block_reduce

# Input parameters
audio_folder = " "
embedding_folder = " "

# Define the embedding size and the OpenL3 model
EMBEDDING_SIZE = 512
model = openl3.models.load_audio_embedding_model(input_repr="mel256", content_type="music", embedding_size=EMBEDDING_SIZE)

# Function to average pool embeddings
def average_pool(embeddings):
    return np.mean(embeddings, axis=0)

# Ensure the embedding folder exists
os.makedirs(embedding_folder, exist_ok=True)

# Walk through all subdirectories and files
for root, dirs, files in os.walk(audio_folder):
    for file in files:
        if file.endswith('.mp3'):
            # Construct the full file path
            file_path = os.path.join(root, file)
            
            # Define the save path for embeddings (flat structure)
            save_path = os.path.join(embedding_folder, file.replace('.mp3', '.npz'))
            
            # Check if the embedding file already exists
            if os.path.exists(save_path):
                print(f"File already exists, skipping: {save_path}")
                continue
            
            try:
                # Load the audio file
                audio, sr = sf.read(file_path)
                
                # Extract embeddings
                emb, ts = openl3.get_audio_embedding(audio, sr, content_type="music",
                                                    input_repr="mel256", embedding_size=EMBEDDING_SIZE, model=model)
                
                # Apply average pooling to reduce the embeddings
                avg_pooled_emb = average_pool(emb)
                
                # Save the embeddings as a .npz file in the embedding folder
                np.savez(save_path, embeddings=avg_pooled_emb)
                
                print(f"Processed and saved: {save_path}")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

print("All files processed.")