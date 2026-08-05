import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ItemSolicitudPublico {
  id: number;
  tipo: string;
  descripcion: string;
  cantidad?: number;
  especificaciones?: string;
  notas?: string;
}

export interface ItemCotizacionPublico {
  id: number;
  item_solicitud_id?: number;
  precio_unitario?: number;
  tiempo_entrega_dias?: number;
  disponible: boolean;
  notas?: string;
  orden: number;
  ficha_tecnica_url?: string;
  moneda?: string;
  item_solicitud?: ItemSolicitudPublico;
}

export interface TasaCambioPublico {
  moneda: string;
  tasa_cop: number;
}

export interface CotizacionPublica {
  id: number;
  token?: string;
  estado: string;
  version_actual: number;
  respuesta_version?: number;
  fecha_limite_respuesta?: string;
  notas_proveedor?: string;
  pdf_cotizacion_url?: string;
  solicitud_titulo: string;
  solicitud_numero?: string;
  solicitud_prioridad: string;
  solicitud_fecha_requerida?: string;
  proveedor_nombre: string;
  proveedor_monedas: string[];
  proveedor_moneda_defecto?: string;
  tasas_cambio: TasaCambioPublico[];
  items: ItemCotizacionPublico[];
}

export interface ItemRespuesta {
  item_cotizacion_id: number;
  precio_unitario?: number | null;
  tiempo_entrega_dias?: number | null;
  disponible: boolean;
  notas?: string | null;
  moneda?: string | null;
}

export interface RespuestaProveedor {
  items: ItemRespuesta[];
  notas_proveedor?: string;
}

@Injectable({ providedIn: 'root' })
export class PublicService {
  private readonly base = '/api/v1/public';

  constructor(private http: HttpClient) {}

  getCotizacionPublica(token: string): Observable<CotizacionPublica> {
    return this.http.get<CotizacionPublica>(`${this.base}/cotizar/${token}`);
  }

  responderCotizacion(token: string, data: RespuestaProveedor): Observable<CotizacionPublica> {
    return this.http.post<CotizacionPublica>(`${this.base}/cotizar/${token}/responder`, data);
  }

  uploadFichaTecnica(token: string, itemId: number, file: File): Observable<{ url: string; nombre: string }> {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<{ url: string; nombre: string }>(`${this.base}/cotizar/${token}/upload-item/${itemId}`, fd);
  }

  uploadPdfCotizacion(token: string, file: File): Observable<{ url: string; nombre: string }> {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<{ url: string; nombre: string }>(`${this.base}/cotizar/${token}/upload-pdf`, fd);
  }
}
