import { UnidadMedida } from './parametros.model';
import { Etiqueta } from './etiquetas.model';

export interface DefinicionCampo {
  id: number;
  nombre: string;
  clave: string;
  orden: number;
  tipo_dato: 'texto' | 'numero' | 'booleano';
  es_obligatorio: boolean;
  es_campo_base: boolean;
  tiene_cantidad: boolean;
  tiene_unidad: boolean;
  unidad_default_id?: number;
  unidad_default?: UnidadMedida;
  opciones_unidad: UnidadMedida[];
  placeholder?: string;
  descripcion_ayuda?: string;
  activo: boolean;
}

export interface CategoriaProducto {
  id: number;
  nombre: string;
  slug: string;
  tipo: 'hardware' | 'software' | 'licencia' | 'servicio';
  icono?: string;
  descripcion?: string;
  activo: boolean;
  campos?: DefinicionCampo[];
}

export interface ValorEspecificacion {
  campo_id: number;
  cantidad?: number;
  valor?: string;
  unidad_medida_id?: number;
}

export interface ModeloProducto {
  id: number;
  fabricante: string;
  modelo: string;
  es_primario: boolean;
  orden: number;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion?: string;
  categoria_producto_id: number;
  categoria_producto?: CategoriaProducto;
  modo_defecto: 'funcional' | 'modelos_especificos';
  fabricante?: string;
  version?: string;
  activo: boolean;
  especificaciones: ValorEspecificacion[];
  modelos_alternativos: ModeloProducto[];
  etiquetas: Etiqueta[];
}

export interface CategoriaServicio {
  id: number;
  nombre: string;
  descripcion?: string;
  activo: boolean;
}

export interface Servicio {
  id: number;
  nombre: string;
  descripcion?: string;
  categoria_servicio_id?: number;
  tipo_servicio_id?: number;
  unidad_medida_id?: number;
  activo: boolean;
  etiquetas: Etiqueta[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}
