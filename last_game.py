import pandas as pd
import ast

def last_game(csv_file_path='data/replay_data.csv'):
    # Path to the CSV file
    csv_file_path = csv_file_path

    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Filter to only include games played by TheLeengwist
    df_leengwist = df[(df['player_1'] == 'TheLeengwist') | (df['player_2'] == 'TheLeengwist')]

    # Sort by start_time to find the last game
    df_leengwist['start_time'] = pd.to_datetime(df_leengwist['start_time'])
    df_leengwist_sorted = df_leengwist.sort_values(by='start_time', ascending=False)

    # Get the last game
    last_game = df_leengwist_sorted.iloc[0]

    # Extract required information
    win_loss = last_game['win']
    game_length = last_game['game_length']
    opponent_name = last_game['player_1'] if last_game['player_2'] == 'TheLeengwist' else last_game['player_2']
    opponent_race = last_game['player_1_race'] if last_game['player_2'] == 'TheLeengwist' else last_game['player_2_race']
    opponent_unit_comp_str = last_game['player_1_unit_comp'] if last_game['player_2'] == 'TheLeengwist' else last_game['player_2_unit_comp']
    self_comp_str = last_game['player_1_unit_comp'] if last_game['player_1'] == 'TheLeengwist' else last_game['player_2_unit_comp']

    # Convert opponent_unit_comp from string to dictionary
    opponent_unit_comp = ast.literal_eval(opponent_unit_comp_str)
    self_unit_comp = ast.literal_eval(self_comp_str)

    # Sort the opponent's unit composition by count (highest first)
    sorted_opponent_unit_comp = dict(sorted(opponent_unit_comp.items(), key=lambda item: item[1][0], reverse=True))
    sorted_self_unit_comp = dict(sorted(self_unit_comp.items(), key=lambda item: item[1][0], reverse=True))

    # Generate the opponent's unit breakdown string
    opponent_unit_breakdown = "".join(
        [f"\n * {unit}: {count} ({percentage * 100:.0f}%)" for unit, (count, percentage) in sorted_opponent_unit_comp.items()]
    )
    self_unit_breakdown = "".join(
        [f"\n * {unit}: {count} ({percentage * 100:.0f}%)" for unit, (count, percentage) in sorted_self_unit_comp.items()]
    )

    # Generate the report
    report = f"""
    Last Game Report for TheLeengwist:
    ----------------------------------
    Win/Loss: {win_loss}
    Time: {round(game_length)} minutes
    Opponent Race/Name: {opponent_name} ({opponent_race})
    Unit Breakdown: {self_unit_breakdown}
    Opponent Unit Breakdown: {opponent_unit_breakdown}
    """

    print(report)

if __name__ == "__main__":
    last_game()