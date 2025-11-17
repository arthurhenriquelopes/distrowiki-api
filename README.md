# DistroWiki API

FastAPI backend for DistroWiki - Linux distribution catalog with Google Sheets integration.

## 🚀 Features

- FastAPI-based REST API
- Google Sheets data integration (72+ Linux distributions)
- Intelligent caching system (24-hour TTL)
- Pagination and filtering support
- CORS enabled for frontend integration

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🏃 Running Locally

```bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`

## 📚 API Endpoints

- **GET /distros** - List all distributions with pagination
- **GET /distros/{id}** - Get details of a specific distribution
- **POST /distros/refresh** - Force cache refresh
- **GET /distros/cache/info** - Get cache information
- **GET /docs** - Interactive API documentation (Swagger UI)

## 🔍 Query Parameters

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)
- `family` - Filter by Linux family
- `desktop_env` - Filter by desktop environment
- `search` - Search by name or description
- `sort_by` - Sort field (name, release_date)
- `order` - Sort order (asc, desc)
- `force_refresh` - Force cache update

## 📊 Data Source

Data is fetched from Google Sheets and includes:
- Distribution name and description
- Family/base information
- Desktop environments
- Release dates
- Package managers
- Architecture support

## 🛠️ Environment Variables

```
ENVIRONMENT=production
USE_REDIS_CACHE=false
```

## 📝 License

MIT - See LICENSE file

## 🔗 Links

- **Frontend Repository**: https://github.com/tutujokes/distrowiki
- **Main Project**: https://github.com/tutujokes/DistroWiki
