#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Uniformity illusion fMRI paradigm
Clement Abbatecola

2025/11/11
    Code version 1.0

Features:
- 4 conditions:
    tra_1 / tra_2 (flat colours to train classifier)
    illus (to test classifier)
    local(izer)
- modifiable timing:
    1 trial = 12s  for loc, 10 for training, 16 for illusion (1-6s for the illusion to take hold)
    ISI = 12s + random jitter in [-1,-.5,0,.5,1]
    5s fixation at the start
- presentation order optimised for fMRI
- 6 reps/run of each condition (balanced latin square for the 3 experimental conditions)
- logfile
- trigger
- task (respond when illusion is complete)
- fade-in and fade-out for training and illusion trials
"""

from psychopy import core, visual, gui, event
import random, datetime, os
import numpy as np
from itertools import permutations


######
#### Initialize experiment
######

## global parameters
trial_time = 12
ITI = 12
tick = 1/5  # flickering per sec for loc
delay = 2 # fading stim time
bg_col = [-1,-1,-1] # background color

is_scanner = False
trigger = "s"
resp_key = '6'

## path
#main_path = 'd:/Mucklis_lab/uniformity_illusion'
main_path = './'
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
#win = visual.Window([1920,1080], allowGUI=False, monitor = 'vision_coil', units = 'deg', color = bg_col, allowStencil=True, fullscr=True, screen = 1)
win = visual.Window([1400,900], allowGUI=False, monitor = 'testMonitor', units = 'deg', color = bg_col, allowStencil=True,fullscr=True, screen = 1) # 3T
#win = visual.Window([1000,1000], allowGUI=False, monitor = 'ICE', units = 'deg', allowStencil=True, fullscr=True, screen = 1)

######
#### Stimulation, sequences & trials
######

mult = 0.6
cent = [0,-.2]

stim = visual.ImageStim(win, image = stim_path + "training_red.bmp", size = [2*mult,2*mult], pos = cent, units = 'norm')
fix = visual.TextStim(win, '+', pos = cent, units = 'norm')
loc_images = [visual.GratingStim(win, color =    [1,1,1], sf = 25, tex="sqrXsqr", size = [2*mult,2*mult], pos = cent, units = 'norm'),
              visual.GratingStim(win, color = [-1,-1,-1], sf = 25, tex="sqrXsqr", size = [2*mult,2*mult], pos = cent, units = 'norm')]
loc_bg = [visual.ImageStim(win, image = stim_path + "bg.bmp", size = [2*mult,2*mult], pos = [cent[0] + 0, cent[1]-1*mult], units = 'norm'),
          visual.ImageStim(win, image = stim_path + "bg.bmp", size = [1.3*mult,1.3*mult], pos = cent, units = 'norm')]


## conditions
conditions = {'tra_R':stim_path + 'training_red.bmp',
              'tra_G':stim_path + 'training_green.bmp',
              'illus':stim_path + 'UI.bmp'}

## sequences
trial_sequence = [0,1,2,3, # balanced latin square for the 3 experimental conditions
                  1,2,0,3, # loc at the end of each repetition
                  2,0,1,3,
                  0,2,1,3,
                  1,0,2,3,
                  2,1,0,3]

jitter_sequence = [-1,-.5,0,.5,1] * (len(trial_sequence) // 5) + [0] * (len(trial_sequence) % 5)
random.shuffle(jitter_sequence)

## correspondence
# each experimental condition is randomly assigned a trial type (numbers 0 to 2 from the sequence)
# loc is always 3 in trial sequence
trial_cor = random.sample(list(permutations(range(3))),1)[0] + (3,)
cond_dict = {0:'tra_R',1:'tra_G',2:'illus', 3: 'local'}
trial_cor = [cond_dict[t] for t in trial_cor]


######
#### Instructions & trigger
######

## first screen
visual.TextStim(win,'During the trials with the illusion, please respond when you perceive the screen as a uniform colour').draw()
win.flip()
k = ['wait']
while k[0] not in ['escape','space']:
    k = event.waitKeys()
if k[0] in ['escape']:
    win.close()
    core.quit()
## wait for trigger
visual.TextStim(win,'Waiting for trigger...').draw()
win.flip()
if is_scanner:
    from button_box_threading import buttonBoxThread
    button_thread = buttonBoxThread(1, "bottom box check")
    button_thread.start()
    button_state = button_thread.button_state
    button_state = button_state['state']
    while 1:
        if(button_state[-1]==0):
            break
else:
    k = ['wait']
    while k[0] not in ['escape', 'space']:
        k = event.waitKeys()
    if k[0] in ['escape']:
        logFile.close()
        os.remove(data_path + filename)
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

    ## trial
    trial_type = trial_cor[trial_sequence[trial]]
    print(trial_type, '\t', str(round(meta_clock.getTime(), 3)), '\t', trial + 1)
    logFile.write(trial_type + '\t' + str(round(meta_clock.getTime(), 3)) + '\n')
    
    this_trial_time = trial_time - 2 * (trial_type[0:3] == 'tra') + 4 * (trial_type == 'illus')
    
    ## timing
    trial_start = ITI_end
    trial_end = ITI_end + this_trial_time
    ITI_end = trial_end + ITI + jitter_sequence[trial]
    
    
    if trial_type != 'local':
        stim.image = conditions[trial_type]
        
        while meta_clock.getTime() < trial_end:
        
            if meta_clock.getTime() < trial_end - this_trial_time + delay:
                stim.opacity = (meta_clock.getTime() - (trial_end - this_trial_time)) / delay
            if meta_clock.getTime() > trial_end - delay:
                stim.opacity = (trial_end - meta_clock.getTime()) / delay
            
            stim.draw()
            fix.draw()
            win.flip()
            
            
            # responses
            if is_scanner:
                if trial_type == 'illus' and any([button_state[1]==1, button_state[2]==1]):
                    print('respo', '\t', str(round(meta_clock.getTime(), 2)))
                    logFile.write('respo\t' + str(round(meta_clock.getTime(), 2)) + '\n')
        
            k = event.getKeys([resp_key, 'escape'])
            if k:
                if trial_type == 'illus' and resp_key in k:
                    print('respo', '\t', str(round(meta_clock.getTime(), 2)))
                    logFile.write('respo\t' + str(round(meta_clock.getTime(), 2)) + '\n')
                if 'escape' in k:
                    abort = True
                if abort:
                    break
            
    else:
        next_tick = meta_clock.getTime()
        which_loc = True
        
        while meta_clock.getTime() < trial_end:   
            t = meta_clock.getTime()
            if t >= next_tick:
                next_tick += tick
                loc_images[which_loc].draw()
                which_loc = not which_loc
                [bg.draw() for bg in loc_bg]
                fix.draw()
                win.flip()
        
            k = event.getKeys(['escape'])
            if 'escape' in k:
                abort = True
            if abort:
                break
                
    
    ## ITI
    fix.draw()
    win.flip()
    while meta_clock.getTime() < ITI_end:
        k = event.getKeys(['escape'])
        if 'escape' in k:
            abort = True
            
        if abort:
            break

    if abort:
        print('abort!\t', str(round(meta_clock.getTime(), 2)))
        logFile.write('abort!\t' + str(round(meta_clock.getTime(), 2)) + '\n')
        break

if is_scanner:
    button_thread.stop()


## last screen
visual.TextStim(win,'Done!').draw()
logFile.close()
win.flip()
k = ['wait']
while k[0] not in ['escape', 'space']:
    k = event.waitKeys()
