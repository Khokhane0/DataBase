import tkinter as tk
from tkinter import messagebox, simpledialog
from connexion import get_connexion  # utilise oracledb maintenant

class ReservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de réservation de matériel")
        self.root.geometry("450x500")

        label = tk.Label(root, text="Menu principal", font=("Arial", 18))
        label.pack(pady=20)

        # Boutons mis à jour selon les 5 tables
        tk.Button(root, text="Rechercher du matériel disponible", width=40, command=self.rechercher_materiel).pack(pady=5)
        tk.Button(root, text="Réserver un matériel", width=40, command=self.reserver_materiel).pack(pady=5)
        tk.Button(root, text="Enregistrer un retour", width=40, command=self.retour_materiel).pack(pady=5)
        tk.Button(root, text="Gérer les utilisateurs", width=40, command=self.gerer_utilisateurs).pack(pady=5)
        tk.Button(root, text="Gérer les matériels", width=40, command=self.gerer_materiel).pack(pady=5)
        tk.Button(root, text="Historique d’un utilisateur", width=40, command=self.historique_utilisateur).pack(pady=5)
        tk.Button(root, text="Afficher le journal des transactions", width=40, command=self.afficher_journal).pack(pady=5)
        tk.Button(root, text="Quitter", width=40, command=root.quit).pack(pady=20)

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
        else:
            messagebox.showerror("Connexion", "Échec de la connexion à Oracle.")

    def reserver_materiel(self):
        conn = get_connexion()
        if conn:
            try:
                id_utilisateur = simpledialog.askstring("Réservation", "ID de l'utilisateur :")
                id_materiel = simpledialog.askstring("Réservation", "ID du matériel à réserver :")

                if not id_utilisateur or not id_materiel:
                    messagebox.showwarning("Champs manquants", "Veuillez fournir tous les champs.")
                    return

                cursor = conn.cursor()

                cursor.execute("SELECT disponible FROM Materiel WHERE id_materiel = :id", {"id": id_materiel})
                statut = cursor.fetchone()
                if not statut or statut[0] != 'O':
                    messagebox.showerror("Erreur", "Matériel non disponible ou inexistant.")
                    return

                cursor.execute("SELECT NVL(MAX(id_reservation), 0) + 1 FROM Reservation")
                new_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO Reservation (id_reservation, id_utilisateur, id_materiel, date_reservation, date_retour_prevu)
                    VALUES (:id, :uid, :mid, SYSDATE, SYSDATE + 7)
                """, {"id": new_id, "uid": id_utilisateur, "mid": id_materiel})

                cursor.execute("UPDATE Materiel SET disponible = 'N' WHERE id_materiel = :id", {"id": id_materiel})

                cursor.execute("""
                    INSERT INTO JournalTransaction (id_log, operation, table_cible, horodatage, details)
                    VALUES ((SELECT NVL(MAX(id_log), 0) + 1 FROM JournalTransaction), 'INSERT', 'Reservation', SYSTIMESTAMP,
                    :details)
                """, {"details": f"Réservation par utilisateur {id_utilisateur} du matériel {id_materiel}"})

                conn.commit()
                messagebox.showinfo("Succès", "Réservation enregistrée avec succès.")

            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()
        else:
            messagebox.showerror("Connexion", "Échec de la connexion à Oracle.")

    def retour_materiel(self):
        conn = get_connexion()
        if conn:
            try:
                id_reservation = simpledialog.askstring("Retour", "ID de la réservation :")
                etat = simpledialog.askstring("Retour", "État du matériel (bon, endommagé, etc.) :")
                if not id_reservation or not etat:
                    messagebox.showwarning("Champs manquants", "Tous les champs sont obligatoires.")
                    return

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
                    VALUES (:idr, :idrsv, SYSDATE, :etat)
                """, {"idr": id_retour, "idrsv": id_reservation, "etat": etat})

                cursor.execute("UPDATE Materiel SET disponible = 'O' WHERE id_materiel = :id", {"id": id_materiel})

                cursor.execute("""
                    INSERT INTO JournalTransaction (id_log, operation, table_cible, horodatage, details)
                    VALUES ((SELECT NVL(MAX(id_log), 0) + 1 FROM JournalTransaction), 'INSERT', 'Retour', SYSTIMESTAMP,
                    :details)
                """, {"details": f"Retour du matériel {id_materiel} pour réservation {id_reservation}"})

                conn.commit()
                messagebox.showinfo("Succès", "Retour enregistré avec succès.")

            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()
        else:
            messagebox.showerror("Connexion", "Échec de la connexion à Oracle.")

    def gerer_utilisateurs(self):
        conn = get_connexion()
        if conn:
            try:
                id_utilisateur = simpledialog.askstring("Utilisateur", "ID utilisateur :")
                nom = simpledialog.askstring("Utilisateur", "Nom :")
                type_utilisateur = simpledialog.askstring("Utilisateur", "Type :")
                email = simpledialog.askstring("Utilisateur", "Email :")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Utilisateur VALUES (:id, :nom, :type, :email)",
                               {"id": id_utilisateur, "nom": nom, "type": type_utilisateur, "email": email})
                conn.commit()
                messagebox.showinfo("Succès", "Utilisateur ajouté.")
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()

    def gerer_materiel(self):
        conn = get_connexion()
        if conn:
            try:
                id_materiel = simpledialog.askstring("Matériel", "ID matériel :")
                nom = simpledialog.askstring("Matériel", "Nom :")
                categorie = simpledialog.askstring("Matériel", "Catégorie :")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Materiel VALUES (:id, :nom, :cat, 'O')",
                               {"id": id_materiel, "nom": nom, "cat": categorie})
                conn.commit()
                messagebox.showinfo("Succès", "Matériel ajouté.")
            except Exception as e:
                conn.rollback()
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
                if not lignes:
                    messagebox.showinfo("Aucun historique", "Aucune réservation trouvée pour cet utilisateur.")
                else:
                    message = ""
                    for row in lignes:
                        message += f"Réservation {row[0]} - {row[1]}\n  Réservé : {row[2]} / Retour prévu : {row[3]}\n"
                        if row[4]:
                            message += f"  Retour effectué : {row[4]} | État : {row[5]}\n"
                        message += "\n"
                    messagebox.showinfo("Historique", message)
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
                if not lignes:
                    messagebox.showinfo("Journal", "Aucune transaction enregistrée.")
                else:
                    message = ""
                    for log in lignes:
                        message += f"{log[3]} | {log[1]} sur {log[2]}: {log[4]}\n"
                    messagebox.showinfo("Journal des transactions", message)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
            finally:
                conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReservationApp(root)
    root.mainloop()

