import sqlite3

def get_db():
    # Membuka/menghubungkan ke file database
    conn = sqlite3.connect("perpustakaan.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Tabel untuk menyimpan akun (Pustakawan & Peminjam)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,          -- "pustakawan" atau "peminjam"
            nama TEXT
        )
    ''')

    # 2. Tabel untuk menyimpan daftar buku
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT,
            penulis TEXT,
            stok INTEGER
        )
    ''')

    # 3. Tabel untuk me-rekam transaksi peminjaman
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_id INTEGER,
            tanggal_pinjam DATE DEFAULT CURRENT_DATE,
            status TEXT DEFAULT 'dipinjam' -- "dipinjam" atau "dikembalikan"
        )
    ''')

    # Isi data awal otomatis jika database masih kosong
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Akun contoh:
        # Pustakawan -> username: admin , password: 123
        # Peminjam   -> username: peminjam , password: 123
        cursor.execute("INSERT INTO users (username, password, role, nama) VALUES ('admin', '123', 'pustakawan', 'Pak Pustakawan')")
        cursor.execute("INSERT INTO users (username, password, role, nama) VALUES ('peminjam', '123', 'peminjam', 'Budi Peminjam')")

        # Buku contoh:
        cursor.execute("INSERT INTO books (judul, penulis, stok) VALUES ('Laskar Pelangi', 'Andrea Hirata', 3)")
        cursor.execute("INSERT INTO books (judul, penulis, stok) VALUES ('Filosofi Teras', 'Henry Manampiring', 2)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database berhasil dibuat!")