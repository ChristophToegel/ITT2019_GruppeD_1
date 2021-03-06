import math

'''
Workload distribution among team:
Julian: AnglePointing
'''
'''
The implemented AnglePointing Technique is a simple implementation of the Angle Mouse. The Idea behind this technique
can be compared to a car race, you are faster on the straight line and slower on the curves. In this case the angle
form the last point and actual point is calculated and if the difference is smaller than a defined difference the
mouse moves faster. The factor of the mouse boost and the difference angle is parameterizable. The boost also includes
the given step form the last point and the current point as a factor. To sum it up this pointing technique will speed
up your mouse if you move within an certain angle (close to linear).

used sources:
Wobbrock, J. O., Fogarty, J., Liu, S. Y. S., Kimuro, S., & Harada, S. (2009, April). The angle mouse: target-agnostic
dynamic gain adjustment based on angular deviation. In Proceedings of the SIGCHI Conferenceon Human Factors in
Computing Systems (pp. 1401-1410). ACM.
https://www.youtube.com/watch?v=O4ahGmHenps
https://stackoverflow.com/questions/42258637/how-to-know-the-angle-between-two-points
'''


class AnglePointing:

    # inits the used variables
    def __init__(self, boost_factor, angle_difference):
        self.last_pos = (0, 0)
        self.last_angle = 0
        self.boost = False
        self.boost_factor = boost_factor
        self.angle_difference = angle_difference
        self.debug = False

    def filter(self, current_x, current_y):
        if self.last_pos != (current_x, current_y):
            # sets the boost
            self.check_boost(current_y, current_x)

            # calclates the step
            step_x, step_y = self.calculate_step(current_x, current_y)

            if self.boost:
                new_x = int(current_x - (step_x * self.boost_factor))
                new_y = int(current_y - (step_y * self.boost_factor))
                self.last_pos = (new_x, new_y)
                self.debug_position(current_x, current_y, new_x, new_y)
                return new_x, new_y
            else:
                self.last_pos = (current_x, current_y)
                return current_x, current_y
        else:
            return current_x, current_y

    # sets the boost if angle has seriously changed
    def check_boost(self, current_y, current_x):
        if self.last_pos != (0, 0):
            radians = math.atan2(self.last_pos[1] - current_y, self.last_pos[0] - current_x)
            current_angle = math.degrees(radians)
            # checks if angle has seriously changed
            if abs(self.last_angle - current_angle) > self.angle_difference:
                self.boost = False
            else:
                self.boost = True
            if current_angle != 0:
                self.last_angle = current_angle

    def calculate_step(self, current_x, current_y):
        step_x = (self.last_pos[0] - current_x)
        step_y = (self.last_pos[1] - current_y)
        return step_x, step_y

    def debug_position(self, current_x, current_y, new_x, new_y):
        if self.debug:
            print('Pos changed from: (' + str(current_x) + ',' + str(current_y) + ') to (' + str(new_x) + ',' + str(
                new_y) + ')')
