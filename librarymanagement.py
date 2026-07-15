import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta

# Database setup
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# Books table
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    status TEXT DEFAULT 'Available',
    issued_to INTEGER,
    return_date TEXT,
    FOREIGN KEY (issued_to) REFERENCES students(id)
)
""")

# Students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    fine REAL DEFAULT 0
)
""")
conn.commit()

# Functions
def add_book():
    title = entry_title.get()
    author = entry_author.get()
    if title and author:
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        conn.commit()
        messagebox.showinfo("Success", "Book added successfully!")
        entry_title.delete(0, tk.END)
        entry_author.delete(0, tk.END)
        view_books()
    else:
        messagebox.showwarning("Input Error", "Please enter both title and author.")

def remove_book():
    try:
        selected = listbox_books.get(listbox_books.curselection())
        book_id = selected.split("|")[0].split(":")[1].strip()
        cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        messagebox.showinfo("Success", "Book removed successfully!")
        view_books()
    except:
        messagebox.showwarning("Selection Error", "Please select a book to remove.")

def update_book():
    try:
        selected = listbox_books.get(listbox_books.curselection())
        book_id = selected.split("|")[0].split(":")[1].strip()
        new_title = entry_title.get()
        new_author = entry_author.get()
        if new_title and new_author:
            cursor.execute("UPDATE books SET title=?, author=? WHERE id=?", (new_title, new_author, book_id))
            conn.commit()
            messagebox.showinfo("Success", "Book updated successfully!")
            view_books()
        else:
            messagebox.showwarning("Input Error", "Enter new title and author.")
    except:
        messagebox.showwarning("Selection Error", "Please select a book to update.")

def add_student():
    name = entry_student.get()
    if name:
        cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        messagebox.showinfo("Success", "Student added successfully!")
        entry_student.delete(0, tk.END)
        view_students()
    else:
        messagebox.showwarning("Input Error", "Please enter student name.")

def view_books():
    listbox_books.delete(0, tk.END)
    cursor.execute("SELECT b.id, b.title, b.author, b.status, s.name, b.return_date FROM books b LEFT JOIN students s ON b.issued_to=s.id")
    for row in cursor.fetchall():
        issued_info = f" | Issued to: {row[4]} | Return by: {row[5]}" if row[4] else ""
        listbox_books.insert(tk.END, f"ID:{row[0]} | {row[1]} by {row[2]} | {row[3]}{issued_info}")

def view_students():
    listbox_students.delete(0, tk.END)
    cursor.execute("SELECT * FROM students")
    for row in cursor.fetchall():
        listbox_students.insert(tk.END, f"ID:{row[0]} | {row[1]} | Fine: ₹{row[2]}")

def issue_book():
    try:
        selected_book = listbox_books.get(listbox_books.curselection())
        book_id = selected_book.split("|")[0].split(":")[1].strip()
        selected_student = listbox_students.get(listbox_students.curselection())
        student_id = selected_student.split("|")[0].split(":")[1].strip()
        return_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute("UPDATE books SET status='Issued', issued_to=?, return_date=? WHERE id=?", (student_id, return_date, book_id))
        conn.commit()
        messagebox.showinfo("Success", f"Book issued until {return_date}")
        view_books()
    except:
        messagebox.showwarning("Selection Error", "Select both a book and a student.")

def return_book():
    try:
        selected_book = listbox_books.get(listbox_books.curselection())
        book_id = selected_book.split("|")[0].split(":")[1].strip()
        cursor.execute("SELECT issued_to, return_date FROM books WHERE id=?", (book_id,))
        issued_to, return_date = cursor.fetchone()
        if issued_to:
            due_date = datetime.strptime(return_date, "%Y-%m-%d")
            if datetime.now() > due_date:
                days_late = (datetime.now() - due_date).days
                fine = days_late * 10  # ₹10 per day late
                cursor.execute("UPDATE students SET fine=fine+? WHERE id=?", (fine, issued_to))
                messagebox.showinfo("Fine", f"Late return! Fine added: ₹{fine}")
            cursor.execute("UPDATE books SET status='Available', issued_to=NULL, return_date=NULL WHERE id=?", (book_id,))
            conn.commit()
            messagebox.showinfo("Success", "Book returned successfully!")
            view_books()
            view_students()
    except:
        messagebox.showwarning("Selection Error", "Please select a book to return.")

# GUI setup
root = tk.Tk()
root.title("Library Management System")

# Add Book Section
frame_add = tk.Frame(root)
frame_add.pack(pady=10)

tk.Label(frame_add, text="Title:").grid(row=0, column=0)
entry_title = tk.Entry(frame_add)
entry_title.grid(row=0, column=1)

tk.Label(frame_add, text="Author:").grid(row=1, column=0)
entry_author = tk.Entry(frame_add)
entry_author.grid(row=1, column=1)

btn_add = tk.Button(frame_add, text="Add Book", command=add_book)
btn_add.grid(row=2, column=0, pady=5)
btn_update = tk.Button(frame_add, text="Update Book", command=update_book)
btn_update.grid(row=2, column=1, pady=5)
btn_remove = tk.Button(frame_add, text="Remove Book", command=remove_book)
btn_remove.grid(row=2, column=2, pady=5)

# Book List Section
frame_list = tk.Frame(root)
frame_list.pack(pady=10)

listbox_books = tk.Listbox(frame_list, width=80, height=10)
listbox_books.pack()

btn_view_books = tk.Button(root, text="View Books", command=view_books)
btn_view_books.pack(pady=5)

# Student Section
frame_student = tk.Frame(root)
frame_student.pack(pady=10)

tk.Label(frame_student, text="Student Name:").grid(row=0, column=0)
entry_student = tk.Entry(frame_student)
entry_student.grid(row=0, column=1)

btn_add_student = tk.Button(frame_student, text="Add Student", command=add_student)
btn_add_student.grid(row=0, column=2, padx=5)

listbox_students = tk.Listbox(root, width=60, height=5)
listbox_students.pack()

btn_view_students = tk.Button(root, text="View Students", command=view_students)
btn_view_students.pack(pady=5)

# Issue/Return Section
btn_issue = tk.Button(root, text="Issue Book", command=issue_book)
btn_issue.pack(pady=5)

btn_return = tk.Button(root, text="Return Book", command=return_book)
btn_return.pack(pady=5)

# Initialize lists
view_books()
view_students()

root.mainloop()
