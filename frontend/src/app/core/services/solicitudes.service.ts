import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import {
  SolicitudCompraCreate,
  SolicitudCompraOut,
} from '../models/solicitudes.model';

@Injectable({ providedIn: 'root' })
export class SolicitudesService extends ApiService {

  constructor(http: HttpClient) {
    super(http);
  }

  getSolicitudes(): Observable<SolicitudCompraOut[]> {
    return this.http
      .get<{ items: SolicitudCompraOut[] }>(`${this.baseUrl}/solicitudes`)
      .pipe(
        map(r => r.items),
        catchError(() => of([]))
      );
  }

  getSolicitud(id: number): Observable<SolicitudCompraOut | null> {
    return this.http
      .get<SolicitudCompraOut>(`${this.baseUrl}/solicitudes/${id}`)
      .pipe(catchError(() => of(null)));
  }

  createSolicitud(data: SolicitudCompraCreate): Observable<SolicitudCompraOut | null> {
    return this.http
      .post<SolicitudCompraOut>(`${this.baseUrl}/solicitudes`, data)
      .pipe(catchError(() => of(null)));
  }

  updateSolicitud(
    id: number,
    data: Partial<SolicitudCompraCreate>
  ): Observable<SolicitudCompraOut | null> {
    return this.http
      .put<SolicitudCompraOut>(`${this.baseUrl}/solicitudes/${id}`, data)
      .pipe(catchError(() => of(null)));
  }

  deleteSolicitud(id: number): Observable<boolean> {
    return this.http
      .delete<void>(`${this.baseUrl}/solicitudes/${id}`)
      .pipe(
        map(() => true),
        catchError(() => of(false))
      );
  }
}
