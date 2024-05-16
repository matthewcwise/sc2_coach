from util import *

import json
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from datetime import datetime
import pytz

# Load JSON data from file
input_file = "data/replays_data.json"
output_csv = "data/cluster_stats.csv"
output_html = "data/report.html"
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
    unit_counts['opponent'] = opponent_name
    unit_counts['win'] = game['replay_info']['win']
    unit_counts['game_length'] = game['replay_info']['game_length']
    unit_counts['start_time'] = game['replay_info']['start_time']
    unit_data.append(unit_counts)

df = pd.DataFrame(unit_data).fillna(0).set_index('game')

# Calculate percentages for unit compositions
unit_columns = df.columns.difference(['win', 'game_length', 'start_time', 'opponent'])
df['total_units'] = df[unit_columns].sum(axis=1)
for col in unit_columns:
    df[col] = df[col] / df['total_units']

# Perform k-means clustering
num_clusters = 5  # You can choose the number of clusters as needed
kmeans = KMeans(n_clusters=num_clusters, random_state=0)
df['cluster'] = kmeans.fit_predict(df.drop(['win', 'total_units', 'start_time', 'opponent'], axis=1))

# Cluster names
cluster_names = {
    0: "Mech + Air",
    1: "Reaper Rush",
    2: "Marines + Battle Cruisers",
    3: "Long Battle Mech+Air",
    4: "Quitter"
}

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
average_unit_percentages = df.groupby('cluster').mean().drop(columns=['win', 'game_length', 'total_units'])

# Combine the statistics into a single DataFrame
cluster_stats = cluster_stats.join(average_unit_percentages)
print(cluster_stats)

# Save the cluster statistics to a CSV file
cluster_stats.to_csv(output_csv)
print(f"Cluster statistics saved to {output_csv}")

# Find the most recent game
df['start_time'] = pd.to_datetime(df['start_time'])
most_recent_game = df.sort_values(by='start_time', ascending=False).iloc[0]

# Convert start time to Pacific Time Zone
utc_time = most_recent_game['start_time'].tz_localize('UTC')
pacific_tz = pytz.timezone('America/Los_Angeles')
pacific_time = utc_time.astimezone(pacific_tz)

# Extract details of the most recent game
opponent = most_recent_game['opponent']
cluster = most_recent_game['cluster']
cluster_title = cluster_names[cluster]
win = most_recent_game['win']
game_length = most_recent_game['game_length']

# Drop specific columns and empty columns from the most recent game details
most_recent_game = most_recent_game.drop(['cluster', 'win', 'opponent', 'start_time'])
most_recent_game = most_recent_game[most_recent_game != 0]

# Apply formatting to cluster stats and most recent game
cluster_stats_formatted = cluster_stats.applymap(format_percentage)
most_recent_game_formatted = most_recent_game.apply(format_percentage)

# Reorder columns
reordered_columns = [
    'wins', 'total_games', 'losses', 'win_rate', 'avg_game_length',  # Main stats
    'SCV',  # Worker
    'Marine', 'Marauder', 'Reaper',  # Bio
    'SiegeTank', 'Hellion', 'Cyclone', 'WidowMine', 'Thor', 'HellionTank',  # Mech
    'Battlecruiser', 'Liberator', 'VikingFighter', 'Banshee', 'Medivac', 'Raven',  # Air
    'Ghost', 'GhostAlternate', 'Nuke'  # Ghost
]
cluster_stats_formatted = cluster_stats_formatted[reordered_columns]

# Create HTML content with headings
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StarCraft II Replay Analysis</title>
    <style>
        body {{
            font-size: 12px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid black;
            padding: 8px;
            text-align: right;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .unit-group {{
            background-color: #d3d3d3;
        }}
    </style>
</head>
<body>
    <h1>StarCraft II Replay Analysis</h1>
    <h2>Most Recent Game Details</h2>
    <p><strong>Opponent:</strong> {opponent}</p>
    <p><strong>Game Time:</strong> {pacific_time.strftime('%Y-%m-%d %H:%M:%S %Z')}</p>
    <p><strong>Cluster Title:</strong> {cluster_title}</p>
    <p><strong>Game Length:</strong> {round(game_length)} minutes</p>
    <p><strong>Win:</strong> {"Yes" if win else "No"}</p>
    {most_recent_game_formatted.to_frame().T.to_html()}
    <h2>Cluster Names</h2>
    <table>
        <tr>
            <th>Cluster</th>
            <th>Title</th>
        </tr>
        {''.join(f'<tr><td>{cluster}</td><td>{title}</td></tr>' for cluster, title in cluster_names.items())}
    </table>
    <h2>Cluster Statistics</h2>
    <table>
        <thead>
            <tr>
                <th colspan="5"></th>
                <th colspan="1" class="unit-group">Worker</th>
                <th colspan="4" class="unit-group">Bio</th>
                <th colspan="6" class="unit-group">Mech</th>
                <th colspan="6" class="unit-group">Air</th>
                <th colspan="3" class="unit-group">Ghost</th>
            </tr>
            <tr>
                <th>wins</th>
                <th>total_games</th>
                <th>losses</th>
                <th>win_rate</th>
                <th>avg_game_length</th>
                <th>SCV</th>
                <th>Marine</th>
                <th>Marauder</th>
                <th>Reaper</th>
                <th>SiegeTank</th>
                <th>Hellion</th>
                <th>Cyclone</th>
                <th>WidowMine</th>
                <th>Thor</th>
                <th>HellionTank</th>
                <th>Battlecruiser</th>
                <th>Liberator</th>
                <th>VikingFighter</th>
                <th>Banshee</th>
                <th>Medivac</th>
                <th>Raven</th>
                <th>Ghost</th>
                <th>GhostAlternate</th>
                <th>Nuke</th>
            </tr>
        </thead>
        <tbody>
            {cluster_stats_formatted.to_html(index=True, header=False, border=0, justify='right').replace('table', 'tbody')}
        </tbody>
    </table>
</body>
</html>
"""

# Save the HTML content to a file
with open(output_html, "w") as f:
    f.write(html_content)

print(f"HTML report saved to {output_html}")
