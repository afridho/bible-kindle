# Teknologi & Perintah

## Stack

- **Python 3** (standar library saja — `sqlite3`, `zipfile`, `html`, `datetime`).
  Tidak ada `requirements.txt` / dependency pihak ketiga.
- **SQLite** sebagai sumber data (`Source/Indonesia/bible.db`).
- **EPUB 3** sebagai format keluaran.

Build dijalankan via `python3` (di mesin dev: pyenv, Python 3.13).

## Perintah utama

```bash
# Bangun kedua varian EPUB (tanpa nomor & dengan nomor ayat)
python3 build_epub.py
```

Skrip membaca dari `Source/Indonesia/bible.db` (konstanta `DB_PATH`) dan
menulis `Alkitab-TB.epub` + `Alkitab-TB-numbers.epub` ke `Output/Indonesia/`
(konstanta `OUT_DIR`; folder dibuat otomatis). Struktur diorganisir per bahasa
(`Source/<Bahasa>/`, `Output/<Bahasa>/`) untuk memudahkan menambah versi lain.

## Cara kerja `build_epub.py`

- Fungsi `main(out_path, show_verse_numbers, book_id)` membangun satu EPUB.
  Blok `__main__` memanggilnya dua kali untuk dua varian.
- `show_verse_numbers=True` menambah `<span class="vnum">` superscript;
  `False` menampilkan ayat sebagai paragraf bersih.
- `book_id` harus **unik per varian** (urn:uuid). Jika sama, Kindle akan
  menganggapnya buku yang sama dan saling menimpa.

## Aturan EPUB yang WAJIB dijaga

Pelanggaran hal-hal ini menyebabkan EPUB rusak atau error di Kindle:

1. **`mimetype` harus entri pertama di zip dan disimpan `ZIP_STORED`** (tidak
   dikompres). Sudah ditangani di blok penulisan zip.
2. **Semua XHTML & OPF harus well-formed XML.** Gunakan entitas numerik
   (`&#183;`) bukan entitas HTML bernama (`&middot;`) — yang bernama tidak valid
   di XHTML tanpa DTD dan akan gagal di-parse.
3. **Setiap `<li>` di nav.xhtml harus berisi `<a>` (atau `<span>`).** `<li>`
   "kosong" akan dibuang Kindle.
4. **Label TOC harus menunjuk ke target yang benar-benar ada.** Heading testament
   menunjuk ke halaman asli `ot.xhtml` / `nt.xhtml` — jangan pakai `<span>` tanpa
   tujuan, karena Kindle melempar "Destination does not exist" saat diklik.
5. **Setiap `href="file#cN"` harus cocok dengan `id="cN"` yang ada** di file
   tujuan, dan setiap `idref` di spine harus ada di manifest.

## Verifikasi setelah build

Selalu validasi sebelum menganggap selesai:

```bash
# well-formed semua xhtml/opf
unzip -p Output/Indonesia/Alkitab-TB.epub OEBPS/book43.xhtml | python3 -c "import sys,xml.dom.minidom as m; m.parseString(sys.stdin.buffer.read()); print('OK')"

# mimetype entri pertama & stored (0=stored)
python3 -c "import zipfile; i=zipfile.ZipFile('Output/Indonesia/Alkitab-TB.epub').infolist()[0]; print(i.filename, i.compress_type)"
```

Pola yang dipakai selama pengembangan: skrip verifikasi sementara yang mengecek
semua href nav menunjuk file+anchor yang ada, lalu dihapus setelah lolos.

## Catatan format

- Amazon menghentikan MOBI; pakai EPUB + Send to Kindle.
- Jika tetap butuh `.azw3`/`.mobi` lokal: install Calibre
  (`brew install --cask calibre`) lalu `ebook-convert Output/Indonesia/Alkitab-TB.epub Output/Indonesia/Alkitab-TB.azw3`.
