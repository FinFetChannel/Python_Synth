# Python_Synth
A simple synthesizer made with Pygame and Numpy in Python.

![Screenshot](python%20synth.png)

## A simple keyboard synthesizer
### What is a soundwave
Soundwaves are pressure fluctuations which travel trough the air (or other physical medium) and hit your eardrums. We can generate these waves with a speaker, which usually consists of a diaphragm with an electrical coil attached and a permanent magnet. When an electrical signal passes through the coil, it vibrates the diaphragm, which in turn moves the air around it creating soundwaves.

The electrical signal consists of an alternating current, usually created by a DAC - Digital Analog Converter and amplified bya a amplifier. Before that, the signal is digital, consisting of ones and zeros in your computer.

And what does this digital signal look like? Basically, it is a long list of numbers.

### Generating a digital signal
The first thing we should consider when generating a digital signal is the sampling rate, that is, how many values we need to define for a second of sound. The default value for the Pygame mixer is 41000 samples per second, so that's what I'll be using.

The second thing is the form of the wave, responsible for the quality of the sound, or timbre, the reason why different instruments sound so dissimilar for the same frequency or pitch. The most pure waveform is the sine, also one of the easiest to generate in numpy, but the are innumerous other types, like square, triangular and sawtooth.

We will start with the sine wave, which will actually be generated by the cosine function (makes things easier for triangular waves later). Cosine is equal to the sine but with a fase shift, which is not relevant in this context, it sounds exactly the same.

To generate the array of values of a sine wave we need the sampling rate, 41000, the frequency, which can be any value lower than 20.5 kHz by the [Nyquist frequency](https://en.wikipedia.org/wiki/Nyquist_frequency) (most people can't hear anything above 16 or 17 kHz anyway) and the duration for the sound sample.

With the duration and the sampling rate we can calculate the number of frames that the sample will have. With the number of frames and the duration we can generate an array with the timings of each frame, which in tur is fed into the cosine function multiplied by 2π and the frequency, this results in an array with all values of the sound signal. 

To hear it, first we have to turn it into a pygame sound array, which first has to be multiplied by the value of 32767, duplicated (for stereo mixer), transposed and turned into the int16 type. Then we can use the function `make_sound` from pygame sndarray, the `.copy()` is necessary to make the array contiguous in memory. After that we can finally play the sound, careful with the volume, it will be at the maximum! After that we simply wait for the duration of the sample an exit pygame.

<details>
  <summary>Generating the first sound sample</summary>
  
```python
import pygame as pg
import numpy as np

pg.init()
pg.mixer.init()

sampling_rate = 41000 # default value for the pygame mixer
frequency = 440 # [Hz]
duration = 1.5 # [s]
frames = int(duration*sampling_rate)
arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
sound = np.asarray([32767*arr,32767*arr]).T.astype(np.int16)
sound = pg.sndarray.make_sound(sound.copy())
sound.play()
```
</details>

Great! Now we can do the same for all the notes in a piano keyboard.

### Generating samples for every key in a piano

But wait, wat are notes anyway? Simply put, notes are selected frequencies which often sound nice when played together. This may sound a bit weird, but the exact frequencies aren't that important, what matters most are the ratios between them. The most used ratio in western music is the [Twelfth root of two](https://en.wikipedia.org/wiki/Twelfth_root_of_two).

So, to generate samples for all the keys in a piano we just need a [list of all the notes](https://en.wikipedia.org/wiki/Piano_key_frequencies), conveniently I have listed them all in a text file: [noteslist.txt](https://github.com/FinFetChannel/Python_Synth/blob/main/noteslist.txt). Then we just need the frequency of the first note (16.35160 Hz) and the remaining frequencies can be calculated from it.

So, we can easily store a sample for each note in a dictionary. For the keys, we are going to use the characters in a regular keyboard, after all, that's what we have to play here. The 108 keys can be subdivided into three groups of 36, since your keyboard probably does not have enough keys for all of them at once.

<details>
  <summary>Generating a sample for each piano key</summary>
  
```python  
import pygame as pg
import numpy as np

pg.init()
pg.mixer.init()

def synth(frequency, duration=1.5, sampling_rate=41000):
    frames = int(duration*sampling_rate)
    arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
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

for i in range(len(noteslist)):
    mod = int(i/36)
    key = keylist[i-mod*36]+str(mod) 
    sample = synth(freq)
    notes[key] = [sample, noteslist[i], freq]
    notes[key][0].set_volume(0.33)
    notes[key][0].play()
    notes[key][0].fadeout(100)
    pg.time.wait(100)
    freq = freq * 2 ** (1/12)
    
pg.mixer.quit()
pg.quit()
  
```
</details>

### Playing with the keyboard

Now that we have all the samples we can start playing and try to make some music. For that we need to create a pygame window, so we can capture the keystrokes and play the corresponding samples. A note starts playing when a keydown event is registered and stops after the duration of the sample or when a keyup event is registered. The range of notes can be changed with the keys 0 - =

<details>
  <summary>Keyboard inputs</summary>
  
```python  
  
...
  
screen = pg.display.set_mode((1280, 720))
running = 1

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
        if event.type == pg.KEYUP and str(event.unicode) != '' and str(event.unicode) in keylist:
            key = str(event.unicode)+str(mod)
            notes[key][0].fadeout(100)

pg.mixer.quit()    
pg.quit()
  
```
</details>

Ok, this works, but this black screen is boring, why not put it to good use?

### Displaying notes 

To display the notes on screen first i'm going to define a position and a color for each one. For the positions I've simply arranged all the notes in a grid of 12 by 9, neatly spaced on the screen. For the colors I tried to mimic a rainbow, where lower sound frequencies are reddish, the middle ones are greenish and the higher ones are blueish. The positions and colors are also stored in the notes dictionary. The notes are then blit into the screen. When playing, the current note gets highlighted with a white color, after the keyup event it returns to its original color. After some adjustments we have a very basic and somewhat pretty sound synthesizer.

<details>
  <summary>Notes display</summary>
  
```python  
  
...
  
import pygame as pg
import numpy as np

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((1280, 720))
font = pg.font.SysFont("Impact", 48)

def synth(frequency, duration=1.5, sampling_rate=41000):
    frames = int(duration*sampling_rate)
    arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
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
                screen.blit(font.render(notes[key][1], 0, (255,255,255)), notes[key][3])
        if event.type == pg.KEYUP and str(event.unicode) != '' and str(event.unicode) in keylist:
            key = str(event.unicode)+str(mod)
            notes[key][0].fadeout(100)
            screen.blit(font.render(notes[key][1], 0, notes[key][4]), notes[key][3])

    pg.display.update()

pg.mixer.quit()
pg.quit()

  
```
</details>

Cool, now with this simple keyboard synthesizer we can start making some music (or at least try), but the sine wave sound is a bit dull. We can explore other waveforms for different timbres.

### Making "square" and "triangular" waves

There are [proper ways](https://docs.scipy.org/doc/scipy/reference/signal.html#waveforms) to generate square and triangular waves but, for this project, I came up with some simple hacks to obtain (approximate) these types of waveforms.

Te square wave can be aproximated easily by multiplying the sine wave by a "big" factor, 10 already looks squarish to me, and clipping the result to the -1 to 1 range. I know, it's more like a trapezoidal wave, but it is close.
Triangular waves can be built on top of the square waves with integration, this os done with the `np.cumsum` function in Numpy, after that we only need to scale it back to the -1 to 1 range. This method works more less fine for short samples but cumulative errors may creep in for longer ones.

<details>
  <summary>Squarish and triangularish waves </summary>
  
```python 
...  
def synth(frequency, duration=1.5, sampling_rate=41000):
    frames = int(duration*sampling_rate)
    arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
##    arr = np.clip(arr*10, -1, 1) # squarish waves
    arr = np.cumsum(np.clip(arr*10, -1, 1)) # triangularish waves pt1
    arr = arr/max(np.abs(arr)) # triangularish waves pt2
    sound = np.asarray([32767*arr,32767*arr]).T.astype(np.int16)
    sound = pg.sndarray.make_sound(sound.copy())
    
    return sound
...
```
</details>

We could go wild and try to come up with more interesting wave forms, for example, adding up multiples of the base frequency, we can have interesting results and theoretically mimic the timbre of any instrument.

## Replay a sound sequency

Now we are able to play any music, not me, I don't have this talent, but maybe after some practice, who knows. But what if we managed to play an epyc sequence, how can we save it for eternity?

Well, we can always use a recording app like audacity, using the PC speaker as its input source, but this only preserves the resulting sound, not exactly the notes which were played.

### Exporting to a text file

There is a better way: store all the relevant keydown and keyup events in a list and later save them to text file. But music is not just a sequence of notes, timing is arguably as important as the notes being played, this is why we also store timestamps for each event. Before saving them to a text file, it's interesting to turn the timestamps into time intervals, which are easier to handle in playback. Te type of the event is also stored as a binary value.

<details>
  <summary>Export text file </summary>
  
```python 
...
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

pg.display.set_caption("Exporting sound sequence to txt")
if len(keypresses) > 1:
    for i in range(len(keypresses)-1):
        keypresses[-i-1][2] = keypresses[-i-1][2] - keypresses[-i-2][2]
    keypresses[0][2] = 0 # first at zero

    with open("soundsequence.txt", "w") as file:
        for i in range(len(keypresses)):
            file.write(str(keypresses[i])+'\n') # separate lines for readability
    file.close()
    
pg.mixer.quit()
pg.quit()
```
</details>

The final result is a text file with all notes that were played, when they start and when they end, this can also be modified in a text editor for adjustments and corrections.

### Replay txt sound sequence

To replay the sound sequency I think it's better to start a new script, but we can borrow most of it from the previous one. The main difference here is that there are no keypresses, instead the program waits until the time for the new note to be played.

<details>
  <summary>Export text file </summary>
  
```python
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
```
</details>
