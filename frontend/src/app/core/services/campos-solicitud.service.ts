import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface CampoSolicitud {
  id: number;
  nombre: string;
  descripcion?: string;
  tipo_dato: 'texto' | 'numero' | 'fecha' | 'booleano' | 'lista';
  opciones?: string[];
  obligatorio: boolean;
  activo: boolean;
  orden: number;
}

@Injectable({ providedIn: 'root' })
export class CamposSolicitudService {
  private readonly base = '/api/v1/campos-solicitud';

  constructor(private http: HttpClient) {}

  getCampos(soloActivos = false): Observable<CampoSolicitud[]> {
    const url = soloActivos ? `${this.base}?solo_activos=true` : this.base;
    return this.http.get<CampoSolicitud[]>(url).pipe(catchError(() => of([])));
  }

  createCampo(data: Partial<CampoSolicitud>): Observable<CampoSolicitud | null> {
    return this.http.post<CampoSolicitud>(this.base, data).pipe(catchError(() => of(null)));
  }

  updateCampo(id: number, data: Partial<CampoSolicitud>): Observable<CampoSolicitud | null> {
    return this.http.put<CampoSolicitud>(`${this.base}/${id}`, data).pipe(catchError(() => of(null)));
  }

  deleteCampo(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`).pipe(catchError(() => of(undefined as any)));
  }
}
