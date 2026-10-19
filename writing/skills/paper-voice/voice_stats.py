"""Prose statistics of a LaTeX paper against the paper-voice corpus.

Usage: python voice_stats.py <file.tex | dir> [...]
Comments, floats, math, citations and \\input lines are dropped; the rest is split into paragraphs and sentences and
counted per 1000 words (or % of sentences). CORPUS is the same count over the abstract, introduction and first method
section of 15 pre-2023 papers by Kaiming He, Joseph E. Gonzalez and Alex Dimakis (ids in SKILL.md), 32,697 words.
A row is marked * when the paper is above twice the corpus value on a '<' metric or below half of it on a '>' metric.
"""
import re, statistics as st, sys
from pathlib import Path

CORPUS = {"words": 32697, "sentences": 1508, "paragraphs": 411, "sent_mean": 21.7, "sent_sd": 10.1, "sent_lt10_pct": 7.7, "sent_gt30_pct": 16.8, "para_words_mean": 79.8, "para_sents_mean": 3.7, "colon": 3.82, "semicolon": 1.25, "paren": 10.43, "emdash": 0.83, "we_our": 16.36, "this_these_open": 6.7, "so_thus_therefore": 1.9, "comma_so_clause": 0.24, "because": 0.89, "while": 1.71, "instead": 0.34, "rather_than": 0.18, "only": 2.08, "not_x_but_y": 0.12, "list3": 4.1, "hedge": 8.56, "intensifier": 2.57, "question": 0.15, "in_this_paper": 0.61, "to_this_end": 0.0, "note_that": 0.4, "fwd_ref": 1.84, "footnote": 0.61, "we_believe_hope": 0.46, "first_person_open_pct": 13.7, "subord_open_pct": 23.8, "numbers": 9.54, "bullets": 26}
LIMIT = {'comma_so_clause': '<', 'not_x_but_y': '<', 'instead': '<', 'only': '<', 'semicolon': '<', 'para_words_mean': '<',
         'para_sents_mean': '<', 'numbers': '<', 'we_our': '>', 'first_person_open_pct': '>', 'this_these_open': '>',
         'hedge': '>', 'paren': '>', 'subord_open_pct': '>'}

DROP_ENVS = ['figure', 'figure*', 'table', 'table*', 'equation', 'equation*', 'align', 'align*', 'eqnarray', 'eqnarray*',
             'algorithm', 'algorithmic', 'tabular', 'lstlisting', 'verbatim', 'wrapfigure', 'multline', 'gather', 'displaymath',
             'subequations', 'minted', 'thebibliography', 'tikzpicture', 'acks', 'proof']


def strip(s):
    for e in DROP_ENVS:
        s = re.sub(r'\\begin\{' + re.escape(e) + r'\}.*?\\end\{' + re.escape(e) + r'\}', ' ', s, flags=re.S)
    s = re.sub(r'\\\[.*?\\\]', ' ', s, flags=re.S)
    s = re.sub(r'\$\$.*?\$\$', ' ', s, flags=re.S)
    s = re.sub(r'\$[^$]*\$', 'X', s)
    s = re.sub(r'\\footnote\{', ' FOOTNOTE{', s)
    s = re.sub(r'~?\\(cite[pt]?|citep|citet|citealp|citeauthor)\*?(\[[^\]]*\])*\{[^}]*\}', '', s)
    s = re.sub(r'\\(C?ref|autoref|eqref|Cref|cref|S)\{[^}]*\}', '1', s)
    s = re.sub(r'\\(label|vspace|hspace|includegraphics|url|href|bibliography|bibliographystyle|newcommand|renewcommand|def)\*?(\[[^\]]*\])?\{[^}]*\}', ' ', s)
    s = re.sub(r'\\(emph|textit|textbf|textsc|texttt|mbox|textrm|underline|text|mathrm|textsf|bf|it)\{([^{}]*)\}', r'\2', s)
    s = re.sub(r'\\(paragraph|subsection|subsubsection|section)\*?\{([^}]*)\}', r'\n\n', s)
    s = re.sub(r'\\item\b', '\n\n• ', s)
    s = re.sub(r'\\begin\{[^}]*\}|\\end\{[^}]*\}', '\n\n', s)
    s = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?', ' ', s)
    s = s.replace('{', '').replace('}', '').replace('~', ' ').replace('``', '"').replace("''", '"')
    s = s.replace('---', ' — ').replace('--', '–')
    s = re.sub(r'\\[,;:! ]', ' ', s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n\n', s)
    return s.strip()


ABBR = r'(e\.g|i\.e|et al|etc|vs|Fig|Figs|Sec|Eq|cf|resp|approx|Tab|No|al)\.'


def sentences(text):
    paras = [p.strip() for p in text.split('\n\n') if len(p.split()) >= 8 and not p.strip().startswith('•')]
    sents = []
    for p in paras:
        q = re.sub(ABBR, lambda m: m.group(0).replace('.', '<DOT>'), p)
        q = re.sub(r'(\d)\.(\d)', r'\1<DOT>\2', q)
        for x in re.split(r'(?<=[.!?])\s+(?=[A-Z"(•])', q):
            x = x.replace('<DOT>', '.').strip()
            if len(x.split()) >= 3:
                sents.append(x)
    return paras, sents


SUBORD = r'^(Although|Though|While|When|Whenever|If|Because|Since|After|Before|Unlike|As|Once|Given|Despite|Without|With|By|For|In|On|At|To|Under|Instead|Rather|Even)\b'


def stats(text):
    paras, sents = sentences(text)
    body = ' '.join(sents)
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*|\d[\d.,]*", body)
    W = len(words) or 1
    per = lambda n: round(1000 * n / W, 2)
    lens = [len(s.split()) for s in sents]
    low = body.lower()
    cnt = lambda pat, flags=re.I: len(re.findall(pat, body, flags))
    opener = lambda pat: sum(bool(re.match(pat, s, re.I)) for s in sents)
    r = {
        'words': W, 'sentences': len(sents), 'paragraphs': len(paras),
        'sent_mean': round(st.mean(lens), 1), 'sent_sd': round(st.pstdev(lens), 1),
        'sent_lt10_pct': round(100 * sum(l < 10 for l in lens) / len(lens), 1),
        'sent_gt30_pct': round(100 * sum(l > 30 for l in lens) / len(lens), 1),
        'para_words_mean': round(st.mean(len(p.split()) for p in paras), 1),
        'para_sents_mean': round(len(sents) / max(1, len(paras)), 1),
        'colon': per(cnt(r':(?!\d)')), 'semicolon': per(cnt(r';')), 'paren': per(cnt(r'\((?!\d+\))')),
        'emdash': per(cnt(r'—|(?<= )–(?= )')),
        'we_our': per(cnt(r'\b(we|our|us)\b')),
        'this_these_open': round(100 * opener(r'^(This|These|That|Those)\b') / len(sents), 1),
        'so_thus_therefore': per(cnt(r'\b(thus|therefore|hence|consequently)\b') + cnt(r',\s+so\b') + cnt(r'(?<=[.;]\s)So\b', 0)),
        'comma_so_clause': per(cnt(r',\s+so\s')),
        'because': per(cnt(r'\bbecause\b')), 'while': per(cnt(r'\bwhile\b')), 'instead': per(cnt(r'\binstead\b')),
        'rather_than': per(cnt(r'\brather than\b')), 'only': per(cnt(r'\bonly\b')),
        'not_x_but_y': per(cnt(r'\bnot\b[^.;:]{1,60}\bbut\b')),
        'list3': per(cnt(r'\b\w+(?: \w+){0,3}, \w+(?: \w+){0,3},? (?:and|or) \w+')),
        'hedge': per(cnt(r'\b(may|might|can|could|likely|possibly|perhaps|suggests?)\b')),
        'intensifier': per(cnt(r'\b(significantly|much|very|substantially|largely|greatly|dramatically|highly|considerably|far)\b')),
        'question': per(cnt(r'\?')),
        'in_this_paper': per(cnt(r'\bin this (paper|work)\b')), 'to_this_end': per(cnt(r'\bto this end\b')),
        'note_that': per(cnt(r'\bnote that\b')),
        'fwd_ref': per(cnt(r'\b(Section|Sec\.|Figure|Fig\.|Table|Appendix)\s*1\b')),
        'footnote': per(cnt(r'FOOTNOTE')),
        'we_believe_hope': per(cnt(r'\bwe (believe|hope|argue|expect|think|conjecture|speculate)\b')),
        'first_person_open_pct': round(100 * opener(r'^(We|Our)\b') / len(sents), 1),
        'subord_open_pct': round(100 * opener(SUBORD) / len(sents), 1),
        'numbers': per(cnt(r'\b\d[\d.,]*%?')),
        'bullets': text.count('•'),
    }
    return r




def read(paths):
    raw = ''
    for p in paths:
        p = Path(p)
        for f in sorted(p.rglob('*.tex')) if p.is_dir() else [p]:
            s = re.sub(r'(?<!\\)%.*', '', f.read_text(errors='ignore'))
            raw += '\n\n' + re.sub(r'\\(input|include)\{[^}]*\}', ' ', s)
    ab = re.search(r'\\begin\{document\}(.*)', raw, re.S)
    return strip(ab.group(1) if ab else raw)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    r = stats(read(sys.argv[1:]))
    print('metric'.ljust(24) + 'corpus'.rjust(10) + 'paper'.rjust(10))
    for k, v in r.items():
        c, lim = CORPUS.get(k), LIMIT.get(k)
        bad = lim == '<' and v > 2 * c or lim == '>' and v < c / 2
        print(k.ljust(24) + str(c).rjust(10) + str(v).rjust(10) + ('  *' if bad else ''))


if __name__ == '__main__':
    main()
