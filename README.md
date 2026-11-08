# First Keys

A gentle, first-month piano tutor that runs in a phone browser. It listens through the microphone (or you can tap the on-screen keys) and walks a beginner through the black-key map, note names, the C major scale, reading the staff, C position, and two first melodies.

Everything is in `index.html`: no build step and no dependencies.

## Practice room

Daily practice is led by Fräulein Anna Czerny, Carl's (fictional) older sister. It has three parts: a find-the-key warm-up, "Knowledge of the notes" flashcards with spaced repetition, and Carl Czerny's own exercises from the *Practical Method for Beginners*, Op. 599 (Nos. 1–7, 9, 11–13). Each exercise has a wait-for-you "Learn the notes" mode and a "Play in time" mode with a count-in, a click, and on-the-beat, early or late feedback. The app plays Czerny's left-hand part.

Exercise data comes from Daniel Studzinski's public-domain LilyPond engravings (Mutopia Project, after the 1893 Schirmer edition), converted with `tools/ly2json.py`. Some right-hand parts are moved down one or two octaves so they sit where a beginner reads. Nos. 8, 10 and 14 need two right-hand notes at once and are left out until the listener can hear chords.
