import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import {
  DxDataGridModule,
  DxDataGridComponent,
  DxSelectBoxModule,
  DxDateBoxModule,
  DxButtonModule,
} from 'devextreme-angular';

interface AuditEntry {
  id: number;
  tabla: string;
  tabla_label: string;
  registro_id: number | null;
  accion: string;
  usuario: string | null;
  descripcion: string | null;
  created_at: string;
}

@Component({
  selector: 'app-auditoria',
  standalone: true,
  imports: [CommonModule, RouterLink, DxDataGridModule, DxSelectBoxModule, DxDateBoxModule, DxButtonModule],
  template: `
    <div class="content-header">
      <div class="container-fluid">
        <div class="row mb-2">
          <div class="col-sm-6"><h1 class="m-0">Auditoría del sistema</h1></div>
          <div class="col-sm-6">
            <ol class="breadcrumb float-sm-right">
              <li class="breadcrumb-item"><a routerLink="/dashboard">Inicio</a></li>
              <li class="breadcrumb-item"><a routerLink="/administracion">Administración</a></li>
              <li class="breadcrumb-item active">Auditoría</li>
            </ol>
          </div>
        </div>
      </div>
    </div>

    <div class="content">
      <div class="container-fluid">

        <!-- Filtros -->
        <div class="card mb-3">
          <div class="card-body py-3">
            <div class="row align-items-end">
              <div class="col-md-3">
                <label class="text-muted small text-uppercase font-weight-bold">Módulo</label>
                <dx-select-box
                  [items]="tablasOptions"
                  displayExpr="label"
                  valueExpr="value"
                  [(value)]="filtroTabla"
                  placeholder="Todos"
                  [showClearButton]="true"
                ></dx-select-box>
              </div>
              <div class="col-md-2">
                <label class="text-muted small text-uppercase font-weight-bold">Acción</label>
                <dx-select-box
                  [items]="accionesOptions"
                  displayExpr="label"
                  valueExpr="value"
                  [(value)]="filtroAccion"
                  placeholder="Todas"
                  [showClearButton]="true"
                ></dx-select-box>
              </div>
              <div class="col-md-2">
                <label class="text-muted small text-uppercase font-weight-bold">Desde</label>
                <dx-date-box
                  [(value)]="filtroDesde"
                  type="date"
                  displayFormat="dd/MM/yyyy"
                  [showClearButton]="true"
                ></dx-date-box>
              </div>
              <div class="col-md-2">
                <label class="text-muted small text-uppercase font-weight-bold">Hasta</label>
                <dx-date-box
                  [(value)]="filtroHasta"
                  type="date"
                  displayFormat="dd/MM/yyyy"
                  [showClearButton]="true"
                ></dx-date-box>
              </div>
              <div class="col-md-3">
                <button class="btn btn-primary btn-sm mr-2" (click)="cargar()">
                  <i class="fas fa-search mr-1"></i>Filtrar
                </button>
                <button class="btn btn-outline-secondary btn-sm" (click)="limpiar()">
                  <i class="fas fa-eraser mr-1"></i>Limpiar
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ total }} registros</h3>
          </div>
          <div class="card-body p-0 position-relative">
            @if (cargando) {
              <div class="overlay"><i class="fas fa-2x fa-sync-alt fa-spin"></i></div>
            }
            <dx-data-grid
              #grid
              [dataSource]="registros"
              [showBorders]="false"
              [rowAlternationEnabled]="true"
              [columnAutoWidth]="true"
            >
              <dxo-search-panel [visible]="true" placeholder="Buscar..."></dxo-search-panel>
              <dxo-toolbar>
                <dxi-item location="before" template="btnLimpiarFiltros"></dxi-item>
                <dxi-item name="searchPanel"></dxi-item>
              </dxo-toolbar>
              <div *dxTemplate="let _ of 'btnLimpiarFiltros'">
                <button class="btn btn-sm btn-outline-secondary" (click)="grid.instance.clearFilter()">
                  <i class="fas fa-eraser mr-1"></i>Limpiar filtros
                </button>
              </div>

              <dxi-column dataField="created_at" caption="Fecha / Hora" dataType="datetime"
                format="dd/MM/yyyy HH:mm:ss" [width]="160" [sortOrder]="'desc'"></dxi-column>

              <dxi-column dataField="tabla_label" caption="Módulo" [width]="160"></dxi-column>

              <dxi-column caption="Acción" [width]="100" cellTemplate="accionTpl" [allowFiltering]="false"></dxi-column>
              <div *dxTemplate="let c of 'accionTpl'">
                <span class="badge" [ngClass]="getAccionClass(c.data.accion)">{{ c.data.accion }}</span>
              </div>

              <dxi-column dataField="registro_id" caption="ID Registro" [width]="100"></dxi-column>

              <dxi-column dataField="descripcion" caption="Descripción" [minWidth]="300"></dxi-column>

              <dxi-column dataField="usuario" caption="Usuario" [width]="150"></dxi-column>

            </dx-data-grid>
          </div>
        </div>

      </div>
    </div>
  `,
})
export class AuditoriaComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  registros: AuditEntry[] = [];
  total = 0;
  cargando = false;

  filtroTabla: string | null = null;
  filtroAccion: string | null = null;
  filtroDesde: any = null;
  filtroHasta: any = null;

  tablasOptions = [
    { value: 'solicitudes_compra', label: 'Oportunidades' },
    { value: 'cotizaciones', label: 'Cotizaciones' },
    { value: 'proveedores', label: 'Proveedores' },
    { value: 'categorias_producto', label: 'Catálogo — Categorías' },
    { value: 'etiquetas', label: 'Etiquetas' },
    { value: 'rubros_presupuestales', label: 'Parámetros — Rubros' },
  ];

  accionesOptions = [
    { value: 'create', label: 'Creación' },
    { value: 'update', label: 'Actualización' },
    { value: 'delete', label: 'Eliminación' },
  ];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando = true;
    const params: Record<string, string> = { limit: '200' };
    if (this.filtroTabla) params['tabla'] = this.filtroTabla;
    if (this.filtroAccion) params['accion'] = this.filtroAccion;
    if (this.filtroDesde) params['desde'] = this.filtroDesde.toISOString().split('T')[0];
    if (this.filtroHasta) params['hasta'] = this.filtroHasta.toISOString().split('T')[0];

    const qs = new URLSearchParams(params).toString();
    this.http.get<any>(`/api/v1/auditoria?${qs}`).subscribe({
      next: data => {
        this.registros = data.items;
        this.total = data.total;
        this.cargando = false;
      },
      error: () => { this.cargando = false; },
    });
  }

  limpiar(): void {
    this.filtroTabla = null;
    this.filtroAccion = null;
    this.filtroDesde = null;
    this.filtroHasta = null;
    this.cargar();
  }

  getAccionClass(accion: string): string {
    const m: Record<string, string> = {
      create: 'badge-success',
      update: 'badge-primary',
      delete: 'badge-danger',
    };
    return m[accion] ?? 'badge-secondary';
  }
}
