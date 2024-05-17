import sc2reader
import os
import pandas as pd
import uuid
from pytz import timezone
import os
import json
import sc2reader
import os

def extract_replay_info(replay_file, personal_account="TheLeengwist"):
    replay = sc2reader.load_replay(replay_file)
    players = [(player.name, player.play_race, player.result) for player in replay.players]
    try:
        winner = [player.name for player in replay.players if player.result == 'Win'][0]
    except:
        winner = [player.name for player in replay.players if player.result == 'Win']
    game_length = replay.frames / replay.game_fps / 60  # convert frames to minutes
    
    utc = timezone('UTC')
    pacific = timezone('America/Los_Angeles')

    # replay.start_time is naive; assume it's in UTC
    utc_start_time = utc.localize(replay.start_time)

    # Convert start time to Pacific Time
    pacific_start_time = utc_start_time.astimezone(pacific)
    start_time = pacific_start_time.strftime("%Y-%m-%d %H:%M:%S")  # format the start time in Pacific Time

    # Determine if the replay involves the personal account
    personal_involved = any(personal_account == player[0] for player in players)
    category = "personal" if personal_involved else "public"

    if category == "public":
        win = "None"
    elif personal_account in winner:
        win = "Win"
    else:
        win = "Loss"
    opponent_race = None

    for player in players:
        if player[0] != personal_account:
            opponent_race = player[1]

    map_name = replay.map_name  # Accessing the map name from the replay object

    replay_info = {
        "game_id": str(uuid.uuid4()),
        "map_name": map_name,  # Add map name to the dictionary
        "category": category,
        "start_time": start_time,
        "game_length": round(game_length, 2),
        "player_1": players[0][0],
        "player_2": players[1][0],
        "player_1_race": players[0][1],
        "player_2_race": players[1][1],
        "winner": winner,
        "win": win,
        "opponent_race": opponent_race,
    }
    return replay_info

def extract_unit_compositions(replay_file):
    replay = sc2reader.load_replay(replay_file)
    unit_compositions = {player.name: {} for player in replay.players}

    # Define a set of invalid units
    invalid_units = {
        "BeaconArmy", "BeaconDefend", "BeaconAttack", "BeaconHarass", "BeaconIdle",
        "BeaconAuto", "BeaconDetect", "BeaconScout", "BeaconClaim", "BeaconExpand",
        "BeaconRally", "BeaconCustom1", "BeaconCustom2", "BeaconCustom3", "BeaconCustom4",
        "CommandCenter", "KD8Charge", "Hatchery", "Lair", "Hive", "Extractor", "Nexus",
        "OrbitalCommand", "AutoTurret", "MULE", "Larva","Interceptor" 'Larva',
        'InvisibleTargetDummy', 'Corruptor', 'SwarmHostMP', 'Infestor', 'ChangelingMarineShield',
        'BroodlingEscort','Interceptor', 'AdeptPhaseShift'}

    for event in replay.events:
        if isinstance(event, sc2reader.events.tracker.UnitBornEvent):
            player_name = event.unit.owner.name if event.unit.owner else "Neutral"
            if player_name not in unit_compositions:
                continue

            unit_type = event.unit_type_name

            # Exclude non-combat units
            if unit_type in invalid_units:
                continue

            # Update total unit counts
            if unit_type in unit_compositions[player_name]:
                unit_compositions[player_name][unit_type] += 1
            else:
                unit_compositions[player_name][unit_type] = 1

    # Calculate percentages
    for player_name in unit_compositions:
        total_units = sum(unit_compositions[player_name].values())
        for unit_type in unit_compositions[player_name]:
            count = unit_compositions[player_name][unit_type]
            percentage = count / total_units if total_units > 0 else 0
            unit_compositions[player_name][unit_type] = (count, round(percentage, 2))

    return unit_compositions

def save_replay_data(directory, filepath="data/replay_data.csv", overwrite=True):
    replay_data = []
    existing_data = pd.DataFrame()

    # Check if the file exists and load it if overwrite is False
    if not overwrite and os.path.exists(filepath):
        existing_data = pd.read_csv(filepath)

    for filename in os.listdir(directory):
        if filename.endswith(".SC2Replay"):
            full_path = os.path.join(directory, filename)
            replay_summary = extract_replay_info(full_path)
            unit_compositions = extract_unit_compositions(full_path)
            # Create a dictionary for each replay
            replay_info = {
                "filename": filename,
                "game_id": replay_summary["game_id"],
                "category": replay_summary["category"],
                "map_name": replay_summary["map_name"],  # Add map name to the dictionary
                "start_time": replay_summary["start_time"],
                "game_length": replay_summary["game_length"],
                "player_1": replay_summary["player_1"],
                "player_2": replay_summary["player_2"],
                "player_1_race": replay_summary["player_1_race"],
                "player_2_race": replay_summary["player_2_race"],
                "winner": replay_summary["winner"],
                "win": replay_summary["win"],
                "opponent_race": replay_summary["opponent_race"],
                "player_1_unit_comp": unit_compositions[replay_summary["player_1"]],
                "player_2_unit_comp": unit_compositions[replay_summary["player_2"]]
            }
            
            # Append new data only if it's not a duplicate
            if not overwrite:
                is_duplicate = ((existing_data['player_1'] == replay_info['player_1']) &
                                (existing_data['player_2'] == replay_info['player_2']) &
                                (existing_data['start_time'] == replay_info['start_time'])).any()
                if not is_duplicate:
                    replay_data.append(replay_info)
            else:
                replay_data.append(replay_info)

            print("Processed", filename)

    if replay_data:
        # Convert the list of dictionaries to a DataFrame
        new_data_df = pd.DataFrame(replay_data)
        
        if not overwrite and not existing_data.empty:
            # Concatenate with existing data and drop duplicates
            final_df = pd.concat([existing_data, new_data_df], ignore_index=True).drop_duplicates(subset=['player_1', 'player_2', 'start_time'])
        else:
            final_df = new_data_df

        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Save to CSV
        final_df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
    else:
        print("No new data to save.")
        
        
if __name__ == "__main__":
    directories = [
        "/mnt/c/Users/matth/Documents/StarCraft II/Accounts/86722028/1-S2-1-3925175/Replays/Multiplayer/",
         "data/public_replays",
         ]
    for directory in directories:
        save_replay_data(directory)
    # x = extract_unit_compositions("public_replays/1-1-1 standard PvT.SC2Replay")
    # print(x)
