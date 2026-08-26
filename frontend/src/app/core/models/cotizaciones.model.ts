export interface ItemCotizacionForm {
  item_solicitud_id?: number;
  precio_unitario?: number;
  tiempo_entrega_dias?: number;
  disponible: boolean;
  notas?: string;
  orden: number;
  valores_especificacion?: Record<string, any>;
}

export interface CotizacionCreate {
  solicitud_id: number;
  proveedor_id: number;
  fecha_limite_respuesta?: string;
  notas_internas?: string;
  items: ItemCotizacionForm[];
}

export interface CotizacionUpdate {
  estado?: string;
  notas_internas?: string;
  notas_proveedor?: string;
  fecha_limite_respuesta?: string;
  items?: ItemCotizacionForm[];
}

export interface ItemCotizacionOut {
  id: number;
  cotizacion_id: number;
  item_solicitud_id?: number;
  precio_unitario?: number;
  tiempo_entrega_dias?: number;
  disponible: boolean;
  notas?: string;
  orden: number;
  valores_especificacion?: Record<string, any>;
  item_solicitud?: {
    id: number;
    tipo: string;
    descripcion: string;
    cantidad?: number;
    unidad_medida_id?: number;
    categoria_producto_id?: number;
    especificaciones?: string;
    notas?: string;
  };
}

export interface CotizacionOut {
  id: number;
  token?: string;
  solicitud_id: number;
  proveedor_id: number;
  moneda?: string;
  estado: 'invitada' | 'respondida' | 'descartada';
  version_actual: number;
  respuesta_version?: number;
  fecha_limite_respuesta?: string;
  notas_internas?: string;
  notas_proveedor?: string;
  created_at: string;
  updated_at?: string;
  items: ItemCotizacionOut[];
  solicitud?: {
    id: number;
    numero?: string;
    titulo: string;
    solicitante_nombre: string;
    estado: string;
    prioridad: string;
    fecha_requerida?: string;
    version_actual: number;
  };
  proveedor?: {
    id: number;
    razon_social: string;
    nombre_comercial?: string;
    pais: string;
    calificacion?: number;
  };
  /** true si a esta cotización se le adjudicó al menos un ítem. */
  adjudicada: boolean;
  /** Cantidad de ítems adjudicados a esta cotización. */
  items_adjudicados: number;
}

export interface EvaluacionResultado {
  cotizacion_id: number;
  proveedor_id: number;
  moneda_cotizacion?: string;
  monedas_utilizadas?: string[];
  total_convertido?: number;
  dias_entrega?: number | null;
  items_disponibles: number;
  items_totales: number;
  calificacion: number;
  subpuntajes: {
    financiero: number;
    tiempo_entrega: number;
    completitud: number;
    calificacion: number;
  };
  puntaje_final: number;
  es_ganador_sugerido: boolean;
}

export interface EvaluacionCriterio {
  clave: string;
  nombre: string;
  descripcion?: string;
  peso: number;
  orden: number;
  activo: boolean;
}

export interface EvaluacionItemCandidato {
  cotizacion_id: number;
  proveedor_id: number;
  precio_unitario_original: number;
  moneda_original: string;
  precio_unitario_convertido: number;
  cantidad: number;
  subtotal_original: number;
  subtotal_convertido: number;
  tiempo_entrega_dias: number | null;
  garantia_meses: number | null;
  subpuntajes: {
    financiero: number;
    tiempo_entrega: number;
    garantia: number;
    calificacion: number;
  };
  puntaje: number;
  es_mejor: boolean;
}

export interface EvaluacionPorItem {
  item_solicitud_id: number;
  descripcion: string;
  tipo: string;
  cantidad: number;
  candidatos: EvaluacionItemCandidato[];
  mejor_cotizacion_id: number | null;
}

export interface EvaluacionComparativo {
  pesos: Record<string, number>;
  moneda_oportunidad?: string;
  criterios: EvaluacionCriterio[];
  por_item: EvaluacionPorItem[];
  adjudicacion_sugerida: Record<string, number | null>;
  resultados: EvaluacionResultado[];
  ganador_sugerido_cotizacion_id: number | null;
}

export interface CotizacionListOut {
  items: CotizacionOut[];
  total: number;
  skip: number;
  limit: number;
}

export interface EnviarRFQRequest {
  solicitud_id: number;
  proveedor_ids: number[];
  asignaciones?: Record<number, number[]>;
  fecha_limite_respuesta?: string;
  notas_internas?: string;
}

export interface ComparativoOut {
  solicitud: {
    id: number;
    numero?: string;
    titulo: string;
    solicitante_nombre: string;
    estado: string;
    prioridad: string;
    moneda?: string;
    version_actual: number;
    motivo_cancelacion?: string | null;
    fecha_cancelacion?: string | null;
    fecha_adjudicacion?: string | null;
  };
  items_solicitud: Array<{
    id: number;
    tipo: string;
    descripcion: string;
    cantidad?: number;
    unidad_medida_id?: number;
  }>;
  cotizaciones: CotizacionOut[];
  evaluacion?: EvaluacionComparativo;
  cotizacion_ganadora_id?: number | null;
  justificacion_seleccion?: string | null;
  adjudicacion_items?: Record<string, number>;
}
