# SolitaireCG 3.4.1 (branch `xt550-libre`)

SolitaireCG by Curtis Gedak (Apache 2.0), from the official SourceForge repository
(`https://git.code.sf.net/p/solitairecg/code`, tag `SolitaireCG-3.4.1`, commit `fea07fa`).

## Change: portrait also on Android below 4.0

Upstream always forces landscape below Android 4.0 (API 14), because older
versions once did not resize the view on rotation. On a Motorola XT550
(Android 2.3.6, 320x480) portrait works, so this branch removes the
`SDK < 14` check in `SolitaireCG`, `Help` and `Preferences`.

- Landscape is now forced only when **Options → Lock Landscape** is on, as on
  Android 4.0 and later. That option now shows on 2.3 too.
- No other code changes.

## Build

`build.py` builds offline (aapt, javac, d8, apksigner) against the Android
2.3.3 `android.jar`, using `--min/target-sdk 4` and version 3041 / 3.4.1 from
`app/build.gradle`. The repo's only binary is the Gradle wrapper jar, which
this build does not use.

## Tested on the XT550

- The saved game survived reinstalling.
- In portrait all 7 columns fit, and dragging cards works.
- Turning Lock Landscape on rotates to landscape and turning it off goes back to
  portrait. The game keeps its state and nothing crashes.
