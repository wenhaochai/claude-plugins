---
description: Write the encode script (grain on the master only, AV1 and H.264 web copies, poster) and the page embed with the AV1 source first, without running ffmpeg.
tags: [video]
max_turns: 10
timeout_seconds: 360
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

讲解视频的帧都渲染好了，在 frames/ 里（f_0001.png 开始，1920x1080，60 fps，一分钟左右）。帮我写个 encode.sh：出一个 master，再出网页用的版本；然后把 site/index.html 里的视频占位换成嵌入代码。ffmpeg 我自己跑，你别跑。
