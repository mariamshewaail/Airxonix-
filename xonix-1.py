import time
import random
import numpy as np
from random import randint
from OpenGL.GL import *
from OpenGL.GLUT import *
from game_over import *
from hearts import *
from OpenGL.GLU import *

####################################
########### constants ##############
####################################
GRID_DIVISION = 40
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
MAX_SPEED = 5
COLLISION_TIME = 0.1  # adjust this value as needed
WINDOW_WIDTH1 = 760
WINDOW_HEIGHT1 = 560
INTERVAL = 1

RIGHT = (1, 0)
LEFT = (-1, 0)
TOP = (0, 1)
BOTTOM = (0, -1)
# global texture


####################################
########### game state #############
####################################

current_delta = RIGHT

# chech lose and run
lose = False
run = False

# position
x = GRID_DIVISION // 2
y = 1

# border
border = []

# path
path = []


BALL_RADIUS = 10
BALL_COLOR = (1, 1, 0)
BALL_SPEED = 2
NUM_BALLS = 3
cell_width = WINDOW_WIDTH / GRID_DIVISION
cell_height = WINDOW_HEIGHT / GRID_DIVISION
balls = []
for i in range(NUM_BALLS):
    ball_x = random.randint(3, GRID_DIVISION - 2)
    print(ball_x)
    ball_y = random.randint(3, GRID_DIVISION - 2)
    print(ball_y)
    ball_direction = [random.choice([-1, 1]), random.choice([-1, 1])]
    balls.append(
        [
            ball_x * cell_width,
            ball_y * cell_height,
            BALL_RADIUS,
            BALL_COLOR,
            BALL_SPEED,
            ball_direction,
        ]
    )


def draw_ball(ball):
    glBegin(GL_POLYGON)
    glColor3f(*ball[3])
    for i in range(360):
        rad = i * np.pi / 180
        x = (ball[0]) + (ball[2] * np.cos(rad))
        y = (ball[1]) + (ball[2] * np.sin(rad))
        glVertex2f(x, y)
    glEnd()


def draw_balls():
    for ball in balls:
        draw_ball(ball)


def update_balls():
    global lose
    for i in range(NUM_BALLS):
        ball1 = balls[i]
        ball1[0] += ball1[4] * ball1[5][0]
        ball1[1] += ball1[4] * ball1[5][1]

        # check if ball hits the walls
        if (
            ball1[0] - ball1[2] == cell_width
            or ball1[0] + ball1[2] == WINDOW_WIDTH - cell_width
        ):
            ball1[5][0] *= -1
        if (
            ball1[1] - ball1[2] == cell_width
            or ball1[1] + ball1[2] == WINDOW_HEIGHT - cell_width
        ):
            ball1[5][1] *= -1

        # check if ball intersects with path
        for cell in path:
            cx, cy = (
                cell[0] * cell_width + cell_width / 2,
                cell[1] * cell_height + cell_height / 2,
            )
            dx, dy = ball1[0] - cx, ball1[1] - cy
            distance = np.sqrt(dx**2 + dy**2)
            if distance < ball1[2] + cell_width / 2:
                lose = True
        # collision with border
        for cell in border:
            cx, cy = (
                cell[0] * cell_width + cell_width / 2,
                cell[1] * cell_height + cell_height / 2,
            )
            dx, dy = ball1[0] - cx, ball1[1] - cy
            distance = np.sqrt(dx**2 + dy**2)
            if distance < ball1[2] + cell_width / 2:
                ball1[5][0] *= -1
                ball1[5][1] *= -1

        # check for collision with other balls
        for j in range(i + 1, NUM_BALLS):
            ball2 = balls[j]
            dx, dy = ball1[0] - ball2[0], ball1[1] - ball2[1]
            distance = np.sqrt(dx**2 + dy**2)
            if distance < ball1[2] + ball2[2]:
                # calculate new velocities after collision
                v1 = np.array(ball1[5]) * ball1[4]
                v2 = np.array(ball2[5]) * ball2[4]
                m1 = np.pi * ball1[2] ** 2  # assuming density is 1
                m2 = np.pi * ball2[2] ** 2
                v1_new = v1 - 2 * m2 / (m1 + m2) * np.dot(
                    v1 - v2, np.array(ball1[0:2]) - np.array(ball2[0:2])
                ) / distance**2 * (np.array(ball1[0:2]) - np.array(ball2[0:2]))
                v2_new = v2 - 2 * m1 / (m1 + m2) * np.dot(
                    v2 - v1, np.array(ball2[0:2]) - np.array(ball1[0:2])
                ) / distance**2 * (np.array(ball2[0:2]) - np.array(ball1[0:2]))
                ball1[5] = list(v1_new / np.linalg.norm(v1_new))
                ball2[5] = list(v2_new / np.linalg.norm(v2_new))
                ball1[4] = np.linalg.norm(v1_new)
                ball2[4] = np.linalg.norm(v2_new)

                # move the balls apart
                overlap_vec = get_overlap_vector(ball1, ball2)
                if overlap_vec is not None:
                    ball1[0] -= overlap_vec[0] * 0.5
                    ball1[1] -= overlap_vec[1] * 0.5
                    ball2[0] += overlap_vec[0] * 0.5
                    ball2[1] += overlap_vec[1] * 0.5


def get_overlap_vector(ball1, ball2):
    """
    Returns the minimum translation vector needed to separate two balls.
    If the balls do not overlap, returns None.
    """
    dx, dy = ball1[0] - ball2[0], ball1[1] - ball2[1]
    distance = np.sqrt(dx**2 + dy**2)
    if distance >= ball1[2] + ball2[2]:
        return None

    # get the axes of separation
    axes = []
    for angle in range(0, 360, 10):
        axes.append(np.array([np.cos(np.radians(angle)), np.sin(np.radians(angle))]))

    # project the balls onto the axes and check for overlap
    overlap = float("inf")
    overlap_axis = None
    for axis in axes:
        projection1 = project_onto_axis(ball1, axis)
        projection2 = project_onto_axis(ball2, axis)
        if not overlap_on_axis(projection1, projection2):
            return None
        else:
            o = get_overlap_on_axis(projection1, projection2)
            if o < overlap:
                overlap = o
                overlap_axis = axis

    # calculate the minimum translation vector
    mtv = overlap_axis * overlap
    return mtv


def project_onto_axis(ball, axis):
    """
    Projects a ball onto an axis and returns the min and max projection values.
    """
    center = np.array(ball[:2])
    radius = ball[2]
    projection = np.dot(center, axis)
    min_proj = projection - radius
    max_proj = projection + radius
    return (min_proj, max_proj)


def overlap_on_axis(projection1, projection2):
    """
    Checks if two 1D projections overlap.
    """
    return (projection1[0] <= projection2[1]) and (projection2[0] <= projection1[1])


def get_overlap_on_axis(projection1, projection2):
    """
    Returns the overlap distance between two 1D projections.
    Assumes that the projections overlap.
    """
    return min(projection1[1], projection2[1]) - max(projection1[0], projection2[0])


# points of walls
for i in range(GRID_DIVISION):
    border.append((i, 0))
    border.append((i, GRID_DIVISION - 1))
for j in range(GRID_DIVISION):
    border.append((0, j))
    border.append((GRID_DIVISION - 1, j))


####################################
######## graphics helpers ##########
####################################
def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)

    glMatrixMode(GL_PROJECTION)  # ortho or perspective NO BRAINER
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, 0, 1)  # l,r,b,t,n,f
    glMatrixMode(GL_MODELVIEW)
    init_tex()

def draw_cell(i, j):
    cell_width = WINDOW_WIDTH / GRID_DIVISION
    cell_height = WINDOW_HEIGHT / GRID_DIVISION
    glBegin(GL_QUADS)
    glVertex2d(cell_width * i, cell_height * j)
    glVertex2d(cell_width * (i + 1), cell_height * j)
    glVertex2d(cell_width * (i + 1), cell_height * (j + 1))
    glVertex2d(cell_width * i, cell_height * (j + 1))
    glEnd()


def draw_border():
    for i, j in border:
        draw_cell(i, j)


def draw_path():
    for i, j in path:
        draw_cell(i, j)


def draw_fan(a, b):
    glColor3f(1.0, 0, 1.0)
    draw_cell(a, b)

def appear_tex():
    global lose
    if lose:
        draw_tex()

def display():
    global path, border, lose, texture

    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)
    draw_balls()

    if not lose:
        update_balls()


    # check losing

    if (x, y) in path:
        if (x, y) not in border:
            lose = True
    # Check if the fan has touched the border
    if (x, y) in border:
        # Append the points in the path and border to the border list
        for point in path:
            if point not in border:
                border.append(point)
        path.clear()
        glColor(1, 1, 0)  # Set color to white
        draw_border()
        glColor(1, 1, 1)
        draw_path()
        glColor(1, 0, 1)
        draw_fan(x, y)

    else:
        glColor(1, 1, 0)  # Set color to white
        draw_border()
        glColor(1, 1, 1)
        draw_path()
        glColor(1, 0, 1)
        draw_fan(x, y)
    appear_tex()
    glutSwapBuffers()


####################################
############### Timers #############
####################################


def game_timer(v):
    display()
    glutTimerFunc(INTERVAL, game_timer, 1)


####################################
############ Callbacks #############
####################################
def keyboard_callback(key, X, Y):
    global x, y, lose
    if not lose:
        path.append((x, y))
        if key == GLUT_KEY_LEFT and x > 0:
            x -= 1
        elif key == GLUT_KEY_RIGHT and x < GRID_DIVISION - 1:
            x += 1
        elif key == GLUT_KEY_UP and y < GRID_DIVISION - 1:
            y += 1
        elif key == GLUT_KEY_DOWN and y > 0:
            y -= 1


if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"airxonix")
    glutDisplayFunc(display)
    glutDisplayFunc(draw_tex)
    glutTimerFunc(INTERVAL, game_timer, 1)
    glutSpecialFunc(keyboard_callback)
    init()
    glutMainLoop()
