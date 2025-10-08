import os, json, time, random
from io import BytesIO
from datetime import datetime, timezone
import boto3, requests
from botocore.exceptions import ClientError

OPENAQ_LOCATIONS   = "https://api.openaq.org/v3/locations"
OPENAQ_LOC_SENSORS = "https://api.openaq.org/v3/locations/{id}/sensors"
OPENAQ_SENSOR_YEARLY = "https://api.openaq.org/v3/sensors/{id}/days/yearly"
PM25_ID = 2

API_KEY   = os.environ.get("OPENAQ_API_KEY")
HEADERS   = {"X-API-Key": API_KEY} if API_KEY else {}
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_PREFIX = os.environ.get("S3_PREFIX", "bronze/openaq/v3/eu27/pm25/yearly/")

EU27 = ["AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT",
        "LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"]
s3 = boto3.client("s3")

def _to_int(x, d=0):
    try: return int(x)
    except (TypeError, ValueError): return d

def _get_json(url, params=None, retries=6, base=0.7):
    for k in range(retries):
        r = requests.get(url, headers=HEADERS, params=params or {}, timeout=60)
        if r.status_code in (429,500,502,503,504):
            time.sleep((base * (2 ** k)) + random.uniform(0, 0.3))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()

def best_sensor_pm25_for_country(iso: str) -> int | None:
    """Returns the ID of the PM2.5 sensor with the highest coverage.observedCount in the country."""
    best = (None, -1)
    page = 1
    while True:
        locs = _get_json(OPENAQ_LOCATIONS, params={"iso": iso, "parameters_id": PM25_ID, "limit": 1000, "page": page})
        for loc in locs.get("results", []):
            lid = loc.get("id")
            if not lid:
                continue
            sp = 1
            while True:
                sens = _get_json(OPENAQ_LOC_SENSORS.format(id=lid), params={"limit": 1000, "page": sp})
                for s in sens.get("results", []):
                    if (s.get("parameter") or {}).get("id") != PM25_ID:
                        continue
                    cov = s.get("coverage") or {}
                    score = _to_int(cov.get("observedCount"), 0)
                    if score > best[1]:
                        best = (s.get("id"), score)
                smeta = sens.get("meta", {})
                sfound = _to_int(smeta.get("found"), 0)
                slimit = _to_int(smeta.get("limit"), 1000)
                if slimit <= 0 or (sp * slimit) >= sfound:
                    break
                sp += 1
                time.sleep(0.05)
        meta = locs.get("meta", {})
        found = _to_int(meta.get("found"), 0)
        limit = _to_int(meta.get("limit"), 1000)
        if limit <= 0 or (page * limit) >= found:
            break
        page += 1
        time.sleep(0.05)
    return best[0]

def fetch_yearly(sensor_id: int) -> list[dict]:
    """Returns the annual averages for a sensor from the /days/yearly endpoint."""
    page, rows = 1, []
    while True:
        j = _get_json(OPENAQ_SENSOR_YEARLY.format(id=sensor_id), params={"limit": 1000, "page": page})
        rows.extend(j.get("results", []))
        meta = j.get("meta", {})
        found = _to_int(meta.get("found"), 0)
        limit = _to_int(meta.get("limit"), 1000)
        if limit <= 0 or (page * limit) >= found:
            break
        page += 1
        time.sleep(0.05)
    return rows

def lambda_handler(event, context):
    if not API_KEY:
        return {"statusCode": 500, "body": json.dumps({"error": "Missing OPENAQ_API_KEY"})}
    if not S3_BUCKET:
        return {"statusCode": 500, "body": json.dumps({"error": "Missing S3_BUCKET"})}

    countries = (event.get("countries") if isinstance(event, dict) else None) or EU27
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary = {}

    for iso in countries:
        try:
            sid = best_sensor_pm25_for_country(iso)
            if not sid:
                summary[iso] = "WARN: no PM2.5 sensor"
                continue

            yearly = fetch_yearly(sid)
            key = f"{S3_PREFIX}{iso}/pm25_yearly_sensor_{sid}_{ts}.json"
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=BytesIO(json.dumps({"iso": iso, "sensor_id": sid, "yearly": yearly}, ensure_ascii=False).encode("utf-8")),
                ContentType="application/json",
            )
            summary[iso] = f"OK: sensor={sid} years={len(yearly)}"
            time.sleep(0.3)
        except requests.HTTPError as e:
            summary[iso] = f"ERROR HTTP {getattr(e.response, 'status_code', 'NA')}"
        except ClientError as e:
            summary[iso] = f"AWS ERROR: {str(e)}"
        except Exception as e:
            summary[iso] = f"ERROR: {str(e)}"

    return {"statusCode": 200, "body": json.dumps({"stored": summary}, ensure_ascii=False)}
