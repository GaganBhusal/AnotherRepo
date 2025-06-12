import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.25)

# Sliders
axx = plt.axes([0.25, 0.15, 0.65, 0.03])
axy = plt.axes([0.25, 0.1, 0.65, 0.03])
x_slider = Slider(axx, "X", 0, 180, valinit=50)
y_slider = Slider(axy, "Y", 0, 180, valinit=90)

"""Arm lengths"""
arm1, arm2 = 40, 40

"""Starting pivot"""
pivotX_init, pivotY = 50, 150

is_animating = [False]


"""Cyclodial Path for forward Movement"""
def cycloidal_between(start, end, steps=25, lift_ratio=0.5):
    t = np.linspace(0, 1, steps)
    dx, dy = end[0] - start[0], end[1] - start[1]
    distance = np.hypot(dx, dy)
    height = lift_ratio * distance
    x = start[0] + dx * (t - (1 / (2 * np.pi)) * np.sin(2 * np.pi * t))
    y_base = start[1] + dy * t
    y = y_base + height * np.sin(np.pi * t)
    return x, y


"""Linear Shape"""
# def stance_phase_fixed_foot(foot_pos, pivot_start, pivot_end, steps=25):
#     t = np.linspace(0, 1, steps)
#     pivot_x = (1 - t) * pivot_start[0] + t * pivot_end[0]
#     pivot_y = (1 - t) * pivot_start[1] + t * pivot_end[1]
#     return pivot_x, pivot_y

"""Bobbing Shape"""
def stance_phase_fixed_foot(foot_pos, pivot_start, pivot_end, steps=25):
    t = np.linspace(0, 1, steps)
    pivot_x = (1 - t) * pivot_start[0] + t * pivot_end[0]

    vertical_bob = 3 * np.sin(np.pi * t)  #
    pivot_y = (1 - t) * pivot_start[1] + t * pivot_end[1] + vertical_bob

    return pivot_x, pivot_y


"""Applied Inverse Kinematics"""
def apply_ik(x, y, pivotX, pivotY):
    dx, dy = x - pivotX, y - pivotY
    b = np.hypot(dx, dy)
    max_dist = arm1 + arm2

    if b > max_dist:
        x = pivotX + dx * max_dist / b
        y = pivotY + dy * max_dist / b
        dx, dy = x - pivotX, y - pivotY
        b = max_dist

    cos_beta = (b**2 - arm1**2 - arm2**2) / (2 * arm1 * arm2)
    beta = np.arccos(np.clip(cos_beta, -1, 1))
    k1 = arm1 + arm2 * np.cos(beta)
    k2 = arm2 * np.sin(beta)
    alpha = np.arctan2(dy, dx) - np.arctan2(k2, k1)

    elbowX = pivotX + arm1 * np.cos(alpha)
    elbowY = pivotY + arm1 * np.sin(alpha)
    wristX = elbowX + arm2 * np.cos(alpha + beta)
    wristY = elbowY + arm2 * np.sin(alpha + beta)

    ax.clear()
    ax.plot([pivotX, elbowX], [pivotY, elbowY], 'ro-', linewidth=4, label='Arm')
    ax.plot([elbowX, wristX], [elbowY, wristY], 'ro-', linewidth=4)
    ax.plot(x, y, 'gx', markersize=10, label='Foot')
    ax.text(0, 180, f"x: {x:.2f}, y: {y:.2f}\nα: {np.rad2deg(alpha):.1f}, β: {np.rad2deg(beta):.1f}")
    ax.axhline(90, color='gray', linestyle='--')
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 200)
    ax.set_aspect('equal')
    ax.legend()
    fig.canvas.draw_idle()


"""Updating Sliders"""
def update(val):
    x = x_slider.val
    y = y_slider.val
    apply_ik(x, y, pivotX_init, pivotY)


"""Updating the plot"""
def drawww(start_foot, end_foot, pivot_start, pivot_end):
    if is_animating[0]:
        return
    is_animating[0] = True


    """Swing"""
    swing_x, swing_y = cycloidal_between(start_foot, end_foot, steps=30)
    for x, y in zip(swing_x, swing_y):
        x_slider.set_val(x)
        y_slider.set_val(y)
        apply_ik(x, y, pivot_start[0], pivot_start[1])
        plt.pause(0.01)

    """Stance"""
    stance_pivot_x, stance_pivot_y = stance_phase_fixed_foot(end_foot, pivot_start, pivot_end, steps=30)
    for px, py in zip(stance_pivot_x, stance_pivot_y):
        x_slider.set_val(end_foot[0])
        y_slider.set_val(end_foot[1])
        apply_ik(end_foot[0], end_foot[1], px, py)
        plt.pause(0.01)

    is_animating[0] = False

x_slider.on_changed(update)
y_slider.on_changed(update)
update(None)

footsteps = [(50, 90), (70, 90), (90, 90), (110, 90)]
pivot_positions = [(50, 150), (70, 150), (90, 150), (110, 150)]


while(1):
    for i in range(len(footsteps) - 1):
        drawww(footsteps[i], footsteps[i+1], pivot_positions[i], pivot_positions[i+1])

plt.show()
