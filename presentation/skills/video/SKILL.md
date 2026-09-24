---
name: video
description: "Make a short explainer video of a blog post, paper or project page: one continuous motion piece drawn frame by frame from the page's own animations and data, then encoded with ffmpeg. Use when the user asks for a video, a teaser, a 30-second clip or 做个视频."
---

# Video

A video of a piece of work runs about 30 to 40 seconds and plays as one piece of motion design.

## Design

- One continuous piece. Objects carry from scene to scene: a node becomes an agent, agents regroup, a chart grows out of what was on screen. No cuts between static cards and no heading-plus-figure layouts.
- The picture carries the story. No text column stays on screen: each scene gets one short caption, one line, that rises in and leaves. Numbers and names sit on the visuals as direct labels, and the takeaway is the one full sentence, at the end.
- Explain a mechanism at least as clearly as its source by porting the source figure's beats, formulas and labels. Where the source shows single runs and their average, so does the video.
- Introduce every named setup on screen before the scene that uses it, show every option from one extreme to the other, and compare two systems as a race on one clock.
- Full frame at 1920×1080 and 60 fps, in the source's palette and fonts, with light grain added at encoding. Nothing overlaps: no text on graphics, and a caption or label leaves before the next one enters.
- Wording and figures follow the `writing` plugin: `style` for the prose and `figures/DOCTRINE.md` for marks and legends.

## Workflow

1. Agree on the chapters and their captions with the user, one idea per chapter.
2. Write a director script that runs in the page's local preview and draws the frame at time t on a 1920×1080 canvas from the page's own code and data. It is deterministic, so it reads no wall clock. Serve it and collect the frames with `python3 scripts/frame_sink.py FRAMES_DIR DIRECTOR_DIR`: the page fetches `/files/director.js` and posts each frame as a PNG data URL.
3. Before the full render, draw test frames at every scene boundary and busy moment, tile them into a contact sheet, and look for overlaps, clipped text and dead time. A hidden browser tab may freeze mid-render; reload the page and resume from the last saved frame.
4. Encode the master with `ffmpeg -framerate 60 -i FRAMES_DIR/f_%04d.png -vf noise=alls=3:allf=t -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart master.mp4`, and a web copy without grain at crf 24 with a poster frame.
5. Keep the director next to the video, so a change is a re-render.
