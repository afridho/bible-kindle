#!/usr/bin/env python3
"""
Generate a Kindle-compatible EPUB from bible.db (Alkitab Terjemahan Baru).

Output: Alkitab-TB.epub  (EPUB 3, readable on Kindle via Send to Kindle)

No external dependencies required.
"""

import html
import os
import sqlite3
import zipfile
from datetime import datetime, timezone

DB_PATH = "Source/Indonesia/bible.db"
OUT_DIR = "Output/Indonesia"
TITLE = "Alkitab Terjemahan Baru"
LANG = "id"
AUTHOR = "Lembaga Alkitab Indonesia"
BOOK_ID = "urn:uuid:alkitab-tb-lai-2024"

CSS = """\
body { font-family: serif; line-height: 1.5; margin: 0 5%; }
h1 { text-align: center; font-size: 1.6em; margin: 1em 0 0.2em; }
h2 { font-size: 1.2em; margin: 1.2em 0 0.4em; border-bottom: 1px solid #ccc; }
.subtitle { text-align: center; color: #666; font-size: 0.9em; margin-bottom: 1.5em; }
.verse { margin: 0.4em 0; }
.verse-num { margin: 0.15em 0; text-indent: -1.2em; padding-left: 1.2em; }
.vnum { font-weight: bold; font-size: 0.75em; vertical-align: super; color: #444; margin-right: 0.3em; }
.testament { text-align: center; font-size: 1.4em; margin-top: 2em; color: #333; }
nav ol { list-style: none; padding-left: 1em; }
.title-page { text-align: center; margin-top: 25%; }
.title-page h1 { font-size: 2.2em; }
.testament-page { text-align: center; margin-top: 40%; }
.testament-page h1 { font-size: 1.9em; border: none; }
.toc-book { font-weight: bold; }
.chap-links a { display: inline-block; min-width: 1.6em; text-align: center; margin: 0.1em; }
"""


def esc(s):
    return html.escape(s, quote=False)


def xhtml_wrap(title, body):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops" lang="%s" xml:lang="%s">\n'
        '<head>\n'
        '<meta charset="utf-8"/>\n'
        '<title>%s</title>\n'
        '<link rel="stylesheet" type="text/css" href="style.css"/>\n'
        '</head>\n'
        '<body>\n%s\n</body>\n</html>\n'
        % (LANG, LANG, esc(title), body)
    )


def main(out_path, show_verse_numbers=False, book_id=BOOK_ID):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    books = cur.execute(
        "SELECT id, name_en, name_id, abbr, testament, chapter_count, book_order "
        "FROM books ORDER BY book_order"
    ).fetchall()

    files = {}  # path -> content (str or bytes)

    # --- mimetype handled separately (stored, first) ---

    # container.xml
    files["META-INF/container.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<container version="1.0" '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '  <rootfiles>\n'
        '    <rootfile full-path="OEBPS/content.opf" '
        'media-type="application/oebps-package+xml"/>\n'
        '  </rootfiles>\n'
        '</container>\n'
    )

    files["OEBPS/style.css"] = CSS

    # Title page
    title_body = (
        '<div class="title-page">\n'
        '<h1>%s</h1>\n'
        '<p class="subtitle">%s</p>\n'
        '<p class="subtitle">66 Kitab &#183; 31.102 Ayat</p>\n'
        '</div>\n' % (esc(TITLE), esc(AUTHOR))
    )
    files["OEBPS/title.xhtml"] = xhtml_wrap(TITLE, title_body)

    # Testament divider pages (real targets for the TOC section headings)
    def testament_page(label, subtitle):
        body = (
            '<div class="testament-page">\n'
            '<h1>%s</h1>\n'
            '<p class="subtitle">%s</p>\n'
            '</div>\n' % (esc(label), esc(subtitle))
        )
        return xhtml_wrap(label, body)

    files["OEBPS/ot.xhtml"] = testament_page(
        "Perjanjian Lama", "39 Kitab"
    )
    files["OEBPS/nt.xhtml"] = testament_page(
        "Perjanjian Baru", "27 Kitab"
    )

    # Build one xhtml per book
    book_files = []  # (book, filename)
    for b in books:
        verses = cur.execute(
            "SELECT chapter, verse, text FROM verses WHERE book_id=? "
            "ORDER BY chapter, verse",
            (b["id"],),
        ).fetchall()

        parts = ['<h1 id="top">%s</h1>' % esc(b["name_id"])]
        parts.append('<p class="subtitle">%s</p>' % esc(b["name_en"]))

        # quick chapter index inside the book
        chap_links = " ".join(
            '<a href="#c%d">%d</a>' % (c, c)
            for c in range(1, b["chapter_count"] + 1)
        )
        parts.append('<p class="chap-links">%s</p>' % chap_links)

        current_chapter = None
        for v in verses:
            if v["chapter"] != current_chapter:
                current_chapter = v["chapter"]
                parts.append(
                    '<h2 id="c%d">%s %d</h2>'
                    % (current_chapter, esc(b["name_id"]), current_chapter)
                )
            if show_verse_numbers:
                parts.append(
                    '<p class="verse-num"><span class="vnum">%d</span>%s</p>'
                    % (v["verse"], esc(v["text"]))
                )
            else:
                parts.append(
                    '<p class="verse">%s</p>' % esc(v["text"])
                )

        fname = "book%02d.xhtml" % b["book_order"]
        files["OEBPS/" + fname] = xhtml_wrap(b["name_id"], "\n".join(parts))
        book_files.append((b, fname))

    # nav.xhtml (EPUB3 navigation)
    # Group books under testament headings. EPUB3 nav requires every <li> to
    # contain an <a> or <span>; a heading label must be a <span>, and its
    # children go in a nested <ol>.
    def book_li(b, fname):
        chap_sub = "\n".join(
            '<li><a href="%s#c%d">Pasal %d</a></li>' % (fname, c, c)
            for c in range(1, b["chapter_count"] + 1)
        )
        return (
            '<li><a href="%s">%s</a>\n<ol>\n%s\n</ol></li>'
            % (fname, esc(b["name_id"]), chap_sub)
        )

    ot_books = [(b, f) for b, f in book_files if b["testament"] == "OT"]
    nt_books = [(b, f) for b, f in book_files if b["testament"] == "NT"]

    nav_items = ['<li><a href="title.xhtml">Halaman Judul</a></li>']
    for label, page, group in (
        ("Perjanjian Lama", "ot.xhtml", ot_books),
        ("Perjanjian Baru", "nt.xhtml", nt_books),
    ):
        inner = "\n".join(book_li(b, f) for b, f in group)
        nav_items.append(
            '<li class="toc-book"><a href="%s">%s</a>\n<ol>\n%s\n</ol></li>'
            % (page, esc(label), inner)
        )

    nav_body = (
        '<nav epub:type="toc" id="toc">\n<h1>Daftar Isi</h1>\n<ol>\n%s\n</ol>\n</nav>\n'
        % "\n".join(nav_items)
    )
    files["OEBPS/nav.xhtml"] = xhtml_wrap("Daftar Isi", nav_body)

    # content.opf
    manifest = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="css" href="style.css" media-type="text/css"/>',
        '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
        '<item id="ot" href="ot.xhtml" media-type="application/xhtml+xml"/>',
        '<item id="nt" href="nt.xhtml" media-type="application/xhtml+xml"/>',
    ]
    spine = ['<itemref idref="title"/>', '<itemref idref="nav"/>']
    seen_ot = seen_nt = False
    for b, fname in book_files:
        item_id = "b%02d" % b["book_order"]
        # insert the testament divider right before its first book
        if b["testament"] == "OT" and not seen_ot:
            spine.append('<itemref idref="ot"/>')
            seen_ot = True
        if b["testament"] == "NT" and not seen_nt:
            spine.append('<itemref idref="nt"/>')
            seen_nt = True
        manifest.append(
            '<item id="%s" href="%s" media-type="application/xhtml+xml"/>'
            % (item_id, fname)
        )
        spine.append('<itemref idref="%s"/>' % item_id)

    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opf = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        'unique-identifier="bookid">\n'
        '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        '    <dc:identifier id="bookid">%s</dc:identifier>\n'
        '    <dc:title>%s</dc:title>\n'
        '    <dc:language>%s</dc:language>\n'
        '    <dc:creator>%s</dc:creator>\n'
        '    <meta property="dcterms:modified">%s</meta>\n'
        '  </metadata>\n'
        '  <manifest>\n    %s\n  </manifest>\n'
        '  <spine>\n    %s\n  </spine>\n'
        '</package>\n'
        % (
            book_id,
            esc(TITLE),
            LANG,
            esc(AUTHOR),
            modified,
            "\n    ".join(manifest),
            "\n    ".join(spine),
        )
    )
    files["OEBPS/content.opf"] = opf

    conn.close()

    # Write EPUB zip
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if os.path.exists(out_path):
        os.remove(out_path)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        # mimetype must be first and uncompressed
        z.writestr(
            zipfile.ZipInfo("mimetype"),
            "application/epub+zip",
            compress_type=zipfile.ZIP_STORED,
        )
        for path, content in files.items():
            if isinstance(content, str):
                content = content.encode("utf-8")
            z.writestr(path, content)

    size = os.path.getsize(out_path)
    print("Created %s (%.1f KB)" % (out_path, size / 1024))
    print("Books: %d" % len(book_files))


if __name__ == "__main__":
    # Version without verse numbers
    main(
        out_path=os.path.join(OUT_DIR, "Alkitab-TB.epub"),
        show_verse_numbers=False,
        book_id="urn:uuid:alkitab-tb-lai-2024",
    )
    # Version with verse numbers
    main(
        out_path=os.path.join(OUT_DIR, "Alkitab-TB-numbers.epub"),
        show_verse_numbers=True,
        book_id="urn:uuid:alkitab-tb-lai-2024-numbers",
    )
