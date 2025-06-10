import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


fig, ax = plt.subplots()

fig.subplots_adjust(bottom = 0.25)
axx = plt.axes([0.25, 0.15, 0.65, 0.03])
axy = plt.axes([0.25, 0.1, 0.65, 0.03])


x_slider = Slider(axx, "X", 0, 180, valinit=90)
y_slider = Slider(axy, "Y", 0, 180, valinit=90)


def apply_ik(x, y):
    

    pivotX, pivotY = 60, 60

    arm1, arm2 = 40, 55
    # xlim, ylim = pivotX + arm1 + arm2, pivotY + arm1 +arm2

    # x, y = min(x, xlim), min(y, ylim)

    max_dist = arm1 + arm2
    dx, dy = x-pivotX, y - pivotY

    b = np.hypot(dx, dy)
    if b>max_dist:
        x = pivotX + dx * max_dist/b
        y = pivotY + dy * max_dist/b
    value_beta = (b**2 - arm1**2 - arm2**2)/(2*arm1*arm2)
    beta = np.arccos(np.clip(value_beta, -1, 1))
    alpha = np.arctan2((y-pivotY), (x-pivotX)) + np.arctan2(arm2 * np.sin(beta), arm2 * np.cos(beta) + arm1)
    
    elbowX = pivotX+arm1* np.cos(alpha)
    elbowY = pivotY + arm1 * np.sin(alpha)

    wristX = elbowX + arm2 * np.cos(alpha - beta)
    wristY = elbowY + arm2 * np.sin(alpha - beta)

    ax.clear()

    ax.plot([pivotX, elbowX], [pivotY, elbowY], 'ro-', linewidth = 4)
    ax.plot([elbowX, wristX], [elbowY, wristY], 'ro-', linewidth = 4)
    ax.plot(x, y, 'gx', markersize =10)

    ax.text(0, 180, f"x : {x:.2f}, y : {y:.2f}\nalpha : {np.rad2deg(alpha):.2f}, beta : {np.rad2deg(beta):.2f}")
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 200)
    ax.set_aspect('equal')
    ax.legend()
    fig.canvas.draw_idle()
    
    # print(alpha, beta)


def update(val):
    x = x_slider.val
    y = y_slider.val

    apply_ik(x, y)


x_slider.on_changed(update)
y_slider.on_changed(update)

update(None)
plt.show()