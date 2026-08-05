export interface UnidadMedida {
  id: number;
  nombre: string;
  simbolo: string;
  categoria?: string;
  activo: boolean;
}

export interface RubroPresupuestal {
  id: number;
  nombre: string;
  codigo?: string;
  monto_max_auto_aprobacion?: number;
  activo: boolean;
}

export interface NivelAprobacion {
  id: number;
  nombre: string;
  monto_max?: number;
  delegable: boolean;
  orden: number;
}

export interface PlantillaANS {
  id: number;
  nombre: string;
  horas: number;
  descripcion?: string;
}

export interface TipoServicio {
  id: number;
  nombre: string;
  descripcion?: string;
  activo: boolean;
}
