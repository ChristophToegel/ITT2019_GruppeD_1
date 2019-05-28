import json
import numpy

num_participants = 4
repetitions = 40
distances = [60, 150]
colors_target = ["yellow", "darkGray"]
colors_noise = ["darkBlue", "lightGray"]

# create empty list for trails
trials_base_list = []

# all possible variations
modi = [(distances[1],'ON'),(distances[0],'OFF'),(distances[1],'OFF'),(distances[0],'ON')]
pointing = []

for i in range(num_participants):

    # current user num
    participant_user = str(i + 1)

    distance_list= []
    pointing_list = []

    # create the counter balanced list?
    for num in range(repetitions):
        pointing_list.append(modi[(num+i) % 4][1])
        distance_list.append(modi[(num+i) % 4][0])

    # get size of
    size_list = [30] * repetitions

    color_target = colors_target[0]
    color_noise = colors_noise[0]

    full_config = {"USER": participant_user,
                   "CONF": {
                    "SIZE": size_list,
                    "DISTANCE": distance_list,
                    "NEW_POINTING_TECHNIQUE:": pointing_list,
                    "COLOR_T": color_target,
                    "COLOR_N": color_noise}}

    json_str = json.dumps(full_config)

    print(json_str)
    conf_file = open("Participant_" + str(participant_user) + ".json", "a")
    conf_file.write(json_str)
    conf_file.close()
