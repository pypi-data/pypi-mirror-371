from .utils import log_error

# =========================
# julimath (fleksibel & auto-print)
# =========================

# --- Helper input ---
def need(pesan="Masukkan angka: "):
    try:
        return int(input(pesan))
    except ValueError:
        print("❌ Input harus berupa bilangan bulat.")
        return need(pesan)

def need_float(pesan="Masukkan angka (desimal boleh): "):
    try:
        return float(input(pesan))
    except ValueError:
        print("❌ Input harus berupa angka desimal.")
        return need_float(pesan)


# --- Wrapper agar auto-print ---
def _auto_print(func):
    def wrapper(*args, **kwargs):
        # Kalau argumen kosong & fungsi punya parameter -> minta input otomatis
        from inspect import signature
        sig = signature(func)
        params = list(sig.parameters.keys())

        new_args = list(args)
        for i in range(len(new_args), len(params)):
            new_args.append(need(f"Masukkan {params[i]}: "))

        result = func(*new_args, **kwargs)
        if result is not None:
            print(result)
        return result
    return wrapper


# =========================
# OPERASI DASAR
# =========================
@_auto_print
def tambah(a, b): return a + b

@_auto_print
def kurang(a, b): return a - b

@_auto_print
def kali(a, b): return a * b

@_auto_print
def bagi(a, b):
    if b == 0:
        log_error("bagi", "Pembagian dengan nol tidak diperbolehkan.")
        return None
    return a / b

# --- Shortcut alias ---
add = tambah
sub = kurang
mul = kali
div = bagi


# =========================
# OPERASI LANJUT
# =========================
@_auto_print
def pangkat(a, b):
    hasil = 1
    for _ in range(b):
        hasil *= a
    return hasil

@_auto_print
def akar(x):
    if x < 0: return None
    guess = x / 2 if x != 0 else 0
    for _ in range(20):
        guess = (guess + x / guess) / 2 if guess != 0 else 0
    return round(guess, 10)

@_auto_print
def modulus(a, b):
    return a - (a // b) * b

@_auto_print
def faktorial(n):
    if n < 0: return None
    hasil = 1
    for i in range(1, n + 1):
        hasil *= i
    return hasil

@_auto_print
def luas_lingkaran(r):
    phi = 3.14
    return round(phi * (r * r), 2)

@_auto_print
def volume_tabung(r, t):
    phi = 3.14
    return round(phi * (r * r) * t, 2)

@_auto_print
def persen(bagian, total):
    return round((bagian / total) * 100, 2)

@_auto_print
def rata_rata(data):
    if not data: return None
    return sum(data) / len(data)

@_auto_print
def fpb(a, b):
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a

@_auto_print
def kpk(a, b):
    if a == 0 or b == 0: return 0
    return abs(a * b) // fpb(a, b)

@_auto_print
def kuadrat(x): return x * x

@_auto_print
def kubik(x): return x * x * x

@_auto_print
def kombinasi(n, r):
    if r < 0 or r > n: return 0
    return faktorial(n) // (faktorial(r) * faktorial(n - r))

@_auto_print
def permutasi(n, r):
    if r < 0 or r > n: return 0
    return faktorial(n) // faktorial(n - r)

@_auto_print
def keliling_persegi(sisi=None, show_formula: bool = False):
    if sisi is None:
        sisi = need("Masukkan panjang sisi: ")
    result = 4 * sisi
    if show_formula:
        print(f"Rumus: 4 * {sisi} = {result}")
    return result

@_auto_print
def luas_persegi(sisi=None, show_formula: bool = False):
    if sisi is None:
        sisi = need("Masukkan panjang sisi: ")
    result = sisi * sisi
    if show_formula:
        print(f"Rumus: {sisi} * {sisi} = {result}")
    return result
