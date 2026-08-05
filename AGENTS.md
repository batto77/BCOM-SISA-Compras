# AGENTS - Reglas Operativas del Proyecto

## 1. Idioma
- Todas las respuestas al usuario deben ser en espanol.
- Solo cambiar de idioma si el usuario lo solicita explicitamente.

## 2. Stack obligatorio
- Frontend: `Angular` + `TypeScript`.
- Backend: `Python` + `FastAPI`.
- No proponer ni generar implementaciones fuera de este stack, salvo instruccion explicita del usuario.

## 3. Calidad de codigo obligatoria
- Codigo legible, modular y mantenible.
- Tipado estricto:
  - TypeScript con `strict: true`.
  - Python con type hints completos.
- Nombres claros para modulos, clases, funciones y variables.
- Documentacion en codigo:
  - Docstrings en modulos/funciones complejas.
  - Comentarios solo cuando aporten contexto no obvio.
- Evitar duplicacion de logica y preferir abstracciones pequenas y claras.

## 4. Seguridad obligatoria (baseline)
Toda salida de codigo debe alinearse con:
- `OWASP Top 10`
- `OWASP API Security Top 10`
- `OWASP ASVS L2`

Controles minimos esperados:
- Validacion estricta de entradas (frontend y backend).
- Autenticacion y autorizacion por minimo privilegio.
- Manejo seguro de sesiones/tokens.
- Manejo de errores sin filtrar datos sensibles.
- Logs estructurados sin secretos ni datos personales innecesarios.
- Proteccion de secretos via variables de entorno y gestor seguro.
- Control de CORS, headers de seguridad y hardening de transporte.
- Control de dependencias (versionado, vulnerabilidades, actualizaciones).
- Defensas para abuso de API (rate limit, throttling, validacion de payload).

## 5. Reglas para codigo frontend (Angular)
- Usar arquitectura por dominios/feature modules.
- Centralizar consumo HTTP en servicios.
- Manejar errores de API con interceptores.
- No almacenar secretos en cliente.
- Sanitizar contenido dinamico y evitar bypass de seguridad del framework.

## 6. Reglas para codigo backend (FastAPI)
- Definir contratos de entrada/salida con Pydantic.
- Validar payloads, parametros y headers.
- Separar capas: API, servicios, dominio, infraestructura.
- Responder con codigos HTTP correctos y mensajes controlados.
- Incluir pruebas para casos felices, validaciones y fallas esperadas.

## 7. Regla de contenerizacion
- Frontend y backend se construyen y ejecutan en contenedores separados.
- Cada componente mantiene su propio ciclo de build/run/deploy.
- No acoplar artefactos de build entre componentes.

## 8. Definicion de terminado (DoD) para cambios
Antes de cerrar cualquier cambio:
1. Compila y/o corre localmente.
2. Mantiene coherencia con README global y README del componente.
3. Cumple baseline OWASP definido.
4. Entrega codigo legible y documentado.
