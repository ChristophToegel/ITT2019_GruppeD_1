import json

num_participants = 4
repetitions = 40
distances = ['NEAR', 'FAR']
colors_target = ["yellow", "darkGray"]
colors_noise = ["darkBlue", "lightGray"]

# create empty list for trails
trials_base_list = []

# all possible variations
modi_p1 = [(distances[1],'ON'),(distances[0],'OFF'),(distances[1],'OFF'),(distances[0],'ON')] #1234
modi_p2 = [(distances[0],'ON'),(distances[1],'OFF'),(distances[0],'OFF'),(distances[1],'ON')] #4321
modi_p3 = [(distances[0],'OFF'),(distances[0],'ON'),(distances[1],'ON'),(distances[1],'OFF')] #2413
modi_p4 = [(distances[1],'OFF'),(distances[1],'ON'),(distances[0],'ON'),(distances[0],'OFF')] #3142

for i in range(num_participants):

    # current user num
    participant_user = str(i + 1)

    distance_list= []
    pointing_list = []

    for num in range(repetitions):
        if i==0:
            pointing_list.append(modi_p1[num % 4][1])
            distance_list.append(modi_p1[num % 4][0])
        elif i==1:
            pointing_list.append(modi_p2[num % 4][1])
            distance_list.append(modi_p2[num % 4][0])
        elif i==2:
            pointing_list.append(modi_p3[num% 4][1])
            distance_list.append(modi_p3[num % 4][0])
        elif i==3:
            pointing_list.append(modi_p4[num % 4][1])
            distance_list.append(modi_p4[num % 4][0])


    color_target = colors_target[0]
    color_noise = colors_noise[0]

    full_config = {"USER": participant_user,
                   "CONF": {
                    "DISTANCE": distance_list,
                    "NEW_POINTING_TECHNIQUE": pointing_list,
                    "COLOR_T": color_target,
                    "COLOR_N": color_noise}}

    json_str = json.dumps(full_config)

    print(json_str)
    conf_file = open("Participant_" + str(participant_user) + ".json", "a")
    conf_file.write(json_str)
    conf_file.close()
