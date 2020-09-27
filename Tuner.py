#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pyaudio

continuer = True
instrument = input('Quel instrument accorder : guitare ou basse ')

while continuer:
    note = input('Quelle note ? : ') # choix de boutons en fonction de l'accordage à faire 
    if instrument == 'guitare':
        NOTE_MIN = 40       
        NOTE_MAX = 63       
    elif instrument == 'basse':  # Séparation des spectre de notes pour ne pas être parasiter par les harmoniques
        if note == 'B0' or note == 'E1':
            NOTE_MIN = 0       
            NOTE_MAX = 30      
        else :
            NOTE_MIN = 0       
            NOTE_MAX = 43      
    else:
        continuer = False
        break
    FSAMP = 22050       
    FRAME_SIZE = 2048   
    FRAMES_PER_FFT = 16 ?
    

    SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
    FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT


    NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()


    def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
    def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
    def note_name(n): return NOTE_NAMES[n % 12] + str(n/12 - 1)


    # Get min/max index within FFT of notes we care about.
    # See docs for numpy.rfftfreq()
    def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
    imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
    imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))

    # Allocate space to run an FFT. 
    buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
    num_frames = 0

    # Initialize audio
    stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=FSAMP,
                                    input=True,
                                    frames_per_buffer=FRAME_SIZE)

    stream.start_stream()
    window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))

    accorder = True 
    a = 0
    # As long as we are getting data:
    while stream.is_active() and accorder:

        # Shift the buffer down and new data in
        buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
        buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)

        # Run the FFT on the windowed buffer
        fft = np.fft.rfft(buf * window)

        # Get frequency of maximum response in range
        freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

        # Get note number and nearest note
        n = freq_to_number(freq)
        n0 = int(round(n))

        # Console output once we have a full buffer
        num_frames += 1
        if num_frames >= FRAMES_PER_FFT:
            print('freq: {:7.2f} Hz     note: {:>3s} {:+.2f}'.format(
                freq, note_name(n0), n-n0))  
            if note_name(n0)[0:2] == note and -0.10 < n-n0 < +0.10 :
                a = a+1
            else:
                a = 0
            if a == 50:
                    accorder = False
    quitter = input("Souhaitez-vous contineur d'accorder (o/n) ? ")
    if quitter == "n" or quitter == "N":
        continuer = False
