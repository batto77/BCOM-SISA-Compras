import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CriterioEvaluacion {
  id: number;
  clave: string;
  nombre: string;
  descripcion?: string;
  peso_default: number;
  orden: number;
  activo: boolean;
}

@Injectable({ providedIn: 'root' })
export class EvaluacionService {
  private readonly baseUrl = '/api/v1/criterios-evaluacion';

  constructor(private http: HttpClient) {}

  /** Criterios base con sus pesos por defecto (tabla paramétrica). */
  getCriterios(): Observable<CriterioEvaluacion[]> {
    return this.http.get<CriterioEvaluacion[]>(this.baseUrl);
  }

  /** Actualiza los pesos base de forma masiva (deben sumar 100). */
  actualizarPesos(pesos: Record<string, number>): Observable<CriterioEvaluacion[]> {
    return this.http.put<CriterioEvaluacion[]>(this.baseUrl, pesos);
  }
}
