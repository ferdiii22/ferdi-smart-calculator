# Ferdi Smart Calculator

Aplikasi kalkulator desktop Windows berbahasa Indonesia yang dibangun dengan
Python dan CustomTkinter. Mendukung perhitungan aman berbasis AST dan `Decimal`,
pratinjau langsung, riwayat lokal, mode ilmiah, serta konversi satuan.

## Menjalankan dari sumber

Target rilis mengikuti PRD: Python 3.11+ 64-bit pada Windows 10/11.

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

Data aplikasi disimpan di folder `data\` di samping sumber atau executable:
`settings.json` menyimpan tema, mode, ukuran jendela, dan preferensi always-on-top;
`history.json` menyimpan hingga 500 perhitungan.

## Fitur

- Mode Standar dengan operasi dasar, persen kontekstual, kurung, preview,
  pemisah angka Indonesia, dan presisi desimal.
- Mode Ilmiah: sin, cos, tan (derajat), akar, pangkat, faktorial, pi, log, dan ln.
- Memori MC/MR/M+/M−, riwayat yang dapat dipakai ulang, dan salin hasil.
- Mode gelap/terang, selalu di atas, pintasan keyboard, dan layout riwayat
  dua kolom pada jendela lebar.
- DPI awareness pada Windows dan ukuran teks hasil yang menyesuaikan lebar layar.
- Konverter panjang, berat, suhu, dan data; kalkulator selisih tanggal; serta
  konversi bilangan programmer DEC/BIN/OCT/HEX.
- Semua ekspresi dievaluasi oleh parser AST whitelist; `eval()` tidak digunakan.

Pintasan: `Enter` menghitung, `Esc` menghapus, `Backspace` menghapus karakter,
`Ctrl+C` menyalin hasil, `Ctrl+H` riwayat, `Ctrl+T` tema, dan `Ctrl+1/2/3`
berpindah Standar/Ilmiah/Konverter.

## Tes

```bat
python -m pytest
```

atau gunakan `python -m unittest discover -v` tanpa dependensi tes tambahan.

## Membuat executable

Di Windows dengan Python 3.11+ dan dependensi pada `requirements.txt`:

```bat
build.bat
```

Executable satu file akan dibuat sebagai
`dist\Ferdi Smart Calculator.exe`. Data tetap ditulis ke folder `data\` di
samping executable. Build lokal yang diuji berukuran sekitar 9,24 MB dan
berhasil dibuka serta menyimpan pengaturan di sebelah executable. Pengukuran
startup lokal sekitar 4 detik, sehingga target PRD ≤3 detik belum terpenuhi;
startup dapat berbeda menurut perangkat, pemindaian antivirus, dan cache.
Build mesin ini memakai Python 3.8 yang tersedia secara lokal; executable tetap
berjalan mandiri, tetapi bukan artefak release yang dibangun dengan Python 3.11.
`build.bat` menolak interpreter di bawah 3.11. Uji ulang target performa pada
mesin rilis sebelum distribusi.
