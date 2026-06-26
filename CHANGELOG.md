# Changelog

Semua perubahan penting pada project ini didokumentasikan di sini.
Format mengikuti [Keep a Changelog](https://keepachangelog.com/),
dan project ini memakai [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- Reorganisasi struktur file per bahasa: sumber data dipindah ke
  `Source/Indonesia/bible.db` dan keluaran EPUB ke `Output/Indonesia/`.
  Mempermudah penambahan versi/bahasa lain ke depan.
- `build_epub.py` kini membaca dari `Source/Indonesia/` dan menulis ke
  `Output/Indonesia/`; folder output dibuat otomatis bila belum ada.

### Added

- `CHANGELOG.md`.

## [0.2.0]

### Added

- Varian `Alkitab-TB-numbers.epub` dengan nomor ayat superscript, di samping
  `Alkitab-TB.epub` yang tanpa nomor. Tiap varian punya `book_id` unik.
- Halaman pembatas testament asli (`ot.xhtml` / `nt.xhtml`) sebagai target TOC.
- Dokumentasi: `README.md`, `DESIGN.md`, `CLAUDE.md`, dan steering Kiro
  (`.kiro/steering/`).

### Changed

- Nomor ayat dihapus dari varian utama; tiap ayat jadi paragraf bersih.
- Generator dirombak agar `main()` menerima parameter (`out_path`,
  `show_verse_numbers`, `book_id`) untuk membangun banyak varian.

### Fixed

- Label "Perjanjian Lama/Baru" di TOC sebelumnya hilang karena `<li>` kosong;
  kini dibungkus dan menunjuk ke halaman pembatas asli.
- Error Kindle "Destination does not exist" saat klik heading testament.
- Entitas HTML bernama `&middot;` yang invalid di XHTML diganti entitas numerik
  `&#183;`.

## [0.1.0]

### Added

- Generator EPUB awal dari `bible.db`: 66 kitab, 31.102 ayat.
- TOC bertingkat (Perjanjian Lama/Baru → kitab → pasal) dan indeks pasal cepat.
- Build tanpa dependency eksternal (Python standard library).
