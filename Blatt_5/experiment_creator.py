import json

num_participants = 4
repetitions = 30
distances = [60, 150]
colors_target = ["yellow", "darkGray"]
colors_noise = ["darkBlue", "lightGray"]

for i in range(num_participants):

    # current user num
    participant_user = str(i + 1)

    # get size of
    size_list = [10] * repetitions
    distance_list = [distances[i % 2]] * repetitions

    if i >= 2:
        color_target = colors_target[0]
        color_noise = colors_noise[0]
    else:
        color_target = colors_target[1]
        color_noise = colors_noise[1]

    full_config = {"USER": participant_user,
                   "CONF": {
                    "SIZE": size_list,
                    "DISTANCE": distance_list,
                    "COLOR_T": color_target,
                    "COLOR_N": color_noise}}

    json_str = json.dumps(full_config)

    print(json_str)
    conf_file = open("Participant_" + str(participant_user) + ".json", "a")
    conf_file.write(json_str)
    conf_file.close()
