# Frontend - Angular

## 1. Objetivo
Aplicacion web del sistema de compras/abastecimiento.
Debe consumir exclusivamente la API del backend FastAPI.

## 2. Stack
- Angular (version LTS recomendada)
- TypeScript en modo estricto
- RxJS
- Angular Router + guards por rol/permisos

## 3. Estructura sugerida
```text
frontend/
├── src/
│   ├── app/
│   │   ├── core/        # servicios base, interceptores, guards
│   │   ├── shared/      # componentes reutilizables
│   │   └── features/    # modulos funcionales (solicitudes, proveedores, etc.)
│   ├── assets/
│   └── environments/
├── package.json
└── Dockerfile
```

## 4. Variables minimas (ejemplo)
Definir por ambiente en `src/environments/*` o runtime config:
- `apiBaseUrl=http://localhost:8000/api/v1`
- `appEnv=local|dev|qa|prod`
- `logLevel=info|warn|error`

## 5. Comandos locales
```bash
npm install
npm run start
npm run build
npm run test
npm run lint
```

## 6. Docker (componente independiente)
Desde la carpeta `frontend`:
```bash
docker build -t sisa-frontend -f Dockerfile .
docker run --rm --name sisa-frontend -p 4200:80 sisa-frontend
```

## 7. Seguridad minima esperada (OWASP)
- Validacion de formularios y datos antes de enviar al backend.
- Manejo centralizado de errores HTTP.
- No exponer secretos ni llaves en cliente.
- Uso de guards para rutas protegidas.
- Sanitizacion de contenido dinamico.
- Politicas CSP y headers de seguridad via servidor web/reverse proxy.

## 8. Criterios de calidad
- Componentes pequenos y enfocadas en una responsabilidad.
- Servicios reutilizables para logica de negocio y consumo API.
- Tipado estricto sin `any` salvo casos justificados.
- Codigo legible y documentado cuando la logica no sea obvia.
