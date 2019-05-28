import math

# https://stackoverflow.com/questions/42258637/how-to-know-the-angle-between-two-points
# https://www.youtube.com/watch?v=O4ahGmHenps

'''
    Simple implementaion of the angle mouse. TODO description text
'''


class AnglePointing:

    def __init__(self, target_near):
        #print('initialisieren mit boost:' + str(target_near))
        self.last_pos = (0, 0)
        self.positions = []
        self.last_angle = 0
        self.boost = False

    def filter(self, current_x, current_y):
        self.positions.append((current_x, current_y))
        if self.last_pos != (0, 0):
            radians = math.atan2(self.last_pos[1] - current_y, self.last_pos[0] - current_x)
            current_angle = math.degrees(radians)
            #print('current_angle:'+str(current_angle))
            #print('last_angle:' + str(self.last_angle))
            # check if angle has changed
            if abs(self.last_angle - current_angle) > 10:
                self.boost = False
                # print('nob')
            else:
                # print('boost')
                self.boost = True
            #print(abs(self.last_angle - current_angle))
            if current_angle != 0:
                self.last_angle=current_angle
            #print(self.boost)

        '''# get direction
        if self.last_pos[0] - current_x > 0:
            print('nach links')
            self.directon_right = False
            if self.last_pos[1] - current_y > 0:
                print('nach oben')
                self.directon_up = True
            else:
                print('nach unten')
                self.directon_up = False
        else:
            print('nach rechts')
            self.directon_right = True
            if self.last_pos[1] - current_y > 0:
                print('nach oben')
                self.directon_up = True
            else:
                print('nach unten')
                self.directon_up = False
        '''

        # step
        step_x = (self.last_pos[0] - current_x)
        step_y = (self.last_pos[1] - current_y)
        #print(step_x)
        #print(step_y)

        #print(self.last_pos)
        #print((current_x, current_y))
        if self.last_pos != (current_x, current_y):
            if self.boost:
                '''if self.directon_right:
                    new_x = current_x + 5
                else:
                    new_x = current_x - 5
                if self.directon_up:
                    new_y = current_y - 5
                else:
                    new_y = current_y + 5'''
                new_x = int(current_x - (step_x * 1.2))
                new_y = int(current_y - (step_y * 1.2))
                #print('changedTo')
                #print(new_x,new_y)
                self.last_pos = (new_x, new_y)
                return new_x, new_y
            else:
                self.last_pos = (current_x, current_y)
                return current_x, current_y
        else:
            return current_x, current_y
