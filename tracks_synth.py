import pygame as pg
import numpy as np

def synth_sine(frames, freq):
    arr = np.sin(2*np.pi*freq*np.linspace(0,frames/44100,frames))
##    arr = arr**3 # triangularish waves
##    arr = arr*2 # sawtoothish wawes (more like bats)
    arr = np.clip(100*arr, -1, 1) # squarish waves
    fade = list(np.ones(int(frames*3/4))) +list(np.linspace(1, 0, frames-int(frames*3/4))**2)
    arr = 32767*np.multiply(arr, np.asarray(fade))
    return arr

pg.init()
pg.mixer.init()

a_file = open("noteslist.txt")
file_contents = a_file.read(); a_file.close()
noteslist = file_contents.splitlines()
freq = 16.3516 #starting frequency
frequencies = []

for i in range(len(noteslist)):
    frequencies.append(freq)
    freq = freq * 2 ** (1/12)

with open("SuperMario.txt", "r") as file:
    keypresses = [eval(line.rstrip()) for line in file]
file.close()

track = []
for ii in range(int(len(keypresses)/2)):
    i = ii*2
    freq = frequencies[noteslist.index(keypresses[i][1])]
    track = track + list(np.zeros(max(0, int(44.1*(keypresses[i][2]-100)))))
    track = track + list(synth_sine(int(44.1*(keypresses[i+1][2]+100)), freq))

arr = np.asarray(track)
sound = np.asarray([arr,arr]).T.astype(np.int16)
sound = pg.sndarray.make_sound(sound.copy())

sound.play()

import wave
sfile = wave.open('mario.wav', 'w')

# set the parameters
sfile.setframerate(44100)
sfile.setnchannels(2)
sfile.setsampwidth(2)

# write raw PyGame sound buffer to wave file
sfile.writeframesraw(sound)

# close file
sfile.close()

pg.time.wait(int(len(arr)/44.1))
pg.quit()    
