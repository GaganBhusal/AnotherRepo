import numpy as np
import matplotlib.pyplot as plt



class GaitMechanism:

    def __init__(self, clock, swing_phase):
        self.clock = clock
        self.swing_phase = swing_phase
        self.stance_phase = 1 - self.swing_phase

    def get_current_phase(self):
        pass


LEG1 = 40
LEG2 = 40
PIVOTx = 50
PIVOTy = 150
START = (50, 90)
STEP_LENGTH = 20


class WalkingMechanism:

    def __init__(self, arm1, arm2, pivotX, pivotY, start, step_length, ax, fig, offset):
        self.arm1 = arm1
        self.arm2 = arm2
        self.pivotX = pivotX
        self.pivotY = pivotY
        self.x1, self.y1 = start[0], start[1]
        self.step_lengthX = step_length
        self.step_lengthY = 10
        self.ax = ax
        self.is_animating = False
        self.fig = fig
        self.swing_steps = 8
        self.stance_steps = 24
        self.gait_cycle_len = self.swing_steps + self.stance_steps
        self.offset = offset
        self.current_phase = 0

    def subplots(self, x, y, pX, pY):

        self.ax.clear()
        self.ax.plot([pX, self.elbowX], [pY, self.elbowY], 'ro-', linewidth=4, label='Arm')
        self.ax.plot([self.elbowX, self.wristX], [self.elbowY, self.wristY], 'ro-', linewidth=4)
        self.ax.plot(x, y, 'gx', markersize=10, label='Foot')
        self.ax.text(0, 180, f"x: {x:.2f}, y: {y:.2f}\nα: {np.rad2deg(self.alpha):.1f}, β: {np.rad2deg(self.beta):.1f}")
        self.ax.axhline(90, color='gray', linestyle='--')
        self.ax.set_xlim(0, 200)
        self.ax.set_ylim(0, 200)
        self.ax.set_aspect('equal')
        self.ax.legend()
        self.fig.canvas.draw_idle()


    
    def elliptical_path(self):
        
        swing_theta = np.linspace(np.pi, 0, self.swing_steps)
        swing_x = self.x1 + (self.step_lengthX / 2) * np.cos(swing_theta)
        swing_y = self.y1 + self.step_lengthY * np.sin(swing_theta)

        stance_x = np.linspace(self.x1 + self.step_lengthX / 2,self.x1 - self.step_lengthX / 2, self.stance_steps)
        stance_y = np.full(self.stance_steps, self.y1)

        x = np.concatenate([swing_x, stance_x])
        y = np.concatenate([swing_y, stance_y])

        print(x)

        return x, y

    def ik(self, x, y, pX = 0, pY = 0):
        dx, dy = x - pX, y - pY
        b = np.hypot(dx, dy)
        max_dist = self.arm1 + self.arm2

        if b > max_dist:
            x = pX + dx * max_dist / b
            y = pY + dy * max_dist / b
            dx, dy = x - pX, y - pY
            b = max_dist

        cos_beta = (b**2 - self.arm1**2 - self.arm2**2) / (2 * self.arm1 * self.arm2)
        self.beta = np.arccos(np.clip(cos_beta, -1, 1))
        k1 = self.arm1 + self.arm2 * np.cos(self.beta)
        k2 = self.arm2 * np.sin(self.beta)
        self.alpha = np.arctan2(dy, dx) - np.arctan2(k2, k1)

        self.elbowX = pX + self.arm1 * np.cos(self.alpha)
        self.elbowY = pY + self.arm1 * np.sin(self.alpha)
        self.wristX = self.elbowX + self.arm2 * np.cos(self.alpha + self.beta)
        self.wristY = self.elbowY + self.arm2 * np.sin(self.alpha + self.beta)

        self.subplots(x, y, pX, pY)


    def swing_phase(self):
        swing_x, swing_y = self.cycloidal_between()

        return swing_x, swing_y, self.pivotX, self.pivotY


    def stance_phase(self):
        stance_pivot_x, stance_pivot_y = self.stance_phase_fixed_pivot()
        return stance_pivot_x, stance_pivot_y, self.pivotX, self.pivotY




class LegMovement():

    def __init__(self, legs):
        self.legs = legs


    def start(self):
        steps = 0
        while True:
            
            leg_trajectories = [leg.elliptical_path() for leg in self.legs]

            leg_positions = []
            for i, (x_path, y_path) in enumerate(leg_trajectories):
                idx = (steps + self.legs[i].offset * self.legs[i].swing_steps) % self.legs[i].gait_cycle_len
                leg_positions.append((x_path[idx], y_path[idx]))

            for i in range(4):
                x, y = leg_positions[i]
                self.legs[i].ik(x, y, self.legs[i].pivotX, self.legs[i].pivotY)

            plt.pause(0.01)
            steps += 1






fig, ax = plt.subplots(2, 2, figsize = (12, 10))
fig
wm = [WalkingMechanism(LEG1, LEG2, PIVOTx, PIVOTy, START, STEP_LENGTH, ax[0][1], fig, 0),
      WalkingMechanism(LEG1, LEG2, PIVOTx, PIVOTy, START, STEP_LENGTH, ax[1][1], fig, 2),
      WalkingMechanism(LEG1, LEG2, PIVOTx, PIVOTy, START, STEP_LENGTH, ax[0][0], fig, 1),
      WalkingMechanism(LEG1, LEG2, PIVOTx, PIVOTy, START, STEP_LENGTH, ax[1][0], fig, 3),
    ]


Lm = LegMovement(wm)
Lm.start()


