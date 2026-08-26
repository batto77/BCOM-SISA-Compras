/**
 * Prioridades de una oportunidad, definidas por el impacto en la operación.
 *
 * Fuente única: los badges, los selectores y los tooltips de ayuda salen todos
 * de acá. Antes el mapa de colores estaba duplicado en cada componente, lo que
 * obligaba a tocar cinco archivos para cambiar una etiqueta.
 */
export interface Prioridad {
  id: string;
  nombre: string;
  /** Estado de la operación que justifica esta prioridad. Se usa como ayuda en pantalla. */
  descripcion: string;
  badgeClass: string;
}

export const PRIORIDADES: Prioridad[] = [
  {
    id: 'critico',
    nombre: 'Crítico',
    descripcion: 'Operación totalmente interrumpida',
    badgeClass: 'badge-danger',
  },
  {
    id: 'alto',
    nombre: 'Alto',
    descripcion: 'Operación con afectación significativa',
    badgeClass: 'badge-warning',
  },
  {
    id: 'medio',
    nombre: 'Medio',
    descripcion: 'Operación sin impacto actual, pero con riesgo de escalamiento',
    badgeClass: 'badge-primary',
  },
  {
    id: 'bajo',
    nombre: 'Bajo',
    descripcion: 'Operación sin impacto y sin riesgo relevante',
    badgeClass: 'badge-secondary',
  },
];

/**
 * Equivalencias de los valores anteriores (urgente/alta/normal/baja).
 * Los registros viejos se migran en el backend, pero esto evita que una
 * oportunidad histórica se vea sin color o sin nombre si algo quedó sin migrar.
 */
const EQUIVALENCIAS_ANTERIORES: Record<string, string> = {
  urgente: 'critico',
  alta: 'alto',
  normal: 'medio',
  baja: 'bajo',
};

function resolver(prioridad: string | null | undefined): Prioridad | undefined {
  if (!prioridad) return undefined;
  const clave = prioridad.trim().toLowerCase();
  const id = EQUIVALENCIAS_ANTERIORES[clave] ?? clave;
  return PRIORIDADES.find(p => p.id === id);
}

export function getPrioridadBadgeClass(prioridad: string | null | undefined): string {
  return resolver(prioridad)?.badgeClass ?? 'badge-secondary';
}

export function getPrioridadNombre(prioridad: string | null | undefined): string {
  return resolver(prioridad)?.nombre ?? (prioridad ?? '—');
}

export function getPrioridadDescripcion(prioridad: string | null | undefined): string {
  return resolver(prioridad)?.descripcion ?? '';
}

/** Texto para tooltips: "Crítico — Operación totalmente interrumpida". */
export function getPrioridadAyuda(prioridad: string | null | undefined): string {
  const p = resolver(prioridad);
  return p ? `${p.nombre} — ${p.descripcion}` : '';
}
