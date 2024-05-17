import sc2reader
import psycopg2
from psycopg2 import sql
import os
import sc2reader
import psycopg2
from psycopg2 import sql
pw = os.getenv("DB_PASSWORD")

def check_user_and_roles(conn):
    try:
        with conn.cursor() as cursor:
            # Check current user
            cursor.execute("SELECT current_user;")
            user = cursor.fetchone()
            print(f"Current user: {user[0]}")

            # Check role memberships
            cursor.execute("SELECT rolname FROM pg_roles WHERE pg_has_role(current_user, oid, 'member');")
            roles = cursor.fetchall()
            print("Roles:", [role[0] for role in roles])
    except Exception as e:
        print("Error checking roles:", e)

# Function to create a database connection
def create_connection():
    conn = None  # Initialize conn to None to ensure it's always declared
    try:
        # Connect to the PostgreSQL database using environment variables
        conn = psycopg2.connect(
            dbname="starcraft_replays",
            user="postgres",
            password=pw,  # Get the password from an environment variable
            host="localhost"
        )
        print("Connection to PostgreSQL DB successful")
    except psycopg2.OperationalError as e:
        print(f"Operational error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return conn

def extract_and_save_replay_info(conn, replay_file, personal_account="TheLeengwist"):
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

    replay_info = {
        "start_time": start_time,
        "game_length": game_length,
        "winner": winner,
        "win": win,
        "opponent_race": opponent_race,
        "category": category
    }
    insert_replay_data(conn, replay_info)

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


import json
import sc2reader
import os
import uuid

player_db = "TheLeengwist"

import sc2reader
import psycopg2
from psycopg2 import sql

# Function to insert replay data into the database
def insert_replay_data(conn, replay_info):
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("""
            INSERT INTO replays (game_uuid, start_time, game_length, player1_name, player1_race, player2_name, player2_race, winner_name, match_up, win, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """), (
            replay_info['game_uuid'], replay_info['start_time'], replay_info['game_length'],
            replay_info['player1_name'], replay_info['player1_race'],
            replay_info['player2_name'], replay_info['player2_race'],
            replay_info['winner_name'], replay_info['match_up'],
            replay_info['win'], replay_info['category']
        ))
        conn.commit()
        print(f"Completed Commit: {replay_info['game_uuid']} {replay_info['player1_name']} v. {replay_info['player2_name']}")

def extract_and_save_replay_info(conn, replay_file, uuid, personal_account="TheLeengwist"):
    replay = sc2reader.load_replay(replay_file)
    players = replay.players
    if len(players) != 2:
        return  # Only process 1v1 replays

    game_length = replay.frames / replay.game_fps / 60  # convert frames to minutes
    start_time = replay.start_time.strftime("%Y-%m-%d %H:%M:%S")  # format the start time
    winner_name = [player.name for player in players if player.result == 'Win'][0]

    # Assume player 1 is always the first player listed
    player1_name = players[0].name
    player1_race = players[0].play_race
    player2_name = players[1].name
    player2_race = players[1].play_race
    match_up = f"{player1_race[0]}v{player2_race[0]}"

    win = personal_account in winner_name
    category = "personal" if personal_account in [player1_name, player2_name] else "public"

    replay_info = {
        "game_uuid": uuid,
        "start_time": start_time,
        "game_length": game_length,
        "player1_name": player1_name,
        "player1_race": player1_race,
        "player2_name": player2_name,
        "player2_race": player2_race,
        "winner_name": winner_name,
        "match_up": match_up,
        "win": win,
        "category": category
    }
    insert_replay_data(conn, replay_info)

# Function to insert unit composition data into the database
def insert_unit_composition_data(conn, replay_id, player_name, unit_type, unit_category, count, percentage):
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("""
            INSERT INTO unit_compositions (replay_id, player_name, unit, unit_category, unit_count, unit_percentage)
            VALUES (%s, %s, %s, %s, %s, %s)
        """), (replay_id, player_name, unit_type, unit_category, count, percentage))
        conn.commit()


def extract_and_save_unit_compositions(conn, replay_file, replay_id):
    replay = sc2reader.load_replay(replay_file)
    replay_id = str(uuid.uuid4())  # Generate a unique ID for each replay
    unit_compositions = {player.name: {} for player in replay.players}
    invalid_units = {
        "BeaconArmy", "BeaconDefend", "BeaconAttack", "BeaconHarass", "BeaconIdle",
        "BeaconAuto", "BeaconDetect", "BeaconScout", "BeaconClaim", "BeaconExpand",
        "BeaconRally", "BeaconCustom1", "BeaconCustom2", "BeaconCustom3", "BeaconCustom4",
        "CommandCenter", "KD8Charge", "Hatchery", "Lair", "Hive", "Extractor", "Nexus",
        "OrbitalCommand", "AutoTurret", "MULE", "Larva","Interceptor", 'Larva',
        'InvisibleTargetDummy', 'Corruptor', 'SwarmHostMP', 'Infestor',
        'ChangelingMarineShield', 'BroodlingEscort', 'Interceptor', 'AdeptPhaseShift'
    }

    for event in replay.events:
        if isinstance(event, sc2reader.events.tracker.UnitBornEvent):
            player_name = event.unit.owner.name if event.unit.owner else "Neutral"
            if player_name not in unit_compositions:
                continue

            unit_type = event.unit_type_name
            if unit_type in invalid_units:
                continue
            if unit_type in unit_compositions[player_name]:
                unit_compositions[player_name][unit_type] += 1
            else:
                unit_compositions[player_name][unit_type] = 1

    # Insert data into the database
    for player_name, units in unit_compositions.items():
        total_units = sum(units.values())
        for unit_type, count in units.items():
            percentage = (count / total_units) if total_units > 0 else 0
            insert_unit_composition_data(conn, replay_id, player_name, unit_type, 'TBD',count, round(percentage, 2))
   


def save_replay_data(directory, conn):
    for filename in os.listdir(directory):
        if filename.endswith(".SC2Replay"):
            try:
                game_uuid = str(uuid.uuid4())
                filepath = os.path.join(directory, filename)
                extract_and_save_replay_info(conn, filepath, uuid=game_uuid)
                extract_and_save_unit_compositions(conn, filepath, game_uuid)
                print(f"Processed {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                continue

# Example usage


if __name__ == "__main__":
    # Example usage
    conn = create_connection()
    check_user_and_roles(conn)
    directory = "/mnt/c/Users/matth/Documents/StarCraft II/Accounts/86722028/1-S2-1-3925175/Replays/Multiplayer/"
    all_replay_data = save_replay_data(directory, conn)


    # input_file = "data/replays_data.json"
    # tvt_output_csv = "data/tvt_cluster_stats.csv"
    # tvp_output_csv = "data/tvp_cluster_stats.csv"
    # tvz_output_csv = "data/tvz_cluster_stats.csv"
    # with open(input_file, "r") as f:
    #     replay_data = json.load(f)

    # analyze_replays_by_race(replay_data, 'Terran', tvt_output_csv)
    # analyze_replays_by_race(replay_data, 'Protoss', tvp_output_csv)
    # analyze_replays_by_race(replay_data, 'Zerg', tvz_output_csv)
