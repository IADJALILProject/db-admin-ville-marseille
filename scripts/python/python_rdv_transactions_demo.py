import logging
from datetime import date

from db_utils import pg_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def create_rdv_transaction():
    with pg_connection(autocommit=False) as conn:
        cur = conn.cursor()
        try:
            logging.info("Création transactionnelle d'une demande de RDV")
            cur.execute(
                """
                SELECT metier.creer_demande_rdv(
                    %s, %s, %s, %s, %s, %s, %s
                );
                """,
                (
                    1738,                        
                    10,                         
                    "Rendez-vous social",         
                    date(2025, 1, 10),            
                    date(2025, 1, 15),          
                    "EN_LIGNE",                  
                    "Créé via démonstration transactionnelle",
                ),
            )
            rdv_id = cur.fetchone()[0]
            conn.commit()
            logging.info("RDV créé avec succès, rdv_id = %s", rdv_id)
            return rdv_id
        except Exception:
            logging.exception("Erreur lors de la création du RDV, rollback de la transaction")
            conn.rollback()
            raise


def cancel_rdv_transaction(rdv_id: int):
    with pg_connection(autocommit=False) as conn:
        cur = conn.cursor()
        try:
            logging.info("Annulation transactionnelle du RDV %s", rdv_id)
            cur.execute(
                "CALL metier.annuler_demande_rdv(%s, %s, %s);",
                (
                    rdv_id,
                    "Annulation de démonstration depuis script Python",
                    "script_rdv_transactions_demo",
                ),
            )
            conn.commit()
            logging.info("RDV %s annulé avec succès", rdv_id)
        except Exception:
            logging.exception("Erreur lors de l'annulation du RDV, rollback de la transaction")
            conn.rollback()
            raise


def simulate_failed_transaction():
    with pg_connection(autocommit=False) as conn:
        cur = conn.cursor()
        try:
            logging.info("Simulation d'une transaction qui doit échouer (citoyen inexistant)")
            cur.execute(
                """
                SELECT metier.creer_demande_rdv(
                    %s, %s, %s, %s, %s, %s, %s
                );
                """,
                (
                    -1,                          
                    10,
                    "Rendez-vous social",
                    date(2025, 1, 10),
                    date(2025, 1, 15),
                    "EN_LIGNE",
                    "Cette demande doit échouer",
                ),
            )
            conn.commit()
        except Exception:
            logging.exception(
                "Erreur attendue, rollback de la transaction de création RDV invalide"
            )
            conn.rollback()


def main():
    rdv_id = create_rdv_transaction()
    cancel_rdv_transaction(rdv_id)
    simulate_failed_transaction()


if __name__ == "__main__":
    main()
