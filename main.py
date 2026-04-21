import sqlite3

def inizializza_database():
    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    with open("database.sql", "r", encoding="utf-8") as file:
        script_sql = file.read()

    cursor.executescript(script_sql)
    conn.commit()
    conn.close()

def aggiungi_categoria():
    nome = input("Inserisci il nome della categoria: ").strip()

    if nome == "":
        print("Errore: il nome della categoria non può essere vuoto.")
        return

    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categorie WHERE nome = ?", (nome,))
    categoria = cursor.fetchone()

    if categoria is not None:
        print("La categoria esiste già.")
    else:
        cursor.execute("INSERT INTO categorie (nome) VALUES (?)", (nome,))
        conn.commit()
        print("Categoria inserita correttamente.")

    conn.close()

def elimina_categoria():
    mostra_categorie()

    id_categoria = input("\nInserisci l'ID della categoria da eliminare: ").strip()

    try:
        id_categoria = int(id_categoria)
    except:
        print("Errore: ID non valido.")
        return

    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categorie WHERE id = ?", (id_categoria,))
    categoria = cursor.fetchone()

    if categoria is None:
        print("Errore: categoria non trovata.")
        conn.close()
        return

    cursor.execute("SELECT COUNT(*) FROM spese WHERE categoria_id = ?", (id_categoria,))
    numero_spese = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM budget WHERE categoria_id = ?", (id_categoria,))
    numero_budget = cursor.fetchone()[0]

    if numero_spese > 0 or numero_budget > 0:
        print("Impossibile eliminare la categoria: è già utilizzata in spese o budget.")
        conn.close()
        return

    cursor.execute("DELETE FROM categorie WHERE id = ?", (id_categoria,))
    conn.commit()
    conn.close()

    print("Categoria eliminata correttamente.")

def inserisci_spesa():
    mostra_categorie()

    data = input("Inserisci la data (YYYY-MM-DD): ").strip()
    importo = input("Inserisci l'importo: ").strip()
    nome_categoria = input("Inserisci la categoria: ").strip()
    descrizione = input("Inserisci descrizione (facoltativa): ").strip()

    try:
        importo = float(importo)
        if importo <= 0:
            print("Errore: l'importo deve essere maggiore di zero.")
            return
    except:
        print("Errore: importo non valido.")
        return

    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categorie WHERE nome = ?", (nome_categoria,))
    risultato = cursor.fetchone()

    if risultato is None:
        print("Errore: la categoria non esiste.")
        conn.close()
        return

    categoria_id = risultato[0]

    cursor.execute("""
        INSERT INTO spese (data, importo, categoria_id, descrizione)
        VALUES (?, ?, ?, ?)
    """, (data, importo, categoria_id, descrizione))

    conn.commit()
    conn.close()

    print("Spesa inserita correttamente.")

def mostra_categorie():
    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome FROM categorie")
    risultati = cursor.fetchall()

    if len(risultati) == 0:
        print("Nessuna categoria trovata.")
    else:
        print("\nELENCO CATEGORIE:")
        print("ID | Nome")
        print("-----------")
        for riga in risultati:
            print(f"{riga[0]} | {riga[1]}")

    conn.close()

def definisci_budget():
    mostra_categorie()
    
    mese = input("Inserisci il mese (YYYY-MM): ").strip()
    nome_categoria = input("Inserisci la categoria: ").strip()
    importo = input("Inserisci l'importo del budget: ").strip()

    try:
        importo = float(importo)
        if importo <= 0:
            print("Errore: il budget deve essere maggiore di zero.")
            return
    except:
        print("Errore: importo non valido.")
        return

    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categorie WHERE nome = ?", (nome_categoria,))
    risultato = cursor.fetchone()

    if risultato is None:
        print("Errore: la categoria non esiste.")
        conn.close()
        return

    categoria_id = risultato[0]

    cursor.execute(
        "SELECT id FROM budget WHERE mese = ? AND categoria_id = ?",
        (mese, categoria_id)
    )
    budget_esistente = cursor.fetchone()

    if budget_esistente is None:
        cursor.execute(
            "INSERT INTO budget (mese, categoria_id, importo) VALUES (?, ?, ?)",
            (mese, categoria_id, importo)
        )
    else:
        cursor.execute(
            "UPDATE budget SET importo = ? WHERE mese = ? AND categoria_id = ?",
            (importo, mese, categoria_id)
        )

    conn.commit()
    conn.close()

    print("Budget mensile salvato correttamente.")

def elimina_spesa():
    mostra_spese() 

    id_spesa = input("\nInserisci l'ID della spesa da eliminare: ").strip()

    try:
        id_spesa = int(id_spesa)
    except:
        print("Errore: ID non valido.")
        return

    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM spese WHERE id = ?", (id_spesa,))
    risultato = cursor.fetchone()

    if risultato is None:
        print("Errore: spesa non trovata.")
    else:
        cursor.execute("DELETE FROM spese WHERE id = ?", (id_spesa,))
        conn.commit()
        print("Spesa eliminata correttamente.")

    conn.close()

def mostra_spese():
    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.data, c.nome, s.importo, s.descrizione
        FROM spese s
        JOIN categorie c ON s.categoria_id = c.id
        ORDER BY s.data
    """)

    risultati = cursor.fetchall()

    if len(risultati) == 0:
        print("Nessuna spesa trovata.")
    else:
        print("\nELENCO SPESE:")
        print("ID | Data | Categoria | Importo | Descrizione")
        print("---------------------------------------------")
        for riga in risultati:
            print(f"{riga[0]} | {riga[1]} | {riga[2]} | {riga[3]} | {riga[4]}")

    conn.close()

def menu_report():
    while True:

        print("\n----- REPORT -----")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese")
        print("4. Torna indietro")

        scelta = input("Scegli un report: ")

        if scelta == "1":
            report_totale_per_categoria()
        elif scelta == "2":
            report_spese_vs_budget()
        elif scelta == "3":
            report_elenco_spese()
        elif scelta == "4":
            break   
        else:
            print("Scelta non valida.")
        
def report_totale_per_categoria():
    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.nome, SUM(s.importo)
        FROM spese s
        JOIN categorie c ON s.categoria_id = c.id
        GROUP BY c.nome
    """)

    risultati = cursor.fetchall()

    print("\nTOTALE SPESE PER CATEGORIA")
    for r in risultati:
        print(f"{r[0]}: {r[1]:.2f}")

    conn.close()

def report_elenco_spese():
    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.data, c.nome, s.importo, s.descrizione
        FROM spese s
        JOIN categorie c ON s.categoria_id = c.id
        ORDER BY s.data
    """)

    risultati = cursor.fetchall()

    print("\nELENCO SPESE:")
    print("ID | Data | Categoria | Importo | Descrizione")

    for r in risultati:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")

    conn.close()

def report_spese_vs_budget():
    conn = sqlite3.connect("spese.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            b.mese,
            c.nome,
            b.importo,
            COALESCE(SUM(s.importo), 0)
        FROM budget b
        JOIN categorie c ON b.categoria_id = c.id
        LEFT JOIN spese s 
            ON s.categoria_id = b.categoria_id 
            AND substr(s.data, 1, 7) = b.mese
        GROUP BY b.mese, c.nome, b.importo
    """)

    risultati = cursor.fetchall()

    print("\nSPESE VS BUDGET")

    for r in risultati:
        mese, categoria, budget, speso = r

        if speso > budget:
            stato = "SUPERATO"
        else:
            stato = "OK"

        print(f"{mese} - {categoria}")
        print(f"Budget: {budget} | Speso: {speso} | Stato: {stato}")
        print("----------------------")

    conn.close()

def mostra_menu():
    while True:
        print("\nGestione spese")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Elimina Spesa")
        print("6. Elimina Categoria")
        print("7. Esci")
        print("-------------------------")

        scelta = input("Inserisci la tua scelta: ")

        if scelta == "1":
            aggiungi_categoria()
        elif scelta == "2":
            inserisci_spesa()
        elif scelta == "3":
            definisci_budget()
        elif scelta == "4":
            menu_report()
        elif scelta == "5":
            elimina_spesa()
        elif scelta == "6":
            elimina_categoria()
        elif scelta == "7":
            print("Uscita dal programma.")
            break
        else:
            print("Scelta non valida. Riprovare.")

inizializza_database()
mostra_menu()