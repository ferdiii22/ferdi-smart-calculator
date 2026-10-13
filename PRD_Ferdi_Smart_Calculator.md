# PRD — Ferdi Smart Calculator

| Item | Detail |
|---|---|
| **Nama Produk** | Ferdi Smart Calculator |
| **Versi Dokumen** | 1.0 |
| **Platform** | Windows 10 / 11 (64-bit) |
| **Bahasa Pemrograman** | Python 3.11+ |
| **Distribusi** | Portable `.exe` tunggal (tanpa instalasi) |
| **Pemilik Produk** | Ferdi |
| **Status** | Draft untuk pengembangan MVP |

---

## 1. Ringkasan Produk

**Ferdi Smart Calculator** adalah aplikasi kalkulator desktop bergaya minimalis yang tidak hanya menghitung, tetapi juga *cerdas*: menampilkan pratinjau hasil secara langsung (*live preview*), memahami ekspresi matematika lengkap, menyimpan riwayat, dan menyediakan konverter satuan. Aplikasi dikemas menjadi satu file `.exe` portabel yang bisa dijalankan dari flashdisk atau folder mana pun tanpa instalasi.

### 1.1 Latar Belakang
Kalkulator bawaan Windows sudah fungsional, tetapi sering terasa berat dan penuh fitur yang jarang dipakai. Proyek ini bertujuan membuat alternatif yang ringan, cepat, bersih secara visual, sekaligus menjadi **media belajar** pembuatan aplikasi desktop dengan Python.

### 1.2 Tujuan
1. Membuat kalkulator yang ringan, cepat, dan nyaman dipakai.
2. Menyediakan UI minimalis modern dengan mode gelap dan terang.
3. Menghasilkan satu file `.exe` portabel (tanpa installer, tanpa dependensi eksternal).
4. Menjadi proyek pembelajaran dengan struktur kode yang rapi dan mudah dikembangkan.

### 1.3 Di Luar Cakupan (Non-Goals) untuk v1.0
- Grafik fungsi 2D/3D
- Sinkronisasi cloud
- Aplikasi mobile / macOS / Linux
- Penyelesaian persamaan simbolik (aljabar CAS)

---

## 2. Target Pengguna

| Persona | Kebutuhan | Fitur Kunci |
|---|---|---|
| **Pelajar / Mahasiswa** | Hitungan cepat, fungsi ilmiah | Mode ilmiah, riwayat |
| **Pekerja kantoran** | Persentase, pajak, diskon | Mode standar, salin hasil |
| **Pemula Python (pembuat)** | Belajar GUI desktop | Kode modular, dokumentasi jelas |

---

## 3. Kebutuhan Fungsional

### 3.1 Prioritas MoSCoW

| ID | Fitur | Prioritas |
|---|---|---|
| F-01 | Operasi dasar: `+ − × ÷`, persen, +/−, desimal | **Must** |
| F-02 | Input ekspresi dengan tanda kurung, contoh `(12+8)×3/4` | **Must** |
| F-03 | **Live preview**: hasil tampil otomatis saat mengetik | **Must** |
| F-04 | Dukungan keyboard penuh (angka, operator, Enter, Backspace, Esc) | **Must** |
| F-05 | Riwayat perhitungan (klik untuk memakai ulang) | **Must** |
| F-06 | Mode gelap / terang | **Must** |
| F-07 | Penanganan error ramah (bagi nol, sintaks salah) | **Must** |
| F-08 | Mode ilmiah: `sin cos tan log ln √ x² xʸ π e n!` | **Should** |
| F-09 | Memori: `MC MR M+ M−` | **Should** |
| F-10 | Salin hasil ke clipboard (klik hasil atau `Ctrl+C`) | **Should** |
| F-11 | Konverter satuan: panjang, berat, suhu, data | **Should** |
| F-12 | Pemisah ribuan otomatis (contoh `1.250.000`) | **Should** |
| F-13 | Selalu di atas (*Always on top*) | **Could** |
| F-14 | Kalkulator tanggal (selisih hari) | **Could** |
| F-15 | Mode Programmer (BIN/HEX/DEC) | **Could** |

### 3.2 Aturan Fitur "Smart"
- **Live preview:** setiap perubahan input memicu evaluasi diam-diam; jika ekspresi valid, hasil tampil abu-abu di bawah input. Jika belum valid, preview dikosongkan (tanpa pesan error mengganggu).
- **Auto-close kurung:** kurung yang belum tertutup ditutup otomatis saat evaluasi.
- **Persen kontekstual:** `200 + 10%` dihitung sebagai `200 + (200 × 10%) = 220`.
- **Operator ganda:** mengetik `+` lalu `×` akan mengganti operator terakhir, bukan menumpuk.
- **Presisi:** memakai `decimal` untuk mode standar agar `0,1 + 0,2 = 0,3` (bukan `0.30000000000000004`).

---

## 4. Kebutuhan Non-Fungsional

| Aspek | Target |
|---|---|
| **Performa** | Startup `.exe` ≤ 3 detik; respons tombol ≤ 50 ms |
| **Ukuran file** | ≤ 40 MB (satu file `.exe`) |
| **Portabel** | Tidak menulis ke Registry; data (pengaturan & riwayat) disimpan di folder `data/` di samping `.exe` |
| **Keamanan** | Evaluasi ekspresi memakai parser AST aman, **dilarang** `eval()` mentah |
| **Responsif** | Ukuran minimal 320×480 px; layout menyesuaikan saat jendela di-resize |
| **Aksesibilitas** | Kontras warna ≥ 4.5:1, ukuran tombol minimal 48×48 px, navigasi penuh via keyboard |
| **Kompatibilitas** | Windows 10/11 64-bit, mendukung DPI scaling 100%–200% |
| **Bahasa UI** | Bahasa Indonesia (default), dapat diperluas ke Inggris |

---

## 5. Desain UI / UX

### 5.1 Prinsip Desain
1. **Minimalis** — hanya elemen penting yang tampak; ruang kosong dipakai sebagai pemisah.
2. **Fokus pada angka** — layar hasil besar dan kontras tinggi.
3. **Konsisten** — satu radius sudut, satu keluarga font, satu aksen warna.
4. **Responsif** — tombol dan teks ikut menyesuaikan ukuran jendela.

### 5.2 Palet Warna

**Mode Gelap (default)**

| Token | Hex | Penggunaan |
|---|---|---|
| `bg` | `#121417` | Latar jendela |
| `surface` | `#1C1F24` | Layar & panel |
| `key` | `#262A31` | Tombol angka |
| `key-op` | `#323844` | Tombol operator |
| `accent` | `#4F8CFF` | Tombol `=`, fokus, highlight |
| `text` | `#F2F4F8` | Teks utama |
| `text-muted` | `#8A93A3` | Preview, label |
| `danger` | `#FF6B6B` | Pesan error |

**Mode Terang**

| Token | Hex |
|---|---|
| `bg` | `#F4F6FA` |
| `surface` | `#FFFFFF` |
| `key` | `#EDEFF4` |
| `key-op` | `#DDE2EC` |
| `accent` | `#2F6BFF` |
| `text` | `#14171C` |
| `text-muted` | `#6B7485` |
| `danger` | `#D64545` |

### 5.3 Tipografi
| Elemen | Font | Ukuran |
|---|---|---|
| Hasil utama | Segoe UI Semibold | 40 pt (mengecil otomatis jika angka panjang) |
| Ekspresi / preview | Segoe UI | 16 pt |
| Tombol | Segoe UI | 18 pt |
| Label kecil | Segoe UI | 11 pt |

### 5.4 Wireframe — Mode Standar (360 × 600 px)

```
┌──────────────────────────────────────┐
│  ☰   Ferdi Smart Calculator    ◐  ⌂  │  ← header: menu, judul, tema
├──────────────────────────────────────┤
│                                      │
│                    (12 + 8) × 3 ÷ 4  │  ← ekspresi (abu-abu)
│                                  15  │  ← hasil besar
│                                      │
├──────────────────────────────────────┤
│  MC    MR    M+    M−     ⏱ Riwayat  │  ← baris memori
├──────────────────────────────────────┤
│  ┌──────┬──────┬──────┬──────┐       │
│  │  AC  │  ⌫   │  %   │  ÷   │       │
│  ├──────┼──────┼──────┼──────┤       │
│  │  7   │  8   │  9   │  ×   │       │
│  ├──────┼──────┼──────┼──────┤       │
│  │  4   │  5   │  6   │  −   │       │
│  ├──────┼──────┼──────┼──────┤       │
│  │  1   │  2   │  3   │  +   │       │
│  ├──────┼──────┼──────┼──────┤       │
│  │  ±   │  0   │  ,   │  =   │       │
│  └──────┴──────┴──────┴──────┘       │
└──────────────────────────────────────┘
```

### 5.5 Wireframe — Mode Ilmiah (lebar ≥ 720 px)

```
┌─────────────────────────────────────────────────────────┐
│  ☰   Ferdi Smart Calculator  [Standar|Ilmiah|Konversi] ◐│
├───────────────────────────────┬─────────────────────────┤
│                  sin(30) + √16│  RIWAYAT                │
│                           4,5 │  ───────────────────    │
├───────────────────────────────┤  (12+8)×3÷4  =  15      │
│  2nd   π    e    (    )   AC  │  sin(30)+√16 =  4,5     │
│  sin  cos  tan  x²   √    ÷   │  200+10%     =  220     │
│  log   ln   7    8    9   ×   │                         │
│  xʸ    n!   4    5    6   −   │  [ Hapus Riwayat ]      │
│  1/x   |x|  1    2    3   +   │                         │
│  Rad   ±    0    ,    =       │                         │
└───────────────────────────────┴─────────────────────────┘
```

### 5.6 Wireframe — Konverter Satuan

```
┌──────────────────────────────────────┐
│  ←   Konverter                    ◐  │
├──────────────────────────────────────┤
│  Kategori:  [ Panjang           ▾ ]  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │ 1.000                  Meter ▾ │  │
│  └────────────────────────────────┘  │
│               ⇅  tukar               │
│  ┌────────────────────────────────┐  │
│  │ 1                  Kilometer ▾ │  │
│  └────────────────────────────────┘  │
│                                      │
│  [ 7 8 9 ]  [ 4 5 6 ]  [ 1 2 3 ]    │
│  [ C 0 , ]                           │
└──────────────────────────────────────┘
```

### 5.7 Perilaku Responsif

| Lebar Jendela | Layout |
|---|---|
| **< 400 px** | Satu kolom, mode standar, riwayat berupa panel geser (*drawer*) |
| **400 – 719 px** | Satu kolom, tombol membesar proporsional |
| **≥ 720 px** | Dua kolom: keypad di kiri, panel riwayat permanen di kanan |

Aturan teknis: tombol memakai `grid` dengan `weight` yang sama sehingga membesar rata; ukuran font hasil dihitung ulang tiap event `<Configure>`.

### 5.8 Micro-Interaction
- **Hover** tombol: warna naik satu tingkat (150 ms).
- **Klik** tombol: efek tekan singkat (skala 0.96).
- **Fokus keyboard:** cincin tipis warna `accent`.
- **Hasil berubah:** transisi *fade* singkat, bukan loncat.
- **Error:** hasil bergetar kecil + teks merah, hilang saat input berikutnya.

### 5.9 Pintasan Keyboard

| Tombol | Aksi |
|---|---|
| `0–9`, `.` / `,` | Input angka |
| `+ - * /` | Operator |
| `Enter` / `=` | Hitung |
| `Backspace` | Hapus satu karakter |
| `Esc` | Hapus semua (AC) |
| `Ctrl+C` | Salin hasil |
| `Ctrl+H` | Buka/tutup riwayat |
| `Ctrl+T` | Ganti tema |
| `Ctrl+1/2/3` | Pindah mode Standar / Ilmiah / Konversi |

---

## 6. Alur Pengguna (User Flow)

```
Buka .exe ──► Layar Kalkulator (Mode terakhir)
                │
                ├─► Ketik angka/ekspresi ──► Preview live ──► Enter ──► Hasil + simpan riwayat
                │
                ├─► Klik riwayat ──► Ekspresi dimuat kembali ke input
                │
                ├─► Ganti mode ──► Standar / Ilmiah / Konverter
                │
                └─► Ganti tema ──► Tersimpan otomatis di data/settings.json
```

---

## 7. Arsitektur Teknis

### 7.1 Pilihan Teknologi

| Komponen | Pilihan | Alasan |
|---|---|---|
| GUI | **CustomTkinter** | Tampilan modern, ringan, mudah dipelajari pemula, tema gelap/terang bawaan |
| Parser ekspresi | Modul `ast` Python (whitelist node) | Aman, tanpa `eval()` mentah |
| Presisi desimal | `decimal` | Menghindari galat floating point |
| Penyimpanan | JSON lokal | Sederhana dan portabel |
| Packaging | **PyInstaller** (`--onefile --windowed`) | Menghasilkan satu `.exe` portabel |

> **Alternatif:** PySide6 (Qt) memberi tampilan lebih profesional, namun ukuran `.exe` lebih besar (±80 MB) dan kurva belajar lebih curam.

### 7.2 Struktur Proyek

```
ferdi-smart-calculator/
├── main.py                  # Titik masuk aplikasi
├── requirements.txt
├── build.bat                # Skrip build .exe
├── assets/
│   └── icon.ico
├── app/
│   ├── __init__.py
│   ├── config.py            # Konstanta, path portabel
│   ├── theme.py             # Token warna & font (gelap/terang)
│   ├── engine/
│   │   ├── evaluator.py     # Parser AST aman + fungsi ilmiah
│   │   ├── formatter.py     # Pemisah ribuan, pembulatan
│   │   └── converter.py     # Logika konversi satuan
│   ├── storage/
│   │   └── store.py         # Baca/tulis settings & riwayat JSON
│   └── ui/
│       ├── main_window.py   # Jendela utama + layout responsif
│       ├── display.py       # Layar ekspresi & hasil
│       ├── keypad.py        # Grid tombol
│       ├── history_panel.py # Panel riwayat
│       └── converter_view.py
└── tests/
    └── test_evaluator.py
```

### 7.3 Path Portabel (Penting!)
Saat berjalan sebagai `.exe` PyInstaller, lokasi data harus berada di samping file `.exe`, bukan di folder temporer:

```python
# app/config.py
import sys
from pathlib import Path

def base_dir() -> Path:
    if getattr(sys, "frozen", False):          # berjalan sebagai .exe
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

def resource_path(rel: str) -> Path:           # untuk aset yang dibundel (ikon, dll.)
    root = Path(getattr(sys, "_MEIPASS", base_dir()))
    return root / rel

DATA_DIR = base_dir() / "data"
DATA_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = DATA_DIR / "settings.json"
HISTORY_FILE = DATA_DIR / "history.json"
```

### 7.4 Contoh Evaluator Aman

```python
# app/engine/evaluator.py
import ast, math, operator as op

_BIN = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod}
_UNARY = {ast.UAdd: op.pos, ast.USub: op.neg}
_FUNC = {"sin": lambda x: math.sin(math.radians(x)),
         "cos": lambda x: math.cos(math.radians(x)),
         "tan": lambda x: math.tan(math.radians(x)),
         "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
         "fact": math.factorial}
_CONST = {"pi": math.pi, "e": math.e}

def evaluate(expr: str) -> float:
    expr = (expr.replace("×", "*").replace("÷", "/")
                .replace("−", "-").replace("^", "**").replace(",", "."))
    return _eval(ast.parse(expr, mode="eval").body)

def _eval(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
        return n.value
    if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
        return _BIN[type(n.op)](_eval(n.left), _eval(n.right))
    if isinstance(n, ast.UnaryOp) and type(n.op) in _UNARY:
        return _UNARY[type(n.op)](_eval(n.operand))
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNC:
        return _FUNC[n.func.id](*[_eval(a) for a in n.args])
    if isinstance(n, ast.Name) and n.id in _CONST:
        return _CONST[n.id]
    raise ValueError("Ekspresi tidak valid")
```

### 7.5 Format Data Tersimpan

```json
// data/settings.json
{ "theme": "dark", "mode": "standard", "always_on_top": false,
  "window": { "width": 360, "height": 600 } }

// data/history.json
[ { "expr": "(12+8)×3÷4", "result": "15", "time": "2026-10-13T09:30:00" } ]
```

---

## 8. Build & Distribusi `.exe` Portabel

### 8.1 Persiapan
```bash
python -m venv venv
venv\Scripts\activate
pip install customtkinter pyinstaller
```

### 8.2 Perintah Build
```bash
pyinstaller --noconfirm --onefile --windowed ^
  --name "Ferdi Smart Calculator" ^
  --icon assets\icon.ico ^
  --add-data "assets;assets" ^
  --collect-all customtkinter ^
  main.py
```

Hasil: `dist\Ferdi Smart Calculator.exe`

### 8.3 Tips Penting
- Gunakan `--collect-all customtkinter` agar tema & aset CustomTkinter ikut terbundel.
- Jika terdeteksi antivirus (false positive), build ulang tanpa UPX atau tandatangani kode (*code signing*).
- Untuk start-up lebih cepat, pertimbangkan `--onedir` lalu zip foldernya (tetap portabel).
- Uji `.exe` di komputer lain yang **tidak** terpasang Python.
- Aktifkan DPI awareness agar tampilan tajam di layar resolusi tinggi:
  ```python
  import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(1)
  ```

---

## 9. Rencana Pengujian

| Kategori | Kasus Uji | Hasil yang Diharapkan |
|---|---|---|
| Aritmetika | `0,1 + 0,2` | `0,3` |
| Prioritas operator | `2 + 3 × 4` | `14` |
| Kurung | `(2+3)×4` | `20` |
| Persen | `200 + 10%` | `220` |
| Bagi nol | `5 ÷ 0` | Pesan "Tidak bisa dibagi nol" |
| Sintaks salah | `5 ++ × 2` | Preview kosong, tanpa crash |
| Ilmiah | `sin(30)` | `0,5` |
| Angka besar | `99999999 × 99999999` | Format ilmiah / ringkas |
| Keamanan | `__import__('os')` | Ditolak oleh parser |
| Portabel | Jalankan dari flashdisk | Data tersimpan di `data/` samping `.exe` |
| Responsif | Resize 320 → 1000 px | Layout berpindah tanpa tumpang tindih |

Gunakan `pytest` untuk unit test pada `evaluator.py` dan `converter.py`.

---

## 10. Roadmap & Milestone

| Fase | Cakupan | Estimasi |
|---|---|---|
| **M1 — Fondasi** | Struktur proyek, evaluator aman, unit test | Minggu 1 |
| **M2 — UI Standar** | Layout, keypad, display, tema gelap/terang, keyboard | Minggu 2 |
| **M3 — Fitur Smart** | Live preview, riwayat, memori, salin hasil | Minggu 3 |
| **M4 — Ilmiah & Konverter** | Mode ilmiah, konverter satuan, layout responsif | Minggu 4 |
| **M5 — Rilis** | Build `.exe`, uji di PC lain, dokumentasi | Minggu 5 |

---

## 11. Kriteria Keberhasilan (Definition of Done)

- [ ] Semua fitur **Must** berfungsi tanpa crash.
- [ ] `.exe` berjalan di Windows 10/11 tanpa Python terpasang.
- [ ] Startup ≤ 3 detik, ukuran ≤ 40 MB.
- [ ] Pengaturan & riwayat tersimpan di folder `data/` samping `.exe`.
- [ ] UI tetap rapi dari lebar 320 px hingga layar penuh.
- [ ] Unit test evaluator lulus 100%.

---

## 12. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| `.exe` ditandai antivirus | Pengguna ragu menjalankan | Build bersih tanpa UPX, sertakan hash SHA-256 |
| Ukuran `.exe` membengkak | Distribusi lambat | Virtualenv bersih, hanya instal dependensi wajib |
| Tampilan kabur di DPI tinggi | UX buruk | Aktifkan DPI awareness + uji skala 150%/200% |
| Galat floating point | Hasil membingungkan | Gunakan `decimal` & pembulatan tampilan |
| Injeksi ekspresi | Celah keamanan | Parser AST whitelist, tanpa `eval()` |

---

## 13. Rencana Pengembangan Lanjutan (v2.0)

- Mode Programmer (BIN / OCT / HEX)
- Konverter mata uang (kurs offline yang bisa diperbarui manual)
- Kalkulator tanggal & diskon/pajak (PPN 11%)
- Pilihan bahasa Indonesia / Inggris
- Ekspor riwayat ke CSV
- Tema kustom warna aksen

---

*Dokumen ini adalah PRD awal untuk **Ferdi Smart Calculator**. Dapat direvisi seiring perkembangan proyek.*
