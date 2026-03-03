#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mapping FOV for fMRI experiments using the Vision Coil
Clement Abbatecola

2026/03/02
    Code version 0.1

Features:
Before starting an experiment with the Vision Coil, run this script to optimise display size/position for the participant's field of view.
Move the screen with arrow keys, change scale with 'q' and 'w' keys.
When participant can see all 4 corners of a maximised size display, save and quit with 'escape' key.
Fuher stimulation scripts should be made compatible with this calibration (i.e. reading position and scale values from output file and implementing them).
"""

from psychopy import core, visual, gui, event
import datetime, os


######
#### Initialize experiment
######

## global parameters
bg_col = [0,0,0] # background color

## path
#main_path = 'd:/Mucklis_lab/uniformity_illusion'
main_path = '.'
data_path = main_path + "/FOV_data/"

## logfile
expInfo = {'ID':'XXX'}
dlg = gui.DlgFromDict(expInfo, title='Infos')
x = 1
filename =  expInfo['ID'].lower() + '_'
while (filename + str(x) + '.txt') in os.listdir(data_path): x += 1
filename = data_path + filename + str(x) + '.txt'

## window and elements
win = visual.Window([1920,1080], allowGUI=False, monitor = 'vision_coil', units = 'deg', color = bg_col, allowStencil=True, fullscr=True, screen = 1)

######
#### Stimulation
######

mult = 1
cent = [0,0]
size = [120,80]

stim = visual.GratingStim(win, color =    [1,1,1], sf = 10, tex="sqrXsqr", size = [size[0]*mult, size[1]*mult], pos = cent, units = 'deg')
fix = visual.TextStim(win, '+', pos = cent, units = 'deg', color = 'red')

## first screen
visual.TextStim(win,'Ready', pos = cent).draw()
win.flip()
k = ['wait']
while k[0] not in ['space']:
    k = event.waitKeys()

######
#### Main loop
######

stim.draw()
fix.draw()
win.flip()

while True:
    
    k = event.getKeys(['up', 'down', 'left', 'right', 'q', 'w', 'escape'])
    
    if k:
        if 'up' in k:
            cent[1] += .1
        elif 'down' in k:
            cent[1] -= .1
        elif 'left' in k:
            cent[0] -= .1
        elif 'right' in k:
            cent[0] += .1
        elif 'q' in k:
            mult += .01
        elif 'w' in k:
            mult -= .01
        elif 'escape' in k:
            ## log
            logFile = open(filename,'w')
            logFile.write('Size:\t{}\tCentre:\t{}\tMult:\t{}'.format(size, cent, mult))
            logFile.close()
            break
        
        fix.pos = cent
        stim.pos = cent
        stim.size = [size[0]*mult, size[1]*mult]
        
        stim.draw()
        fix.draw()
        win.flip()

## last screen
visual.TextStim(win,'Done!', pos = cent).draw()
win.flip()
k = ['wait']
while k[0] not in ['escape', 'space']:
    k = event.waitKeys()
