# Backend - FastAPI

## 1. Objetivo
API del sistema de compras/abastecimiento.
Expone endpoints para oportunidades, cotizaciones, aprobaciones y evaluación de proveedores.

## 2. Stack
- Python 3.11+
- FastAPI
- Pydantic v2
- Uvicorn

## 3. Estructura sugerida
```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   ├── core/         # config, seguridad, middlewares
│   ├── schemas/      # contratos entrada/salida
│   ├── services/     # logica de negocio
│   └── repositories/ # acceso a datos
├── tests/
├── requirements.txt
└── Dockerfile
```

## 4. Variables minimas (ejemplo)
- `APP_ENV=local|dev|qa|prod`
- `API_PREFIX=/api/v1`
- `HOST=0.0.0.0`
- `PORT=8000`
- `CORS_ALLOWED_ORIGINS=http://localhost:4200`
- `LOG_LEVEL=INFO`

## 5. Comandos locales
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest
```

## 6. Docker (componente independiente)
Desde la carpeta `backend`:
```bash
docker build -t sisa-backend -f Dockerfile .
docker run --rm --name sisa-backend -p 8000:8000 sisa-backend
```

## 7. Seguridad minima esperada (OWASP)
- Validacion estricta de input con Pydantic.
- Controles de autenticacion y autorizacion por rol.
- Manejo de errores con mensajes controlados (sin fuga de datos).
- Logging estructurado sin secretos.
- CORS/headers de seguridad configurados explicitamente.
- Limitacion de abuso de API (rate limit/throttling segun caso).
- Gestion de secretos por entorno (no hardcodear credenciales).
- Revision periodica de dependencias y vulnerabilidades.

## 8. Criterios de calidad
- Contratos API claros y versionados (`/api/v1`).
- Separacion de responsabilidades por capas.
- Cobertura de pruebas en casos funcionales y de error.
- Codigo legible, tipado y documentado cuando sea necesario.
