import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ApiService } from './api.service';
import {
  Proveedor,
  ContactoProveedor,
  EmailContacto,
  TelefonoContacto,
  ProveedorFiltros
} from '../models/proveedores.model';

export interface ImportacionProveedoresResultado {
  creados: number;
  omitidos_duplicados: string[];
  errores: Array<{ fila: number; motivo: string }>;
}

export interface ProveedorSugerido extends Proveedor {
  id: number;
  sugerido: boolean;
  score: number;
  item_ids_sugeridos: number[];
  criterios: Array<{
    tipo: string;
    item_id: number;
    item_descripcion: string;
    etiqueta: string;
    coincidencia: string;
  }>;
}

@Injectable({ providedIn: 'root' })
export class ProveedoresService extends ApiService {

  constructor(http: HttpClient) {
    super(http);
  }

  getProveedores(filtros?: ProveedorFiltros): Observable<Proveedor[]> {
    let params = new HttpParams();
    if (filtros?.search) params = params.set('search', filtros.search);
    if (filtros?.pais) params = params.set('pais', filtros.pais);
    if (filtros?.estado) params = params.set('estado', filtros.estado);
    if (filtros?.etiquetas?.length) {
      filtros.etiquetas.forEach(id => { params = params.append('etiqueta_id', String(id)); });
    }
    return this.http.get<{items: Proveedor[]}>(`${this.baseUrl}/proveedores`, { params }).pipe(
      map(r => r.items),
      catchError(() => of([]))
    );
  }

  getProveedoresSugeridos(solicitudId: number): Observable<ProveedorSugerido[]> {
    return this.http
      .get<ProveedorSugerido[]>(`${this.baseUrl}/solicitudes/${solicitudId}/proveedores-sugeridos`)
      .pipe(catchError(() => of([])));
  }

  getProveedor(id: number): Observable<Proveedor | null> {
    return this.http.get<Proveedor>(`${this.baseUrl}/proveedores/${id}`).pipe(
      catchError(() => of(null))
    );
  }

  createProveedor(data: Partial<Proveedor>): Observable<Proveedor | null> {
    return this.http.post<Proveedor>(`${this.baseUrl}/proveedores`, data).pipe(
      catchError(() => of(null))
    );
  }

  updateProveedor(id: number, data: Partial<Proveedor>): Observable<Proveedor | null> {
    return this.http.put<Proveedor>(`${this.baseUrl}/proveedores/${id}`, data).pipe(
      catchError(() => of(null))
    );
  }

  descargarPlantilla(): Observable<Blob | null> {
    return this.http.get(`${this.baseUrl}/proveedores/plantilla`, { responseType: 'blob' }).pipe(
      catchError(() => of(null))
    );
  }

  importarProveedores(file: File): Observable<ImportacionProveedoresResultado | null> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post<ImportacionProveedoresResultado>(
      `${this.baseUrl}/proveedores/importar`, formData
    ).pipe(
      catchError(() => of(null))
    );
  }

  // --- Contactos ---

  addContacto(proveedorId: number, data: Partial<ContactoProveedor>): Observable<ContactoProveedor | null> {
    return this.http.post<ContactoProveedor>(
      `${this.baseUrl}/proveedores/${proveedorId}/contactos`, data
    ).pipe(catchError(() => of(null)));
  }

  updateContacto(proveedorId: number, contactoId: number, data: Partial<ContactoProveedor>): Observable<ContactoProveedor | null> {
    return this.http.put<ContactoProveedor>(
      `${this.baseUrl}/proveedores/${proveedorId}/contactos/${contactoId}`, data
    ).pipe(catchError(() => of(null)));
  }

  deleteContacto(proveedorId: number, contactoId: number): Observable<boolean> {
    return this.http.delete<void>(
      `${this.baseUrl}/proveedores/${proveedorId}/contactos/${contactoId}`
    ).pipe(catchError(() => of(false))) as any;
  }

  // --- Emails ---

  addEmail(proveedorId: number, contactoId: number, data: Partial<EmailContacto>): Observable<EmailContacto | null> {
    return this.http.post<EmailContacto>(
      `${this.baseUrl}/proveedores/${proveedorId}/contactos/${contactoId}/emails`, data
    ).pipe(catchError(() => of(null)));
  }

  updateEmail(proveedorId: number, contactoId: number, emailId: number, data: Partial<EmailContacto>): Observable<EmailContacto | null> {
    return this.http.put<EmailContacto>(
      `${this.baseUrl}/proveedores/${proveedorId}/contactos/${contactoId}/emails/${emailId}`, data
    ).pipe(catchError(() => of(null)));
  }

  deleteEmail(proveedorId: number, contactoId: number, emailId: number): Observable<boolean> {
    return this.http.delete<void>(
      `${this.baseUrl}/proveedores/${proveedorId}/contactos/${contactoId}/emails/${emailId}`
    ).pipe(catchError(() => of(false))) as any;
  }

  // --- Teléfonos ---

  addTelefono(proveedorId: number, contactoId: number, data: Partial<TelefonoContacto>): Observable<TelefonoContacto | null> {
    return this.http.post<TelefonoContacto>(
      `${this.baseUrl}/proveedores/${proveedorId}/contactos/${contactoId}/telefonos`, data
    ).pipe(catchError(() => of(null)));
  }

  updateTelefono(proveedorId: number, contactoId: number, telefonoId: number, data: Partial<TelefonoContacto>): Observable<TelefonoContacto | null> {
    return this.http.put<TelefonoContacto>(
      `${this.baseUrl}/proveedores/${proveedorId}/contactos/${contactoId}/telefonos/${telefonoId}`, data
    ).pipe(catchError(() => of(null)));
  }

  deleteTelefono(proveedorId: number, contactoId: number, telefonoId: number): Observable<boolean> {
    return this.http.delete<void>(
      `${this.baseUrl}/proveedores/${proveedorId}/contactos/${contactoId}/telefonos/${telefonoId}`
    ).pipe(catchError(() => of(false))) as any;
  }
}
