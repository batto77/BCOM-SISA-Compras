export interface OportunidadReciente {
  id: number;
  numero?: string;
  titulo: string;
  estado: string;
  prioridad: string;
  fecha_requerida?: string;
  created_at: string;
  proveedores_invitados: number;
  respuestas_recibidas: number;
}

export interface DashboardResumen {
  oportunidades_activas: number;
  cotizaciones_pendientes: number;
  cotizaciones_respondidas: number;
  proveedores_activos: number;
  tasa_respuesta: number;
  oportunidades_por_estado: Record<string, number>;
  oportunidades_recientes: OportunidadReciente[];
}
