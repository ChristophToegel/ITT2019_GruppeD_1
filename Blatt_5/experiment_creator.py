import json
import random


num_participants = 4
repetitions = 30

for i in range(num_participants):

    # current user num
    participant_user = str(i + 1)

    # get size of
    size_list = [10] * repetitions
    distances = []

    print(size_list)

    full_config = {"USER": participant_user, "SIZE": size_list, "DISTANCES": distances}

    json_str = json.dumps(full_config)

    #conf_file = open("Participant_" + str(participant_user) + ".json", "a")
    #conf_file.write(json_str)
    #conf_file.close()
