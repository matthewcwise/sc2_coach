import sc2reader
import os

replay_path = '/mnt/c/Users/matth/Documents/StarCraft II/Accounts/86722028/1-S2-1-3925175/Replays/Multiplayer/Solaris LE (10).SC2Replay'

# Loop through all files in the replay folder
replay = sc2reader.load_replay(replay_path)
print(f"Replay: {replay}")
print("Game Length:", replay.game_length)
print("Map Name:", replay.map_name)
print("Players:", replay.players)

player_name_search = "TheLeengwist"
player_id = None

# for event in replay.events[:2]:  # Adjust the slice as needed
#     try:
#         if type(event).control_pid != 0:
#             print(f"Event: {type(event).__name__}")
#             attrs = [attr for attr in dir(event) if not attr.startswith('__') and not callable(getattr(event, attr))]
#             for attr in attrs:
#                 print(f"  {attr}: {getattr(event, attr)}")
#             try:
#                 print("Player:",event.player)
#             except:
#                 lasdf = 0
#             print("\n")
#     except:
#         print(f"Event: {type(event).__name__}, {type(event).second}")
        
        
for event in replay.events[:2]:  # Adjust the slice as needed
    print(f"Event: {type(event).__name__}, at: {getattr(event, 'second', None) }, affecting pid {getattr(event, 'pid', None)}")
    # attrs = [attr for attr in dir(event) if not attr.startswith('__') and not callable(getattr(event, attr))]
    # for attr in attrs:
    #     print(f"  {attr}: {getattr(event, attr)}")
    # try:
    #     print("Player:",event.player)
    # except:
    #     lasdf = 0
    print("\n")