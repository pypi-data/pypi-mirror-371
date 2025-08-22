import logging

# --- Warna untuk log ---
COLORS = {
    "INFO": "\033[92m",   # Hijau
    "ERROR": "\033[91m",  # Merah
    "RESET": "\033[0m",   # Reset warna
}

class FriendlyFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        msg = super().format(record)
        if levelname in COLORS:
            msg = f"{COLORS[levelname]}{msg}{COLORS['RESET']}"
        return msg

# --- Logger Setup ---
logger = logging.getLogger("julimath")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = FriendlyFormatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def log_error(func_name, error):
    logger.error(f"Terjadi error di fungsi '{func_name}': {error}")

def log_info(message):
    logger.info(message)

# --- Help Menu ---
def jm_help():
    msg = """
📘 === JULIMATH HELP MENU ===

Fungsi Utama:
- jm.tambah(a, b)  | alias: jm.add(a, b)
- jm.kurang(a, b)  | alias: jm.sub(a, b)
- jm.kali(a, b)    | alias: jm.mul(a, b)
- jm.bagi(a, b)    | alias: jm.div(a, b)

Fungsi Lanjutan:
- jm.pangkat(a, b), jm.akar(x), jm.modulus(a, b)
- jm.faktorial(n), jm.luas_lingkaran(r), jm.volume_tabung(r, t)
- jm.persen(bagian, total), jm.rata_rata([data])
- jm.fpb(a, b), jm.kpk(a, b)
- jm.kuadrat(x), jm.kubik(x)
- jm.kombinasi(n, r), jm.permutasi(n, r)
- jm.keliling_persegi(sisi), jm.luas_persegi(sisi)

Tips:
- Semua fungsi bisa otomatis input jika argumen kosong.
- Shortcut: add, sub, mul, div.
"""
    print(msg)
