import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import {
  UnidadMedida,
  RubroPresupuestal,
  NivelAprobacion,
  PlantillaANS,
  TipoServicio
} from '../models/parametros.model';

@Injectable({ providedIn: 'root' })
export class ParametrosService extends ApiService {

  constructor(http: HttpClient) {
    super(http);
  }

  getUnidadesMedida(): Observable<UnidadMedida[]> {
    return this.http.get<{items: UnidadMedida[]}>(`${this.baseUrl}/unidades-medida`).pipe(
      map(r => r.items), catchError(() => of([])));
  }
  createUnidadMedida(data: Partial<UnidadMedida>): Observable<UnidadMedida | null> {
    return this.http.post<UnidadMedida>(`${this.baseUrl}/unidades-medida`, data).pipe(catchError(() => of(null)));
  }
  updateUnidadMedida(id: number, data: Partial<UnidadMedida>): Observable<UnidadMedida | null> {
    return this.http.put<UnidadMedida>(`${this.baseUrl}/unidades-medida/${id}`, data).pipe(catchError(() => of(null)));
  }
  deleteUnidadMedida(id: number): Observable<boolean> {
    return this.http.delete<void>(`${this.baseUrl}/unidades-medida/${id}`).pipe(catchError(() => of(false))) as any;
  }

  getRubros(): Observable<RubroPresupuestal[]> {
    return this.http.get<{items: RubroPresupuestal[]}>(`${this.baseUrl}/rubros-presupuestales`).pipe(
      map(r => r.items), catchError(() => of([])));
  }
  createRubro(data: Partial<RubroPresupuestal>): Observable<RubroPresupuestal | null> {
    return this.http.post<RubroPresupuestal>(`${this.baseUrl}/rubros-presupuestales`, data).pipe(catchError(() => of(null)));
  }
  updateRubro(id: number, data: Partial<RubroPresupuestal>): Observable<RubroPresupuestal | null> {
    return this.http.put<RubroPresupuestal>(`${this.baseUrl}/rubros-presupuestales/${id}`, data).pipe(catchError(() => of(null)));
  }
  deleteRubro(id: number): Observable<boolean> {
    return this.http.delete<void>(`${this.baseUrl}/rubros-presupuestales/${id}`).pipe(catchError(() => of(false))) as any;
  }

  getNivelesAprobacion(): Observable<NivelAprobacion[]> {
    return this.http.get<{items: NivelAprobacion[]}>(`${this.baseUrl}/niveles-aprobacion`).pipe(
      map(r => r.items), catchError(() => of([])));
  }
  createNivelAprobacion(data: Partial<NivelAprobacion>): Observable<NivelAprobacion | null> {
    return this.http.post<NivelAprobacion>(`${this.baseUrl}/niveles-aprobacion`, data).pipe(catchError(() => of(null)));
  }
  updateNivelAprobacion(id: number, data: Partial<NivelAprobacion>): Observable<NivelAprobacion | null> {
    return this.http.put<NivelAprobacion>(`${this.baseUrl}/niveles-aprobacion/${id}`, data).pipe(catchError(() => of(null)));
  }
  deleteNivelAprobacion(id: number): Observable<boolean> {
    return this.http.delete<void>(`${this.baseUrl}/niveles-aprobacion/${id}`).pipe(catchError(() => of(false))) as any;
  }

  getPlantillasANS(): Observable<PlantillaANS[]> {
    return this.http.get<{items: PlantillaANS[]}>(`${this.baseUrl}/plantillas-ans`).pipe(
      map(r => r.items), catchError(() => of([])));
  }
  createPlantillaANS(data: Partial<PlantillaANS>): Observable<PlantillaANS | null> {
    return this.http.post<PlantillaANS>(`${this.baseUrl}/plantillas-ans`, data).pipe(catchError(() => of(null)));
  }
  updatePlantillaANS(id: number, data: Partial<PlantillaANS>): Observable<PlantillaANS | null> {
    return this.http.put<PlantillaANS>(`${this.baseUrl}/plantillas-ans/${id}`, data).pipe(catchError(() => of(null)));
  }
  deletePlantillaANS(id: number): Observable<boolean> {
    return this.http.delete<void>(`${this.baseUrl}/plantillas-ans/${id}`).pipe(catchError(() => of(false))) as any;
  }

  getTiposServicio(): Observable<TipoServicio[]> {
    return this.http.get<{items: TipoServicio[]}>(`${this.baseUrl}/tipos-servicio`).pipe(
      map(r => r.items), catchError(() => of([])));
  }
  createTipoServicio(data: Partial<TipoServicio>): Observable<TipoServicio | null> {
    return this.http.post<TipoServicio>(`${this.baseUrl}/tipos-servicio`, data).pipe(catchError(() => of(null)));
  }
  updateTipoServicio(id: number, data: Partial<TipoServicio>): Observable<TipoServicio | null> {
    return this.http.put<TipoServicio>(`${this.baseUrl}/tipos-servicio/${id}`, data).pipe(catchError(() => of(null)));
  }
  deleteTipoServicio(id: number): Observable<boolean> {
    return this.http.delete<void>(`${this.baseUrl}/tipos-servicio/${id}`).pipe(catchError(() => of(false))) as any;
  }
}
