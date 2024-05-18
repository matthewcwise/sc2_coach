def generate_race_csv(race):
    import pandas as pd
    
    df = pd.read_csv("data/replay_data.csv")

    import json
    import pandas as pd
    import ast
    def safe_eval_dict(s):
        try:
            # Evaluating the string as a Python literal if it's not in JSON format
            return ast.literal_eval(s)
        except ValueError as e:
            print(f"Failed to evaluate string as dict: {s}, Error: {e}")
            return {}

    # Load CSV

    # Apply the safe_eval_dict function
    df['player_1_unit_comp'] = df['player_1_unit_comp'].apply(safe_eval_dict)
    df['player_2_unit_comp'] = df['player_2_unit_comp'].apply(safe_eval_dict)

    import pandas as pd
    import ast
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    import seaborn as sns

    def safe_eval_dict(data_str):
        try:
            return ast.literal_eval(data_str)
        except ValueError as e:
            print(f"Error parsing string: {data_str}, Error: {e}")
            return {}  # Return an empty dictionary in case of an error

    filtered_df = df[(df['player_1_race'] == race) | (df['player_2_race'] == race)]
    race_data = []

    for idx, row in filtered_df.iterrows():
        if row['player_1_race'] == race:
            race_data.append({
                'game_id': row['game_id'],
                'player_name': row['player_1'],
                'opponent_name': row['player_2'],
                'win_loss': 1 if row['winner'] == row['player_1'] else 0,
                'opponent_race': row['player_2_race'],
                'game_length': row['game_length'],
                'unit_composition': row['player_1_unit_comp'],
                'opponent_unit_composition': row['player_2_unit_comp']
            })
        if row['player_2_race'] == race:
            race_data.append({
                'game_id': row['game_id'],
                'player_name': row['player_2'],
                'opponent_name': row['player_1'],
                'win_loss': 1 if row['winner'] == row['player_2'] else 0,
                'opponent_race': row['player_1_race'],
                'game_length': row['game_length'],
                'unit_composition': row['player_2_unit_comp'],
                'opponent_unit_composition': row['player_1_unit_comp']
            })
    
    race_df = pd.DataFrame(race_data)
    # race_df['unit_composition'] = race_df['unit_composition'].apply(safe_eval_dict)
    # race_df['opponent_unit_composition'] = race_df['opponent_unit_composition'].apply(safe_eval_dict)
    # for unit in set().union(*(d.keys() for d in race_df['unit_composition'])):
    #     race_df[f"{unit}_pct"] = race_df['unit_composition'].apply(lambda d: d.get(unit, (0, 0.0))[1])  # [1] to get percentage

    race_df.to_csv(f"data/cluster_input_{race.lower()}.csv", index=False)
    print(f"{race} cluster input data saved to data/cluster_input_{race.lower()}.csv")
    
    
if __name__ == "__main__":
    # Call the function for each race
    generate_race_csv('Terran')
    generate_race_csv('Protoss')
    generate_race_csv('Zerg')
