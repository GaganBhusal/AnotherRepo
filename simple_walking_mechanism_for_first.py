import numpy as np
import matplotlib.pyplot as plt

class WalkingMechanism:

    def __init__(self, arm1, arm2, pivotX, pivotY, start, step_length, ax, fig):
        self.arm1 = arm1
        self.arm2 = arm2
        self.pivotX = pivotX
        self.pivotY = pivotY
        self.x0, self.y0 = start[0], start[1]
        self.step_length = step_length
        self.ax = ax
        self.is_animating = False
        self.fig = fig

        self.cycloidal_between()


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



    """Cyclodial Path for forward Movement"""
    def cycloidal_between(self, steps=15, lift_ratio=0.5):
        t = np.linspace(0, 1, steps)

        dx, dy = self.step_length, 0
        distance = np.hypot(dx, dy)
        height = lift_ratio * distance
        x = self.x0 + dx * (t - (1 / (2 * np.pi)) * np.sin(2 * np.pi * t))
        y_base = self.y0 + dy * t
        y = y_base + height * np.sin(np.pi * t)
        return x, y

    """Bobbing Shape"""
    def stance_phase_fixed_foot(self, steps=15):
        t = np.linspace(0, 1, steps)
        pivot_x = (1 - t) * self.pivotX + t * (self.pivotX + self.step_length)

        vertical_bob = 3 * np.sin(np.pi * t)  
        pivot_y = (1 - t) * self.pivotY + t * self.pivotY + vertical_bob

        return pivot_x, pivot_y

    def ik(self, x, y, pX, pY):
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

    
    def working_pipeline(self):
        if self.is_animating:
            return
        self.is_animating = True


        swing_x, swing_y = self.cycloidal_between()
        for x, y in zip(swing_x, swing_y):
            # x_slider.set_val(x)
            # y_slider.set_val(y)
            # self.ik(x, y, self.pivotX, self.pivotY)  #ELBOW DOWN
            self.ik(self.pivotX, self.pivotY, x, y)   #ELBOW UP
            plt.pause(0.01)

        self.x0 += self.step_length
        self.y0 = self.y0

        stance_pivot_x, stance_pivot_y = self.stance_phase_fixed_foot()
        for px, py in zip(stance_pivot_x, stance_pivot_y):
            # x_slider.set_val(self.x0 + s[0])
            # y_slider.set_val(end_foot[1])
            self.ik(px, py, self.x0, self.y0)      #ELBOW UP
            # self.ik(self.x0, self.y0, px, py)   # ELBOW DOWN
            plt.pause(0.01)

        self.pivotX += self.step_length
        self.pivotY = self.pivotY

        self.is_animating = False



fig, ax = plt.subplots(2, 2)
wm = [WalkingMechanism(40, 40, 50, 150, (50, 90), 20, ax[0][0], fig),
      WalkingMechanism(40, 40, 50, 150, (50, 90), 20, ax[0][1], fig),
      WalkingMechanism(40, 40, 50, 150, (50, 90), 20, ax[1][0], fig),
      WalkingMechanism(40, 40, 50, 150, (50, 90), 20, ax[1][1], fig),
    ]

while 1:
    for i in range(4):


        wm[i].working_pipeline()


