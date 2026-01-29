import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import pandas as pd


def connect_db():
    return psycopg2.connect(
        dbname='Sklep_sportowy',
        user='postgres',
        password='123456',
        host='localhost',
        port='5432'
    )

def apply_scope():
    scope_year = combo_scope.get()
    try:
        conn = connect_db()
        cur = conn.cursor()

        if scope_year == "Wszystkie":
            sql = "CREATE OR REPLACE VIEW Widok_Zawezony AS SELECT * FROM Sprzedaż;"
        else:
            sql = f"""
                CREATE OR REPLACE VIEW Widok_Zawezony AS 
                SELECT s.* FROM Sprzedaż s 
                JOIN Data d ON s.ID_daty = d.ID_daty 
                WHERE d.rok = {scope_year};
            """
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("Zakres", f"Ustawiono zakres danych na: {scope_year}")
    except Exception as e:
        messagebox.showerror("Błąd Zakresu", str(e))

def pivot_table():
    cols = [tree.heading(c)['text'] for c in tree['columns']]
    data = [tree.item(i)['values'] for i in tree.get_children()]

    if not data:
        return

    df = pd.DataFrame(data, columns=cols)
    df = df.set_index(cols[0]).T.reset_index()

    if df.columns[0] == 'index':
        df.rename(columns={'index': 'marka'}, inplace=True)
    elif df.columns[0] == 'marka':
        df.rename(columns={'marka': 'atrybut'}, inplace=True)

    for i in tree.get_children():
        tree.delete(i)

    tree["columns"] = list(df.columns)
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    for row in df.values.tolist():
        tree.insert("", "end", values=row)


def run_query(query, tree):
    for i in tree.get_children():
        tree.delete(i)
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(query)
        colnames = [desc[0] for desc in cur.description]
        tree["columns"] = colnames
        for col in colnames:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Błąd SQL", str(e))


root = tk.Tk()
root.title("System Analityczny Sklepu Sportowego")
root.geometry("1100x650")

frame_top = tk.Frame(root)
frame_top.pack(pady=10)

tk.Label(frame_top, text="1. Zakres (Rok):").pack(side=tk.LEFT, padx=5)
combo_scope = ttk.Combobox(frame_top, values=["Wszystkie", "2021", "2022", "2023", "2024"], width=10, state="readonly")
combo_scope.set("Wszystkie")
combo_scope.pack(side=tk.LEFT, padx=5)

btn_scope = tk.Button(frame_top, text="Ustaw Zakres", command=apply_scope, bg="#e1e1e1")
btn_scope.pack(side=tk.LEFT, padx=5)

tk.Label(frame_top, text=" 2. Analiza:").pack(side=tk.LEFT, padx=5)
analyses = [
    "Ranking Marek i Miast",
    "Analiza Czasowa",
    "Miasta w Regionie",
    "Marki vs Kwartały",
    "Skuteczność Rabatów (Top 5)",
    "Profil Klienta (Lojalność)"
]
combo_analysis = ttk.Combobox(frame_top, values=analyses, width=30, state="readonly")
combo_analysis.pack(side=tk.LEFT, padx=10)

frame_params = tk.Frame(root)
frame_params.pack(pady=5)

var_drill_down = tk.BooleanVar()
var_region = tk.StringVar()
var_category = tk.StringVar()


def update_params(event):
    for widget in frame_params.winfo_children():
        widget.destroy()
    wybor = combo_analysis.get()

    if wybor == "Analiza Czasowa":
        tk.Checkbutton(frame_params, text="Rozwiń (Drill-down)", variable=var_drill_down).pack()
    elif wybor in ["Miasta w Regionie", "Profil Klienta (Lojalność)"]:
        tk.Label(frame_params, text="Region:").pack(side=tk.LEFT)
        conn = connect_db();
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT region FROM Adres ORDER BY region")
        regiony = [r[0] for r in cur.fetchall()];
        cur.close();
        conn.close()
        ttk.Combobox(frame_params, values=regiony, textvariable=var_region, state="readonly").pack(side=tk.LEFT, padx=5)
    elif wybor == "Marki vs Kwartały":
        tk.Button(frame_params, text="Obróć widok (Pivot)", command=pivot_table).pack()
    elif wybor == "Skuteczność Rabatów (Top 5)":
        tk.Label(frame_params, text="Kategoria:").pack(side=tk.LEFT)
        conn = connect_db();
        cur = conn.cursor()
        cur.execute("SELECT nazwa_kategorii FROM Kategoria ORDER BY nazwa_kategorii")
        kategorie = [k[0] for k in cur.fetchall()];
        cur.close();
        conn.close()
        ttk.Combobox(frame_params, values=kategorie, textvariable=var_category, state="readonly").pack(side=tk.LEFT,
                                                                                                       padx=5)


combo_analysis.bind("<<ComboboxSelected>>", update_params)

frame_mid = tk.Frame(root)
frame_mid.pack(expand=True, fill='both', padx=20, pady=20)
scrollbar = ttk.Scrollbar(frame_mid, orient="vertical")
tree = ttk.Treeview(frame_mid, show="headings", yscrollcommand=scrollbar.set)
scrollbar.config(command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(side=tk.LEFT, expand=True, fill='both')

def on_generate():
    choice = combo_analysis.get()
    if not choice: return

    if choice == "Ranking Marek i Miast":
        sql = """
              SELECT p.marka,
                     a.miasto,
                     SUM(v.ilosc) AS "Sztuki",
                     ROUND(SUM(v.cena_ostateczna), 2) AS "Przychód"
              FROM Widok_Zawezony v
                       JOIN Produkt p ON v.ID_produktu = p.ID_produktu
                       JOIN Klient k ON v.ID_klienta = k.ID_klienta
                       JOIN Adres a ON k.ID_adresu = a.ID_adresu
              GROUP BY p.marka, a.miasto
              ORDER BY a.miasto, "Przychód" DESC;
              """
        run_query(sql, tree)

    elif choice == "Analiza Czasowa":
        if var_drill_down.get():
            sql = """
                  SELECT d.rok,
                         d.kwartal,
                         d.miesiac,
                         SUM(v.ilosc) AS "Sztuki",
                         ROUND(SUM(v.cena_ostateczna), 2) AS "Przychód"
                  FROM Widok_Zawezony v
                           JOIN Data d ON v.ID_daty = d.ID_daty
                  GROUP BY d.rok, d.kwartal, d.miesiac
                  ORDER BY d.rok, d.kwartal, d.miesiac;
                  """
        else:
            sql = """
                  SELECT d.rok,
                         SUM(v.ilosc) AS "Sztuki",
                         ROUND(SUM(v.cena_ostateczna), 2) AS "Przychód"
                  FROM Widok_Zawezony v
                           JOIN Data d ON v.ID_daty = d.ID_daty
                  GROUP BY d.rok
                  ORDER BY d.rok;
                  """
        run_query(sql, tree)

    elif choice == "Miasta w Regionie":
        reg = var_region.get()
        if not reg: return messagebox.showwarning("Uwaga", "Wybierz region!")
        sql = f"""
              SELECT a.miasto,
                    COUNT(v.ID_sprzedaży) AS "Transakcje",
                    SUM(v.ilosc) AS "Sztuki",
                    ROUND(SUM(v.cena_ostateczna), 2) AS "Przychód"
              FROM Widok_Zawezony v 
                    JOIN Klient k ON v.ID_klienta = k.ID_klienta
                    JOIN Adres a ON k.ID_adresu = a.ID_adresu
              WHERE a.region = '{reg}'
              GROUP BY a.miasto
              ORDER BY "Przychód" DESC;
              """
        run_query(sql, tree)

    elif choice == "Marki vs Kwartały":
        sql = """
              SELECT p.marka,
                     ROUND(SUM(CASE WHEN d.kwartal = 1 THEN v.cena_ostateczna ELSE 0 END), 2) AS "Q1",
                     ROUND(SUM(CASE WHEN d.kwartal = 2 THEN v.cena_ostateczna ELSE 0 END), 2) AS "Q2",
                     ROUND(SUM(CASE WHEN d.kwartal = 3 THEN v.cena_ostateczna ELSE 0 END), 2) AS "Q3",
                     ROUND(SUM(CASE WHEN d.kwartal = 4 THEN v.cena_ostateczna ELSE 0 END), 2) AS "Q4",
                     ROUND(SUM(v.cena_ostateczna), 2) AS "SUMA"
              FROM Widok_Zawezony v
                       JOIN Produkt p ON v.ID_produktu = p.ID_produktu
                       JOIN Data d ON v.ID_daty = d.ID_daty
              GROUP BY p.marka
              ORDER BY "SUMA" DESC;
              """
        run_query(sql, tree)

    elif choice == "Skuteczność Rabatów (Top 5)":
        cat = var_category.get()
        if not cat: return messagebox.showwarning("Uwaga", "Wybierz kategorię!")
        sql = f"""
              SELECT p.nazwa,
                     p.marka,
                     SUM(v.ilosc) AS "Sztuki",
                     ROUND(SUM((v.cena_podstawowa - v.cena_ostateczna) * v.ilosc), 2) AS "Suma Rabatów"
              FROM Widok_Zawezony v
                     JOIN Produkt p ON v.ID_produktu = p.ID_produktu
                     JOIN Kategoria k ON p.ID_kategorii = k.ID_kategorii
              WHERE k.nazwa_kategorii = '{cat}'
              GROUP BY p.nazwa, p.marka
              ORDER BY "Sztuki" DESC
              LIMIT 5;
              """
        run_query(sql, tree)

    elif choice == "Profil Klienta (Lojalność)":
        reg = var_region.get()
        if not reg: return messagebox.showwarning("Uwaga", "Wybierz region!")
        sql = f"""
              SELECT k.imie,
                     k.nazwisko,
                     a.miasto,
                     COUNT(v.ID_sprzedaży) AS "Liczba Zakupów",
                     ROUND(SUM(v.cena_ostateczna), 2) AS "Suma"
              FROM Widok_Zawezony v
                     JOIN Klient k ON v.ID_klienta = k.ID_klienta
                     JOIN Adres a ON k.ID_adresu = a.ID_adresu
              WHERE a.region = '{reg}'
              GROUP BY k.imie, k.nazwisko, a.miasto
              HAVING COUNT(v.ID_sprzedaży) > 1
              ORDER BY "Suma" DESC;
              """
        run_query(sql, tree)


btn_generate = tk.Button(frame_top, text="Generuj Raport", command=on_generate, bg="#d4edda")
btn_generate.pack(side=tk.LEFT, padx=10)

root.mainloop()