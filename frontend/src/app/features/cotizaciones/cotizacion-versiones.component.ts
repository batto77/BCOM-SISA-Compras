import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { DxDataGridModule, DxLoadIndicatorModule } from 'devextreme-angular';

interface VersionRow {
  id: number;
  numero_version: number;
  created_at: string;
  snapshot: any;
}

interface HistorialOut {
  cotizacion_id: number;
  solicitud_titulo: string | null;
  solicitud_numero: string | null;
  proveedor: string | null;
  version_actual: number;
  estado: string;
  versiones: VersionRow[];
}

@Component({
  selector: 'app-cotizacion-versiones',
  standalone: true,
  imports: [CommonModule, RouterLink, DxDataGridModule, DxLoadIndicatorModule],
  template: `
    <div class="content-header">
      <div class="container-fluid">
        <div class="row mb-2">
          <div class="col-sm-6">
            <h1 class="m-0">Historial de versiones</h1>
          </div>
          <div class="col-sm-6">
            <ol class="breadcrumb float-sm-right">
              <li class="breadcrumb-item"><a routerLink="/dashboard">Inicio</a></li>
              <li class="breadcrumb-item"><a routerLink="/cotizaciones">Cotizaciones</a></li>
              <li class="breadcrumb-item">
                <a [routerLink]="['/cotizaciones', cotizacionId]">Cotización #{{ cotizacionId }}</a>
              </li>
              <li class="breadcrumb-item active">Historial</li>
            </ol>
          </div>
        </div>
      </div>
    </div>

    <div class="content">
      <div class="container-fluid">

        @if (cargando) {
          <div class="text-center py-5">
            <dx-load-indicator></dx-load-indicator>
            <p class="mt-2 text-muted">Cargando historial...</p>
          </div>
        } @else if (error) {
          <div class="alert alert-danger">{{ error }}</div>
        } @else if (historial) {

          <div class="card card-outline card-primary mb-3">
            <div class="card-body py-3">
              <div class="row">
                <div class="col-md-3">
                  <small class="text-muted d-block text-uppercase font-weight-bold">Oportunidad</small>
                  <span>{{ historial.solicitud_numero ?? '—' }} — {{ historial.solicitud_titulo ?? '—' }}</span>
                </div>
                <div class="col-md-3">
                  <small class="text-muted d-block text-uppercase font-weight-bold">Proveedor</small>
                  <span>{{ historial.proveedor ?? '—' }}</span>
                </div>
                <div class="col-md-2">
                  <small class="text-muted d-block text-uppercase font-weight-bold">Versión actual</small>
                  <span class="badge badge-primary">v{{ historial.version_actual }}</span>
                </div>
                <div class="col-md-2">
                  <small class="text-muted d-block text-uppercase font-weight-bold">Estado</small>
                  <span class="badge" [ngClass]="getEstadoBadge(historial.estado)">{{ historial.estado }}</span>
                </div>
                <div class="col-md-2 text-right">
                  <a [routerLink]="['/cotizaciones', cotizacionId]" class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-arrow-left mr-1"></i>Volver a cotización
                  </a>
                </div>
              </div>
            </div>
          </div>

          @if (historial.versiones.length === 0) {
            <div class="card">
              <div class="card-body text-center text-muted py-5">
                <i class="fas fa-history fa-3x mb-3 d-block"></i>
                No hay versiones registradas para esta cotización.
                Las versiones se crean automáticamente cuando se re-envía el RFQ con cambios.
              </div>
            </div>
          } @else {
            @for (ver of historial.versiones; track ver.id) {
              <div class="card card-outline card-secondary mb-3">
                <div class="card-header">
                  <h3 class="card-title">
                    <span class="badge badge-secondary mr-2">v{{ ver.numero_version }}</span>
                    Guardada el {{ ver.created_at | date:'dd/MM/yyyy HH:mm' }}
                  </h3>
                </div>
                <div class="card-body p-0">
                  @if (ver.snapshot && ver.snapshot.items?.length) {
                    <table class="table table-sm table-bordered mb-0">
                      <thead class="thead-light">
                        <tr>
                          <th>Ítem</th>
                          <th class="text-right" style="width:120px">Precio unit.</th>
                          <th class="text-center" style="width:100px">Entrega (días)</th>
                          <th class="text-center" style="width:90px">Disponible</th>
                          <th>Notas</th>
                        </tr>
                      </thead>
                      <tbody>
                        @for (item of ver.snapshot.items; track item.id) {
                          <tr>
                            <td>{{ item.item_solicitud?.descripcion ?? ('Ítem #' + item.item_solicitud_id) }}</td>
                            <td class="text-right">
                              {{ item.precio_unitario != null ? (item.precio_unitario | number:'1.0-2') : '—' }}
                            </td>
                            <td class="text-center">{{ item.tiempo_entrega_dias ?? '—' }}</td>
                            <td class="text-center">
                              @if (item.disponible) {
                                <span class="badge badge-success">Sí</span>
                              } @else {
                                <span class="badge badge-danger">No</span>
                              }
                            </td>
                            <td>{{ item.notas ?? '—' }}</td>
                          </tr>
                        }
                      </tbody>
                    </table>
                  } @else {
                    <div class="p-3 text-muted">Sin detalle de ítems en este snapshot.</div>
                  }
                </div>
              </div>
            }
          }

        }

      </div>
    </div>
  `,
})
export class CotizacionVersionesComponent implements OnInit {
  cotizacionId!: number;
  historial: HistorialOut | null = null;
  cargando = false;
  error = '';

  constructor(private route: ActivatedRoute, private http: HttpClient) {}

  ngOnInit(): void {
    this.cotizacionId = Number(this.route.snapshot.paramMap.get('id'));
    this.cargar();
  }

  cargar(): void {
    this.cargando = true;
    this.http.get<HistorialOut>(`/api/v1/cotizaciones/${this.cotizacionId}/versiones`).subscribe({
      next: data => {
        this.historial = data;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el historial de versiones.';
        this.cargando = false;
      },
    });
  }

  getEstadoBadge(estado: string): string {
    const m: Record<string, string> = {
      invitada: 'badge-warning',
      respondida: 'badge-success',
      descartada: 'badge-secondary',
    };
    return m[estado] ?? 'badge-secondary';
  }
}
