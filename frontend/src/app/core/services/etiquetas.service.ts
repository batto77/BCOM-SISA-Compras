import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import { Dimension, Etiqueta } from '../models/etiquetas.model';

@Injectable({ providedIn: 'root' })
export class EtiquetasService extends ApiService {

  constructor(http: HttpClient) {
    super(http);
  }

  getDimensiones(): Observable<Dimension[]> {
    return this.http.get<{items: Dimension[]}>(`${this.baseUrl}/dimensiones`).pipe(
      map(r => r.items),
      catchError(() => of([]))
    );
  }

  createDimension(data: Partial<Dimension>): Observable<Dimension | null> {
    return this.http.post<Dimension>(`${this.baseUrl}/dimensiones`, data).pipe(
      catchError(() => of(null))
    );
  }

  updateDimension(id: number, data: Partial<Dimension>): Observable<Dimension | null> {
    return this.http.put<Dimension>(`${this.baseUrl}/dimensiones/${id}`, data).pipe(
      catchError(() => of(null))
    );
  }

  deleteDimension(id: number): Observable<boolean> {
    return this.http.delete<void>(`${this.baseUrl}/dimensiones/${id}`).pipe(
      catchError(() => of(false))
    ) as any;
  }

  getEtiquetas(dimensionId?: number): Observable<Etiqueta[]> {
    const params: Record<string, string> = {};
    if (dimensionId !== undefined) params['dimension_id'] = String(dimensionId);
    return this.http.get<{items: Etiqueta[]}>(`${this.baseUrl}/etiquetas`, { params }).pipe(
      map(r => r.items),
      catchError(() => of([]))
    );
  }

  createEtiqueta(data: Partial<Etiqueta>): Observable<Etiqueta | null> {
    return this.http.post<Etiqueta>(`${this.baseUrl}/etiquetas`, data).pipe(
      catchError(() => of(null))
    );
  }

  updateEtiqueta(id: number, data: Partial<Etiqueta>): Observable<Etiqueta | null> {
    return this.http.put<Etiqueta>(`${this.baseUrl}/etiquetas/${id}`, data).pipe(
      catchError(() => of(null))
    );
  }

  deleteEtiqueta(id: number): Observable<boolean> {
    return this.http.delete<void>(`${this.baseUrl}/etiquetas/${id}`).pipe(
      catchError(() => of(false))
    ) as any;
  }
}
