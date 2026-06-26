# Produk

## Apa ini

Project untuk mengubah database Alkitab **Terjemahan Baru (TB)** dari Lembaga
Alkitab Indonesia menjadi ebook yang bisa dibaca di **Amazon Kindle**.

Sumber data adalah `bible.db` (SQLite), dan keluarannya berupa file EPUB yang
dikirim ke Kindle lewat **Send to Kindle**.

## Kenapa EPUB, bukan MOBI/AZW3

Amazon sudah menghentikan dukungan format MOBI untuk pengiriman baru. EPUB adalah
jalur resmi yang direkomendasikan sekarang — Amazon otomatis mengonversinya ke
format internal Kindle saat dikirim via Send to Kindle atau email `@kindle.com`.

Tidak ada dependency eksternal (Calibre/kindlegen tidak dibutuhkan); EPUB dibangun
langsung dari Python standar.

## Keluaran

Project menghasilkan dua varian, masing-masing dengan identifier unik supaya
Kindle memperlakukannya sebagai dua buku terpisah:

- **`Alkitab-TB.epub`** — teks bersih tanpa nomor ayat (tiap ayat satu paragraf).
- **`Alkitab-TB-numbers.epub`** — dengan nomor ayat superscript di awal tiap ayat.

## Isi & fitur

- 66 kitab, 31.102 ayat lengkap (Indonesia + nama Inggris).
- Daftar isi (TOC) bertingkat: Perjanjian Lama / Perjanjian Baru → kitab → pasal.
- Halaman pembatas asli untuk tiap testament (bisa diklik dari TOC tanpa error).
- Indeks pasal cepat di awal tiap kitab.

## Cara baca di Kindle

1. Buka app/website **Send to Kindle** (`send.amazon.com`).
2. Drag file `.epub` ke sana, atau email ke alamat `@kindle.com` kamu.
3. Amazon mengonversi dan mengirim ke device otomatis.
