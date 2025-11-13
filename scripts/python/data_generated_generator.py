import csv
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

RNG = random.Random(123)

BASE_DIR = Path("data")
SOURCES_DIR = BASE_DIR / "sources"
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def read_csv(path):
    rows = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_sources():
    citoyens = read_csv(SOURCES_DIR / "citoyens.csv")
    services = read_csv(SOURCES_DIR / "services_municipaux.csv")
    rdv = read_csv(SOURCES_DIR / "demandes_rdv.csv")
    etat_civil = read_csv(SOURCES_DIR / "demandes_etat_civil.csv")
    urbanisme = read_csv(SOURCES_DIR / "demandes_urbanisme.csv")
    return citoyens, services, rdv, etat_civil, urbanisme


def generate_citoyens_enrichis(citoyens, services, rdv, etat_civil, urbanisme):
    services_by_id = {int(s["service_id"]): s for s in services}
    rdv_by_citoyen = defaultdict(list)
    ec_by_citoyen = defaultdict(list)
    urba_by_citoyen = defaultdict(list)

    for r in rdv:
        rdv_by_citoyen[int(r["citoyen_id"])].append(r)

    for e in etat_civil:
        ec_by_citoyen[int(e["citoyen_id"])].append(e)

    for u in urbanisme:
        urba_by_citoyen[int(u["citoyen_id"])].append(u)

    rows = []

    for c in citoyens:
        cid = int(c["citoyen_id"])
        rdvs = rdv_by_citoyen.get(cid, [])
        ecs = ec_by_citoyen.get(cid, [])
        urbs = urba_by_citoyen.get(cid, [])

        nb_rdv = len(rdvs)
        nb_ec = len(ecs)
        nb_urbs = len(urbs)

        last_rdv_date = ""
        first_demande_date = ""
        last_demande_date = ""

        if rdvs:
            dates_rdv = [parse_date(r["date_rdv"]) for r in rdvs]
            last_rdv_date = max(dates_rdv).isoformat()

        all_dates = []

        for r in rdvs:
            all_dates.append(parse_date(r["date_demande"]))
        for e in ecs:
            all_dates.append(parse_date(e["date_demande"]))
        for u in urbs:
            all_dates.append(parse_date(u["date_demande"]))

        if all_dates:
            first_demande_date = min(all_dates).isoformat()
            last_demande_date = max(all_dates).isoformat()

        service_codes = []
        for r in rdvs:
            sid = int(r["service_id"])
            svc = services_by_id.get(sid)
            if svc:
                service_codes.append(svc["code_service"])

        frequent_service_code = ""
        if service_codes:
            frequent_service_code = Counter(service_codes).most_common(1)[0][0]

        activite_score = nb_rdv + nb_ec + nb_urbs
        if activite_score == 0:
            segment = "INACTIF"
        elif activite_score < 3:
            segment = "FAIBLE"
        elif activite_score < 7:
            segment = "MOYEN"
        else:
            segment = "ELEVE"

        proba_contact_mail = RNG.uniform(0.0, 1.0)
        proba_contact_guichet = RNG.uniform(0.0, 1.0)
        proba_contact_tel = max(0.0, 1.0 - (proba_contact_mail + proba_contact_guichet) / 1.5)

        row = {
            "citoyen_id": c["citoyen_id"],
            "nom": c["nom"],
            "prenom": c["prenom"],
            "date_naissance": c["date_naissance"],
            "email": c["email"],
            "telephone": c["telephone"],
            "adresse": c["adresse"],
            "code_postal": c["code_postal"],
            "ville": c["ville"],
            "arrondissement": c["arrondissement"],
            "nb_rdv": nb_rdv,
            "nb_demandes_etat_civil": nb_ec,
            "nb_demandes_urbanisme": nb_urbs,
            "last_rdv_date": last_rdv_date,
            "first_demande_date": first_demande_date,
            "last_demande_date": last_demande_date,
            "frequent_service_code": frequent_service_code,
            "segment_activite": segment,
            "proba_contact_mail": round(proba_contact_mail, 3),
            "proba_contact_guichet": round(proba_contact_guichet, 3),
            "proba_contact_tel": round(proba_contact_tel, 3),
        }
        rows.append(row)

    return rows


def generate_rdv_planifies(rdv, services):
    services_by_id = {int(s["service_id"]): s for s in services}
    rows = []

    guichets_par_service = defaultdict(list)
    for s in services:
        sid = int(s["service_id"])
        for i in range(1, RNG.randint(2, 5)):
            guichets_par_service[sid].append(f"G-{sid:03d}-{i:02d}")

    for r in rdv:
        date_rdv = parse_date(r["date_rdv"])
        hour = RNG.randint(8, 17)
        minute = RNG.choice([0, 15, 30, 45])
        start_dt = datetime.combine(date_rdv, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
        duration_min = RNG.choice([15, 20, 30])
        end_dt = start_dt + timedelta(minutes=duration_min)

        is_peak_hour = 1 if 9 <= hour <= 11 or 14 <= hour <= 16 else 0
        delay_days = (date_rdv - parse_date(r["date_demande"])).days

        sid = int(r["service_id"])
        guichets = guichets_par_service.get(sid) or [f"G-{sid:03d}-01"]
        guichet_id = RNG.choice(guichets)

        svc = services_by_id.get(sid)
        code_service = svc["code_service"] if svc else ""
        arrondissement_service = svc["arrondissement"] if svc else ""

        row = {
            "rdv_id": r["rdv_id"],
            "citoyen_id": r["citoyen_id"],
            "service_id": r["service_id"],
            "code_service": code_service,
            "arrondissement_service": arrondissement_service,
            "type_rdv": r["type_rdv"],
            "date_demande": r["date_demande"],
            "date_rdv": r["date_rdv"],
            "rdv_start_ts": start_dt.isoformat(),
            "rdv_end_ts": end_dt.isoformat(),
            "slot_duration_min": duration_min,
            "is_peak_hour": is_peak_hour,
            "statut": r["statut"],
            "canal": r["canal"],
            "delai_jours_demande_rdv": delay_days,
        }
        rows.append(row)

    return rows


def generate_stats_quotidiennes(rdv, etat_civil, urbanisme):
    stats = {}

    def ensure(date_str):
        if date_str not in stats:
            stats[date_str] = {
                "date": date_str,
                "nb_rdv_total": 0,
                "nb_rdv_confirme": 0,
                "nb_rdv_honore": 0,
                "nb_rdv_annule": 0,
                "nb_dem_etat_civil": 0,
                "nb_dem_urbanisme": 0,
                "nb_citoyens_distincts": 0,
            }

    citoyens_par_date = defaultdict(set)

    for r in rdv:
        d = r["date_demande"]
        ensure(d)
        stats[d]["nb_rdv_total"] += 1
        statut = r["statut"]
        if statut == "CONFIRME":
            stats[d]["nb_rdv_confirme"] += 1
        if statut == "HONORE":
            stats[d]["nb_rdv_honore"] += 1
        if statut == "ANNULE":
            stats[d]["nb_rdv_annule"] += 1
        citoyens_par_date[d].add(r["citoyen_id"])

    for e in etat_civil:
        d = e["date_demande"]
        ensure(d)
        stats[d]["nb_dem_etat_civil"] += 1
        citoyens_par_date[d].add(e["citoyen_id"])

    for u in urbanisme:
        d = u["date_demande"]
        ensure(d)
        stats[d]["nb_dem_urbanisme"] += 1
        citoyens_par_date[d].add(u["citoyen_id"])

    for d, s in stats.items():
        s["nb_citoyens_distincts"] = len(citoyens_par_date[d])

    ordered_dates = sorted(stats.keys())
    rows = [stats[d] for d in ordered_dates]
    return rows


def main():
    citoyens, services, rdv, etat_civil, urbanisme = load_sources()

    citoyens_enrichis = generate_citoyens_enrichis(citoyens, services, rdv, etat_civil, urbanisme)
    rdv_planifies = generate_rdv_planifies(rdv, services)
    stats_quotidiennes = generate_stats_quotidiennes(rdv, etat_civil, urbanisme)

    write_csv(
        GENERATED_DIR / "citoyens_enrichis.csv",
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
            "nb_rdv",
            "nb_demandes_etat_civil",
            "nb_demandes_urbanisme",
            "last_rdv_date",
            "first_demande_date",
            "last_demande_date",
            "frequent_service_code",
            "segment_activite",
            "proba_contact_mail",
            "proba_contact_guichet",
            "proba_contact_tel",
        ],
        citoyens_enrichis,
    )

    write_csv(
        GENERATED_DIR / "rdv_planifies.csv",
        [
            "rdv_id",
            "citoyen_id",
            "service_id",
            "code_service",
            "arrondissement_service",
            "type_rdv",
            "date_demande",
            "date_rdv",
            "rdv_start_ts",
            "rdv_end_ts",
            "slot_duration_min",
            "is_peak_hour",
            "statut",
            "canal",
            "delai_jours_demande_rdv",
        ],
        rdv_planifies,
    )

    write_csv(
        GENERATED_DIR / "stats_quotidiennes.csv",
        [
            "date",
            "nb_rdv_total",
            "nb_rdv_confirme",
            "nb_rdv_honore",
            "nb_rdv_annule",
            "nb_dem_etat_civil",
            "nb_dem_urbanisme",
            "nb_citoyens_distincts",
        ],
        stats_quotidiennes,
    )


if __name__ == "__main__":
    main()
