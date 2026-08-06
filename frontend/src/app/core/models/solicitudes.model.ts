export interface ItemSolicitudForm {
  id?: number;
  tipo: 'producto' | 'servicio' | 'licencia' | 'libre';
  descripcion: string;
  cantidad: number;
  unidad_medida_id?: number;
  producto_id?: number;
  categoria_producto_id?: number;
  servicio_id?: number;
  especificaciones?: string;
  notas?: string;
  presupuesto_estimado?: number;
  orden: number;
  // helpers de display (no se envían al backend)
  _productoNombre?: string;
  _servicioNombre?: string;
  _unidadNombre?: string;
}

export interface SolicitudCompraCreate {
  numero?: string;
  campos_extra?: Record<string, any>;
  titulo: string;
  descripcion?: string;
  solicitante_nombre: string;
  aprobador?: string;
  rubro_id?: number;
  rubro_ids?: number[];
  fecha_requerida?: string; // YYYY-MM-DD
  prioridad: 'urgente' | 'alta' | 'normal' | 'baja';
  moneda?: string;
  notas?: string;
  /** Pesos de los criterios de evaluación para esta oportunidad (suman 100) */
  pesos_evaluacion?: Record<string, number>;
  items: ItemSolicitudForm[];
}

export interface ItemSolicitudOut extends ItemSolicitudForm {
  id: number;
  solicitud_id: number;
  producto?: { id: number; nombre: string };
  categoria_producto?: { id: number; nombre: string; tipo: string };
  servicio?: { id: number; nombre: string };
  unidad?: { id: number; nombre: string; simbolo: string };
}

export interface SolicitudCompraOut {
  id: number;
  numero?: string;
  campos_extra?: Record<string, any>;
  titulo: string;
  descripcion?: string;
  solicitante_nombre: string;
  aprobador?: string;
  rubro_id?: number;
  rubro_ids?: number[];
  fecha_requerida?: string;
  prioridad: string;
  moneda: string;
  estado: string;
  version_actual: number;
  notas?: string;
  created_at: string;
  updated_at?: string;
  items: ItemSolicitudOut[];
  rubro?: { id: number; nombre: string; codigo?: string };
  rubros: Array<{ id: number; nombre: string; codigo?: string }>;
}
