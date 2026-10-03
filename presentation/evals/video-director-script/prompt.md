---
description: Write the frame-drawing director script for a one-minute explainer from a project page's own animation and data, following the author's video design rules (deterministic draw(t), 1920x1080, cover opening, still camera, corner mark, verbatim copy).
tags: [video]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

给 site/ 这个项目页做个一分钟左右的讲解视频，章节就按页面那三段来。先只把画帧的脚本写出来，放到 video/director.js，渲染我自己来（这台机器没有 ffmpeg，也没有浏览器，不用跑）。
