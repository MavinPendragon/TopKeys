# First Keys

A gentle, first-month piano tutor that runs in a phone browser. It listens through the microphone (or you can tap the on-screen keys) and walks a beginner through the black-key map, note names, the C major scale, reading the staff, C position, and two first melodies.

Everything is in `index.html`: no build step and no dependencies.

## Practice room

Daily practice is led by Fräulein Anna Czerny, Carl's (fictional) older sister. It has three parts: a find-the-key warm-up, "Knowledge of the notes" flashcards with spaced repetition, and Carl Czerny's own exercises from the *Practical Method for Beginners*, Op. 599 (Nos. 1–14). Each exercise has a wait-for-you "Learn the notes" mode and a "Play in time" mode with a count-in, a click, and on-the-beat, early or late feedback. The app plays Czerny's left-hand part.

Exercise data comes from Daniel Studzinski's public-domain LilyPond engravings (Mutopia Project, after the 1893 Schirmer edition), converted with `tools/ly2json.py`. Some right-hand parts are moved down one or two octaves so they sit where a beginner reads.

## How it listens

- **Single notes:** YIN pitch detection on a 2048-sample window, with onset detection so repeated notes register. Matching ignores the octave.
- **Chords (expected-note checking):** like the commercial apps, it doesn't try to transcribe freely. It knows which notes the exercise expects and checks an 8192-point spectrum for each one. A note counts if it stands well above the room's noise floor, beats its semitone neighbours, and got louder at the moment of the strike, so notes still ringing from the previous chord don't count. It accepts the chord an octave low but never an octave high, where a lower note's overtones would fool it.
- **The app's own left hand** plays as pure sine tones below the right hand's range, and the listener ignores sounds that start when its own notes do.

## Pieces (follow mode)

Load any score as MusicXML (`.musicxml`, `.xml` or zipped `.mxl`, as exported by MuseScore and most notation programs) and the app follows you through it on a grand staff, waiting at each moment and checking both hands. **Loaded scores never leave the device.** They are parsed in the browser and kept in its local storage, so scores you own stay private and this public repository holds only public-domain music.

Built in: **Erik Satie, Gnossienne No. 1 (1890)**. Note data is derived from Knute Snortum's engraving for the [Mutopia Project](https://www.mutopiaproject.org) (piece 2035, after the 1913 Salabert edition), licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The derived data embedded in `index.html` is shared under the same license.

How follow mode listens:

- **New notes** are found by spectral change (how much new energy appeared since the last moment), which still works with the pedal down when overall loudness barely changes.
- **Every expected note** in both hands is checked with the expected-note checker. Bass notes below C3 (the phone mic's weak range), grace notes and tied continuations are optional.
- **Single notes** are confirmed against the spectrum first, because with notes ringing the pitch detector can lock onto the wrong octave.
- **For 300 ms after each advance** it ignores the ringing of what was just played, so overtones of a chord can't skip it ahead.
- **Practice tools:** one hand at a time (the app plays the other), tap any note to start there, loop a line, and an amber mark on every moment that took more than one try.
