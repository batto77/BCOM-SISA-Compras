import { UnidadMedida } from '../../core/models/parametros.model';

export interface EspecificacionVisible {
  nombre: string;
  valor: string;
  tipoDato?: string;
  cantidad?: string;
  unidad?: string;
}

interface EspecificacionGuardada {
  nombre?: string;
  clave?: string;
  tipo_dato?: string;
  valor?: unknown;
  cantidad?: unknown;
  unidad_medida_id?: number | null;
  unidad_nombre?: string;
  unidad_simbolo?: string;
}

export function parsearEspecificaciones(
  especificaciones: string | null | undefined,
  unidades: UnidadMedida[] = [],
): EspecificacionVisible[] {
  if (!especificaciones) return [];

  try {
    const specs = JSON.parse(especificaciones) as EspecificacionGuardada[];
    if (!Array.isArray(specs)) return [];

    const unidadesPorId = new Map(unidades.map(unidad => [unidad.id, unidad]));
    return specs.map((spec, index) => {
      const unidad = spec.unidad_medida_id
        ? unidadesPorId.get(spec.unidad_medida_id)
        : undefined;

      return {
        nombre: spec.nombre?.trim() || spec.clave?.trim() || `Especificación ${index + 1}`,
        valor: formatearValor(spec.valor),
        tipoDato: formatearTipoDato(spec.tipo_dato),
        cantidad: tieneValor(spec.cantidad) ? formatearValor(spec.cantidad) : undefined,
        unidad: spec.unidad_simbolo
          || unidad?.simbolo
          || spec.unidad_nombre
          || unidad?.nombre
          || (spec.unidad_medida_id ? `Unidad #${spec.unidad_medida_id}` : undefined),
      };
    });
  } catch {
    return [{ nombre: 'Especificaciones', valor: especificaciones }];
  }
}

function formatearTipoDato(tipoDato: string | undefined): string | undefined {
  const tipos: Record<string, string> = {
    booleano: 'Sí / No',
    fecha: 'Fecha',
    numero: 'Número',
    seleccion: 'Selección',
    texto: 'Texto',
  };
  return tipoDato ? (tipos[tipoDato] ?? tipoDato) : undefined;
}

function tieneValor(valor: unknown): boolean {
  return valor !== null && valor !== undefined && valor !== '';
}

function formatearValor(valor: unknown): string {
  if (!tieneValor(valor)) return 'Sin definir';
  if (valor === true) return 'Sí';
  if (valor === false) return 'No';
  if (Array.isArray(valor)) return valor.length ? valor.join(', ') : 'Sin definir';
  if (typeof valor === 'object') return JSON.stringify(valor);
  return String(valor);
}
