import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import {
  CategoriaProducto,
  DefinicionCampo,
  Producto,
  CategoriaServicio,
  Servicio,
} from '../models/catalogos.model';

export interface ProductoFiltros {
  categoria_id?: number;
  modo_defecto?: string;
  etiqueta_id?: number;
  search?: string;
}

@Injectable({ providedIn: 'root' })
export class CatalogosService extends ApiService {

  constructor(http: HttpClient) {
    super(http);
  }

  getCategorias(): Observable<CategoriaProducto[]> {
    return this.http.get<{items: CategoriaProducto[]}>(`${this.baseUrl}/categorias-producto`).pipe(
      map(r => r.items), catchError(() => of([])));
  }

  getCategoria(id: number): Observable<CategoriaProducto | null> {
    return this.http.get<CategoriaProducto>(`${this.baseUrl}/categorias-producto/${id}`).pipe(
      catchError(() => of(null)));
  }

  createCategoria(data: Partial<CategoriaProducto>): Observable<CategoriaProducto | null> {
    return this.http.post<CategoriaProducto>(`${this.baseUrl}/categorias-producto`, data).pipe(
      catchError(() => of(null)));
  }

  updateCategoria(id: number, data: Partial<CategoriaProducto>): Observable<CategoriaProducto | null> {
    return this.http.put<CategoriaProducto>(`${this.baseUrl}/categorias-producto/${id}`, data).pipe(
      catchError(() => of(null)));
  }

  getCamposCategoria(categoriaId: number): Observable<DefinicionCampo[]> {
    return this.http.get<{campos: DefinicionCampo[]}>(
      `${this.baseUrl}/categorias/${categoriaId}/campos`
    ).pipe(map(r => r.campos), catchError(() => of([])));
  }

  createCampo(categoriaId: number, data: Partial<DefinicionCampo>): Observable<DefinicionCampo | null> {
    return this.http.post<DefinicionCampo>(
      `${this.baseUrl}/categorias-producto/${categoriaId}/campos`, data
    ).pipe(catchError(() => of(null)));
  }

  updateCampo(categoriaId: number, campoId: number, data: Partial<DefinicionCampo>): Observable<DefinicionCampo | null> {
    return this.http.put<DefinicionCampo>(
      `${this.baseUrl}/campos/${campoId}`, data
    ).pipe(catchError(() => of(null)));
  }

  deleteCampo(categoriaId: number, campoId: number): Observable<boolean> {
    return this.http.delete<void>(
      `${this.baseUrl}/campos/${campoId}`
    ).pipe(catchError(() => of(false))) as any;
  }

  getProductos(filtros?: ProductoFiltros): Observable<Producto[]> {
    let params = new HttpParams();
    if (filtros?.categoria_id) params = params.set('categoria_id', String(filtros.categoria_id));
    if (filtros?.modo_defecto) params = params.set('modo_defecto', filtros.modo_defecto);
    if (filtros?.etiqueta_id) params = params.set('etiqueta_id', String(filtros.etiqueta_id));
    if (filtros?.search) params = params.set('search', filtros.search);
    return this.http.get<{items: Producto[]}>(`${this.baseUrl}/productos`, { params }).pipe(
      map(r => r.items), catchError(() => of([])));
  }

  getProducto(id: number): Observable<Producto | null> {
    return this.http.get<Producto>(`${this.baseUrl}/productos/${id}`).pipe(
      catchError(() => of(null)));
  }

  createProducto(data: Partial<Producto>): Observable<Producto | null> {
    return this.http.post<Producto>(`${this.baseUrl}/productos`, data).pipe(
      catchError(() => of(null)));
  }

  updateProducto(id: number, data: Partial<Producto>): Observable<Producto | null> {
    return this.http.put<Producto>(`${this.baseUrl}/productos/${id}`, data).pipe(
      catchError(() => of(null)));
  }

  getCategoriasServicio(): Observable<CategoriaServicio[]> {
    return this.http.get<{items: CategoriaServicio[]}>(`${this.baseUrl}/categorias-servicio`).pipe(
      map(r => r.items), catchError(() => of([])));
  }

  getServicios(): Observable<Servicio[]> {
    return this.http.get<{items: Servicio[]}>(`${this.baseUrl}/servicios`).pipe(
      map(r => r.items), catchError(() => of([])));
  }

  getServicio(id: number): Observable<Servicio | null> {
    return this.http.get<Servicio>(`${this.baseUrl}/servicios/${id}`).pipe(
      catchError(() => of(null)));
  }

  createServicio(data: Partial<Servicio>): Observable<Servicio | null> {
    return this.http.post<Servicio>(`${this.baseUrl}/servicios`, data).pipe(
      catchError(() => of(null)));
  }

  updateServicio(id: number, data: Partial<Servicio>): Observable<Servicio | null> {
    return this.http.put<Servicio>(`${this.baseUrl}/servicios/${id}`, data).pipe(
      catchError(() => of(null)));
  }
}
