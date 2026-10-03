#!/usr/bin/env bash
# A two-slide deck in the Slides file layout; results.html breaks the author's slide and script rules.
set -euo pipefail
mkdir -p deck/project/slides

cat > deck/project/deck.json <<'EOF'
{
  "v": 4,
  "createdOnFiles": {"v": 1, "at": "2026-09-28T10:00:00Z"},
  "title": "Sparse Routing for Long Context",
  "order": ["cover", "results"],
  "sections": {"s0": {"description": "Title", "start": "cover"}, "s1": {"description": "The paper", "start": "results"}},
  "faces": {
    "newsreader": {"family": "Newsreader", "href": "https://fonts.googleapis.com/css2?family=Newsreader:wght@400;500&display=swap"},
    "inter-tight": {"family": "Inter Tight", "href": "https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;600&display=swap"}
  },
  "designSystems": []
}
EOF

cat > deck/project/slides/cover.html <<'EOF'
<section id="cover" data-transition="fade" style="background:#15141A; color:#EDE9DE; font-family:'Inter Tight', Arial, sans-serif; padding:128px; display:flex; flex-direction:column; justify-content:space-between">
  <p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:#D0705F">Reading group</p>
  <div style="display:flex; flex-direction:column; gap:32px">
    <h1 style="font-family:'Newsreader', Georgia, serif; font-size:120px; font-weight:500; line-height:1.05; color:#EDE9DE">Sparse Routing for Long Context</h1>
    <p style="font-size:36px; line-height:1.3; color:#BDB8AC; width:1300px">Paper by the Halcyon team, September 2026</p>
  </div>
  <div style="display:flex; justify-content:space-between; border-top:1px solid #3A3842; padding:32px 0 0 0">
    <p style="font-size:28px; color:#EDE9DE">Presented by Lin</p>
    <p style="font-size:28px; color:#BDB8AC">October 2026</p>
  </div>
  <aside>This talk covers one paper on sparse routing.<br>
这次讲一篇关于稀疏路由的论文。</aside>
</section>
EOF

cat > deck/project/slides/results.html <<'EOF'
<section id="results" data-transition="fade" style="background:#F6F3EC; color:#15141A; font-family:'Inter Tight', Arial, sans-serif; padding:128px; display:flex; flex-direction:column; gap:40px">
  <div style="display:flex; flex-direction:column; gap:12px">
    <p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:#7A1A1A">The paper</p>
    <h2 style="font-family:'Newsreader', Georgia, serif; font-size:64px; font-weight:700; line-height:1.1; color:#15141A">Sparse routing wins, beats dense, cheaper to train</h2>
  </div>
  <div style="display:flex; gap:56px">
    <div style="width:820px; display:flex; flex-direction:column; gap:16px">
      <p style="font-size:20px; font-style:italic; color:#4A4852">Accuracy on the five held-out suites — higher is better</p>
      <div style="display:flex; gap:16px; align-items:center"><p style="width:220px; font-size:28px">Retrieval</p><div style="width:420px; height:28px; background:#7A1A1A"></div><p style="font-size:28px">78.1 vs 74.0</p></div>
      <div style="display:flex; gap:16px; align-items:center"><p style="width:220px; font-size:28px">Summaries</p><div style="width:390px; height:28px; background:#7A1A1A"></div><p style="font-size:28px">72.5 vs 69.9</p></div>
      <div style="display:flex; gap:16px; align-items:center"><p style="width:220px; font-size:28px">Code</p><div style="width:380px; height:28px; background:#7A1A1A"></div><p style="font-size:28px">70.2 vs 66.8</p></div>
      <div style="display:flex; gap:16px; align-items:center"><p style="width:220px; font-size:28px">Math</p><div style="width:390px; height:28px; background:#7A1A1A"></div><p style="font-size:28px">73.2 vs 67.5</p></div>
      <div style="display:flex; gap:16px; align-items:center"><p style="width:220px; font-size:28px">Long context</p><div style="width:340px; height:28px; background:#7A1A1A"></div><p style="font-size:28px">63.0 vs 54.8</p></div>
    </div>
    <div style="flex:1; display:flex; flex-direction:column; gap:24px">
      <p style="font-size:32px; line-height:1.3">It is a routing problem, not a capacity problem. The sparse model reaches 71.4 on average while the dense baseline reaches 66.2, and the gap holds on every suite, with the largest gain on the long-context suite where sparse reaches 63.0 against 54.8.</p>
    </div>
  </div>
  <aside>
This slide shows the main results table from the paper where the sparse routing model gets 71.4 average accuracy compared to the dense baseline which gets 66.2 and this is consistent across all five suites.
The biggest gain is on long context, 63.0 versus 54.8, which is what the authors care about most.
  </aside>
</section>
EOF
