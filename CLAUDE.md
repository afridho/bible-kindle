# CLAUDE.md

Panduan untuk agent AI (Claude Code, dll.) saat bekerja di repo ini. Setara
dengan steering files Kiro di `.kiro/steering/`. Balas dalam Bahasa Indonesia.

## Ringkasan project

Mengubah database Alkitab Terjemahan Baru (`bible.db`, SQLite) menjadi ebook
**EPUB 3** yang kompatibel Kindle. Tanpa dependency eksternal — hanya Python
standard library. Detail desain ada di `DESIGN.md`.

## Perintah

```bash
# Build kedua varian EPUB
python3 build_epub.py
```

Keluaran di `Output/Indonesia/`:

- `Alkitab-TB.epub` — tanpa nomor ayat.
- `Alkitab-TB-numbers.epub` — dengan nomor ayat superscript.

Tidak ada test runner / linter / package manager. Sumber data
`Source/Indonesia/bible.db` jangan diedit manual. File `.epub` adalah artefak —
selalu bisa di-generate ulang. Path diatur lewat `DB_PATH` & `OUT_DIR` di
`build_epub.py`; struktur per bahasa (`Source/<Bahasa>/`, `Output/<Bahasa>/`).

## Struktur kode

- `build_epub.py` — satu-satunya skrip. Fungsi `main(out_path,
show_verse_numbers, book_id)` membangun satu EPUB; blok `__main__` memanggilnya
  dua kali untuk dua varian.
- Helper `esc()` meng-escape semua teks yang masuk XHTML — selalu pakai ini.
- `xhtml_wrap()` membungkus body jadi dokumen XHTML lengkap.

## Skema database

```
books(id, name_en, name_id, abbr, testament['OT'|'NT'], chapter_count, book_order UNIQUE)
verses(id, book_id, chapter, verse, text, UNIQUE(book_id,chapter,verse))
```

66 kitab (book_order 1–66), 31.102 ayat. FTS5 `verses_fts*` ada tapi tidak
dipakai build.

## Aturan EPUB yang WAJIB dijaga

Melanggar ini = EPUB rusak atau error di Kindle:

1. `mimetype` harus entri zip **pertama** dan `ZIP_STORED` (tidak dikompres).
2. Semua XHTML & OPF harus **well-formed XML**. Gunakan entitas numerik
   (`&#183;`), bukan entitas HTML bernama (`&middot;`) — yang bernama invalid di
   XHTML dan gagal di-parse.
3. Setiap `<li>` di `nav.xhtml` harus berisi `<a>` atau `<span>`. `<li>` kosong
   dibuang Kindle.
4. Label/heading TOC harus menunjuk **target yang benar-benar ada**. Heading
   testament menunjuk ke `ot.xhtml` / `nt.xhtml` (halaman asli), bukan `<span>`
   tanpa tujuan — kalau tidak, Kindle melempar "Destination does not exist".
5. Tiap `href="file#cN"` harus cocok dengan `id="cN"` di file tujuan; tiap
   `idref` di spine harus ada di manifest.

## Verifikasi sebelum selesai

Selalu validasi setelah build:

```bash
# well-formed
unzip -p Output/Indonesia/Alkitab-TB.epub OEBPS/book43.xhtml | python3 -c "import sys,xml.dom.minidom as m; m.parseString(sys.stdin.buffer.read()); print('OK')"
# mimetype pertama & stored (0=stored)
python3 -c "import zipfile; i=zipfile.ZipFile('Output/Indonesia/Alkitab-TB.epub').infolist()[0]; print(i.filename, i.compress_type)"
```

Idealnya juga cek semua href nav menunjuk file+anchor yang ada (skrip sementara,
hapus setelah lolos).

## Konvensi

- Bahasa balasan & dokumentasi: **Indonesia**. Komentar kode boleh Inggris.
- Saat menambah varian EPUB baru, beri `book_id` (urn:uuid) **unik** agar tidak
  bertabrakan di Kindle.
- Amazon menghentikan MOBI; target adalah EPUB + Send to Kindle. AZW3/MOBI lokal
  opsional via Calibre (`ebook-convert Output/Indonesia/Alkitab-TB.epub Output/Indonesia/Alkitab-TB.azw3`).

## Referensi

- `DESIGN.md` — keputusan & arsitektur desain.
- `CHANGELOG.md` — riwayat perubahan.
- `.kiro/steering/` — steering files setara (product / tech / structure).
