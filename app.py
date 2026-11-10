from flask import Flask, render_template, request, redirect, url_for, session
from db import get_db

app = Flask(__name__)
app.secret_key = "kunci_rahasia_perpustakaan"  # Untuk keamanan sesi login


# 1. Halaman Login (Satu halaman untuk Pustakawan & Peminjam)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        db.close()

        if user:
            # Simpan data user ke sesi
            session["user_id"] = user["id"]
            session["nama"] = user["nama"]
            session["role"] = user["role"]

            # Arahkan sesuai peran (role)
            if user["role"] == "pustakawan":
                return redirect(url_for("dashboard_pustakawan"))
            else:
                return redirect(url_for("katalog_buku"))
        else:
            return render_template("login.html", error="Username atau Password salah!")

    return render_template("login.html")


# 2. Halaman Katalog & Pinjam Buku (Khusus Peminjam)
@app.route("/katalog")
def katalog_buku():
    if "user_id" not in session or session["role"] != "peminjam":
        return redirect(url_for("login"))

    db = get_db()
    books = db.execute("SELECT * FROM books").fetchall()

    # Ambil riwayat pinjaman user yang sedang login
    loans = db.execute("""
        SELECT loans.id, books.judul, loans.tanggal_pinjam, loans.status 
        FROM loans 
        JOIN books ON loans.book_id = books.id 
        WHERE loans.user_id = ?
    """, (session["user_id"],)).fetchall()
    db.close()

    return render_template("catalog.html", books=books, loans=loans, nama=session["nama"])


# Proses Pinjam Buku
@app.route("/pinjam/<int:book_id>")
def pinjam_buku(book_id):
    if "user_id" not in session or session["role"] != "peminjam":
        return redirect(url_for("login"))

    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()

    if book and book["stok"] > 0:
        # Kurangi stok buku
        db.execute("UPDATE books SET stok = stok - 1 WHERE id = ?", (book_id,))
        # Catat peminjaman
        db.execute("INSERT INTO loans (user_id, book_id) VALUES (?, ?)", (session["user_id"], book_id))
        db.commit()

    db.close()
    return redirect(url_for("katalog_buku"))


# 3. Halaman Dashboard Pustakawan (Kelola Buku)
@app.route("/pustakawan", methods=["GET", "POST"])
def dashboard_pustakawan():
    if "user_id" not in session or session["role"] != "pustakawan":
        return redirect(url_for("login"))

    db = get_db()

    # Jika pustakawan menambah buku baru
    if request.method == "POST":
        judul = request.form["judul"]
        penulis = request.form["penulis"]
        stok = request.form["stok"]

        db.execute("INSERT INTO books (judul, penulis, stok) VALUES (?, ?, ?)", (judul, penulis, stok))
        db.commit()
        return redirect(url_for("dashboard_pustakawan"))

    books = db.execute("SELECT * FROM books").fetchall()

    # Lihat semua daftar yang meminjam buku
    all_loans = db.execute("""
        SELECT loans.id, users.nama AS peminjam, books.judul, loans.tanggal_pinjam, loans.status 
        FROM loans 
        JOIN users ON loans.user_id = users.id 
        JOIN books ON loans.book_id = books.id
    """).fetchall()

    db.close()

    return render_template("dashboard.html", books=books, loans=all_loans, nama=session["nama"])


# Proses Buku Dikembalikan
@app.route("/kembalikan/<int:loan_id>/<int:book_id>")
def kembalikan_buku(loan_id, book_id):
    if "user_id" not in session or session["role"] != "pustakawan":
        return redirect(url_for("login"))

    db = get_db()
    # Ubah status pinjam jadi dikembalikan
    db.execute("UPDATE loans SET status = 'dikembalikan' WHERE id = ?", (loan_id,))
    # Kembalikan stok buku +1
    db.execute("UPDATE books SET stok = stok + 1 WHERE id = ?", (book_id,))
    db.commit()
    db.close()

    return redirect(url_for("dashboard_pustakawan"))


# 4. Tombol Keluar (Logout)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)