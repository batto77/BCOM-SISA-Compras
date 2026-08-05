import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import {
  CotizacionCreate,
  CotizacionListOut,
  CotizacionOut,
  CotizacionUpdate,
  ComparativoOut,
  EnviarRFQRequest,
} from '../models/cotizaciones.model';

export interface CotizacionFiltros {
  solicitud_id?: number;
  estado?: string;
  proveedor_id?: number;
  skip?: number;
  limit?: number;
}

@Injectable({ providedIn: 'root' })
export class CotizacionesService extends ApiService {

  constructor(http: HttpClient) {
    super(http);
  }

  getCotizaciones(filtros?: CotizacionFiltros): Observable<CotizacionListOut> {
    let params = new HttpParams();
    if (filtros?.solicitud_id != null) params = params.set('solicitud_id', String(filtros.solicitud_id));
    if (filtros?.estado) params = params.set('estado', filtros.estado);
    if (filtros?.proveedor_id != null) params = params.set('proveedor_id', String(filtros.proveedor_id));
    if (filtros?.skip != null) params = params.set('skip', String(filtros.skip));
    if (filtros?.limit != null) params = params.set('limit', String(filtros.limit));

    return this.http
      .get<CotizacionListOut>(`${this.baseUrl}/cotizaciones`, { params })
      .pipe(
        catchError(() => of({ items: [], total: 0, skip: 0, limit: 20 }))
      );
  }

  getCotizacion(id: number): Observable<CotizacionOut | null> {
    return this.http
      .get<CotizacionOut>(`${this.baseUrl}/cotizaciones/${id}`)
      .pipe(catchError(() => of(null)));
  }

  createCotizacion(data: CotizacionCreate): Observable<CotizacionOut | null> {
    return this.http
      .post<CotizacionOut>(`${this.baseUrl}/cotizaciones`, data)
      .pipe(catchError(() => of(null)));
  }

  updateCotizacion(id: number, data: CotizacionUpdate): Observable<CotizacionOut | null> {
    return this.http
      .put<CotizacionOut>(`${this.baseUrl}/cotizaciones/${id}`, data)
      .pipe(catchError(() => of(null)));
  }

  deleteCotizacion(id: number): Observable<boolean> {
    return this.http
      .delete<void>(`${this.baseUrl}/cotizaciones/${id}`)
      .pipe(
        map(() => true),
        catchError(() => of(false))
      );
  }

  enviarRFQ(data: EnviarRFQRequest): Observable<CotizacionOut[]> {
    return this.http
      .post<CotizacionOut[]>(`${this.baseUrl}/cotizaciones/rfq`, data)
      .pipe(catchError(() => of([])));
  }

  getCotizacionesBySolicitud(solicitudId: number): Observable<CotizacionOut[]> {
    return this.http
      .get<CotizacionOut[]>(`${this.baseUrl}/solicitudes/${solicitudId}/cotizaciones`)
      .pipe(catchError(() => of([])));
  }

  getComparativo(solicitudId: number): Observable<ComparativoOut | null> {
    return this.http
      .get<ComparativoOut>(`${this.baseUrl}/solicitudes/${solicitudId}/comparativo`)
      .pipe(catchError(() => of(null)));
  }

  seleccionarGanador(
    solicitudId: number,
    cotizacionId: number | null,
    justificacion?: string,
  ): Observable<{ cotizacion_ganadora_id: number | null; justificacion_seleccion: string | null }> {
    return this.http.post<{ cotizacion_ganadora_id: number | null; justificacion_seleccion: string | null }>(
      `${this.baseUrl}/solicitudes/${solicitudId}/seleccionar-ganador`,
      { cotizacion_id: cotizacionId, justificacion: justificacion ?? null },
    );
  }

  adjudicar(
    solicitudId: number,
    adjudicacion: Record<number, number | null>,
    justificacion?: string,
  ): Observable<{ adjudicacion_items: Record<string, number>; cotizacion_ganadora_id: number | null; justificacion_seleccion: string | null }> {
    return this.http.post<{ adjudicacion_items: Record<string, number>; cotizacion_ganadora_id: number | null; justificacion_seleccion: string | null }>(
      `${this.baseUrl}/solicitudes/${solicitudId}/adjudicar`,
      { adjudicacion, justificacion: justificacion ?? null },
    );
  }

  getCamposCategoria(categoriaId: number): Observable<any> {
    return this.http.get<any>(`/api/v1/categorias/${categoriaId}/campos`);
  }

  enviarRecordatorio(cotizacionId: number): Observable<any> {
    return this.http
      .post<any>(`${this.baseUrl}/cotizaciones/${cotizacionId}/recordatorio`, {})
      .pipe(catchError(err => { throw err; }));
  }
}
