# Struktur Project

## Layout

```
bible-kindle/
├── Source/
│   └── Indonesia/
│       └── bible.db          # Sumber data SQLite (jangan diedit manual)
├── Output/
│   └── Indonesia/
│       ├── Alkitab-TB.epub          # Keluaran: tanpa nomor ayat (di-generate)
│       └── Alkitab-TB-numbers.epub  # Keluaran: dengan nomor ayat (di-generate)
├── build_epub.py             # Generator EPUB (satu-satunya skrip)
├── README.md
├── CHANGELOG.md
├── DESIGN.md
├── CLAUDE.md
└── .kiro/
    └── steering/             # Konteks untuk Kiro
        ├── product.md
        ├── tech.md
        └── structure.md
```

Sumber & keluaran diorganisir per bahasa (`Source/<Bahasa>/`,
`Output/<Bahasa>/`) agar mudah menambah versi/bahasa lain. File `.epub` adalah
artefak hasil build — selalu bisa dibuat ulang dari `bible.db` + `build_epub.py`.
Tidak perlu diedit manual.

## Skema database (`Source/Indonesia/bible.db`)

```
books(
  id, name_en, name_id, abbr,
  testament TEXT CHECK(IN ('OT','NT')),
  chapter_count, book_order UNIQUE
)

verses(
  id, book_id REFERENCES books(id),
  chapter, verse, text,
  UNIQUE(book_id, chapter, verse)
)
```

- 66 baris di `books`, `book_order` berurutan 1–66 dan unik.
- 31.102 baris di `verses`.
- Ada juga FTS5 (`verses_fts*`) untuk pencarian — tidak dipakai oleh build EPUB.
- `chapter_count` di `books` sudah dikonfirmasi cocok dengan jumlah pasal nyata
  di `verses` (tidak ada pasal bolong). Link pasal dibuat dari `chapter_count`.

## Struktur EPUB yang dihasilkan

```
mimetype                      # harus pertama, ZIP_STORED
META-INF/container.xml
OEBPS/
├── content.opf               # metadata + manifest + spine
├── nav.xhtml                 # TOC EPUB3 (PL/PB → kitab → pasal)
├── style.css
├── title.xhtml               # halaman judul
├── ot.xhtml                  # pembatas Perjanjian Lama
├── nt.xhtml                  # pembatas Perjanjian Baru
└── book01.xhtml ... book66.xhtml   # satu file per kitab, dinamai book_order
```

- Nama file kitab: `book%02d.xhtml` memakai `book_order`.
- Anchor pasal di tiap kitab: `id="cN"` (N = nomor pasal). Link TOC & indeks
  internal menunjuk ke `bookXX.xhtml#cN`.
- Urutan spine: title → nav → ot → kitab PL → nt → kitab PB.

## Konvensi

- Bahasa balasan & dokumentasi: **Indonesia**.
- Semua teks yang masuk XHTML di-escape lewat helper `esc()`.
- Komentar/penjelasan di kode boleh Inggris; konten ebook Indonesia.
- Saat menambah varian baru, selalu beri `book_id` (urn:uuid) yang unik.
