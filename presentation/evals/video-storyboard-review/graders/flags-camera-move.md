---
type: regex
pattern: '(?:zoom|\bpan|camera|镜头|推拉|摇镜|运镜)[^\n]{0,160}(?:still|static|fixed|remove|drop|no |不动|固定|去掉|删|不要|避免)|(?:still|static|fixed|remove|drop|no |不动|固定|去掉|删|不要|避免)[^\n]{0,160}(?:zoom|\bpan|camera|镜头|推拉|摇镜|运镜)'
flags: i
match: contains
target: last_message
---

The review asks for a still camera: no zoom into the map and no pan following the leader.
