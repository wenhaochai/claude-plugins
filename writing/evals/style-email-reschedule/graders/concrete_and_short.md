---
type: llm
focus: last_message
---
Look only at the email text in the response (ignore any one-line preamble such as a note that a style guide is active).

PASS if all of the following hold:
1. The email states both proposed slots, Friday 2pm and Monday 10am.
2. It states the concrete reason: the cluster was down for two days (Monday and Tuesday).
3. It states that 3 of the 5 ablation results are in and that plots will come Thursday night.
4. The email body is short: roughly 120 words or fewer, not counting the greeting and sign-off.

FAIL if any of the four is missing, or if the email body is clearly longer than about 120 words.
