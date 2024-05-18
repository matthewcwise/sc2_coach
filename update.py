from save_replay_data import save_replay_data
from cluster_preprocessing import generate_race_csv
from cluster_generation import cluster_gen
from last_game import last_game

directories = [
    "/mnt/c/Users/matth/Documents/StarCraft II/Accounts/86722028/1-S2-1-3925175/Replays/Multiplayer/",
    #  "data/public_replays",
        ]

for directory in directories:
    save_replay_data(directory, overwrite=False)


# Call the function for each race
generate_race_csv('Terran')
generate_race_csv('Protoss')
generate_race_csv('Zerg')


for race in ["Terran", "Protoss", "Zerg"]:
    cluster_gen(race)


last_game()