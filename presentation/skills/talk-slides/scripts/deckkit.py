"""Design tokens and layout builders for talk decks in the claude.ai Slides artifact format.

The look is Google's: a white 1920x1080 canvas with generous margins, Google Sans for display type and
Google Sans Text for the rest, no boxed cards (whitespace and hairlines separate the parts), and the four
Google colors used to mark the parts of the talk and the one number that matters on a slide, never as
decoration. Every builder returns an HTML string in the Slides subset: inline styles, px units, text at
24px or larger, and pinned children only inside a sized `position:relative` host. Under a one-line
title the body has about 680px of height above a source line and 1664px of width. Charts are drawn
per deck from the source data, in these tokens.
"""
import html as _html
import re

# ---------------------------------------------------------------- tokens
# neutrals, the Google grey ramp
INK, SOFT, MUTED, FAINT = '#1F1F1F', '#3C4043', '#5F6368', '#9AA0A6'
RULE, HAIR, WHITE = '#DADCE0', '#E8EAED', '#FFFFFF'
PAPER, CARD, CHIP = WHITE, '#F3F6FC', '#F3F6FC'          # slide ground, filled card, neutral chip
# text-safe tones on white; ACC is the one accent, for the number that matters
ACC, DEEP, RED, GREEN, AMBER = '#0B57D0', '#041E49', '#8C1D18', '#137333', '#E37400'
# Material 3 tonal containers
T_BLUE, T_RED, T_GREEN, T_YELLOW = '#E8F0FE', '#F9DEDC', '#E6F4EA', '#FEF7E0'
PINK = T_RED
# brand fills for marks: the four Google colors, one per part of the talk, and two greys
G_BLUE, G_RED, G_YELLOW, G_GREEN = '#4285F4', '#EA4335', '#FBBC04', '#34A853'
SECTION = (G_BLUE, G_RED, G_YELLOW, G_GREEN)
BLUE, GREY, LGREY = G_BLUE, FAINT, RULE
RED_STRIPE = f'repeating-linear-gradient(135deg, {G_RED} 0px, {G_RED} 9px, #F28B82 9px, #F28B82 18px)'
DISPLAY = "'Google Sans', 'Product Sans', Arial, sans-serif"
SANS = "'Google Sans Text', 'Google Sans', Arial, sans-serif"
MONO = "'Google Sans Code', Menlo, monospace"
FACES = {
    'google-sans': {'family': 'Google Sans',
                    'href': 'https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap'},
    'google-sans-text': {'family': 'Google Sans Text',
                         'href': 'https://fonts.googleapis.com/css2?family=Google+Sans+Text:wght@400;500&display=swap'},
    'google-sans-code': {'family': 'Google Sans Code',
                         'href': 'https://fonts.googleapis.com/css2?family=Google+Sans+Code:wght@400;500&display=swap'},
}


def esc(text):
    return _html.escape(text, quote=False)


def disp(size, weight=400, color=INK, extra=''):
    """Inline style for display type: Google Sans at one of the display sizes."""
    return f'font-family:{DISPLAY}; font-size:{size}px; font-weight:{weight}; color:{color}' + (f'; {extra}' if extra else '')


# ---------------------------------------------------------------- slide shells


def eyebrow(text, color=G_BLUE):
    """The kicker: a small display label after a dot in the part's color."""
    return (f'<div style="display:flex; align-items:center; gap:12px">'
            f'<div style="width:14px; height:14px; border-radius:7px; background:{color}"></div>'
            f'<p style="{disp(24, 500, MUTED)}">{text}</p></div>')


def head(eyebrow_text, title_text, color=G_BLUE):
    return f'''<div style="display:flex; flex-direction:column; gap:18px">
    {eyebrow(eyebrow_text, color)}
    <h2 style="{disp(52, 400, INK, 'line-height:1.16; letter-spacing:-0.6px')}">{title_text}</h2>
  </div>'''


def foot(text):
    return f'<p style="position:absolute; left:128px; bottom:64px; width:1664px; font-size:24px; color:{FAINT}">{text}</p>'


def aside(note):
    """Speaker notes. The runtime reads <aside> like HTML text and turns a raw newline into a space,
    so every line break is written as <br>; the raw newline after it only keeps the file readable."""
    if not note:
        return ''
    body = re.sub(r'<br>(?!<br>)', '<br>\n', esc(note).replace('\n', '<br>'))
    return f'\n  <aside>{body}</aside>'


def slide(sid, eyebrow_text, title_text, body, source=None, gap=44, note='', color=G_BLUE):
    """A content slide: kicker with the part's color dot, title, body, optional pinned source line, notes."""
    pad = '92px 128px 160px' if source else '92px 128px 128px'
    f = '\n  ' + foot(source) if source else ''
    return f'''<section id="{sid}" data-transition="fade" style="background:{PAPER}; color:{INK}; font-family:{SANS}; padding:{pad}; display:flex; flex-direction:column; gap:{gap}px">
  {head(eyebrow_text, title_text, color)}
  {body}{f}{aside(note)}
</section>
'''


def cover(sid, eyebrow_text, title_html, subtitle, left, right, note=''):
    """White cover: kicker, title, subtitle, then the author (left) and the affiliation or date (right)."""
    return f'''<section id="{sid}" data-transition="fade" style="background:{PAPER}; color:{INK}; font-family:{SANS}; padding:128px; display:flex; flex-direction:column; justify-content:center; gap:28px">
  {eyebrow(eyebrow_text)}
  <h1 style="{disp(104, 400, INK, 'line-height:1.02; letter-spacing:-2px; width:1300px')}">{title_html}</h1>
  <p style="{disp(32, 400, MUTED, 'line-height:1.35; width:1300px')}">{subtitle}</p>
  <div style="display:flex; flex-direction:column; gap:8px; padding:80px 0 0 0">
    <p style="{disp(32, 500, INK)}">{left}</p>
    <p style="font-size:26px; line-height:1.45; color:{MUTED}">{right}</p>
  </div>{aside(note)}
</section>
'''


def part(sid, number_label, title, subtitle, tone=T_BLUE, note=''):
    """A part divider on a tonal ground: the part's number, a large title and one line under it."""
    return f'''<section id="{sid}" data-transition="fade" style="background:{tone}; color:{INK}; font-family:{SANS}; padding:128px; display:flex; flex-direction:column; justify-content:center; gap:28px">
  <p style="{disp(28, 500, MUTED, 'letter-spacing:3px; text-transform:uppercase')}">{number_label}</p>
  <h2 style="{disp(96, 400, INK, 'line-height:1.04; letter-spacing:-1.5px; width:1180px')}">{title}</h2>
  <p style="{disp(32, 400, MUTED, 'line-height:1.35; width:1100px')}">{subtitle}</p>{aside(note)}
</section>
'''


# ---------------------------------------------------------------- small parts


def pin(x, top, w, text, style):
    """Pinned text. Keep x and top at 0 or more: the runtime clamps negative offsets to 0."""
    assert x >= 0 and top >= 0, 'negative offset is clamped to 0 by the runtime'
    return f'<p style="position:absolute; left:{round(x)}px; top:{round(top)}px; width:{round(w)}px; {style}">{text}</p>'


def lede(text, width=1500):
    """The one lead sentence of a slide: display 32 in the muted grey."""
    return f'<p style="{disp(32, 400, MUTED, f"line-height:1.4; width:{width}px")}">{text}</p>'


def ctitle(text):
    """Chart title: a short noun phrase in display 28, medium."""
    return f'<p style="{disp(28, 500, INK)}">{text}</p>'


def label(text, color=INK):
    """Panel heading: the same style as ctitle."""
    return f'<p style="{disp(28, 500, color)}">{text}</p>'


def image(alt, w, h, src='', extra=''):
    """An image frame. With src empty the slide shows a sized placeholder until the file is uploaded.
    Figures sit straight on white; paper figures have white grounds."""
    s = f' src="{src}"' if src else ''
    return f'<img{s} alt="{esc(alt)}" style="width:{w}px; height:{h}px; object-fit:contain{"; " + extra if extra else ""}">'


# ---------------------------------------------------------------- cards


def stat(num, text, src='', accent=False):
    """A big number on the white ground with its sentence and source under it; no box."""
    s_ = f'<p style="font-size:24px; color:{FAINT}">{src}</p>' if src else ''
    return f'''<div style="display:flex; flex-direction:column; gap:16px">
      <p style="{disp(104, 400, ACC if accent else INK, "line-height:0.95; letter-spacing:-3px")}">{num}</p>
      <p style="font-size:26px; line-height:1.45; color:{SOFT}">{text}</p>{s_}
    </div>'''


def column(head_text, text):
    """An open column: a hairline above, a heading and a sentence."""
    return f'''<div style="flex:1; border-top:2px solid {INK}; padding:24px 0 0 0; display:flex; flex-direction:column; gap:12px">
      <p style="{disp(32, 400, INK)}">{head_text}</p>
      <p style="font-size:26px; line-height:1.45; color:{SOFT}">{text}</p>
    </div>'''


def big(text, color=INK):
    """A standalone number in display 84."""
    return f'<p style="{disp(84, 400, color, "line-height:1; letter-spacing:-2px")}">{text}</p>'


def sub(text):
    return f'<p style="font-size:24px; line-height:1.3; color:{MUTED}">{text}</p>'


def pill(text, bg=T_BLUE, color=DEEP):
    """A tonal pill: T_BLUE with DEEP, T_RED with RED, T_GREEN with GREEN, CHIP with MUTED."""
    return f'<p style="background:{bg}; {disp(24, 500, color)}; padding:4px 16px; border-radius:99px">{text}</p>'
