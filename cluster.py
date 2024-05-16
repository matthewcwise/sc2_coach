import json
import sc2reader
import os

player_db = "TheLeengwist"


def extract_replay_info(replay_file, personal_account = "TheLeengwist"):
    replay = sc2reader.load_replay(replay_file)
    players = [(player.name, player.play_race, player.result) for player in replay.players]
    winner = [player.name for player in replay.winner.players]
    game_length = replay.frames / replay.game_fps / 60  # convert frames to minutes
    start_time = replay.start_time.strftime("%Y-%m-%d %H:%M:%S")  # format the start time

    win = "TheLeengwist" in winner
    opponent_race = None

    for player in players:
        if player[0] != "TheLeengwist":
            opponent_race = player[1]

    return {
        "players": players,
        "winner": winner,
        "game_length": game_length,
        "start_time": start_time,
        "win": win,
        "opponent_race": opponent_race
    }

def extract_unit_compositions(replay_file):
    replay = sc2reader.load_replay(replay_file)
    unit_compositions = {player.name: {} for player in replay.players}

    # Define a set of invalid units
    invalid_units = {
        "BeaconArmy", "BeaconDefend", "BeaconAttack", "BeaconHarass", "BeaconIdle",
        "BeaconAuto", "BeaconDetect", "BeaconScout", "BeaconClaim", "BeaconExpand",
        "BeaconRally", "BeaconCustom1", "BeaconCustom2", "BeaconCustom3", "BeaconCustom4",
        "CommandCenter", "KD8Charge", "Hatchery", "Lair", "Hive", "Extractor", "Nexus", "OrbitalCommand", "AutoTurret", "MULE", "Larva","Interceptor"
    'Larva', 'InvisibleTargetDummy',
    'Corruptor', 'SwarmHostMP', 'Infestor', 'ChangelingMarineShield','BroodlingEscort',
    'Interceptor', 'AdeptPhaseShift'}

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

def process_replays(directory):
    all_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".SC2Replay"):
            try:
                filepath = os.path.join(directory, filename)
                replay_info = extract_replay_info(filepath)
                unit_compositions = extract_unit_compositions(filepath)
                
                replay_data = {
                    "replay_file": filename,
                    "replay_info": replay_info,
                    "unit_compositions": unit_compositions
                }
                all_data.append(replay_data)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                continue
    
    return all_data

# Example usage
directory = "/mnt/c/Users/matth/Documents/StarCraft II/Accounts/86722028/1-S2-1-3925175/Replays/Multiplayer/"
all_replay_data = process_replays(directory)

# Write the data to a JSON file
output_file = "data/replays_data.json"
with open(output_file, "w") as f:
    json.dump(all_replay_data, f, indent=4)

print(f"Data saved to {output_file}")


with open(output_file, "r") as f:
    replay_data = json.load(f)

# Initialize counters for wins and total games against each race
race_stats = {}

# Process each replay entry
for replay in replay_data:
    replay_info = replay["replay_info"]
    opponent_race = replay_info["opponent_race"]
    win = replay_info["win"]

    if opponent_race not in race_stats:
        race_stats[opponent_race] = {"wins": 0, "total": 0}

    race_stats[opponent_race]["total"] += 1
    if win:
        race_stats[opponent_race]["wins"] += 1

# Calculate and print win rates
print("Win rates against different races:")
for race, stats in race_stats.items():
    win_rate = stats["wins"] / stats["total"] * 100
    print(f"{race}: {win_rate:.2f}% ({stats['wins']} wins out of {stats['total']} games)")


# from sklearn.cluster import KMeans
# import numpy as np

# # Example feature data (You'll replace this with your actual features)
# X = np.array([
#     [feature1_for_game1, feature2_for_game1],
#     [feature1_for_game2, feature2_for_game2],
#     # Add more games
# ])

# kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
# print(kmeans.labels_)
