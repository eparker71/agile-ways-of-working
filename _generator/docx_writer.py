"""A tiny .docx writer using only the standard library (zipfile + WordprocessingML).

Supports what the facilitator guides need: a title, headings, paragraphs with bold/italic
runs, real bullet lists, simple tables and a quote. Text can include a little HTML
(<b>, <i>, <a>, <br>, entities), which is converted to Word runs.
"""
import re
import zipfile
from html import unescape
from xml.sax.saxutils import escape as xesc

W_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def _runs(html, bold=False, italic=False, size=None, color=None):
    """Convert a small HTML fragment into <w:r> runs."""
    out = []
    b, i = bold, italic
    for tok in re.split(r"(<[^>]+>)", html or ""):
        if not tok:
            continue
        if tok.startswith("<"):
            t = tok.lower()
            if t.startswith("<b") and not t.startswith("<br"):
                b = True
            elif t.startswith("</b"):
                b = bold
            elif t.startswith("<i"):
                i = True
            elif t.startswith("</i"):
                i = italic
            elif t.startswith("<br"):
                out.append("<w:r><w:br/></w:r>")
            continue
        text = unescape(tok)
        props = ""
        if b:
            props += "<w:b/>"
        if i:
            props += "<w:i/>"
        if color:
            props += f'<w:color w:val="{color}"/>'
        if size:
            props += f'<w:sz w:val="{size}"/>'
        rpr = f"<w:rPr>{props}</w:rPr>" if props else ""
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{xesc(text)}</w:t></w:r>')
    return "".join(out)


class Doc:
    def __init__(self, title, author=""):
        self.title, self.author, self.body = title, author, []

    def _p(self, runs, style=None, extra=""):
        ppr = f'<w:pStyle w:val="{style}"/>' if style else ""
        ppr = f"<w:pPr>{ppr}{extra}</w:pPr>" if (ppr or extra) else ""
        self.body.append(f"<w:p>{ppr}{runs}</w:p>")

    def heading(self, text, level=1):
        self._p(_runs(text), {0: "Title", 1: "Heading1", 2: "Heading2"}[level])

    def para(self, html, style=None, **kw):
        self._p(_runs(html, **kw), style)

    def quote(self, html):
        self._p(_runs(html, italic=True), "Quote")

    def bullets(self, items):
        for it in items:
            self._p(_runs(it), "ListBullet", '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>')

    def labelled(self, label, html):
        """A paragraph starting with a bold label."""
        self._p(_runs(label + " ", bold=True) + _runs(html))

    def table(self, header, rows, widths=None):
        n = len(header)
        widths = widths or [int(9000 / n)] * n
        grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)

        def row(cells, head=False):
            tcs = []
            for c, w in zip(cells, widths):
                shade = '<w:shd w:val="clear" w:color="auto" w:fill="EEF2F6"/>' if head else ""
                tcs.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shade}</w:tcPr>'
                           f'<w:p>{_runs(c, bold=head)}</w:p></w:tc>')
            hdr = "<w:trPr><w:tblHeader/></w:trPr>" if head else ""
            return f"<w:tr>{hdr}{''.join(tcs)}</w:tr>"

        self.body.append(
            '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/></w:tblPr>'
            f"<w:tblGrid>{grid}</w:tblGrid>{row(header, True)}{''.join(row(r) for r in rows)}</w:tbl>")
        self._p("")

    # ------------------------------------------------------------- package
    def save(self, path):
        document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {W_NS}><w:body>'
                    + "".join(self.body)
                    + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
                      '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" w:gutter="0"/>'
                      "</w:sectPr></w:body></w:document>")
        files = {
            "[Content_Types].xml": CONTENT_TYPES,
            "_rels/.rels": ROOT_RELS,
            "word/_rels/document.xml.rels": DOC_RELS,
            "word/document.xml": document,
            "word/styles.xml": STYLES,
            "word/numbering.xml": NUMBERING,
            "docProps/core.xml": CORE.format(title=xesc(self.title), author=xesc(self.author)),
        }
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in files.items():
                z.writestr(name, data)


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>"""

CORE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>{title}</dc:title><dc:creator>{author}</dc:creator></cp:coreProperties>"""

NUMBERING = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering {W_NS}>
<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/>
<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/>
<w:pPr><w:ind w:left="567" w:hanging="283"/></w:pPr></w:lvl></w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""

STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {W_NS}>
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:sz w:val="21"/><w:color w:val="1E293B"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/>
<w:pPr><w:spacing w:after="60"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="48"/><w:color w:val="0C1A2E"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/>
<w:pPr><w:keepNext/><w:spacing w:before="320" w:after="100"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="32"/><w:color w:val="0C1A2E"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/>
<w:pPr><w:keepNext/><w:spacing w:before="200" w:after="60"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:sz w:val="23"/><w:color w:val="9A3412"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/>
<w:pPr><w:ind w:left="284"/><w:pBdr><w:left w:val="single" w:sz="18" w:space="8" w:color="EB6C36"/></w:pBdr></w:pPr><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:i/><w:sz w:val="26"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="40"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Small"><w:name w:val="Small"/><w:basedOn w:val="Normal"/><w:rPr><w:sz w:val="17"/><w:color w:val="64748B"/></w:rPr></w:style>
<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders>
<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
<w:insideH w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
</w:tblBorders><w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="60" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>
</w:styles>"""
