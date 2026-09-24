---
name: video
description: "Make a short explainer video of a blog post, paper or project page: one continuous motion piece drawn frame by frame from the page's own animations and data, then encoded with ffmpeg. Use when the user asks for a video, a teaser, a one-minute clip or 做个视频."
---

# Video

A video of a piece of work runs about a minute and plays as one piece of motion design.

## Design

- One continuous piece. Objects carry from scene to scene: a node becomes an agent, agents regroup, a chart grows out of what was on screen. No cuts between static cards and no heading-plus-figure layouts.
- Open on the work itself: the source's mechanism runs from the first frame, and the title comes into focus alone in the clear space above it. Then the title leaves and that picture carries into the first chapter. The opening has no kicker, author or date line, or tagline.
- The camera stays still: motion comes from the objects themselves, and nothing zooms or pans the whole frame.
- The picture carries the story. No text column stays on screen: each statement is one short line placed next to the action it describes, on screen only for that moment, with its key words in the accent. Numbers and names sit on the visuals as direct labels, and the takeaway is the one full sentence, at the end.
- Copy comes from the source. Titles, names and the takeaway are quoted verbatim, the video adds no summary lines of its own, and it never uses the middle dot (U+00B7).
- Give it rhythm: when a beat repeats, play it slowly the first time and quickly after.
- Explain a mechanism at least as clearly as its source by porting the source figure's beats, formulas and labels. Where the source shows single runs and their average, so does the video.
- Introduce every named setup on screen before the scene that uses it, and show every option from one extreme to the other.
- Show every comparison the source supports, each as a race on one clock, and make each result explicit: the winner gets an accent frame and its number, the loser dims, and a ranking closes the set.
- Choose an example where the obvious option loses at least one race. Keep it typical: each option's run is the session closest to its mean over many sessions, and the video states only results that hold on most sessions.
- Full frame at 1920×1080 and 60 fps, in the source's palette and fonts, with light grain added at encoding. Nothing overlaps: no text on graphics, and a caption or label leaves before the next one enters.
- Wording and figures follow the `writing` plugin: `style` for the prose and `figures/DOCTRINE.md` for marks and legends.

## Workflow

1. Agree on the chapters and their captions with the user, one idea per chapter.
2. Write a director script that runs in the page's local preview and draws the frame at time t on a 1920×1080 canvas from the page's own code and data. It is deterministic, so it reads no wall clock. Serve it and collect the frames with `python3 scripts/frame_sink.py FRAMES_DIR DIRECTOR_DIR`: the page fetches `/files/director.js` and posts each frame as a PNG data URL.
3. Before the full render, draw test frames at every scene boundary and busy moment, tile them into a contact sheet, and look for overlaps, clipped text and dead time. A hidden browser tab may freeze mid-render; reload the page and resume from the last saved frame.
4. Encode the master with `ffmpeg -framerate 60 -i FRAMES_DIR/f_%04d.png -vf noise=alls=3:allf=t -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart master.mp4`. The web copies drop the grain: AV1 with `-c:v libsvtav1 -preset 4 -crf 30` and H.264 with `-c:v libx264 -preset veryslow -tune animation -crf 20`, each with `-pix_fmt yuv420p -movflags +faststart`. A minute at 1080p60 comes to about 5 MB in each, and the AV1 copy keeps moving lines clean. Take the poster JPEG from the opening. Embed two `<source>` elements with the AV1 file first, `type='video/mp4; codecs="av01.0.09M.08"'`, so browsers without AV1 play the H.264 file.
5. Keep the director next to the video, so a change is a re-render.
