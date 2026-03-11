#!/usr/bin/env python3
"""
Renfe Flota LD Archiver
Descarga https://tiempo-real.largorecorrido.renfe.com/renfe-visor/flotaLD.json
y lo guarda con timestamp UTC en data/YYYY/MM/.
Solo guarda si el contenido ha cambiado respecto al archivo anterior.
"""

import os
import json
import hashlib
import urllib.request
import datetime
import glob
import sys
import time

BASE_URL = "https://tiempo-real.largorecorrido.renfe.com/renfe-visor/flotaLD.json"


def get_url():
    """Genera la URL con timestamp Unix para evitar caché del servidor."""
    ts = int(time.time() * 1000)  # milisegundos, como hace la web original
    return f"{BASE_URL}?v={ts}"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch() -> bytes:
    url = get_url()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "renfe-flota-archiver/1.0",
            "Referer": "https://tiempo-real.largorecorrido.renfe.com/",
            "Accept": "application/json, */*",
        },
        method="GET",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                return resp.read()
        except Exception as e:
            if attempt == 2:
                print(f"ERROR tras 3 intentos: {e}", file=sys.stderr)
                sys.exit(1)
            print(f"Intento {attempt + 1} fallido: {e}. Reintentando...", file=sys.stderr)
            time.sleep(5)


def last_saved_bytes(out_dir: str):
    """Devuelve el contenido del último archivo guardado en out_dir, o None."""
    files = sorted(glob.glob(os.path.join(out_dir, "flota-*.json")))
    if not files:
        return None
    with open(files[-1], "rb") as f:
        return f.read()


def main():
    now_utc = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None)
    out_dir = os.path.join("data", now_utc.strftime("%Y"), now_utc.strftime("%m"))
    os.makedirs(out_dir, exist_ok=True)

    data = fetch()

    # Validación JSON
    try:
        parsed = json.loads(data)
        num_trenes = len(parsed.get("trenes", []))
        fecha_renfe = parsed.get("fechaActualizacion", "desconocida")
    except Exception:
        print("WARNING: El contenido no es JSON válido (se guarda igualmente).", file=sys.stderr)
        num_trenes = "?"
        fecha_renfe = "desconocida"

    # Solo guardar si hay cambios
    prev = last_saved_bytes(out_dir)
    if prev is not None and sha256(data) == sha256(prev):
        print(f"Sin cambios respecto al archivo anterior. No se crea archivo nuevo.")
        sys.exit(0)

    # Guardar con timestamp en el nombre
    ts_str = now_utc.isoformat().replace(":", "-") + "Z"
    filename = f"flota-{ts_str}.json"
    out_path = os.path.join(out_dir, filename)

    with open(out_path, "wb") as f:
        f.write(data)

    # Puntero estable al último archivo
    latest_path = os.path.join("data", "latest.json")
    with open(latest_path, "wb") as f:
        f.write(data)

    print(f"Guardado: {out_path}")
    print(f"  Trenes activos : {num_trenes}")
    print(f"  Actualizado    : {fecha_renfe}")


if __name__ == "__main__":
    main()
