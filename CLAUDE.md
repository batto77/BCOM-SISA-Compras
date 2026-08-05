# CLAUDE.md — Reglas operativas para Claude Code

## Idioma
Responder siempre en español. Solo cambiar de idioma si el usuario lo solicita.

---

## Routing de subagentes por modelo

Antes de lanzar un Agent, elegí el modelo según la tarea. El costo y la velocidad importan: no uses Opus donde Haiku alcanza.

### Haiku — búsqueda, lectura y tareas simples
**Cuándo usarlo:** Cualquier tarea que no requiere razonamiento profundo ni generación de código complejo.

```
Agent({ model: "haiku", subagent_type: "Explore", ... })
Agent({ model: "haiku", ... })  // para lookups y lecturas
```

Tareas típicas para Haiku:
- Buscar archivos por nombre o patrón (`find`, `grep`, `ls`)
- Leer un archivo y extraer información específica (campos, valores, conteo)
- Verificar si un símbolo, función o clase existe en el código
- Listar endpoints, imports, dependencias
- Extraer texto de documentos (.docx, .pdf, .eml, .srt)
- Contar ítems, validar formato, comparar valores simples
- Buscar en el historial de git (`git log`, `git grep`)
- Cualquier tarea del agente `Explore` — siempre usar Haiku ahí
- Validar que un archivo cumple una convención de nombre o estructura

### Sonnet — código, escritura y lógica de negocio
**Cuándo usarlo:** Generación de código nuevo, refactors, documentación técnica, lógica compleja pero conocida.

```
Agent({ model: "sonnet", ... })  // default para código
```

Tareas típicas para Sonnet:
- Escribir endpoints FastAPI (rutas, schemas Pydantic, servicios)
- Crear componentes Angular (TypeScript strict, templates, servicios)
- Implementar lógica de negocio (módulos de cotización, comparativo, aprobación)
- Escribir tests unitarios e integración
- Refactorizar código existente
- Crear o editar archivos de documentación (.md)
- Implementar modelos de datos, migraciones, fixtures
- Resolver bugs con contexto claro
- Generar el mock/HTML de pantallas
- Implementar integraciones (BC365, SharePoint, email)

### Opus — arquitectura, decisiones críticas y revisiones
**Cuándo usarlo:** Decisiones que afectan toda la base de código, tradeoffs complejos con múltiples variables, revisiones de seguridad, diseño del modelo de datos canónico.

```
Agent({ model: "opus", ... })  // solo cuando sea justificado
```

Tareas justificadas para Opus:
- Diseñar el modelo de datos definitivo (entidades, relaciones, índices)
- Revisar la arquitectura de un módulo completo antes de implementar
- Evaluar tradeoffs de seguridad (OWASP, autenticación, manejo de secretos)
- Definir la estrategia de integración con BC365 o SharePoint
- Revisar código en busca de vulnerabilidades críticas (`/code-review` o `/security-review`)
- Decidir entre dos enfoques de implementación con impacto en escalabilidad
- Analizar si una decisión de diseño es correcta cuando hay ambigüedad real
- Revisar el modelo de aprobaciones/roles desde seguridad

---

## Regla de escalada

Si empezás con Haiku y la tarea resulta más compleja de lo esperado, escala a Sonnet.
Si empezás con Sonnet y hay una decisión arquitectónica que bloquea, escala a Opus **solo para esa decisión** — no para implementar.

**Nunca uses Opus para tareas que Sonnet puede hacer.** El criterio es: ¿la respuesta correcta depende de razonamiento sobre múltiples sistemas interdependientes y tradeoffs no obvios? Si no, no es Opus.

---

## Paralelismo

Cuando haya tareas independientes, lanzalas en paralelo en el mismo mensaje:

```
// Bien: dos búsquedas independientes en paralelo con Haiku
Agent({ model: "haiku", description: "Buscar endpoints existentes" })
Agent({ model: "haiku", description: "Buscar schemas Pydantic existentes" })

// Mal: lanzar secuencialmente cuando no hay dependencia
```

---

## Stack del proyecto

- **Frontend:** Angular + TypeScript strict — `frontend/`
- **Backend:** Python + FastAPI + Pydantic v2 — `backend/`
- **Integración objetivo:** Microsoft Dynamics 365 Business Central
- **Idioma operativo:** español en todo: código, comentarios cuando aplique, respuestas

Ver `AGENTS.md` para reglas de calidad de código, seguridad OWASP y DoD.
Ver `README.md` para stack completo y convenciones de ramas/PR.

---

## Contexto del proyecto

Sistema de gestión de compras y cotizaciones para SISA (empresa colombiana de tecnología).
Proceso: solicitud → cotización a proveedores → comparativo → aprobación → OC → recepción → evaluación de proveedor.
Documentación completa en `docs/` y memoria del proyecto en `.claude/projects/`.

---

## Decisiones de arquitectura registradas

| Fecha | Decisión | Motivo |
|---|---|---|
| 2026-06-01 | No usar Copilot/IA externa para analizar cotizaciones | Riesgo de confidencialidad + resultados no confiables. Ver memoria del proyecto. |
| 2026-06-01 | Prioridad de construcción: 1) Cotizaciones, 2) Proveedores, 3) Integración SD | Acordado en sesión de requerimientos 2026-05-20 |
| 2026-06-02 | Wizard de 3 pasos para armar solicitud (Productos/Servicios/Software) | Revisado con mock interactivo, aprobado por usuario |
