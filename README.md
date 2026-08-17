# தமிழ் ஜோதிடம்

Tamil Astrology / Thirukanitha Panchangam Web Application

## Installation

1. Create a virtual environment:

```powershell
python -m venv myenv
myenv\Scripts\activate
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running the application

```powershell
python app.py
```

Open `http://127.0.0.1:5001`.

## Project structure

- `app.py` — Flask entrypoint
- `config.py` — application settings
- `astrology/` — calculation engine modules
- `routes/` — web and API routes
- `services/` — calculation orchestration
- `templates/` — Jinja2 views
- `static/` — CSS/JS assets
- `tests/` — pytest coverage

## Calculation architecture

- Astronomical engine: Swiss Ephemeris via `pyswisseph`
- Astrological mapping: sign, nakshatra, pada, house, dasa
- Panchangam rules: Tithi, Yoga, Karana, sunrise/sunset
- Presentation: Flask + Jinja2

## Configuration

Use `.env` or environment variables:

- `SECRET_KEY`
- `TIMEZONE`
- `SIDEREAL_MODE` (default: `LAHIRI`)
- `NODE_MODE` (default: `MEAN`)
- `HOUSE_SYSTEM` (default: `P`)
- `EPHEMERIS_PATH`
- `DEBUG`

## Testing

```powershell
python -m pytest
```
