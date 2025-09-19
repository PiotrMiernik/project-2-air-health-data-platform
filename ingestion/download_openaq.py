import os
import json
import time
import math
import boto3
import requests
import unicodedata
from io import BytesIO
from datetime import datetime, timezone

# === Konfiguracja API v3 ===
OPENAQ_API_URL = "https://api.openaq.org/v3"
API_KEY = os.environ.get("OPENAQ_API_KEY")  # wymagane w v3
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

# Parametry (v3 parameter IDs z dokumentacji: pm10=1, pm25=2, no2=7, so2=9, o3=10, co=8)
POLLUTANTS = {
    "pm25": 2,
    "pm10": 1,
    "no2": 7,
    "o3": 10,
    "co": 8,
    "so2": 9,
}

# Okres
DATE_FROM = "2014-01-01"
DATE_TO = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Limity miast (połowa poprzednich; 3 domyślnie; LU/MT=1)
CITY_LIMITS = {
    "DE": 5, "FR": 5, "IT": 4, "ES": 4, "PL": 4,
    "LU": 1, "MT": 1, "default": 3
}

# UE27 (ISO2)
EU27_COUNTRIES = [
    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR",
    "HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK",
    "SI","ES","SE"
]

# Największe miasta (ang./lokalne egzonimy; lista skrócona do limitu CITY_LIMITS)
TOP_CITIES_BY_COUNTRY = {
    "AT": ["Vienna", "Graz", "Linz"],
    "BE": ["Brussels", "Antwerp", "Ghent"],
    "BG": ["Sofia", "Plovdiv", "Varna"],
    "HR": ["Zagreb", "Split", "Rijeka"],
    "CY": ["Nicosia", "Limassol", "Larnaca"],
    "CZ": ["Prague", "Brno", "Ostrava"],
    "DK": ["Copenhagen", "Aarhus", "Odense"],
    "EE": ["Tallinn", "Tartu", "Narva"],
    "FI": ["Helsinki", "Espoo", "Tampere"],
    "FR": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
    "DE": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt"],
    "GR": ["Athens", "Thessaloniki", "Patras"],
    "HU": ["Budapest", "Debrecen", "Szeged"],
    "IE": ["Dublin", "Cork", "Limerick"],
    "IT": ["Rome", "Milan", "Naples", "Turin"],
    "LV": ["Riga", "Daugavpils", "Liepaja"],
    "LT": ["Vilnius", "Kaunas", "Klaipeda"],
    "LU": ["Luxembourg"],
    "MT": ["Valletta"],
    "NL": ["Amsterdam", "Rotterdam", "The Hague"],
    "PL": ["Warsaw", "Krakow", "Lodz", "Wroclaw"],
    "PT": ["Lisbon", "Porto", "Vila Nova de Gaia"],
    "RO": ["Bucharest", "Cluj-Napoca", "Timisoara"],
    "SK": ["Bratislava", "Kosice", "Presov"],
    "SI": ["Ljubljana", "Maribor", "Celje"],
    "ES": ["Madrid", "Barcelona", "Valencia", "Seville"],
    "SE": ["Stockholm", "Gothenburg", "Malmo"],
}

# Aliasowa normalizacja nazw (egzonimy/diakrytyki)
CITY_ALIASES = {
    # DE
    "munich": ["muenchen", "münchen", "munchen"],
    "cologne": ["koeln", "köln"],
    # IT
    "rome": ["roma"],
    "milan": ["milano"],
    "naples": ["napoli"],
    "turin": ["torino"],
    # ES
    "seville": ["sevilla"],
    # FR
    "lyon": [],
    "marseille": [],
    # NL
    "the hague": ["den haag", "'s-gravenhage", "s-gravenhage"],
    # AT / CZ / PL / GR / RO / SK
    "vienna": ["wien"],
    "prague": ["praha"],
    "krakow": ["kraków", "krakow"],
    "lodz": ["łódź", "lodz"],
    "wroclaw": ["wrocław", "wroclaw"],
    "athens": ["athína", "athina"],
    "thessaloniki": ["thessaloníki", "salonica", "saloniki"],
    "bucharest": ["bucuresti", "bucurești"],
    "timisoara": ["timișoara", "timisoara"],
    "kosice": ["košice", "kosice"],
    "presov": ["prešov", "presov"],
    # PT
    "lisbon": ["lisboa"],
    # SE
    "malmo": ["malmö"],
    "gothenburg": ["goteborg", "göteborg", "goteburg"],
    # LV/LT
    "klaipeda": ["klaipėda"],
    "liepaja": ["liepāja"],
}

# AWS
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PREFIX = os.environ.get("S3_PREFIX", "bronze/openaq/v3/eu27/")
s3 = boto3.client("s3")

# --- narzędzia ---

def _norm(txt: str) -> str:
    if txt is None:
        return ""
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join([c for c in txt if not unicodedata.combining(c)])
    return txt.lower().strip()

def _city_matches(locality: str, target: str) -> bool:
    n_loc = _norm(locality)
    n_tar = _norm(target)
    if n_loc == n_tar:
        return True
    # aliasy
    al = CITY_ALIASES.get(n_tar, [])
    return n_loc in {_norm(a) for a in ([target] + al)}

def _request(url: str, params: dict = None, retries: int = 3, backoff: float = 1.5):
    if not API_KEY:
        raise RuntimeError("Brak OPENAQ_API_KEY w zmiennych środowiskowych.")
    for attempt in range(retries):
        r = requests.get(url, headers=HEADERS, params=params, timeout=60)
        if r.status_code == 429:
            time.sleep(backoff * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()  # jeśli dalej 429, podniesie wyjątek

def list_locations_for_city(iso: str, city: str):
    # Pobierz wszystkie lokalizacje w kraju, potem filtruj po locality ~ city
    url = f"{OPENAQ_API_URL}/locations"
    page = 1
    out = []
    while True:
        data = _request(url, params={"iso": iso, "limit": 1000, "page": page})
        for loc in data.get("results", []):
            locality = loc.get("locality") or loc.get("name")  # fallback
            if locality and _city_matches(locality, city):
                out.append(loc)
        found = data.get("meta", {}).get("found") or 0
        limit = data.get("meta", {}).get("limit") or 1000
        if page * limit >= found:
            break
        page += 1
    return out

def list_sensors_for_locations(location_ids):
    sensors = []
    for lid in location_ids:
        url = f"{OPENAQ_API_URL}/locations/{lid}/sensors"
        data = _request(url, params={"limit": 1000, "page": 1})
        sensors.extend(data.get("results", []))
    return sensors

def sensor_coverage_hours(sensor_id: int, date_from: str, date_to: str):
    # Pobiera 1 rekord z agregacji godzinowej, ale czyta coverage.observedCount z odpowiedzi
    url = f"{OPENAQ_API_URL}/sensors/{sensor_id}/measurements/hourly"
    data = _request(url, params={
        "datetime_from": date_from,
        "datetime_to": date_to,
        "limit": 1,
        "page": 1
    })
    results = data.get("results", [])
    if results:
        cov = results[0].get("coverage") or {}
        return int(cov.get("observedCount") or 0)
    # jeśli brak wyników, observedCount=0
    return 0

def pick_best_sensor_per_parameter(sensors, param_id: int, date_from: str, date_to: str):
    candidates = [s for s in sensors if (s.get("parameter") or {}).get("id") == param_id]
    best = None
    best_cnt = -1
    for s in candidates:
        sid = s.get("id")
        try:
            cnt = sensor_coverage_hours(sid, date_from, date_to)
        except requests.HTTPError:
            cnt = 0
        if cnt > best_cnt:
            best_cnt = cnt
            best = s
    return best, best_cnt

def save_json_to_s3(obj: dict, key: str):
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=BytesIO(json.dumps(obj, ensure_ascii=False).encode("utf-8")),
        ContentType="application/json",
    )

def stream_hourly_to_s3(sensor_id: int, country: str, city: str, param_name: str, date_from: str, date_to: str, request_id: str):
    # Paginacja i zapis stron do S3
    url = f"{OPENAQ_API_URL}/sensors/{sensor_id}/measurements/hourly"
    page = 1
    total_found = None
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    city_slug = _norm(city).replace(" ", "-")
    while True:
        data = _request(url, params={
            "datetime_from": date_from,
            "datetime_to": date_to,
            "limit": 1000,
            "page": page
        })
        meta = data.get("meta", {})
        found = meta.get("found") or 0
        limit = meta.get("limit") or 1000
        total_found = found if total_found is None else total_found
        part_key = f"{S3_PREFIX}{country}/{city_slug}/{param_name}/sensor={sensor_id}/page={page}_{request_id}_{ts}.json"
        save_json_to_s3(data, part_key)
        if page * limit >= found or found == 0:
            break
        page += 1
    return total_found or 0

def lambda_handler(event, context):
    if not S3_BUCKET:
        return {"statusCode": 500, "body": json.dumps({"error": "Brak S3_BUCKET w env"})}
    if not API_KEY:
        return {"statusCode": 500, "body": json.dumps({"error": "Brak OPENAQ_API_KEY w env (wymagany w v3)"})}

    stored = {}
    summary = []
    for iso in EU27_COUNTRIES:
        limit = CITY_LIMITS.get(iso, CITY_LIMITS["default"])
        cities = TOP_CITIES_BY_COUNTRY.get(iso, [])[:limit]
        for city in cities:
            city_key = f"{iso}:{city}"
            try:
                locs = list_locations_for_city(iso, city)
                if not locs:
                    stored[city_key] = "WARN: brak lokalizacji w OpenAQ"
                    continue
                loc_ids = [loc["id"] for loc in locs]
                sensors = list_sensors_for_locations(loc_ids)

                chosen = {}
                for pname, pid in POLLUTANTS.items():
                    best, observed = pick_best_sensor_per_parameter(sensors, pid, DATE_FROM, DATE_TO)
                    if not best:
                        stored[f"{city_key}_{pname}"] = "WARN: brak sensora dla parametru"
                        continue
                    sid = best["id"]
                    n_saved = stream_hourly_to_s3(
                        sensor_id=sid,
                        country=iso,
                        city=city,
                        param_name=pname,
                        date_from=DATE_FROM,
                        date_to=DATE_TO,
                        request_id=context.aws_request_id if context else "local"
                    )
                    stored[f"{city_key}_{pname}"] = f"OK: sensor {sid}, records={n_saved}"
                    chosen[pname] = {"sensor_id": sid, "observed_hours": observed}

                # manifest miasta
                manifest_key = f"{S3_PREFIX}{iso}/{_norm(city).replace(' ','-')}/_manifest_{context.aws_request_id if context else 'local'}.json"
                save_json_to_s3({
                    "iso": iso,
                    "city": city,
                    "date_from": DATE_FROM,
                    "date_to": DATE_TO,
                    "chosen_sensors": chosen
                }, manifest_key)
                summary.append({"iso": iso, "city": city, "chosen": chosen})
            except Exception as e:
                stored[city_key] = f"ERROR: {str(e)}"

    return {
        "statusCode": 200,
        "body": json.dumps({"stored_files": stored, "summary": summary}, ensure_ascii=False)
    }
