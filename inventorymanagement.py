import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Database setup
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER,
    price REAL,
    supplier TEXT
)
""")
conn.commit()

# Functions
def add_item():
    name = entry_name.get()
    category = entry_category.get()
    quantity = int(entry_quantity.get())
    price = float(entry_price.get())
    supplier = entry_supplier.get()

    cursor.execute("INSERT INTO inventory (name, category, quantity, price, supplier) VALUES (?, ?, ?, ?, ?)",
                   (name, category, quantity, price, supplier))
    conn.commit()
    messagebox.showinfo("Success", "Item added successfully!")
    view_items()

def view_items():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM inventory")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

def delete_item():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an item to delete")
        return
    item_id = tree.item(selected[0])['values'][0]
    cursor.execute("DELETE FROM inventory WHERE id=?", (item_id,))
    conn.commit()
    view_items()

def update_item():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an item to update")
        return
    item_id = tree.item(selected[0])['values'][0]
    cursor.execute("UPDATE inventory SET name=?, category=?, quantity=?, price=?, supplier=? WHERE id=?",
                   (entry_name.get(), entry_category.get(), int(entry_quantity.get()), float(entry_price.get()), entry_supplier.get(), item_id))
    conn.commit()
    view_items()

# GUI setup
root = tk.Tk()
root.title("Inventory Management System")

tk.Label(root, text="Name").grid(row=0, column=0)
tk.Label(root, text="Category").grid(row=1, column=0)
tk.Label(root, text="Quantity").grid(row=2, column=0)
tk.Label(root, text="Price").grid(row=3, column=0)
tk.Label(root, text="Supplier").grid(row=4, column=0)

entry_name = tk.Entry(root); entry_name.grid(row=0, column=1)
entry_category = tk.Entry(root); entry_category.grid(row=1, column=1)
entry_quantity = tk.Entry(root); entry_quantity.grid(row=2, column=1)
entry_price = tk.Entry(root); entry_price.grid(row=3, column=1)
entry_supplier = tk.Entry(root); entry_supplier.grid(row=4, column=1)

tk.Button(root, text="Add Item", command=add_item).grid(row=5, column=0)
tk.Button(root, text="Update Item", command=update_item).grid(row=5, column=1)
tk.Button(root, text="Delete Item", command=delete_item).grid(row=5, column=2)
tk.Button(root, text="View Items", command=view_items).grid(row=5, column=3)

# Treeview for displaying items
tree = ttk.Treeview(root, columns=("ID", "Name", "Category", "Quantity", "Price", "Supplier"), show="headings")
for col in ("ID", "Name", "Category", "Quantity", "Price", "Supplier"):
    tree.heading(col, text=col)
tree.grid(row=6, column=0, columnspan=4)

view_items()
root.mainloop()
