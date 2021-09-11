import pygame as pg
import numpy as np

def synth(frequency, duration=1.5, sampling_rate=41000):
    frames = int(duration*sampling_rate)
    arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
    arr = arr + np.cos(4*np.pi*frequency*np.linspace(0,duration, frames)) # organ like
    arr = arr + np.cos(6*np.pi*frequency*np.linspace(0,duration, frames)) # organ like
##    arr = np.clip(arr*10, -1, 1) # squarish waves
##    arr = np.cumsum(np.clip(arr*10, -1, 1)) # triangularish waves pt1
##    arr = arr+np.sin(2*np.pi*frequency*np.linspace(0,duration, frames)) # triangularish waves pt1
    arr = arr/max(np.abs(arr)) # triangularish waves pt1
    sound = np.asarray([32767*arr,32767*arr]).T.astype(np.int16)
    sound = pg.sndarray.make_sound(sound.copy())
    
    return sound

pg.init()
pg.mixer.init()
font2 = pg.font.SysFont("Impact", 48)
screen = pg.display.set_mode((1280, 720))
pg.display.set_caption("FinFET Synth - replay txt" )

a_file = open("noteslist.txt")
file_contents = a_file.read(); a_file.close()
noteslist = file_contents.splitlines()
keymod = '0-='
notes = {}
posx, posy = 25, 25 #start position
freq = 16.3516 #starting frequency

for i in range(len(noteslist)):
    mod = int(i/36)
    key = noteslist[i]
    sample = synth(freq)
    color = np.array([np.sin(i/25+1.7)*130+125,np.sin(i/30-0.21)*215+40, np.sin(i/25+3.7)*130+125])
    color = np.clip(color, 0, 255)
    notes[key] = [freq, sample, (posx, posy), 255*color/max(color), noteslist[i]]
    notes[key][1].set_volume(0.33)
    freq = freq * 2 ** (1/12)
    posx = posx + 140
    if posx > 1220:
        posx, posy = 25, posy+56
        
    screen.blit(font2.render(notes[key][4], 0, notes[key][3]), notes[key][2])
    pg.display.update()

with open("SuperMario.txt", "r") as file:
    keypresses = [eval(line.rstrip()) for line in file]
file.close()

running = 1
for i in range(len(keypresses)):
    if not running:
        break
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            running = False
    
    key = keypresses[i][1]
    pg.time.wait(keypresses[i][2])
    if keypresses[i][0]:
        notes[key][1].play()
        screen.blit(font2.render(notes[key][4], 0, (255,255,255)), notes[key][2])
    else:
        notes[key][1].fadeout(100)
        screen.blit(font2.render(notes[key][4], 0, notes[key][3]), notes[key][2])

    pg.display.update()

pg.time.wait(500)
pg.quit() 
