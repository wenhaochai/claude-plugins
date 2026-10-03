---
type: llm
focus: {source: file, path: encode.sh}
---

PASS if encode.sh does all of the following:
1. Reads the frames as an image sequence at 60 fps (for example -framerate 60 -i frames/f_%04d.png).
2. Encodes a high-quality H.264 master with light film grain from the noise filter (for example noise=alls=3:allf=t, -preset slow -crf 16).
3. Encodes two web copies without grain: AV1 with libsvtav1 (about crf 30) and H.264 (for example -preset veryslow -tune animation -crf 20).
4. Uses -pix_fmt yuv420p and -movflags +faststart on the outputs.
5. Extracts a poster JPEG from the opening frames.

FAIL if any of these is missing, if grain is added to a web copy, or if the web copies are WebM/VP9 instead of the AV1 and H.264 MP4 pair.
