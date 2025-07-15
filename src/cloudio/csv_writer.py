from collections import defaultdict
import csv
from datetime import datetime, timedelta
from pytz import timezone, utc

def write_to_csv(data: dict, filename: str):
    # Préparer les données sous forme : {time: {topic: value, ...}, ...}
    time_series = defaultdict(dict)

    for topic, entries in data.items():
        for entry in entries:
            timestamp = entry["time"]
            value = entry["value"]
            time_series[timestamp][topic] = value

    # Obtenir tous les timestamps triés
    sorted_times = sorted(time_series.keys())

    # Obtenir tous les topics (en-têtes de colonnes)
    topics = list(data.keys())

    # Écrire dans le fichier CSV
    with open(filename, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)

        # Ligne d'en-tête
        header = ["time"] + topics
        writer.writerow(header)

        # Écrire les lignes avec les valeurs, vides si absentes
        for timestamp in sorted_times:
            row = [timestamp]
            for topic in topics:
                row.append(time_series[timestamp].get(topic, ""))
            writer.writerow(row)

    print(f"CSV écrit avec succès dans : {filename}")

def write_to_csv_aligned(data: dict, filename: str):
    tz_local = timezone('Europe/Amsterdam')

    # Étape 1 : structure {time arrondie (locale, sans ms) : {topic: value}}
    time_series = defaultdict(dict)
    all_times = set()
    per_topic_seen_times = defaultdict(set)

    for topic, entries in data.items():
        for entry in entries:
            # UTC → datetime → arrondi → converti Europe/Amsterdam
            timestamp_raw = entry["time"]

            try:
                dt_utc = datetime.strptime(timestamp_raw, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=utc)
            except ValueError:
                dt_utc = datetime.strptime(timestamp_raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=utc)
            dt_local = dt_utc.astimezone(tz_local).replace(microsecond=0)
            timestamp = dt_local.isoformat()

            # Ne garder que la première valeur par seconde pour ce topic
            if timestamp not in per_topic_seen_times[topic]:
                time_series[timestamp][topic] = entry["value"]
                per_topic_seen_times[topic].add(timestamp)
                all_times.add(timestamp)

    # Étape 2 : trier les timestamps (et générer toutes les secondes entre min et max)
    all_times = sorted(all_times)
    if not all_times:
        print("Aucune donnée à exporter.")
        return

    start_time = datetime.fromisoformat(all_times[0])
    end_time = datetime.fromisoformat(all_times[-1])
    full_time_range = []

    t = start_time
    while t <= end_time:
        full_time_range.append(t.isoformat())
        t += timedelta(seconds=1)

    # Étape 3 : écrire le CSV avec forward-fill
    topics = list(data.keys())
    last_values = {topic: "" for topic in topics}

    with open(filename, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)

        # En-tête
        writer.writerow(["time"] + topics)

        # Lignes
        for timestamp in full_time_range:
            row = [timestamp]
            for topic in topics:
                if topic in time_series.get(timestamp, {}):
                    last_values[topic] = time_series[timestamp][topic]
                row.append(last_values[topic])
            writer.writerow(row)

    print(f"CSV généré avec succès : {filename}")