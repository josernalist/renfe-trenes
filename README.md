# Renfe Flota LD Archiver

Automatización en Python que descarga la posición en tiempo real de los trenes de largo recorrido de Renfe cada 30 minutos con GitHub Actions y guarda el JSON con timestamp UTC en `data/YYYY/MM/`.

## Fuente

- **Web**: https://tiempo-real.largorecorrido.renfe.com/
- **JSON**: `https://tiempo-real.largorecorrido.renfe.com/renfe-visor/flotaLD.json?v={timestamp_ms}`

El parámetro `?v=` es un timestamp en milisegundos que el script genera automáticamente para evitar respuestas cacheadas.

## Estructura del repositorio

```
renfe-flota-archiver/
├── .github/
│   └── workflows/
│       ├── fetch.yml            # Descarga cada 30 min
│       └── archive-month.yml    # Comprime datos del mes anterior
├── scripts/
│   └── fetch_flota.py           # Script principal
├── data/
│   ├── latest.json              # Siempre apunta al último archivo guardado
│   └── YYYY/
│       └── MM/
│           └── flota-YYYY-MM-DDTHH-MM-SSZ.json
├── archives/                    # .tar.gz de meses anteriores (creado automáticamente)
└── README.md
```

## Campos del JSON

Cada archivo contiene:

| Campo | Descripción |
|---|---|
| `fechaActualizacion` | Timestamp de la última actualización de Renfe |
| `trenes[]` | Array con todos los trenes activos |
| `trenes[].codComercial` | Número de tren |
| `trenes[].latitud` / `longitud` | Posición GPS actual |
| `trenes[].ultRetraso` | Retraso en minutos (negativo = adelantado) |
| `trenes[].desCorridor` | Línea / corredor del tren |
| `trenes[].codOrigen` / `codDestino` | Códigos de estación origen y destino |
| `trenes[].accesible` | Si el tren es accesible |
| `trenes[].mat` | Número de material rodante |

## Instalación local (Windows)

### 0) Requisitos
- Git instalado
- Python 3.x en PATH (`python --version` debe funcionar)

### 1) Clonar el repo

```powershell
git clone https://github.com/<tu-usuario>/renfe-flota-archiver.git
cd renfe-flota-archiver
```

### 2) Probar en local

```powershell
python .\scripts\fetch_flota.py
Get-ChildItem -Recurse .\data | Format-List
```

Deberías ver un archivo `flota-YYYY-MM-DDTHH-MM-SSZ.json` dentro de `data\YYYY\MM`.

### 3) Commit y push

```powershell
git add .
git commit -m "feat: initial archiver setup"
git push
```

## Activar en GitHub Actions

1. Ve a tu repo en GitHub → pestaña **Actions**
2. Selecciona el workflow **Fetch Renfe Flota LD**
3. Pulsa **Run workflow** para la primera ejecución manual
4. A partir de ahí correrá automáticamente cada 30 minutos

> **Nota**: GitHub Actions puede retrasar hasta ~10 minutos los workflows con cron en repositorios con poca actividad. Es comportamiento normal.

## Consideraciones

- El script **solo guarda un archivo nuevo si el contenido ha cambiado** (comparación SHA-256), evitando duplicados.
- `data/latest.json` siempre apunta al JSON más reciente, útil para consumo externo.
- El workflow mensual comprime `data/YYYY/MM/` en `archives/flota-YYYY-MM.tar.gz` y elimina la carpeta para no saturar el repo.

## Licencia

MIT
