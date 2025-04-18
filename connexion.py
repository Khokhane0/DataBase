import oracledb

def get_connexion():
    try:
        #  Remplace par tes vraies infos serveur
        dsn = oracledb.makedsn(
            host="gaia.emp.uqtr.ca",   # ou l'adresse de ton serveur Oracle
            port=1521,
            service_name="coursbd.uqtr.ca"         # ou "orcl" ou autre nom du service
        )
        conn = oracledb.connect(
            user="SMI1002_025",
            password="79kzus93",
            dsn=dsn
        )
        return conn
    except oracledb.Error as e:
        print("Erreur de connexion Oracle:", e)
        return None
