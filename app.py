import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname = 'Sklep_sportowy',
        user = 'postgres',
        password = '123456',
        host = 'localhost',
        port = '5432'
    )


def run_query(query, tree):
    # 1. Czyścimy stare dane z tabeli w GUI
    for i in tree.get_children():
        tree.delete(i)

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(query)

        # 2. Pobieramy nazwy kolumn z bazy, żeby ustawić nagłówki
        colnames = [desc[0] for desc in cur.description]
        tree["columns"] = colnames
        for col in colnames:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        # 3. Wstawiamy wiersze
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)

        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Błąd SQL", str(e))


root = tk.Tk()
root.title("System Analityczny Sklepu Sportowego")
root.geometry("1000x600")

# --- GÓRA: WYBÓR ANALIZY ---
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

tk.Label(frame_top, text="Wybierz analizę:").pack(side=tk.LEFT)
analyses = ["Ranking Marek i Miast", "Analiza Czasowa (Zwijanie)"]
combo_analysis = ttk.Combobox(frame_top, values=analyses, width=30, state="readonly")
combo_analysis.pack(side=tk.LEFT, padx=10)

# --- PANEL PARAMETRÓW (Dynamiczny) ---
frame_params = tk.Frame(root)
frame_params.pack(pady=5)

# Zmienna dla checkboxa
var_drill_down = tk.BooleanVar()


def update_params(event):
    # Czyścimy ramkę parametrów przed dodaniem nowych
    for widget in frame_params.winfo_children():
        widget.destroy()

    wybor = combo_analysis.get()

    if wybor == "Analiza Czasowa (Zwijanie)":
        chk = tk.Checkbutton(frame_params, text="Rozwiń do kwartału i miesiąca (Drill-down)",
                             variable=var_drill_down)
        chk.pack()


# Łączymy wybór w Combobox z funkcją aktualizacji pól
combo_analysis.bind("<<ComboboxSelected>>", update_params)


# --- ŚRODEK: TABELA WYNIKÓW ---
frame_mid = tk.Frame(root)
frame_mid.pack(expand=True, fill='both', padx=20, pady=20)

# 1. Tworzymy scrollbar
scrollbar = ttk.Scrollbar(frame_mid, orient="vertical")

# 2. Tworzymy Treeview i od razu łączymy go ze scrollbarem za pomocą yscrollcommand
tree = ttk.Treeview(frame_mid, show="headings", yscrollcommand=scrollbar.set)

# 3. Konfigurujemy scrollbar, aby sterował widokiem tabeli
scrollbar.config(command=tree.yview)

# 4. PAKOWANIE: Najpierw scrollbar do prawej, potem tree do lewej
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(side=tk.LEFT, expand=True, fill='both')

def on_generate():
    choice = combo_analysis.get()

    if choice == "Ranking Marek i Miast":
        sql = """
              SELECT p.marka,
                     a.miasto,
                     SUM(s.ilosc)                              AS "Sztuki",
                     ROUND(SUM(s.cena_ostateczna)::numeric, 2) AS "Przychód"
              FROM Sprzedaż s
                       JOIN Produkt p ON s.ID_produktu = p.ID_produktu
                       JOIN Klient k ON s.ID_klienta = k.ID_klienta
                       JOIN Adres a ON k.ID_adresu = a.ID_adresu
              GROUP BY p.marka, a.miasto
              ORDER BY a.miasto, "Przychód" DESC; \
              """
        run_query(sql, tree)

    elif choice == "Analiza Czasowa (Zwijanie)":
        # Sprawdzamy stan checkboxa: True = Drill-down, False = Roll-up
        if var_drill_down.get():
            # Operacja DRILL-DOWN: Rozwijamy do kwartału i miesiąca
            sql = """
                  SELECT d.rok, \
                         d.kwartal, \
                         d.miesiac,
                         SUM(s.ilosc)                              AS "Sztuki",
                         ROUND(SUM(s.cena_ostateczna)::numeric, 2) AS "Przychód"
                  FROM Sprzedaż s
                           JOIN Data d ON s.ID_daty = d.ID_daty
                  GROUP BY d.rok, d.kwartal, d.miesiac
                  ORDER BY d.rok, d.kwartal, d.miesiac; \
                  """
        else:
            # Operacja ROLL-UP: Zwijamy dane tylko do poziomu roku
            sql = """
                  SELECT d.rok,
                         SUM(s.ilosc)                              AS "Sztuki",
                         ROUND(SUM(s.cena_ostateczna)::numeric, 2) AS "Przychód"
                  FROM Sprzedaż s
                           JOIN Data d ON s.ID_daty = d.ID_daty
                  GROUP BY d.rok
                  ORDER BY d.rok; \
                  """
        run_query(sql, tree)


btn_generate = tk.Button(frame_top, text="Generuj Raport", command=on_generate)
btn_generate.pack(side=tk.LEFT)

root.mainloop()

