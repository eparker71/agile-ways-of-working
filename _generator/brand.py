"""Brand settings shared by every generator. Change these to rebrand the generated files.

The hand-written pages (index.html, the cheat sheets, the Marginal Gains board and guide)
don't read this file; update their colours and footer text by hand if you rebrand.
"""

# Colours
ACCENT = "#eb6c36"   # orange: top rule, badges, highlights
NAVY = "#0C1A2E"     # header band

# Fonts (Google Fonts). Change the URL and the three family names together.
FONT_URL = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
            "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
SANS = "'Geist',Inter,system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',Consolas,monospace"

# Credit line, printed on every generated board, guide and page
AUTHOR = "Eric Parker"
YEAR = "2026"
LICENCE = "CC BY 4.0"
SITE = "eparker71.github.io/agile-ways-of-working"
CREDIT = f"© {YEAR} {AUTHOR} · {LICENCE} · {SITE}"
