
-- ========================================
-- Base de données : Réservation de matériel
-- Projet SMI1002
-- ========================================

-- TABLE 1 : Utilisateur
CREATE TABLE Utilisateur (
    id_utilisateur NUMBER PRIMARY KEY,
    nom VARCHAR2(100),
    type_utilisateur VARCHAR2(20),
    email VARCHAR2(100)
);

-- TABLE 2 : Materiel
CREATE TABLE Materiel (
    id_materiel NUMBER PRIMARY KEY,
    nom VARCHAR2(100),
    categorie VARCHAR2(50),
    disponible CHAR(1) CHECK (disponible IN ('O', 'N'))
);

-- TABLE 3 : Reservation
CREATE TABLE Reservation (
    id_reservation NUMBER PRIMARY KEY,
    id_utilisateur NUMBER,
    id_materiel NUMBER,
    date_reservation DATE,
    date_retour_prevu DATE,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur),
    FOREIGN KEY (id_materiel) REFERENCES Materiel(id_materiel)
);

-- TABLE 4 : Retour
CREATE TABLE Retour (
    id_retour NUMBER PRIMARY KEY,
    id_reservation NUMBER,
    date_retour_effectif DATE,
    etat_retour VARCHAR2(100),
    FOREIGN KEY (id_reservation) REFERENCES Reservation(id_reservation)
);

ALTER TABLE Retour
MODIFY date_retour_effectif TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
-- TABLE 5 : JournalTransaction
CREATE TABLE JournalTransaction (
    id_log NUMBER PRIMARY KEY,
    operation VARCHAR2(20),
    table_cible VARCHAR2(50),
    horodatage TIMESTAMP DEFAULT SYSTIMESTAMP,
    details VARCHAR2(500)
);

-- INSERTS DE TEST
INSERT INTO Utilisateur VALUES (1, 'Alice Tremblay', 'étudiant', 'alice@example.com');
INSERT INTO Utilisateur VALUES (2, 'Jean Dupuis', 'technicien', 'jean@example.com');

INSERT INTO Materiel VALUES (1, 'Ordinateur portable HP', 'Ordinateur', 'O');
INSERT INTO Materiel VALUES (2, 'Caméra Canon', 'Caméra', 'O');
INSERT INTO Materiel VALUES (3, 'Tablette Samsung', 'Tablette', 'O');

-- TRIGGERS POUR LOGGING (Exemple de base pour Reservation)
CREATE OR REPLACE TRIGGER trg_log_reservation_insert
AFTER INSERT ON Reservation
FOR EACH ROW
BEGIN
    INSERT INTO JournalTransaction (
        id_log, operation, table_cible, horodatage, details
    ) VALUES (
        (SELECT NVL(MAX(id_log), 0) + 1 FROM JournalTransaction),
        'INSERT',
        'Reservation',
        SYSTIMESTAMP,
        'Nouvelle réservation ajoutée ID: ' || :NEW.id_reservation
    );
END;
/

-- Idem pour Retour
CREATE OR REPLACE TRIGGER trg_log_retour_insert
AFTER INSERT ON Retour
FOR EACH ROW
BEGIN
    INSERT INTO JournalTransaction (
        id_log, operation, table_cible, horodatage, details
    ) VALUES (
        (SELECT NVL(MAX(id_log), 0) + 1 FROM JournalTransaction),
        'INSERT',
        'Retour',
        SYSTIMESTAMP,
        'Retour enregistré ID: ' || :NEW.id_retour
    );
END;
/
