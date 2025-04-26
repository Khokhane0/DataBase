import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from connexion import get_connexion
import re

# --- CONSTANTES DE STYLE ---
BG_COLOR = "#f0f4f7"
BUTTON_COLOR = "#007acc"
TEXT_COLOR = "#333333"
FONT_GENERAL = ("Arial", 12)

class ReservationApp:

    def center_window(win, width, height):
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f'{width}x{height}+{x}+{y}')

    def __init__(self, root):
        self.root = root
        self.root.title("Système de réservation de matériel")
        self.root.geometry("600x800")
        self.root.configure(bg=BG_COLOR)

        label = tk.Label(root, text="Menu principal", font=("Arial", 18), bg=BG_COLOR, fg=TEXT_COLOR)
        label.pack(pady=20)

        options = [
            ("Rechercher du matériel disponible", self.rechercher_materiel),
            ("Réserver un matériel (formulaire)", self.reserver_materiel),
            ("Enregistrer un retour (formulaire)", self.retour_materiel),
            ("Gérer les utilisateurs", self.afficher_gestion_utilisateurs),
            ("Gérer les matériels", self.afficher_gestion_materiels),
            ("Gérer les réservations", self.afficher_gestion_reservations),
            ("Gérer les retours", self.afficher_gestion_retours),
            ("Historique d’un utilisateur", self.historique_utilisateur),
            ("Afficher le journal des transactions", self.afficher_journal),
            ("Quitter", root.quit)
        ]

        for text, command in options:
            tk.Button(root, text=text, width=40, command=command,
                      bg=BUTTON_COLOR, fg="white", font=FONT_GENERAL, padx=10, pady=5).pack(pady=5)
            

    def _verifier_champs(self, valeurs):
        return all(v.strip() for v in valeurs if v is not None)

    def _verifier_email(self, email):
        if not email:
            return False
        regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        return re.match(regex, email)

    def _verifier_et_submit(self, table, champs, valeurs, form, charger_donnees):
        if not self._verifier_champs(valeurs):
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
            return

        if "email" in champs:
            idx = champs.index("email")
            if not self._verifier_email(valeurs[idx]):
                messagebox.showerror("Erreur", "Format d'email invalide.")
                return

        placeholders = ", ".join([":" + champ for champ in champs])
        requete = f"INSERT INTO {table} VALUES ({placeholders})"
        conn = get_connexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(requete, dict(zip(champs, valeurs)))
                conn.commit()
                form.destroy()
                charger_donnees()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()

    def _verifier_et_update(self, table, champs, nouveaux, form, charger_donnees):
        if not self._verifier_champs(nouveaux):
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
            return

        if "email" in champs:
            idx = champs.index("email")
            if not self._verifier_email(nouveaux[idx]):
                messagebox.showerror("Erreur", "Format d'email invalide.")
                return

        set_clause = ", ".join([f"{champs[i]} = :{champs[i]}" for i in range(1, len(champs))])
        requete = f"UPDATE {table} SET {set_clause} WHERE {champs[0]} = :{champs[0]}"
        conn = get_connexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(requete, dict(zip(champs, nouveaux)))
                conn.commit()
                form.destroy()
                charger_donnees()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()



    def _afficher_gestion_table(self, table, headers, champs):
        fenetre = tk.Toplevel(self.root)
        fenetre.title(f"Gestion de la table {table}")
        fenetre.geometry("800x400")

        frame = tk.Frame(fenetre)
        frame.pack(pady=10, fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=headers, show='headings')
        for col in headers:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        def charger_donnees():
            for i in tree.get_children():
                tree.delete(i)
            conn = get_connexion()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM {table}")
                    for row in cursor.fetchall():
                        tree.insert("", "end", values=row)
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))
                finally:
                    conn.close()

        def ajouter_entree():
            form = tk.Toplevel(fenetre)
            form.title("Ajouter")
            entries = {}
            for idx, champ in enumerate(champs):
                tk.Label(form, text=champ).grid(row=idx, column=0, padx=10, pady=5)
                entry = tk.Entry(form)
                entry.grid(row=idx, column=1, padx=10, pady=5)
                entries[champ] = entry

            def submit():
                valeurs = [e.get().strip() for e in entries.values()]
                self._verifier_et_submit(table, champs, valeurs, form, charger_donnees)
                placeholders = ", ".join([":" + champ for champ in champs])
                requete = f"INSERT INTO {table} VALUES ({placeholders})"
                conn = get_connexion()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(requete, dict(zip(champs, valeurs)))
                        conn.commit()
                        form.destroy()
                        charger_donnees()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Erreur", str(e))
                    finally:
                        conn.close()

            tk.Button(form, text="Enregistrer", command=submit).grid(row=len(champs), columnspan=2, pady=10)

        def modifier_entree():
            item = tree.selection()
            if not item:
                messagebox.showwarning("Sélection", "Veuillez sélectionner une ligne.")
                return
            valeurs = tree.item(item)['values']
            form = tk.Toplevel(fenetre)
            form.title("Modifier")
            entries = {}
            for i, champ in enumerate(champs):
                tk.Label(form, text=champ).grid(row=i, column=0, padx=10, pady=5)
                entry = tk.Entry(form)
                entry.insert(0, valeurs[i])
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[champ] = entry

            def update():
                nouveaux = [e.get().strip() for e in entries.values()]
                if not self._verifier_champs(nouveaux):
                    messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
                    return
                if "email" in champs:
                    idx = champs.index("email")
                    if not self._verifier_email(nouveaux[idx]):
                        messagebox.showerror("Erreur", "Format d'email invalide.")
                    return
                set_clause = ", ".join([f"{champs[i]} = :{champs[i]}" for i in range(1, len(champs))])
                requete = f"UPDATE {table} SET {set_clause} WHERE {champs[0]} = :{champs[0]}"
                conn = get_connexion()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(requete, dict(zip(champs, nouveaux)))
                        conn.commit()
                        form.destroy()
                        charger_donnees()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Erreur", str(e))
                    finally:
                        conn.close()

            tk.Button(form, text="Enregistrer les modifications", command=update).grid(row=len(champs), columnspan=2, pady=10)

        def supprimer_entree():
            item = tree.selection()
            if not item:
                messagebox.showwarning("Sélection", "Veuillez sélectionner une ligne.")
                return
            identifiant = tree.item(item)['values'][0]
            if messagebox.askyesno("Confirmer", "Supprimer cet élément ?"):
                conn = get_connexion()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(f"DELETE FROM {table} WHERE {champs[0]} = :id", {"id": identifiant})
                        conn.commit()
                        charger_donnees()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Erreur", str(e))
                    finally:
                        conn.close()

        bouton_frame = tk.Frame(fenetre)
        bouton_frame.pack(pady=10)
        tk.Button(bouton_frame, text="Ajouter", command=ajouter_entree).pack(side="left", padx=5)
        tk.Button(bouton_frame, text="Modifier", command=modifier_entree).pack(side="left", padx=5)
        tk.Button(bouton_frame, text="Supprimer", command=supprimer_entree).pack(side="left", padx=5)
        tk.Button(bouton_frame, text="Retour au menu principal", command=fenetre.destroy).pack(side="right", padx=10)

        charger_donnees()

    def afficher_gestion_utilisateurs(self):
        self._afficher_gestion_table("Utilisateur", ["ID", "Nom", "Type", "Email"],
                                     ["id_utilisateur", "nom", "type_utilisateur", "email"])

    def afficher_gestion_materiels(self):
        self._afficher_gestion_table("Materiel", ["ID", "Nom", "Catégorie", "Disponible"],
                                     ["id_materiel", "nom", "categorie", "disponible"])

    def afficher_gestion_reservations(self):
        self._afficher_gestion_table("Reservation", ["ID", "Utilisateur", "Matériel", "Date", "Retour prévu"],
                                     ["id_reservation", "id_utilisateur", "id_materiel", "date_reservation", "date_retour_prevu"])

    def afficher_gestion_retours(self):
        self._afficher_gestion_table("Retour", ["ID", "Réservation", "Date retour", "État"],
                                     ["id_retour", "id_reservation", "date_retour_effectif", "etat_retour"])

    def reserver_materiel(self):
        form = tk.Toplevel(self.root)
        form.title("Réservation de matériel")

        tk.Label(form, text="ID utilisateur").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        entry_user = tk.Entry(form)
        entry_user.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="ID matériel").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        entry_mat = tk.Entry(form)
        entry_mat.grid(row=1, column=1, padx=10, pady=5)

        def valider():
            id_utilisateur = entry_user.get()
            id_materiel = entry_mat.get()
            conn = get_connexion()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT disponible FROM Materiel WHERE id_materiel = :id", {"id": id_materiel})
                    statut = cursor.fetchone()
                    if not statut or statut[0] != 'O':
                        messagebox.showerror("Erreur", "Matériel non disponible.")
                        return
                    cursor.execute("SELECT NVL(MAX(id_reservation), 0) + 1 FROM Reservation")
                    new_id = cursor.fetchone()[0]
                    cursor.execute("""
    INSERT INTO Reservation (id_reservation, id_utilisateur, id_materiel, date_reservation, date_retour_prevu)
    VALUES (:id_reservation, :id_utilisateur, :id_materiel, SYSDATE, SYSDATE + 7)
""", {
    "id_reservation": new_id,
    "id_utilisateur": id_utilisateur,
    "id_materiel": id_materiel
})


                    cursor.execute("UPDATE Materiel SET disponible = 'N' WHERE id_materiel = :id", {"id": id_materiel})
                    conn.commit()
                    messagebox.showinfo("Succès", "Réservation enregistrée.")
                    form.destroy()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Erreur", str(e))
                finally:
                    conn.close()

        tk.Button(form, text="Réserver", command=valider).grid(row=2, columnspan=2, pady=15)

    def retour_materiel(self):
        form = tk.Toplevel(self.root)
        form.title("Retour de matériel")

        tk.Label(form, text="ID réservation").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        entry_resa = tk.Entry(form)
        entry_resa.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="État du matériel").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        entry_etat = tk.Entry(form)
        entry_etat.grid(row=1, column=1, padx=10, pady=5)

        def valider():
            id_reservation = entry_resa.get()
            etat = entry_etat.get()
            conn = get_connexion()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id_materiel FROM Reservation WHERE id_reservation = :id", {"id": id_reservation})
                    row = cursor.fetchone()
                    if not row:
                        messagebox.showerror("Erreur", "Réservation introuvable.")
                        return
                    id_materiel = row[0]
                    cursor.execute("SELECT NVL(MAX(id_retour), 0) + 1 FROM Retour")
                    id_retour = cursor.fetchone()[0]
                    cursor.execute("""
                        INSERT INTO Retour (id_retour, id_reservation, date_retour_effectif, etat_retour)
                        VALUES (:idr, :idrsv, CURRENT_TIMESTAMP, :etat)
                    """, {"idr": id_retour, "idrsv": id_reservation, "etat": etat})
                    cursor.execute("UPDATE Materiel SET disponible = 'O' WHERE id_materiel = :id", {"id": id_materiel})
                    conn.commit()
                    messagebox.showinfo("Succès", "Retour enregistré.")
                    form.destroy()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Erreur", str(e))
                finally:
                    conn.close()

        tk.Button(form, text="Enregistrer le retour", command=valider).grid(row=2, columnspan=2, pady=15)

    def rechercher_materiel(self):
        conn = get_connexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id_materiel, nom, categorie FROM Materiel WHERE disponible = 'O'")
                resultats = cursor.fetchall()
                if resultats:
                    message = "Matériels disponibles :\n"
                    for row in resultats:
                        message += f"ID: {row[0]} | Nom: {row[1]} | Catégorie: {row[2]}\n"
                    messagebox.showinfo("Résultats", message)
                else:
                    messagebox.showinfo("Résultats", "Aucun matériel disponible.")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()

    def historique_utilisateur(self):
        conn = get_connexion()
        if conn:
            try:
                id_utilisateur = simpledialog.askstring("Historique", "ID de l'utilisateur :")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT R.id_reservation, M.nom, R.date_reservation, R.date_retour_prevu,
                           RET.date_retour_effectif, RET.etat_retour
                    FROM Reservation R
                    JOIN Materiel M ON R.id_materiel = M.id_materiel
                    LEFT JOIN Retour RET ON R.id_reservation = RET.id_reservation
                    WHERE R.id_utilisateur = :id
                """, {"id": id_utilisateur})
                lignes = cursor.fetchall()
                if lignes:
                    message = ""
                    for row in lignes:
                        message += f"Réservation {row[0]} - {row[1]}\nRéservé : {row[2]} / Retour prévu : {row[3]}\n"
                        if row[4]:
                            message += f"Retour effectué : {row[4]} | État : {row[5]}\n"
                        message += "\n"
                    messagebox.showinfo("Historique", message)
                else:
                    messagebox.showinfo("Aucun", "Aucun historique trouvé.")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()

    def afficher_journal(self):
        conn = get_connexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id_log, operation, table_cible, horodatage, details FROM JournalTransaction ORDER BY horodatage DESC")
                lignes = cursor.fetchall()
                if lignes:
                    message = ""
                    for log in lignes:
                        message += f"{log[3]} | {log[1]} sur {log[2]}: {log[4]}\n"
                    messagebox.showinfo("Journal des transactions", message)
                else:
                    messagebox.showinfo("Journal", "Aucune transaction enregistrée.")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReservationApp(root)
    root.mainloop()

