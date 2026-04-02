# 🏡 Dompet Keluarga — Fauzan & Venska

> Aplikasi pencatatan keuangan keluarga berbasis web. Gratis selamanya, tanpa server, tanpa kartu kredit.

![status](https://img.shields.io/badge/status-production-4CAF82?style=flat-square)
![platform](https://img.shields.io/badge/platform-web%20%7C%20mobile-C8865C?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

---

## 🌐 Demo

---

## ✨ Fitur

- 💰 Catat pemasukan & pengeluaran harian
- 👨👩 Multi-user — Fauzan & Venska masing-masing bisa input
- ⚡ Input cepat gaya Telegram — `makan 35rb, bensin 100rb`
- 📊 Grafik pie per kategori (pengeluaran & pemasukan)
- 📈 Tren bar chart 6 bulan terakhir
- 📋 Riwayat lengkap — filter, search, hapus
- 🔄 Real-time sync — data tersimpan di Google Sheets
- 📱 Responsif — HP & laptop

---

## 🏗️ Arsitektur

```
Web (GitHub Pages)
       │
       │  GET request (JSONP)
       ▼
Google Apps Script (Web App)
       │
       │  Read / Write
       ▼
Google Sheets (Database)
```

| Komponen | Teknologi | Biaya |
|----------|-----------|-------|
| Frontend | HTML + CSS + Vanilla JS | Gratis (GitHub Pages) |
| Backend/API | Google Apps Script | Gratis |
| Database | Google Sheets | Gratis |
| Grafik | Chart.js v4 (CDN) | Gratis |
| Font | Google Fonts | Gratis |

---

## 📁 Struktur File

```
├── index.html       # Frontend lengkap (1 file)
└── Code.gs          # Backend API (Google Apps Script)
```

---

## 🔬 Bedah Kode

### `Code.gs` — Backend API

#### Konfigurasi
```javascript
const SPREADSHEET_ID = "...";       // ID Google Sheet
const SHEET_TX       = "transaksi"; // Nama tab sheet
```

#### Entry Point — `doGet(e)`
Semua request masuk lewat satu fungsi ini. Parameter `action` menentukan operasi:

| `action` | Fungsi | Parameter tambahan |
|----------|--------|--------------------|
| `ping` | Health check | — |
| `get_transactions` | Ambil data transaksi | `month`, `nama` |
| `get_summary` | Ringkasan keuangan | `month` |
| `add_transaction` | Tambah transaksi | `nama`, `keterangan`, `kategori`, `jumlah`, `tanggal`, `tipe` |
| `delete_transaction` | Hapus transaksi | `id` |
| `debug_dates` | Debug format tanggal | — |

#### JSONP Support
Apps Script tidak mendukung CORS untuk request dari domain lain. Solusinya **JSONP** — response dibungkus nama fungsi callback:
```
GET /exec?action=ping&callback=myFunc
→ myFunc({"status":"ok"})
```

#### Konversi Tanggal — `tglToStr(tgl)`
Google Sheets menyimpan tanggal sebagai **Date object**, bukan string. Fungsi ini mengkonversi semua format ke `yyyy-MM-dd`:
```javascript
tglToStr(new Date("2026-03-31"))  // → "2026-03-31"
tglToStr(45931)                   // → "2026-03-31" (serial Excel)
tglToStr("2026-03-31")            // → "2026-03-31" (sudah string)
```

#### Struktur Tabel Google Sheets
Tab `transaksi`:

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| id | Integer | Auto-increment |
| nama | String | "Fauzan" atau "Venska" |
| keterangan | String | Deskripsi transaksi |
| kategori | String | Makanan, Transportasi, dll |
| jumlah | Integer | Nominal dalam Rupiah |
| tanggal | Date | Format yyyy-MM-dd |
| tipe | String | "pengeluaran" atau "pemasukan" |

---

### `index.html` — Frontend

#### Konfigurasi
```javascript
const API_URL = "https://script.google.com/macros/s/.../exec";
```

#### Kategori
**Pengeluaran (8 kategori):**
Makanan 🍔 · Transportasi 🚗 · Rumah 🏠 · Si Kecil 👶 · Kesehatan 💊 · Pakaian 👕 · Elektronik 📱 · Lain-lain 📦

**Pemasukan (5 kategori):**
Gaji 💼 · Freelance 💻 · Hadiah/THR 🎁 · Investasi 📈 · Lainnya ✨

#### Auto-deteksi Kategori — `autoKategori(ket)`
Mendeteksi kategori otomatis dari kata kunci di keterangan:
```
"bensin 100rb"     → Transportasi
"makan siang 35rb" → Makanan
"shafiyyah 50rb"   → Anak
"listrik 200rb"    → Rumah
```

#### Parser Input Cepat
Tiga fungsi bekerja bersama untuk mengurai teks bebas:

```
parseAngka("35rb")   → 35000
parseAngka("1.5jt")  → 1500000
parseAngka("35000")  → 35000

parseSatu("makan 35rb")
→ { keterangan: "Makan", jumlah: 35000 }

parseMulti("makan 35rb, bensin 100rb, parkir 5000")
→ [
    { keterangan: "Makan",   jumlah: 35000  },
    { keterangan: "Bensin",  jumlah: 100000 },
    { keterangan: "Parkir",  jumlah: 5000   }
  ]
```

Format angka yang didukung: `35rb` · `1.5jt` · `500ribu` · `35000` · `35,000`
Pemisah multi-transaksi: koma `,` · titik koma `;` · enter · kata `dan`

#### JSONP Client — `jsonp(params)`
Membuat script tag dinamis dengan callback unik per request:
```javascript
// Setiap request punya callback name unik: _cb1234abc
window['_cb1234abc'] = (data) => resolve(data);
// <script src="API_URL?action=...&callback=_cb1234abc">
// Timeout 15 detik otomatis untuk mencegah hang
```

#### State Management
State disimpan sebagai variabel global:
```javascript
let selMonth  // Bulan aktif di header, format "yyyy-MM"
let allTx     // Cache transaksi bulan ini (array)
let curNama   // "Fauzan" atau "Venska"
let curType   // "pengeluaran" atau "pemasukan"
let curCatId  // ID kategori yang dipilih
```

#### Alur Data Simpan Transaksi
```
User klik Simpan
  → saveTx()
    → apiAdd() = jsonp({action:'add_transaction', ...})
      → Apps Script addTransaction()
        → sheet.appendRow([...])
      ← return {success: true, id: 38}
    ← resolve
  → loadTx()  // refresh dari Sheets
  → renderHome()  // update UI
```

---

## 🚀 Setup dari Nol

### 1. Google Sheets
1. Buka [sheets.google.com](https://sheets.google.com) → buat spreadsheet baru
2. Rename tab pertama menjadi `transaksi`
3. Copy **ID** dari URL: `docs.google.com/spreadsheets/d/**ID_INI**/edit`

### 2. Google Apps Script
1. Buka [script.google.com](https://script.google.com) → New Project
2. Paste isi `Code.gs` → isi `SPREADSHEET_ID`
3. **Deploy → New Deployment:**
   - Type: **Web App**
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Copy URL deployment (format: `https://script.google.com/macros/s/.../exec`)

### 3. GitHub Pages
1. Upload `index.html` ke repo GitHub
2. Ganti `API_URL` di baris pertama script dengan URL Apps Script
3. Settings → Pages → Deploy from branch `main`
4. Akses via `https://username.github.io/nama-repo/`

---

## 📲 Cara Penggunaan

### Input Manual
1. Buka tab **➕ Tambah**
2. Pilih nama (Fauzan / Venska)
3. Pilih tipe (Pengeluaran / Pemasukan)
4. Isi jumlah, kategori, keterangan, tanggal
5. Klik **💾 Simpan**

### Input Cepat ⚡
```
makan siang 35rb, bensin 100rb
ganti oli 75rb dan parkir 5000
listrik 200000
gaji masuk 6500000
```
Klik **🔍 Analisa** → preview → **✅ Simpan Semua**

### Navigasi Bulan
Gunakan tombol **‹** dan **›** di header untuk pindah bulan.

---

## 🔮 Rencana Pengembangan

- [ ] Edit transaksi (fitur update)
- [ ] Export ke Excel / CSV
- [ ] Budget bulanan per kategori
- [ ] Rekap tahunan (12 bulan)
- [ ] Dark mode
- [ ] PWA (bisa diinstall di HP)

---

## 🛠️ Teknologi

| Library | Versi | Kegunaan |
|---------|-------|---------|
| Chart.js | 4.4.0 | Grafik pie & bar |
| Google Fonts | — | Playfair Display + Plus Jakarta Sans |
| Google Apps Script | — | Backend API |
| Google Sheets | — | Database |

---

## 📄 Lisensi

MIT — bebas dipakai dan dimodifikasi.

---

*Dibuat dengan ❤️ untuk keluarga kecil Fauzan & Venska, dan dua malaikat kecil Shafiyyah & Athiyyah 🍼*
