import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path("data") / "sources"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RNG = random.Random(42)


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=RNG.randint(0, delta.days), seconds=RNG.randint(0, 86400))


def random_phone() -> str:
    return "0" + str(RNG.randint(6, 7)) + "".join(str(RNG.randint(0, 9)) for _ in range(8))


def random_email(prenom: str, nom: str) -> str:
    domaines = ["gmail.com", "outlook.com", "yahoo.fr", "ville-marseille.fr"]
    base = f"{prenom.lower()}.{nom.lower()}".replace(" ", "").replace("'", "")
    return f"{base}@{RNG.choice(domaines)}"


def random_name():
    prenoms = [
        "Sophie", "Thomas", "Nicolas", "Clara", "Youssef", "Lea", "Marc", "Julie",
        "Karim", "Sarah", "Antoine", "Camille", "Rachid", "Marine", "Hugo", "Emma",
    ]
    noms = [
        "Martin", "Durand", "Dubois", "Moreau", "Lefevre", "Garcia", "Rossi",
        "Benali", "Ahmed", "Gonzalez", "Petit", "Royer", "Lambert", "Fournier",
    ]
    return RNG.choice(prenoms), RNG.choice(noms)


def random_address():
    rues = [
        "Rue de la République", "Avenue du Prado", "Boulevard Baille",
        "Rue Paradis", "Rue de Lodi", "Boulevard National",
        "Rue Saint-Ferréol", "Rue d'Aubagne", "Rue de Rome",
    ]
    num = RNG.randint(1, 250)
    return f"{num} {RNG.choice(rues)}"


def random_arrondissement():
    return f"{RNG.randint(1, 16)}e"


def random_code_postal():
    # Marseille = 13001 à 13016
    return f"130{RNG.randint(1, 16):02d}"


def generate_citoyens(n: int):
    citoyens = []
    start_birth = datetime(1940, 1, 1)
    end_birth = datetime(2005, 12, 31)
    for i in range(1, n + 1):
        prenom, nom = random_name()
        date_naissance = random_date(start_birth, end_birth).date()
        adresse = random_address()
        code_postal = random_code_postal()
        ville = "Marseille"
        arrondissement = random_arrondissement()
        email = random_email(prenom, nom)
        telephone = random_phone()
        citoyens.append(
            {
                "citoyen_id": i,
                "nom": nom,
                "prenom": prenom,
                "date_naissance": date_naissance.isoformat(),
                "email": email,
                "telephone": telephone,
                "adresse": adresse,
                "code_postal": code_postal,
                "ville": ville,
                "arrondissement": arrondissement,
            }
        )
    return citoyens


def generate_services():
    services_base = [
        ("ETAT_CIVIL", "Etat civil", "Etat civil"),
        ("URBANISME", "Urbanisme", "Urbanisme"),
        ("PETITE_ENFANCE", "Petite enfance", "Famille"),
        ("SCOLARITE", "Scolarité", "Education"),
        ("SPORT", "Sports", "Sports"),
        ("CITOYENNETE", "Citoyenneté", "Vie citoyenne"),
        ("SOCIAL", "Action sociale", "Social"),
        ("MAIRIE_ANNEXE", "Mairie de secteur", "Accueil"),
    ]
    services = []
    service_id = 1
    for code, nom, type_service in services_base:
        for _ in range(RNG.randint(1, 3)):
            arr = random_arrondissement()
            email_contact = f"{code.lower()}_{arr.replace('e','').zfill(2)}@ville-marseille.fr"
            telephone_contact = random_phone()
            services.append(
                {
                    "service_id": service_id,
                    "code_service": code,
                    "nom_service": nom,
                    "type_service": type_service,
                    "arrondissement": arr,
                    "email_contact": email_contact,
                    "telephone_contact": telephone_contact,
                }
            )
            service_id += 1
    return services


def generate_demandes_rdv(n: int, citoyens, services):
    demandes = []
    start_demande = datetime(2023, 1, 1)
    end_demande = datetime(2025, 11, 1)
    types_rdv = [
        "Etat civil",
        "Urbanisme",
        "Carte d'identité",
        "Passeport",
        "Mariage",
        "Naissance",
        "Rendez-vous social",
    ]
    statuts = ["EN_ATTENTE", "CONFIRME", "HONORE", "ANNULE"]
    canaux = ["EN_LIGNE", "TELEPHONE", "GUICHET"]
    for i in range(1, n + 1):
        citoyen = RNG.choice(citoyens)
        service = RNG.choice(services)
        type_rdv = RNG.choice(types_rdv)
        date_demande = random_date(start_demande, end_demande)
        # date_rdv après la demande
        date_rdv = date_demande + timedelta(days=RNG.randint(0, 30))
        statut = RNG.choice(statuts)
        canal = RNG.choice(canaux)
        commentaire = ""
        demandes.append(
            {
                "rdv_id": i,
                "citoyen_id": citoyen["citoyen_id"],
                "service_id": service["service_id"],
                "type_rdv": type_rdv,
                "date_demande": date_demande.date().isoformat(),
                "date_rdv": date_rdv.date().isoformat(),
                "statut": statut,
                "canal": canal,
                "commentaire": commentaire,
            }
        )
    return demandes


def generate_demandes_etat_civil(n: int, citoyens):
    demandes = []
    start_demande = datetime(2023, 1, 1)
    end_demande = datetime(2025, 11, 1)
    types_demande = ["ACTE_NAISSANCE", "ACTE_MARIAGE", "ACTE_DECES", "LIVRET_FAMILLE"]
    statuts = ["ENREGISTREE", "EN_COURS", "TERMINEE", "REFUSEE"]
    modes_retrait = ["COURRIER", "GUICHET", "EN_LIGNE"]
    for i in range(1, n + 1):
        citoyen = RNG.choice(citoyens)
        type_demande = RNG.choice(types_demande)
        date_demande = random_date(start_demande, end_demande)
        delta_jours = RNG.randint(0, 20)
        date_traitement = date_demande + timedelta(days=delta_jours)
        statut = RNG.choice(statuts)
        mode_retrait = RNG.choice(modes_retrait)
        demandes.append(
            {
                "demande_id": i,
                "citoyen_id": citoyen["citoyen_id"],
                "type_demande": type_demande,
                "date_demande": date_demande.date().isoformat(),
                "date_traitement": date_traitement.date().isoformat(),
                "statut": statut,
                "mode_retrait": mode_retrait,
            }
        )
    return demandes


def generate_demandes_urbanisme(n: int, citoyens):
    demandes = []
    start_demande = datetime(2023, 1, 1)
    end_demande = datetime(2025, 11, 1)
    types_demande = [
        "PERMIS_CONSTRUIRE",
        "DECLARATION_PREALABLE",
        "AUTORISATION_TRAVAUX",
    ]
    statuts = ["ENREGISTREE", "INSTRUCTION", "ACCEPTEE", "REFUSEE"]
    for i in range(1, n + 1):
        citoyen = RNG.choice(citoyens)
        type_demande = RNG.choice(types_demande)
        adresse_projet = random_address()
        code_postal = random_code_postal()
        arrondissement = random_arrondissement()
        date_demande = random_date(start_demande, end_demande)
        delta_jours = RNG.randint(10, 120)
        date_decision = date_demande + timedelta(days=delta_jours)
        statut = RNG.choice(statuts)
        demandes.append(
            {
                "demande_id": i,
                "citoyen_id": citoyen["citoyen_id"],
                "type_demande": type_demande,
                "adresse_projet": adresse_projet,
                "code_postal": code_postal,
                "arrondissement": arrondissement,
                "date_demande": date_demande.date().isoformat(),
                "date_decision": date_decision.date().isoformat(),
                "statut": statut,
            }
        )
    return demandes


def write_csv(path: Path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    n_citoyens = 3000
    n_rdv = 5000
    n_etat_civil = 3000
    n_urbanisme = 1500

    citoyens = generate_citoyens(n_citoyens)
    services = generate_services()
    demandes_rdv = generate_demandes_rdv(n_rdv, citoyens, services)
    demandes_etat_civil = generate_demandes_etat_civil(n_etat_civil, citoyens)
    demandes_urbanisme = generate_demandes_urbanisme(n_urbanisme, citoyens)

    write_csv(
        OUTPUT_DIR / "citoyens.csv",
        [
            "citoyen_id",
            "nom",
            "prenom",
            "date_naissance",
            "email",
            "telephone",
            "adresse",
            "code_postal",
            "ville",
            "arrondissement",
        ],
        citoyens,
    )

    write_csv(
        OUTPUT_DIR / "services_municipaux.csv",
        [
            "service_id",
            "code_service",
            "nom_service",
            "type_service",
            "arrondissement",
            "email_contact",
            "telephone_contact",
        ],
        services,
    )

    write_csv(
        OUTPUT_DIR / "demandes_rdv.csv",
        [
            "rdv_id",
            "citoyen_id",
            "service_id",
            "type_rdv",
            "date_demande",
            "date_rdv",
            "statut",
            "canal",
            "commentaire",
        ],
        demandes_rdv,
    )

    write_csv(
        OUTPUT_DIR / "demandes_etat_civil.csv",
        [
            "demande_id",
            "citoyen_id",
            "type_demande",
            "date_demande",
            "date_traitement",
            "statut",
            "mode_retrait",
        ],
        demandes_etat_civil,
    )

    write_csv(
        OUTPUT_DIR / "demandes_urbanisme.csv",
        [
            "demande_id",
            "citoyen_id",
            "type_demande",
            "adresse_projet",
            "code_postal",
            "arrondissement",
            "date_demande",
            "date_decision",
            "statut",
        ],
        demandes_urbanisme,
    )


if __name__ == "__main__":
    main()
