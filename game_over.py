from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame

global texture


def init_tex():
    global texture

    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_MODELVIEW)

    texture = glGenTextures(1)  # Generate 5 textures

    #######################################################################################################
    # Create MipMapped Texture
    imgload = pygame.image.load("unnamed.jpg")
    img = pygame.image.tostring(imgload, "RGBA", 1)
    width = imgload.get_width()
    height = imgload.get_height()
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    gluBuild2DMipmaps(GL_TEXTURE_2D, 4, width, height, GL_RGBA, GL_UNSIGNED_BYTE, img)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)


def draw_tex():
    global texture

    glClear(GL_COLOR_BUFFER_BIT)

    glColor(1, 1, 1)
    glBegin(GL_QUADS)

    glTexCoord(0, 0)
    glVertex2d(0,0)

    glTexCoord(1, 0)
    glVertex2d(800,0)

    glTexCoord(1, 1)
    glVertex2d(800,800)

    glTexCoord(0, 1)
    glVertex2d(0,800)

    glEnd()

    glFlush()

    # glDeleteTextures(texture)




