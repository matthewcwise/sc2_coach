import pandas as pd
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits
import ast

def safe_eval_dict(data_str):
    try:
        return ast.literal_eval(data_str)
    except ValueError as e:
        print(f"Error parsing string: {data_str}, Error: {e}")
        return {}  # Return an empty dictionary in case of an error

races = ["Terran", "Protoss", "Zerg"]

def cluster_gen(race):
    # Load CSV data from file
    df = pd.read_csv(f"data/cluster_input_{race.lower()}.csv")
    df['unit_composition'] = df['unit_composition'].apply(safe_eval_dict)
    df['opponent_unit_composition'] = df['opponent_unit_composition'].apply(safe_eval_dict)

    # Flatten unit percentages into columns for clustering
    for unit in set().union(*(d.keys() for d in df['unit_composition'])):
        df[f"{unit}_pct"] = df['unit_composition'].apply(lambda d: d.get(unit, (0, 0.0))[1])  # [1] to get percentage

    # One-hot encode the 'opponent_race' column
    opponent_race_dummies = pd.get_dummies(df['opponent_race'], prefix='opponent_race')
    df = pd.concat([df, opponent_race_dummies], axis=1)

    # Create a list of percentage features for clustering
    percentage_features = [col for col in df.columns if '_pct' in col]

    # Include game length in features for clustering
    features_for_clustering = ['game_length'] + list(opponent_race_dummies.columns) + percentage_features

    # Set threadpool limits to mitigate the exception
    with threadpool_limits(limits=1):
        # KMeans clustering
        kmeans = KMeans(n_clusters=10, random_state=0)
        df['cluster'] = kmeans.fit_predict(df[features_for_clustering])
    
    # Save the clustered data
    df.to_csv(f'data/cluster_outputs_{race.lower()}.csv')
    
    # Summarize the clusters
    cluster_summary = df.groupby('cluster').agg(
        num_games=pd.NamedAgg(column='game_length', aggfunc='count'),
        win_ratio=pd.NamedAgg(column='win_loss', aggfunc='mean'),  # Average of binary win column gives win ratio
        avg_game_length=pd.NamedAgg(column='game_length', aggfunc='mean')
    ).join(
        df.groupby('cluster')[percentage_features].mean()
    )

    # Calculate win ratios and number of games against each opponent race within each cluster
    opponent_races = opponent_race_dummies.columns
    for opponent_race in opponent_races:
        race_name = opponent_race.split('_')[-1]  # Extract race name from column
        win_ratios = []
        game_counts = []
        for cluster in cluster_summary.index:
            cluster_games = df[(df['cluster'] == cluster) & (df[opponent_race] == 1)]
            game_count = len(cluster_games)
            if game_count > 0:
                win_ratio = cluster_games['win_loss'].mean()
            else:
                win_ratio = float('nan')  # Indicate no games against this race in this cluster
            win_ratios.append(win_ratio)
            game_counts.append(game_count)
        cluster_summary[f'win_ratio_vs_{race_name}'] = win_ratios
        cluster_summary[f'num_games_vs_{race_name}'] = game_counts

    # Save the summary DataFrame
    cluster_summary = cluster_summary.round(2)
    cluster_summary.to_csv(f'data/cluster_summary_{race.lower()}.csv')

    print(cluster_summary)
