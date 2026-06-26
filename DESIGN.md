# Design — Bible Kindle

Dokumen desain teknis untuk konversi database Alkitab Terjemahan Baru (TB)
menjadi ebook EPUB yang kompatibel dengan Amazon Kindle.

## Tujuan

- Menghasilkan EPUB dari `bible.db` yang bisa dibaca di Kindle via Send to Kindle.
- Tanpa dependency eksternal (hanya Python standard library).
- Navigasi yang benar: Perjanjian Lama/Baru → kitab → pasal, tanpa link rusak.

## Non-tujuan

- Tidak menargetkan MOBI/AZW3 (Amazon sudah menghentikan MOBI; EPUB dikonversi
  otomatis oleh Amazon). Konversi lokal opsional via Calibre, di luar scope skrip.
- Tidak mengubah/menormalisasi isi teks Alkitab di `bible.db`.
- Tidak ada UI; murni skrip build.

## Arsitektur

```
bible.db (SQLite)  ──►  build_epub.py  ──►  *.epub (EPUB 3)
Source/Indonesia/         │                  Output/Indonesia/
                          ├─ baca tabel books + verses
                          ├─ render XHTML per kitab + halaman bantu
                          ├─ susun nav.xhtml (TOC) + content.opf
                          └─ paket jadi zip EPUB
```

Satu fungsi `main(out_path, show_verse_numbers, book_id)` membangun satu EPUB
penuh di memori (dict `path -> content`), lalu menuliskannya sebagai zip. Blok
`__main__` memanggil `main()` dua kali untuk dua varian. Path sumber & keluaran
diatur lewat konstanta `DB_PATH` dan `OUT_DIR`.

Sumber data dan keluaran diorganisir per bahasa (`Source/<Bahasa>/`,
`Output/<Bahasa>/`) supaya mudah menambah versi/bahasa lain.

## Sumber data

Lihat skema lengkap di `.kiro/steering/structure.md`. Ringkas:

- `books`: 66 baris, `book_order` unik 1–66, `testament` ∈ {OT, NT}.
- `verses`: 31.102 baris, unik per (book_id, chapter, verse).
- `chapter_count` dikonfirmasi cocok dengan jumlah pasal nyata (tidak ada bolong).
- Ada FTS5 (`verses_fts*`) — tidak dipakai untuk build.

## Struktur keluaran EPUB

```
mimetype                          # entri pertama, ZIP_STORED
META-INF/container.xml
OEBPS/
  content.opf                     # metadata + manifest + spine
  nav.xhtml                       # TOC EPUB3
  style.css
  title.xhtml                     # halaman judul
  ot.xhtml / nt.xhtml             # pembatas testament (target TOC)
  book01.xhtml .. book66.xhtml    # satu file per kitab (book_order)
```

Urutan spine: `title → nav → ot → kitab PL → nt → kitab PB`.
Anchor pasal: `id="cN"`; link menunjuk `bookXX.xhtml#cN`.

## Keputusan desain

### Kenapa satu file per kitab

Memecah per kitab membuat tiap file kecil, navigasi cepat, dan reader Kindle
tidak perlu memuat 31k ayat sekaligus. Penamaan `book%02d` mengikuti `book_order`
sehingga urutan kanonik terjaga dan stabil.

### Kenapa halaman pembatas testament asli (ot/nt.xhtml)

Awalnya label "Perjanjian Lama/Baru" di TOC dibuat sebagai `<span>` tanpa tujuan.
Di Kindle, entri itu tetap bisa diklik tapi melempar **"Destination does not
exist"**. Solusinya: buat halaman XHTML nyata sebagai target, dan masukkan ke
spine sebelum kitab pertama tiap testament.

### Varian dengan/tanpa nomor ayat

Dikendalikan flag `show_verse_numbers`. Tiap varian punya `book_id` (urn:uuid)
**berbeda** supaya Kindle tidak menganggapnya buku yang sama dan saling menimpa.

## Invarian yang wajib dijaga (sumber bug bila dilanggar)

1. `mimetype` = entri zip pertama, `ZIP_STORED` (tidak dikompres).
2. Semua XHTML & OPF harus well-formed XML. Pakai entitas numerik (`&#183;`),
   bukan entitas HTML bernama (`&middot;`) yang invalid di XHTML tanpa DTD.
3. Setiap `<li>` di nav harus berisi `<a>`/`<span>` (li kosong dibuang Kindle).
4. Label/heading TOC harus menunjuk target yang benar-benar ada.
5. Tiap `href="file#cN"` cocok dengan `id="cN"` yang ada; tiap `idref` di spine
   ada di manifest.

## Strategi verifikasi

Setelah build, validasi (lihat perintah di `.kiro/steering/tech.md`):

- Parse semua XHTML/OPF untuk well-formedness.
- Cek `mimetype` entri pertama + stored.
- Cek semua `href` nav menunjuk file+anchor yang ada, dan semua `idref` spine
  ada di manifest (skrip cek sementara, dihapus setelah lolos).

## Pengembangan lanjutan (ide)

- Cover image.
- Cross-reference antar ayat.
- Varian dwibahasa (ID + EN) memanfaatkan `name_en` / kolom teks tambahan.
- Output AZW3 via Calibre sebagai langkah opsional.
