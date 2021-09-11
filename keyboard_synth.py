import pygame as pg
import numpy as np

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((1280, 720))
font = pg.font.SysFont("Impact", 48)

def synth(frequency, duration=1.5, sampling_rate=41000):
    frames = int(duration*sampling_rate)
    arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
    arr = arr + np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
    arr = arr - np.cos(3*np.pi*frequency*np.linspace(0,duration, frames))
##    arr = np.clip(arr*10, -1, 1) # squarish waves
##    arr = np.cumsum(np.clip(arr*10, -1, 1)) # triangularish waves pt1
##    arr = arr+np.sin(2*np.pi*frequency*np.linspace(0,duration, frames)) # triangularish waves pt1
    arr = arr/max(np.abs(arr)) # triangularish waves pt1
    sound = np.asarray([32767*arr,32767*arr]).T.astype(np.int16)
    sound = pg.sndarray.make_sound(sound.copy())
    
    return sound


keylist = '123456789qwertyuioasdfghjklzxcvbnm,.'
notes_file = open("noteslist.txt")
file_contents = notes_file.read()
notes_file.close()
noteslist = file_contents.splitlines()

keymod = '0-='
notes = {} # dict to store samples
freq = 16.3516 # start frequency
posx, posy = 25, 25 #start position


for i in range(len(noteslist)):
    mod = int(i/36)
    key = keylist[i-mod*36]+str(mod) 
    sample = synth(freq)
    color = np.array([np.sin(i/25+1.7)*130+125,np.sin(i/30-0.21)*215+40, np.sin(i/25+3.7)*130+125])
    color = np.clip(color, 0, 255)
    notes[key] = [sample, noteslist[i], freq, (posx, posy), 255*color/max(color)]
    notes[key][0].set_volume(0.33)
    notes[key][0].play()
    notes[key][0].fadeout(100)
    freq = freq * 2 ** (1/12)
    posx = posx + 140
    if posx > 1220:
        posx, posy = 25, posy+56
        
    screen.blit(font.render(notes[key][1], 0, notes[key][4]), notes[key][3])
    pg.display.update()
    

running = 1
mod = 1
pg.display.set_caption("FinFET Synth - Change range: 0 - = // Play with keys: "+keylist )

keypresses = []
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            running = False
        if event.type == pg.KEYDOWN:
            key = str(event.unicode)
            if key in keymod:
                mod = keymod.index(str(event.unicode))
            elif key in keylist:
                key = key+str(mod)
                notes[key][0].play()
                keypresses.append([1, notes[key][1], pg.time.get_ticks()])
                screen.blit(font.render(notes[key][1], 0, (255,255,255)), notes[key][3])
        if event.type == pg.KEYUP and str(event.unicode) != '' and str(event.unicode) in keylist:
            key = str(event.unicode)+str(mod)
            notes[key][0].fadeout(100)
            keypresses.append([0, notes[key][1], pg.time.get_ticks()])
            screen.blit(font.render(notes[key][1], 0, notes[key][4]), notes[key][3])

    pg.display.update()

pg.display.set_caption("Exporting sound sequence")
if len(keypresses) > 1:
    for i in range(len(keypresses)-1):
        keypresses[-i-1][2] = keypresses[-i-1][2] - keypresses[-i-2][2]
    keypresses[0][2] = 0 # first at zero

    with open("test.txt", "w") as file:
        for i in range(len(keypresses)):
            file.write(str(keypresses[i])+'\n') # separate lines for readability
    file.close()
    
pg.mixer.quit()
pg.quit()
