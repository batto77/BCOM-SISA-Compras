export interface Dimension {
  id: number;
  nombre: string;
  color?: string;
  descripcion?: string;
  activo: boolean;
}

export interface Etiqueta {
  id: number;
  nombre: string;
  color?: string;
  dimension_id?: number;
  dimension?: Dimension;
  descripcion?: string;
  activo: boolean;
}
