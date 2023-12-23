import sc2reader
import os

replay_folder = '/mnt/c/Users/matth/Documents/StarCraft II/Accounts/86722028/1-S2-1-3925175/Replays/Multiplayer/'


def find_earliest_x_scv_time(replay, player_id, scv_count_benchmark = 45):
    scv_count = 0
    time_at_x_scv = None

    for event in replay.events:
        if getattr(event, 'pid', None) == player_id:
            
        # if isinstance(event, sc2reader.events.tracker.UnitBornEvent) and event.unit.name == 'SCV':
        #     if event.pid == player_id:
        #         scv_count += 1
        # elif isinstance(event, sc2reader.events.tracker.UnitDiedEvent) and event.unit.name == 'SCV':
        #     if event.pid == player_id:
        #         scv_count -= 1

        # if scv_count == scv_count_benchmark:
        #     time_at_x_scv = event.second
        #     break
        # print(event.player)

    return time_at_x_scv, scv_count_benchmark

# Loop through all files in the replay folder
for file_name in os.listdir(replay_folder):
    if file_name == 'Solaris LE (10).SC2Replay':
        replay_path = os.path.join(replay_folder, file_name)
        replay = sc2reader.load_replay(replay_path)
        print(f"Replay: {file_name}")
        print("Game Length:", replay.game_length)
        print("Map Name:", replay.map_name)
        print("Players:", replay.players)

        player_name_search = "TheLeengwist"
        player_id = None

        for player in replay.players:
            if player.name == player_name_search:
                player_id = player.pid
                break

        if player_id is not None:
            print(f"Player ID of '{player_name_search}' is: {player_id}")
        else:
            print(f"Player '{player_name_search}' not found in this replay.")
            
        x = find_earliest_x_scv_time(replay, player_id, scv_count_benchmark = 10)
        print(x)
