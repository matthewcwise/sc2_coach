
# Format percentages
def format_percentage(value):
    if isinstance(value, (int, float)) and value < 1:
        return f"{value * 100:.0f}%"
    elif isinstance(value, (int, float)):
        return f"{value:.0f}"
    return value

import sc2reader

def extract_replay_info(replay_file, personal_account="TheLeengwist"):
    replay = sc2reader.load_replay(replay_file)
    players = [(player.name, player.play_race, player.result) for player in replay.players]
    winner = [player.name for player in replay.players if player.result == 'Win']
    game_length = replay.frames / replay.game_fps / 60  # convert frames to minutes
    start_time = replay.start_time.strftime("%Y-%m-%d %H:%M:%S")  # format the start time
    
    # Determine if the replay involves the personal account
    personal_involved = any(personal_account == player[0] for player in players)
    category = "personal" if personal_involved else "public"

    win = personal_account in winner
    opponent_race = None

    for player in players:
        if player[0] != personal_account:
            opponent_race = player[1]

    return {
        "players": players,
        "winner": winner,
        "game_length": game_length,
        "start_time": start_time,
        "win": win,
        "opponent_race": opponent_race,
        "category": category  # Added to classify the replay type
    }


# Cluster names
terran_cluster_names = {
    0: "Mech + Air",
    1: "Reaper Rush",
    2: "Marines + Battle Cruisers",
    3: "Long Battle Mech+Air",
    4: "Quitter"
}

tvp_cluster_names = {
    0: "Cannon Rush",
    1: "Void Ray",
    2: "Marines + Battle Cruisers",
    3: "Carrier+Void Ray",
    4: "Stalkers, Oracles, Dark Templars"
}

tvz_cluster_names = {
    0: "Zergling Rush",
    1: "Zergling +Hydra",
    2: "Broodling (Long)",
    3: "Zergling+Roach+Hydra (Medium)",
    4: "Zerling+Roach (Short)"
}

import json
import pandas as pd
from sklearn.cluster import KMeans

def analyze_replays_by_race(replay_data, race, output_csv, k = 5):
    # Filter games where the opponent race matches the specified race
    games = [game for game in replay_data if game['replay_info']['opponent_race'] == race]

    # Prepare a DataFrame to hold unit composition data and game length
    unit_data = []
    for game in games:
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
    num_clusters = k  # You can choose the number of clusters as needed
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    df['cluster'] = kmeans.fit_predict(df.drop(['win', 'total_units', 'start_time', 'opponent'], axis=1))


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


if __name__ == "__main__":
    # Example usage
    input_file = "data/replays_data.json"
    tvt_output_csv = "data/tvt_cluster_stats.csv"
    tvp_output_csv = "data/tvp_cluster_stats.csv"
    tvz_output_csv = "data/tvz_cluster_stats.csv"
    with open(input_file, "r") as f:
        replay_data = json.load(f)

    analyze_replays_by_race(replay_data, 'Terran', tvt_output_csv)
    analyze_replays_by_race(replay_data, 'Protoss', tvp_output_csv)
    analyze_replays_by_race(replay_data, 'Zerg', tvz_output_csv)
