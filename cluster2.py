import json
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import seaborn as sns

# Load JSON data from file
input_file = "data/replays_data.json"
output_csv = "data/cluster_stats.csv"
with open(input_file, "r") as f:
    replay_data = json.load(f)

# Filter games where the opponent race is Terran
terran_games = [game for game in replay_data if game['replay_info']['opponent_race'] == 'Terran']

# Prepare a DataFrame to hold unit composition data and game length
unit_data = []
for game in terran_games:
    opponent_name = next(player[0] for player in game['replay_info']['players'] if player[0] != 'TheLeengwist')
    opponent_units = game['unit_compositions'][opponent_name]
    unit_counts = {unit: count for unit, (count, percentage) in opponent_units.items()}
    unit_counts['game'] = game['replay_file']
    unit_counts['win'] = game['replay_info']['win']
    unit_counts['game_length'] = game['replay_info']['game_length']
    unit_counts['start_time'] = game['replay_info']['start_time']
    unit_data.append(unit_counts)

df = pd.DataFrame(unit_data).fillna(0).set_index('game')

# Calculate percentages for unit compositions
unit_columns = df.columns.difference(['win', 'game_length', 'start_time'])
df['total_units'] = df[unit_columns].sum(axis=1)
for col in unit_columns:
    df[col] = df[col] / df['total_units']

# Perform k-means clustering
num_clusters = 5  # You can choose the number of clusters as needed
kmeans = KMeans(n_clusters=num_clusters, random_state=0)
df['cluster'] = kmeans.fit_predict(df.drop(['win', 'total_units', 'start_time'], axis=1))

# Print cluster assignments
print(df['cluster'])

# Calculate statistics for each cluster
cluster_stats = df.groupby('cluster').agg(
    wins=('win', 'sum'),
    total_games=('win', 'count'),
    losses=('win', lambda x: x.count() - x.sum()),
    win_rate=('win', lambda x: x.sum() / x.count() * 100),
    avg_game_length=('game_length', 'mean')
).round({'win_rate': 1, 'avg_game_length': 1})

# Calculate average unit percentages for each unit type for each cluster
average_unit_percentages = df.groupby('cluster').mean().drop(columns=['win', 'game_length', 'total_units']).round(2)

# Combine the statistics into a single DataFrame
cluster_stats = cluster_stats.join(average_unit_percentages)
print(cluster_stats)

# Save the cluster statistics to a CSV file
cluster_stats.to_csv(output_csv)
print(f"Cluster statistics saved to {output_csv}")

# Plot the clusters using PCA for dimensionality reduction (optional)
pca = PCA(n_components=2)
principal_components = pca.fit_transform(df.drop(['cluster', 'win', 'total_units', 'start_time'], axis=1))
df_pca = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
df_pca['cluster'] = df['cluster'].values
df_pca['win'] = df['win'].values

plt.figure(figsize=(10, 8))

# Define markers for wins and losses
markers = {True: 'o', False: 'X'}
sizes = {True: 100, False: 100}  # Increase the size of the markers

# Plot each cluster with different color
for cluster in df_pca['cluster'].unique():
    for win in markers:
        subset = df_pca[(df_pca['cluster'] == cluster) & (df_pca['win'] == win)]
        plt.scatter(subset['PC1'], subset['PC2'], c=f'C{cluster}', marker=markers[win], s=sizes[win],
                    label=f'Cluster {cluster} - {"Win" if win else "Loss"}')

plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('K-Means Clustering of Terran Opponent Unit Compositions')
plt.legend()
plt.show()

# Find the most recent game
df['start_time'] = pd.to_datetime(df['start_time'])
most_recent_game = df.sort_values(by='start_time', ascending=False).iloc[0]

# Print the details of the most recent game
print("Most Recent Game Details:")
print(most_recent_game)
