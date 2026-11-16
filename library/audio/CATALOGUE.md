# Music the films may use: CC0, vetted 2026-11-14

Every track below is dedicated to the public domain (CC0 1.0): commercial use in a rendered film on Instagram,
Facebook and Pinterest, no credit to write (son.md, « What may go in the file »). Each licence was read on the
track's own page the day it was taken: the page links https://creativecommons.org/publicdomain/zero/1.0/ as the
sound's licence. Found through the Openverse API (no account: `https://api.openverse.org/v1/audio/?q=…&license=cc0,pdm`),
chosen among 431 CC0 candidates of 30 s or more by the page's own rating and download count (a proxy for quality:
nobody listened), then measured here. The files are Freesound's high-quality previews (MP3 about 180 kbit/s),
the only version reachable without an account; kept as fetched, never re-encoded.

Measured with FFmpeg (EBU R128) and our own onset autocorrelation. `beat` is the strength of the measured tempo
(0-1): under 0.3 the track has no steady beat and the tempo is not to be cut on. The estimator can land on half or
double the real tempo, and 172.3 is the top of its search range: before cutting on beats, count them on the track. Moods come from the author's title
and tags: they were not heard. Rejected for clipping (hundreds to 35 000 clipped samples): Hip Hop beat Chill
(klaudux), Chill Lofi Melody Loop 95 BPM (holizna), Folk Guitar Music Track (Dvideoguy), Cute Happy Background
Music (Seth_Makes_Sounds), Slow Cinematic Music (DeVern); for being a field recording: Spring morning atmosphere
(Cinetony).

| File | Title | Author | Licence (read on the page) | Page | Taken | Length | Tempo (beat) | Loudness | True peak | Mood | Level spread | Offsets passing (Nuvia take) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `soir-late-jazz-piano.mp3` | Late Jazz Piano.wav | szegvari | CC0 1.0 | https://freesound.org/people/szegvari/sounds/570347 | 2026-11-14 | 48.0 s | no steady beat (0.13) | -17.6 LUFS | -0.3 dBTP | warm evening: slow jazz piano | 4.4 dB | 43/54 (80 %) |
| `soir-piano-remix.mp3` | Piano Remix.mp3 | cheesepuff | CC0 1.0 | https://freesound.org/people/cheesepuff/sounds/112071 | 2026-11-14 | 110.8 s | 172.3 BPM (0.38) | -23.0 LUFS | -11.2 dBTP | warm evening, calm: solo piano | 4.1 dB | 148/164 (90 %) |
| `matin-guitar-and-keys.mp3` | Acoustic Guitar and Keys - Plains Soundtrack | tyballer92 | CC0 1.0 | https://freesound.org/people/tyballer92/sounds/449812 | 2026-11-14 | 60.3 s | 129.2 BPM (0.35) | -24.6 LUFS | -9.5 dBTP | calm morning: acoustic guitar and keys | **7.8 dB: uneven, last** | 9/58 (16 %) |
| `matin-relaxing-guitar.mp3` | simple relaxing guitar loop | Kodack | CC0 1.0 | https://freesound.org/people/Kodack/sounds/395037 | 2026-11-14 | 48.5 s | 66.3 BPM (0.4) | -20.3 LUFS | -3.0 dBTP | calm morning, minimal: one acoustic guitar loop | **8.6 dB: uneven, last** | 5/57 (9 %) |
| `entrain-happy-guitar.mp3` | Happy Guitar | edtijo | CC0 1.0 | https://freesound.org/people/edtijo/sounds/207558 | 2026-11-14 | 91.9 s | 63.0 BPM (0.49) | -21.8 LUFS | -9.3 dBTP | upbeat, light: acoustic guitar | 2.4 dB | 133/135 (99 %) |
| `entrain-little-happy-tune.mp3` | Little, happy tune - 22.10.2015 | cabled_mess | CC0 1.0 | https://freesound.org/people/cabled_mess/sounds/335361 | 2026-11-14 | 40.1 s | 60.1 BPM (0.84) | -18.3 LUFS | -1.7 dBTP | upbeat, playful: short tune | **18.6 dB: uneven, last** | 6/39 (15 %) |
| `entrain-full-of-energy.mp3` | Full of Energy | code_box | CC0 1.0 | https://freesound.org/people/code_box/sounds/520192 | 2026-11-14 | 34.8 s | 136.0 BPM (0.56) | -18.5 LUFS | -1.2 dBTP | upbeat, energetic: band | 4.3 dB | 27/27 (100 %) |
| `minimal-piano-abstract.mp3` | PianoAbstract_ubik.wav | yewbic | CC0 1.0 | https://freesound.org/people/yewbic/sounds/27871 | 2026-11-14 | 35.2 s | no steady beat (0.17) | -21.3 LUFS | -4.7 dBTP | minimal: sparse piano | 5.8 dB | 11/20 (55 %) |
| `minimal-dreamy-piano.mp3` | Dreamy Piano Atmosphere | lunaowwwww | CC0 1.0 | https://freesound.org/people/lunaowwwww/sounds/394675 | 2026-11-14 | 45.2 s | 172.3 BPM (0.74) | -25.5 LUFS | -14.0 dBTP | minimal, cinematic: dreamy piano atmosphere | 2.3 dB | 29/34 (85 %) |
| `cinema-beautiful-strings.mp3` | Beautiful String Music.mp3 | Cunningar0807 | CC0 1.0 | https://freesound.org/people/Cunningar0807/sounds/353964 | 2026-11-14 | 103.0 s | 161.5 BPM (0.69) | -17.6 LUFS | -0.3 dBTP | cinematic: strings | 5.0 dB | 137/162 (85 %) |

`Level spread`: standard deviation of the track's level in 0.1 s windows over the part that holds (`ecart_niveau` in
the skill's `scripts/lit_musique.py`, which prints it for any track). The render measures breaths as short as 0.09 s:
a staccato tune or a track that swells and dips leaves holes no gain can fill. `Offsets passing`: start offsets
(every 0.5 s) for which `lit_musique.py` predicts that every sound gate passes on the fifth test's take (essai-nuvia-5,
2026-11-14; its predictions matched four renders within 0.1 dB). Tracks at 6 dB or more are marked uneven: take
them last.

Use: `"musique.mp3": "library/audio/<file>"` in the manifest's `assets`; then `scripts/lit_musique.py` writes
its level from the track's own loudness. `soft-pad.m4a` (an original pad made by code) stays for a bed with no melody.
