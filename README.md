# SISA Compras - Base Documental del Proyecto

## 1. Proposito
Este repositorio define la base documental para una solucion de compras y abastecimiento con trazabilidad end-to-end:
- Oportunidad de compra/cotización
- Gestion de proveedores y cotizaciones
- Aprobacion de gasto
- Emision de orden de compra
- Recepcion del bien/servicio
- Evaluacion y reevaluacion de proveedores

## 2. Alcance funcional (alto nivel)
La plataforma cubrira el flujo completo desde la necesidad hasta el cierre del caso, alineado con:
- Procedimiento de compras (`CYL-P-001`)
- Procedimiento de seleccion/evaluacion/reevaluacion de proveedores (`CYL-P-010`)

## 3. Stack tecnico oficial
- Frontend: `Angular` (TypeScript, strict mode)
- Backend: `Python` con `FastAPI`
- Integracion objetivo: `Microsoft Dynamics 365 Business Central`

## 4. Estructura del repositorio
```text
.
├── README.md
├── AGENTS.md
├── docs/
├── frontend/
│   └── README.md
└── backend/
    └── README.md
```

## 5. Flujo de trabajo local
### Frontend (Angular)
```bash
cd frontend
npm install
npm run start
```

### Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6. Contenerizacion separada por componente
Cada componente se construye y despliega por separado.

### Frontend container
```bash
docker build -t sisa-frontend -f frontend/Dockerfile frontend
docker run --rm --name sisa-frontend -p 4200:80 sisa-frontend
```

### Backend container
```bash
docker build -t sisa-backend -f backend/Dockerfile backend
docker run --rm --name sisa-backend -p 8000:8000 sisa-backend
```

## 7. Contrato de comunicacion entre servicios
- Frontend expuesto en: `http://localhost:4200`
- Backend API expuesta en: `http://localhost:8000`
- Base URL sugerida para frontend: `http://localhost:8000/api/v1`
- El frontend consume solo API publica del backend (sin acceso directo a DB)

## 8. Convenciones globales
- Idioma operativo del proyecto: espanol
- Convencion de ramas:
  - `main`: rama estable
  - `develop`: integracion
  - `feature/<modulo>-<descripcion-corta>`
  - `fix/<modulo>-<descripcion-corta>`
- Convencion de PR:
  - Titulo claro con prefijo (`feat:`, `fix:`, `docs:`, `refactor:`)
  - Descripcion de alcance, riesgo y validacion ejecutada
  - Checklist de seguridad y calidad completado
- Todo cambio debe mantener coherencia con `AGENTS.md`
- Codigo legible, modular, tipado y documentado cuando el contexto lo requiera
- No introducir secretos en codigo fuente
- Registrar decisiones tecnicas relevantes en documentacion

## 9. Seguridad obligatoria
El proyecto adopta como baseline:
- `OWASP Top 10`
- `OWASP API Security Top 10`
- `OWASP ASVS Level 2`

Toda implementacion nueva debe demostrar controles de seguridad acordes a ese baseline.

## 10. Documentacion por componente
- Frontend: [frontend/README.md](frontend/README.md)
- Backend: [backend/README.md](backend/README.md)
- Reglas operativas para agentes y asistentes: [AGENTS.md](AGENTS.md)
