import pygame as pg
import numpy as np

def synth_sine(frames, freq):
    arr = np.sin(2*np.pi*freq*np.linspace(0,frames/44100,frames))
##    arr = arr**3 # triangularish waves
##    arr = arr*2 # sawtoothish wawes (more like bats)
    arr = np.clip(100*arr, -1, 1) # squarish waves
    fade = list(np.ones(int(frames*3/4))) +list(np.linspace(1, 0, frames-int(frames*3/4))**2)
    arr = 32767*np.multiply(arr, np.asarray(fade))
    sound = np.asarray([arr,arr]).T.astype(np.int16)
    sound = pg.sndarray.make_sound(sound.copy())
    return sound

pg.init()
pg.mixer.init()

font2 = pg.font.SysFont("Impact", 48)
screen = pg.display.set_mode((1280, 720))
surfbg = pg.Surface((1280,720))
pg.display.set_caption("FinFET Synth - replay keyboard" )

##keylist = '123456789qwertyuioasdfghjklzxcvbnm,.'
a_file = open("noteslist.txt")
file_contents = a_file.read(); a_file.close()
noteslist = file_contents.splitlines()
keymod = '0-='
notes = {}
posx, posy = 25, 25 #start position
freq = 16.3516 #starting frequency
reds, greens, blues = [], [], []

for i in range(len(noteslist)):
    mod = int(i/36)
##    key = keylist[i-mod*36]+str(mod)
    key = noteslist[i]
    sample = synth_sine(100000, freq)
    color = np.array([np.sin(i/25+1.7)*130+125,np.sin(i/30-0.21)*215+40, np.sin(i/25+3.7)*130+125])
    color = np.clip(color, 0, 255)
    notes[key] = [freq, sample, (posx, posy), 255*color/max(color), noteslist[i]]
    freq = freq * 2 ** (1/12)
    posx = posx + 140
    if posx > 1220:
        posx, posy = 25, posy+56

    notes[key][1].set_volume(0.33)
##    notes[key][1].play()
##    notes[key][1].fadeout(100)
    surfbg.blit(font2.render(notes[key][4], 0, notes[key][3]), notes[key][2])
    screen.blit(surfbg, (0, 0))
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
        surfbg.blit(font2.render(notes[key][4], 0, (255,255,255)), notes[key][2])
    else:
        notes[key][1].fadeout(100)
        surfbg.blit(font2.render(notes[key][4], 0, notes[key][3]), notes[key][2])

    screen.blit(surfbg, (0, 0))
    pg.display.update()

pg.time.wait(500)
pg.quit()    
