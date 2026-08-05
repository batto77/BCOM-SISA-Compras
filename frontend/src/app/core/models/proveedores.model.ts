import { Etiqueta } from './etiquetas.model';

export interface EmailContacto {
  id?: number;
  email: string;
  tipo: 'comercial' | 'tecnico' | 'facturacion';
  es_principal: boolean;
}

export interface TelefonoContacto {
  id?: number;
  numero: string;
  tipo: 'celular' | 'fijo' | 'whatsapp';
  extension?: string;
}

export interface ContactoProveedor {
  id?: number;
  nombre: string;
  cargo?: string;
  es_principal: boolean;
  activo: boolean;
  emails: EmailContacto[];
  telefonos: TelefonoContacto[];
}

export interface Proveedor {
  id?: number;
  nit?: string;
  tipo_persona?: 'juridica' | 'natural';
  monedas?: string[];
  moneda_defecto?: string;
  /** Calificación del proveedor de 0 a 10 (ranking de estrellas) */
  calificacion?: number;
  razon_social: string;
  nombre_comercial?: string;
  pais: string;
  idioma: 'ES' | 'EN';
  sitio_web?: string;
  notas?: string;
  estado: 'activo' | 'inactivo';
  contactos: ContactoProveedor[];
  etiquetas: Etiqueta[];
  /** IDs de etiquetas — solo para enviar al backend en create/update */
  etiqueta_ids?: number[];
  created_at?: string;
}

export interface ProveedorFiltros {
  search?: string;
  pais?: string;
  etiquetas?: number[];
  estado?: string;
}
