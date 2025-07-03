 main.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db, connect
from auth import register, login
from charts import show_pie_chart
from export import export_to_csv
from theme import toggle_theme

init_db()

current_user = None  # Tracks logged-in user

# ------------------ Transaction Functions ------------------ #
def add_transaction():
    global current_user
    t_type = type_var.get()
    amount = amount_var.get()
    category = category_var.get()
    description = desc_entry.get()
    date = date_var.get()

    if not amount or not date:
        messagebox.showwarning("Missing Info", "Amount and date required.")
        return

    try:
        amount = float(amount)
    except:
        messagebox.showerror("Invalid", "Amount must be a number.")
        return

    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, type, amount, category, description, date) VALUES (?, ?, ?, ?, ?, ?)",
              (current_user[0], t_type, amount, category, description, date))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Transaction added.")
    update_summary()
    clear_form()

def clear_form():
    amount_var.set("")
    category_var.set("Food")
    desc_entry.delete(0, tk.END)
    date_var.set("YYYY-MM-DD")

# ------------------ Login/Register UI ------------------ #
def show_login():
    login_win = tk.Toplevel(app)
    login_win.title("Login / Register")

    tk.Label(login_win, text="Username").pack()
    username_entry = tk.Entry(login_win)
    username_entry.pack()

    tk.Label(login_win, text="Password").pack()
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack()

    def do_login():
        global current_user
        user = login(username_entry.get(), password_entry.get())
        if user:
            current_user = user
            login_win.destroy()
            app.title(f"Expense Tracker - {current_user[1]}")
            update_summary()
        else:
            messagebox.showerror("Failed", "Invalid credentials")

    def do_register():
        if register(username_entry.get(), password_entry.get()):
            messagebox.showinfo("Success", "Registered. Now login.")
        else:
            messagebox.showerror("Error", "Username already exists")

    tk.Button(login_win, text="Login", command=do_login).pack(pady=5)
    tk.Button(login_win, text="Register", command=do_register).pack()

# ------------------ Summary ------------------ #
def update_summary():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type='Income'", (current_user[0],))
    income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type='Expense'", (current_user[0],))
    expense = c.fetchone()[0] or 0
    balance = income - expense

    summary_label.config(text=f"Income: {income:.2f}   |   Expense: {expense:.2f}   |   Balance: {balance:.2f}")
    conn.close()

# ------------------ App UI ------------------ #
app = tk.Tk()
app.geometry("500x450")
app.title("Expense Tracker")

ttk.Label(app, text="Add Transaction", font=("Arial", 14)).pack(pady=10)

type_var = tk.StringVar(value="Expense")
amount_var = tk.StringVar()
category_var = tk.StringVar(value="Food")
date_var = tk.StringVar(value="YYYY-MM-DD")

ttk.Label(app, text="Type:").pack()
ttk.Combobox(app, textvariable=type_var, values=["Income", "Expense"]).pack()

ttk.Label(app, text="Amount:").pack()
tk.Entry(app, textvariable=amount_var).pack()

ttk.Label(app, text="Category:").pack()
ttk.Combobox(app, textvariable=category_var, values=["Food", "Transport", "Bills", "Salary", "Entertainment", "Others"]).pack()

ttk.Label(app, text="Description:").pack()
desc_entry = tk.Entry(app)
desc_entry.pack()

ttk.Label(app, text="Date (YYYY-MM-DD):").pack()
tk.Entry(app, textvariable=date_var).pack()

tk.Button(app, text="Add Transaction", command=add_transaction, bg="#4CAF50", fg="white").pack(pady=10)

summary_label = tk.Label(app, text="Login to view summary", font=("Arial", 10), fg="blue")
summary_label.pack(pady=10)

# Extra Features
tk.Button(app, text="View Chart", command=lambda: show_pie_chart(current_user[0])).pack(pady=2)
tk.Button(app, text="Export to CSV", command=lambda: export_to_csv(current_user[0])).pack(pady=2)
tk.Button(app, text="Toggle Theme", command=lambda: toggle_theme(app)).pack(pady=2)
tk.Button(app, text="Login / Register", command=show_login).pack(pady=5)

app.mainloop()