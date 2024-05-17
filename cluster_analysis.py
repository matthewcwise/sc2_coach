import pandas as pd



races = ["Terran", "Protoss", "Zerg"]

for race in races:
    # Load CSV data from file
    df = pd.read_csv(f"data/cluster_outputs_{race.lower()}.csv")
    
    # Filter to only include games where 'TheLeengwist' is the opponent
    df_leengwist = df[df['opponent_name'] == 'TheLeengwist']

    # Summarize the clusters: calculate win and loss counts for each cluster
    cluster_summary_leengwist = df_leengwist.groupby('cluster').agg(
        num_games=pd.NamedAgg(column='win_loss', aggfunc='count'),
        num_wins=pd.NamedAgg(column='win_loss', aggfunc=lambda x: (x == 0).sum()),
        num_losses=pd.NamedAgg(column='win_loss', aggfunc=lambda x: (x == 1).sum())
    )

    # Calculate win ratio
    cluster_summary_leengwist['win_ratio'] = cluster_summary_leengwist['num_wins'] / cluster_summary_leengwist['num_games']

    # Save the summary DataFrame
    cluster_summary_leengwist = cluster_summary_leengwist.round(2)
    cluster_summary_leengwist.to_csv('data/cluster_summary_theleengwist.csv')
    print(f"\n\nSummary vs. {race} for TheLeengwist")
    print(cluster_summary_leengwist)
