#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Uniformity illusion fMRI paradigm
Clement Abbatecola

2025/03/17
    Code version 0.1

Features:
- 5 conditions:
    Control 1 / control 2 (to train classifier)
    Uniformity illusion 1 / uniformity illusion 2 (to test classifier)
    Localizer
- modifiable timing, so far:
    1 trial = 12s (1-6s for the illusion to take hold depending on stim)
    ISI = 12s + random jitter in [-1,-.5,0,.5,1]
    5s fixation at the start
- presentation order optimised for fMRI
- 4 reps/run of each condition, which is the minimum for controlled order
- logfile

Roadmap:
- non placeholder stims
- MRI compatibility (trigger)
- occlusion?
- responses?
- ?
"""

from psychopy import core, visual, gui, event
import random, datetime, os
from itertools import permutations


######
#### Initialize experiment
######

## global parameters
trial_time = 12
ITI = 12

## path
main_path = "."
stim_path = main_path + "/stim/"
data_path = main_path + "/data/"

## logfile
expInfo = {'ID':'XXX'}
dlg = gui.DlgFromDict(expInfo, title='Infos')
x = 1
filename =  expInfo['ID'].lower() + '_'
while (filename + str(x) + '.txt') in os.listdir(data_path): x += 1
filename = data_path + filename + str(x) + '.txt'

## window and elements
win = visual.Window([1400,900], allowGUI=False, monitor = 'testMonitor', units = 'deg',allowStencil=True,fullscr=False, screen = 1)


######
#### Stimulation, sequences & trials
######

stim = visual.ImageStim(win, image = stim_path + "placeholder_loc.bmp")
fix = visual.TextStim(win, '+')

## conditions
conditions = {'con_1':stim_path + 'placeholder_control1.bmp',
              'con_2':stim_path + 'placeholder_control2.bmp',
              'uil_1':stim_path + 'placeholder_UI1.bmp',
              'uil_2':stim_path + 'placeholder_UI2.bmp',
              'local':stim_path + 'placeholder_loc.bmp'}

## sequences
trial_sequence = [0,1,2,3,4, # each trial type is presented once after all others except for 3->0
                  3,2,1,0,4, # each trial type is presented once within each batch of 5 trials
                  0,2,4,1,3,
                  1,4,2,0,3]

jitter_sequence = [-1,-.5,0,.5,1] * (len(trial_sequence) // 5) + [0] * (len(trial_sequence) % 5)
random.shuffle(jitter_sequence)

## correspondence
# each condition is randomly assigned a trial type (numbers 0 to 4 from the sequence)
trial_cor = random.sample(list(permutations(range(5))),1)[0]
cond_dict = {0:'con_1',1:'con_2',2:'uil_1',3:'uil_2',4:'local'}
trial_cor = [cond_dict[t] for t in trial_cor]


######
#### Instructions & trigger
######

## first screen
visual.TextStim(win,'instructions').draw()
win.flip()
k = ['wait']
while k[0] not in ['escape','space']:
    k = event.waitKeys()
if k[0] in ['escape']:
    win.close()
    core.quit()


######
#### Main loop
######

## prepare loop
logFile = open(filename,'w')
logFile.write(''.join(map(str, ["Start:\t" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + "\n"])))
logFile.write("Event\tOnset\n")
print("Start : \t" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
print("Event\tOnset\t")
meta_clock = core.Clock()
abort = False
trial_end = 0
ITI_end = 0

## first screen
ITI_end += 5
fix.draw()
win.flip()
while meta_clock.getTime() < ITI_end:
    k = event.getKeys(['escape'])
    if 'escape' in k:
        abort = True
        
    if abort:
        break

## main loop
for trial in range(len(trial_sequence)):

    ## timing
    trial_start = ITI_end
    trial_end = ITI_end + trial_time
    ITI_end = trial_end + ITI + jitter_sequence[trial]

    ## trial start
    trial_type = trial_cor[trial_sequence[trial]]
    stim.image = conditions[trial_type]
    print(trial_type, '\t', str(round(meta_clock.getTime(), 3)), '\t', trial + 1)
    logFile.write(trial_type + '\t' + str(round(meta_clock.getTime(), 3)) + '\n')
    
    stim.draw()
    fix.draw()
    win.flip()
    while meta_clock.getTime() < trial_end:   
        k = event.getKeys(['escape'])
        if 'escape' in k:
            abort = True
            
        if abort:
            break
    fix.draw()
    win.flip()
    while meta_clock.getTime() < ITI_end:
        k = event.getKeys(['escape'])
        if 'escape' in k:
            abort = True
            
        if abort:
            break

    if abort:
        print('abort!\t', str(round(meta_clock.getTime(), 3)))
        logFile.write('abort!\t' + str(round(meta_clock.getTime(), 3)) + '\n')
        break

## last screen
visual.TextStim(win,'Done!').draw()
logFile.close()
win.flip()
k = ['wait']
while k[0] not in ['escape', 'space']:
    k = event.waitKeys()