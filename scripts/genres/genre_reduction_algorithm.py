import pandas as pd
import json
from collections import Counter

# Load the dataset
data = pd.read_csv("")  # Update with the actual file path

# Load the genre mapping JSON file
with open("choisic_music_genres.json", 'r') as f:
    genre_mapping = json.load(f)

# Define main music genres based on https://www.chosic.com/list-of-music-genres/
main_genres = [
    "Pop", "Electronic", "Hip Hop", "R&B", "Latin", "Rock", "Metal",
    "Country", "Folk/Acoustic", "Classical", "Jazz", "Blues", 
    "Easy listening", "New age", "World/Traditional"
]

print(f"Current amount of genres selected: {len(main_genres)}")

# Check for missing genres
missing_genre_count = data['Spotify genres'].isna().sum()
print(f"Number of tracks without a genre specified: {missing_genre_count}")

# Filter and display tracks without a genre specified
missing_genre_tracks = data[data['Spotify genres'].isna()]
print("Tracks without a genre specified:\n", missing_genre_tracks)

# Drop rows where 'Spotify genres' is NaN
data = data.dropna(subset=['Spotify genres'])
print(f"Number of tracks with a genre specified: {len(data)}")

# Extract all Spotify genres
all_genres = data['Spotify genres']
print("Tracks with a genre specified:\n", all_genres)

def map_to_main_genre(spotify_genres):
    """
    Maps Spotify genres to the closest main genre based on a predefined mapping.
    """
    def get_main_genre(subgenres):
        subgenres_list = [genre.strip() for genre in subgenres.split(',')]

        # Check for a direct match with main genres
        for subgenre in subgenres_list:
            if subgenre.lower() in (g.lower() for g in main_genres):
                return next(g for g in main_genres if g.lower() == subgenre.lower())

        # Count occurrences of subgenres in the genre mapping
        genre_counts = Counter()
        for subgenre in subgenres_list:
            for main_genre, subgenre_list in genre_mapping.items():
                if subgenre in subgenre_list:
                    genre_counts[main_genre] += 1

        # Return the most common main genre or None if no match is found
        if not genre_counts:
            return None

        most_common_genres = genre_counts.most_common()
        max_count = most_common_genres[0][1]
        top_genres = [genre for genre, count in most_common_genres if count == max_count]

        # Resolve ties based on the order in the original list
        for subgenre in subgenres_list:
            for main_genre, subgenre_list in genre_mapping.items():
                if main_genre in top_genres and subgenre in subgenre_list:
                    return main_genre

    return spotify_genres.apply(get_main_genre)

# Apply genre mapping function
data['reducedGenre'] = map_to_main_genre(data['Spotify genres'])

# Count categorized and uncategorized genres
uncategorized_count = data['reducedGenre'].isna().sum()
categorized_count = len(data) - uncategorized_count
total_count = len(data)

# Calculate percentages
uncategorized_percentage = (uncategorized_count / total_count) * 100
categorized_percentage = (categorized_count / total_count) * 100

# Print statistics
print(f"Number of uncategorized genres: {uncategorized_count} ({uncategorized_percentage:.2f}%)")
print(f"Number of categorized genres: {categorized_count} ({categorized_percentage:.2f}%)")

# Save the results to CSV
data.to_csv("data_reduced_genres.csv", index=False)
