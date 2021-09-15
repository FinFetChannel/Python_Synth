import pygame as pg
import numpy as np

def synth(frequency, duration=1.5, sampling_rate=44100):
    frames = int(duration*sampling_rate)
    arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
##    arr = arr + np.cos(4*np.pi*frequency*np.linspace(0,duration, frames)) # organ like
##    arr = arr + np.cos(6*np.pi*frequency*np.linspace(0,duration, frames)) # organ like
    arr = np.clip(arr*10, -1, 1) # squarish waves
##    arr = np.cumsum(np.clip(arr*10, -1, 1)) # triangularish waves pt1
##    arr = arr+np.sin(2*np.pi*frequency*np.linspace(0,duration, frames)) # triangularish waves pt1
##    arr = arr/max(np.abs(arr)) # adjust to -1, 1 range
    fade = list(np.ones(frames-4410))+list(np.linspace(1, 0, 4410))
    arr = np.multiply(arr, np.asarray(fade))
    return list(arr)

pg.init()
pg.mixer.init()

a_file = open("noteslist.txt")
file_contents = a_file.read(); a_file.close()
noteslist = file_contents.splitlines()
freq = 16.3516 #starting frequency
freqs = {}

for i in range(len(noteslist)):
    freqs[noteslist[i]]= freq
    freq = freq * 2 ** (1/12)

with open("SuperMario.txt", "r") as file:
    notes = [eval(line.rstrip()) for line in file]
file.close()

track = []
for i in range(int(len(notes)/2)):
    track = track + list(np.zeros(max(0, int(44.1*(notes[i*2][2]-100)))))
    track = track + synth(freqs[notes[i*2][1]], 1e-3*(notes[i*2+1][2]+100))
   
arr = 32767*np.asarray(track)*0.5
sound = np.asarray([arr,arr]).T.astype(np.int16)
sound = pg.sndarray.make_sound(sound.copy())

sound.play()
pg.time.wait(int(len(arr)/44.1))

import wave

sfile = wave.open('mario.wav', 'w')
sfile.setframerate(44100)
sfile.setnchannels(2)
sfile.setsampwidth(2)
sfile.writeframesraw(sound)
sfile.close()

pg.mixer.quit()
pg.quit()    
