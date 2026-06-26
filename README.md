# Bible Kindle

Mengubah database Alkitab **Terjemahan Baru (TB)** dari Lembaga Alkitab Indonesia
menjadi ebook **EPUB** yang bisa dibaca di Amazon Kindle — tanpa dependency
eksternal, hanya Python standard library.

## Fitur

- 66 kitab, 31.102 ayat lengkap (nama Indonesia + Inggris).
- Daftar isi bertingkat: Perjanjian Lama / Perjanjian Baru → kitab → pasal.
- Halaman pembatas testament yang bisa diklik dari TOC.
- Indeks pasal cepat di awal tiap kitab.
- Dua varian: tanpa nomor ayat & dengan nomor ayat.

## Prasyarat

- Python 3 (dikembangkan dengan 3.13).
- File sumber `bible.db` (SQLite) di `Source/Indonesia/`.

Tidak perlu Calibre, kindlegen, atau pip install apa pun.

## Cara pakai

```bash
python3 build_epub.py
```

Menghasilkan dua file di `Output/Indonesia/`:

| File                                       | Keterangan                                               |
| ------------------------------------------ | -------------------------------------------------------- |
| `Output/Indonesia/Alkitab-TB.epub`         | Teks bersih, tanpa nomor ayat (tiap ayat satu paragraf). |
| `Output/Indonesia/Alkitab-TB-numbers.epub` | Dengan nomor ayat superscript di awal tiap ayat.         |

## Kirim ke Kindle

Amazon sudah menghentikan format MOBI, jadi EPUB adalah jalur yang
direkomendasikan:

1. Buka app/website **Send to Kindle** (`send.amazon.com`).
2. Drag file `.epub`, atau email ke alamat `@kindle.com` kamu.
3. Amazon mengonversi ke format Kindle dan mengirim ke device otomatis.

Butuh `.azw3`/`.mobi` lokal? Pakai Calibre:

```bash
brew install --cask calibre
ebook-convert Output/Indonesia/Alkitab-TB.epub Output/Indonesia/Alkitab-TB.azw3
```

## Struktur project

```
bible-kindle/
├── Source/
│   └── Indonesia/
│       └── bible.db              # Sumber data SQLite (jangan diedit manual)
├── Output/
│   └── Indonesia/
│       ├── Alkitab-TB.epub          # Keluaran (di-generate)
│       └── Alkitab-TB-numbers.epub  # Keluaran (di-generate)
├── build_epub.py             # Generator EPUB
├── README.md
├── CHANGELOG.md
├── DESIGN.md                 # Dokumen desain teknis
├── CLAUDE.md                 # Konteks untuk agent AI
└── .kiro/steering/           # Steering files Kiro
```

## Menambah varian / bahasa baru

- **Bahasa baru:** taruh database di `Source/<Bahasa>/` dan arahkan keluaran ke
  `Output/<Bahasa>/` (sesuaikan `DB_PATH` / `OUT_DIR` di `build_epub.py`).
- **Varian baru:** panggil `main()` dengan `out_path` dan `book_id` (urn:uuid)
  **unik** — identifier wajib beda agar Kindle tidak menganggapnya buku yang
  sama dan saling menimpa. Atur nomor ayat lewat flag `show_verse_numbers`.

## Dokumentasi lanjutan

- [`DESIGN.md`](DESIGN.md) — arsitektur, keputusan desain, dan invarian EPUB.
- [`CHANGELOG.md`](CHANGELOG.md) — riwayat perubahan.
- [`CLAUDE.md`](CLAUDE.md) — panduan untuk agent AI.
- `.kiro/steering/` — konteks project untuk Kiro (product / tech / structure).
