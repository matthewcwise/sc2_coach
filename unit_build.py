import sc2reader
from sc2reader.engine.plugins import APMTracker
sc2reader.engine.register_plugin(APMTracker())
import os

player_name_search = "TheLeengwist"

replay_folder = '/mnt/c/Users/matth/Documents/StarCraft II/Accounts/86722028/1-S2-1-3925175/Replays/Multiplayer/'

# Loop through all files in the replay folder
for file_name in os.listdir(replay_folder):
    if file_name.endswith('Site Delta LE (2).SC2Replay'):
        replay_path = os.path.join(replay_folder, file_name)
        replay = sc2reader.load_replay(replay_path)
        print(f"Replay: {file_name}")
        print("Game Length:", replay.game_length)
        print("Map Name:", replay.map_name)
        game_events = replay.events
        player_events = []
        # print("Players:", replay.players)
        for player in replay.players:
            if player.name == player_name_search:
                subject = player.pid
            print(f"Player: {player.name}, {player.pid}")
            print(f"  * APM: {player.name}, {player.avg_apm:.02f}")
            attributes = dir(player)
            # Filter out private and special methods/attributes
            filtered_attributes = [attr for attr in attributes if not attr.startswith('__')]
            attribute_data = player.attribute_data
            pid = player.pid
            pick_race = player.pick_race
            play_race = player.play_race
            player_events.append({pid:player.events})
            # for event in player_events[:1]:
            #     print(event)
            print(f"  * {len(player.events)} events")
            if pick_race==play_race:
                print(f"  * Picked and played {play_race}")
            else:
                print(f"  * Picked {pick_race} ({play_race})")
            print("\n")  # Print a newline for better separation between players

        player_name_search = "TheLeengwist"
        player_id = None
        
        replay_attributes = dir(replay)
        filtered_attributes = [attr for attr in replay_attributes if not attr.startswith('__')]
        for attr in filtered_attributes:
            value = getattr(replay, attr)  # Get the value of each attribute
            print(attr)
            # print(f"{attr}: {value}")
        print("\n")  # Print a newline for better separation between players
        replay_real_length = replay.real_length
        filtered_events = [
            event for event in replay.game_events 
            if hasattr(event, 'pid') and event.name != 'CameraEvent'
        ]
        # filtered_camera_events = [attr for attr in filtered_events if not attr.name('CameraEvent')]
        print("\n\n\n Game Events")
        for event in filtered_events[:30]:
        # Here we will print out a more readable format if needed
            # if hasattr(event, 'second'):
            #     # Convert seconds to a time format if it exists
            #     time_minutes = event.second // 60
            #     time_seconds = event.second % 60
            #     print(f"{time_minutes:02d}:{time_seconds:02d} {event.player.name}\t{event.name}")
            # else:
            print(event)
            # new_event_filter = [attr for attr in dir(event) if not attr.startswith('__')]
            # for item in new_event_filter:
            #     value = getattr(event, item)
            #     print("   * ", item, ":",value)
            # print("\n\n\n Events")
        # filtered_events = [event for event in replay.events if hasattr(pid, )]
        # for event in filtered_events[:100]:
        #     print(event)
        
        CommandManagerStateEvents = [
            event for event in replay.game_events 
            if hasattr(event, 'pid') and event.name == 'CommandManagerStateEvent'
        ]
        print("\n\n\nCommand Manager State Events:")
        for event in CommandManagerStateEvents[:5]:
            print(f"\nEvent at {event.second if hasattr(event, 'second') else 'unknown time'} seconds:")
            attributes = dir(event)
            # Filter out private and special methods/attributes
            filtered_attributes = [attr for attr in attributes if not attr.startswith('__')]
            for attr in filtered_attributes:
                value = getattr(event, attr)
                print(f"{attr}: {value}")
        
        # "Matt's Events:"
        # subject_events = [event for event in replay.game_events if hasattr(event, 'pid') and event.pid == subject]
        # for item in subject_events:
            # print(item)

        # for element in replay.data:
        #     if element.Unit:
        #         print(element.Unit)
        #     if player.name == player_name_search:
        #         player_id = player.pid
        #         break

        # if player_id is not None:
        #     print(f"Player ID of '{player_name_search}' is: {player_id}")
        #     time_at_x_scv, count = find_earliest_x_scv_time(replay, player_id)
        #     if time_at_x_scv is not None:
        #         print(f"Time to produce {scv_count_benchmark} SCVs: {time_at_x_scv} seconds")
        #     else:
        #         print("Benchmark SCV count not reached during the game.")
        # else:
        #     print(f"Player '{player_name_search}' not found in this replay.")
