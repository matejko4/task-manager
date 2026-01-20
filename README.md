# 📋 Task Manager Web App

Webová aplikace pro správu úkolů postavená na Flask frameworku s podporou PostgreSQL a SQLite databáze.

## ✨ Funkce

- 🔐 **Registrace a přihlášení uživatelů** - bezpečná autentizace s hashováním hesel
- ✅ **Správa úkolů** - vytváření, úprava, mazání a označování jako dokončené
- 🎯 **Priority úkolů** - nízká, střední a vysoká priorita
- 📱 **Responzivní design** - moderní UI pro desktop i mobil
- 🐳 **Docker podpora** - snadné nasazení pomocí Docker Compose

## 🚀 Instalace a spuštění

### Lokální spuštění (SQLite)

1. Nainstaluj závislosti:
```bash
pip install -r requirements.txt
```

2. Spusť aplikaci:
```bash
python app.py
```

3. Otevři v prohlížeči:
```
http://127.0.0.1:5000
```

### Docker spuštění (PostgreSQL)

1. Spusť pomocí Docker Compose:
```bash
docker-compose up --build
```

2. Otevři v prohlížeči:
```
http://localhost:5000
```

## ⚙️ Konfigurace

Aplikace podporuje konfiguraci pomocí proměnných prostředí:

| Proměnná | Popis | Výchozí hodnota |
|----------|-------|-----------------|
| `SECRET_KEY` | Tajný klíč pro session | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | URL databáze | `sqlite:///tasks.db` |

### Podporované databáze
- **SQLite**: `sqlite:///tasks.db`
- **PostgreSQL**: `postgresql://user:password@host:port/database`
- **MySQL**: `mysql://user:password@host:port/database`

## 🛠️ Použité technologie

- **Backend**: Flask 3.0, Flask-SQLAlchemy, Flask-Migrate
- **Databáze**: PostgreSQL / SQLite
- **Frontend**: HTML5, CSS3, Jinja2 šablony
- **Kontejnerizace**: Docker, Docker Compose
- **Bezpečnost**: Werkzeug (hashování hesel)

## 📁 Struktura projektu

```
task-manager/
├── app.py                 # Hlavní Flask aplikace
├── requirements.txt       # Python závislosti
├── Dockerfile            # Docker konfigurace
├── docker-compose.yml    # Docker Compose konfigurace
├── .gitignore            # Git ignore soubor
├── .env.example          # Příklad konfigurace prostředí
├── .github/
│   └── workflows/
│       └── docker-publish.yml  # GitHub Actions pro Docker
├── migrations/           # Databázové migrace (Alembic)
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
├── templates/            # Jinja2 šablony
│   ├── base.html         # Základní šablona
│   ├── login.html        # Přihlášení
│   ├── register.html     # Registrace
│   ├── dashboard.html    # Dashboard s úkoly
│   ├── add_task.html     # Přidání úkolu
│   ├── edit_task.html    # Úprava úkolu
│   └── macros.html       # Makra pro šablony
└── static/
    └── css/
        └── style.css     # Styly
```

## 📝 Licence

MIT

