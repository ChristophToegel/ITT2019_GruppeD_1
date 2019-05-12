import numpy

# constants
PARTICIPANTS = 4
TIME_BETWEEN_SIGNALS = 1000
TRIALS = 40

# create empty list for trails
trials_base_list = []

# all possible variations
modi = ['AD', 'AN', 'PD', 'PN']

#create basic list
for i in range (TRIALS):
    trials_base_list.append(modi[i%len(modi)])


for i in range (PARTICIPANTS):
    # convert participant number to 1-based index
    particip_num = i + 1

    # open file
    file = open("Participant_" + str(particip_num) + ".txt", "a")

    # randomly permutate List
    trials_perm_list = numpy.random.permutation(trials_base_list).tolist()
    # https://www.geeksforgeeks.org/join-function-python/
    trials_string = ", ".join(trials_perm_list)

    # add lines to file
    line_1 = f"PARTICIPANT: {str(particip_num)}\n"
    line_2 = f"TRIALS: {trials_string}\n"
    line_3 = f"TIME_BETWEEN_SIGNALS: {str(TIME_BETWEEN_SIGNALS)}\n"

    # add lines
    file.write(line_1)
    file.write(line_2)
    file.write(line_3)

    # close file
    file.close()
