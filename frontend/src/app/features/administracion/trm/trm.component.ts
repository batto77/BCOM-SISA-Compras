import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import {
  DxNumberBoxModule,
  DxButtonModule,
  DxLoadIndicatorModule,
  DxTextBoxModule,
  DxDataGridModule,
} from 'devextreme-angular';

interface TasaCambio {
  id: number;
  moneda: string;
  tasa_cop: number;
  updated_at: string;
}

interface HistorialItem {
  id: number;
  moneda: string;
  tasa_cop_anterior: number | null;
  tasa_cop_nueva: number;
  usuario: string | null;
  created_at: string;
}

@Component({
  selector: 'app-trm',
  standalone: true,
  imports: [CommonModule, RouterLink, DxDataGridModule, DxNumberBoxModule, DxButtonModule, DxLoadIndicatorModule, DxTextBoxModule],
  template: `
    <div class="content-header">
      <div class="container-fluid">
        <div class="row mb-2">
          <div class="col-sm-6"><h1 class="m-0">Tasas de cambio (TRM)</h1></div>
          <div class="col-sm-6">
            <ol class="breadcrumb float-sm-right">
              <li class="breadcrumb-item"><a routerLink="/dashboard">Inicio</a></li>
              <li class="breadcrumb-item"><a routerLink="/administracion">Administración</a></li>
              <li class="breadcrumb-item active">TRM</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
    <div class="content">
      <div class="container-fluid">
        @if (cargando) {
          <div class="text-center py-5">
            <dx-load-indicator [visible]="true"></dx-load-indicator>
          </div>
        } @else {
          @if (error) {
            <div class="alert alert-danger">{{ error }}</div>
          }
          @if (exito) {
            <div class="alert alert-success">{{ exito }}</div>
          }

          <div class="row">
            <div class="col-md-9">
              @for (t of tasas; track t.moneda) {
                <div class="card mb-3">
                  <div class="card-header d-flex align-items-center">
                    <span class="badge badge-primary mr-2" style="font-size:15px;padding:6px 12px;">{{ t.moneda }}</span>
                    <span class="text-muted small flex-grow-1">
                      Última actualización: {{ t.updated_at | date:'dd/MM/yyyy HH:mm' }}
                      @if (ultimoUsuario(t.moneda)) {
                        &nbsp;·&nbsp; por <strong>{{ ultimoUsuario(t.moneda) }}</strong>
                      }
                    </span>
                    <button class="btn btn-sm btn-outline-secondary" (click)="toggleHistorial(t.moneda)">
                      <i class="fas fa-history mr-1"></i>
                      {{ historialExpanded[t.moneda] ? 'Ocultar historial' : 'Ver historial' }}
                    </button>
                  </div>
                  <div class="card-body">
                    <div class="row align-items-end">
                      <div class="col-sm-4">
                        <label class="small font-weight-bold text-muted text-uppercase mb-1">
                          1 {{ t.moneda }} → COP
                        </label>
                        <dx-number-box
                          [(value)]="editValues[t.moneda]"
                          [min]="1"
                          format="#,##0.0000"
                          placeholder="Ej: 4200.0000"
                        ></dx-number-box>
                      </div>
                      <div class="col-sm-4">
                        <label class="small font-weight-bold text-muted text-uppercase mb-1">
                          Actualizado por
                        </label>
                        <dx-text-box
                          [(value)]="usuariosEdit[t.moneda]"
                          placeholder="Nombre de quien actualiza"
                        ></dx-text-box>
                      </div>
                      <div class="col-sm-4">
                        <button
                          class="btn btn-primary btn-block"
                          [disabled]="guardando[t.moneda]"
                          (click)="guardar(t.moneda)"
                        >
                          @if (guardando[t.moneda]) {
                            <span class="spinner-border spinner-border-sm mr-1"></span>
                          }
                          <i class="fas fa-save mr-1"></i>Actualizar tasa
                        </button>
                      </div>
                    </div>

                    @if (historialExpanded[t.moneda]) {
                      <hr class="mt-3 mb-2">
                      <h6 class="font-weight-bold text-muted mb-2">
                        <i class="fas fa-history mr-1"></i>Historial de cambios — {{ t.moneda }}
                      </h6>
                      @if (cargandoHistorial[t.moneda]) {
                        <div class="text-center py-3">
                          <dx-load-indicator [visible]="true"></dx-load-indicator>
                        </div>
                      } @else if ((historial[t.moneda] || []).length === 0) {
                        <p class="text-muted small">Sin cambios registrados todavía.</p>
                      } @else {
                        <div class="table-responsive">
                          <table class="table table-sm table-bordered mb-0">
                            <thead class="thead-light">
                              <tr>
                                <th style="width:160px;">Fecha y hora</th>
                                <th style="width:140px;">Valor anterior</th>
                                <th style="width:140px;">Valor nuevo</th>
                                <th>Actualizado por</th>
                              </tr>
                            </thead>
                            <tbody>
                              @for (h of historial[t.moneda]; track h.id) {
                                <tr>
                                  <td class="text-muted small">{{ h.created_at | date:'dd/MM/yyyy HH:mm' }}</td>
                                  <td class="text-right">
                                    @if (h.tasa_cop_anterior !== null) {
                                      {{ h.tasa_cop_anterior | number:'1.4-4' }}
                                    } @else {
                                      <span class="text-muted">—</span>
                                    }
                                  </td>
                                  <td class="text-right font-weight-bold">
                                    {{ h.tasa_cop_nueva | number:'1.4-4' }}
                                    @if (h.tasa_cop_anterior !== null) {
                                      @if (h.tasa_cop_nueva > h.tasa_cop_anterior) {
                                        <i class="fas fa-arrow-up text-danger ml-1 small"></i>
                                      } @else if (h.tasa_cop_nueva < h.tasa_cop_anterior) {
                                        <i class="fas fa-arrow-down text-success ml-1 small"></i>
                                      }
                                    }
                                  </td>
                                  <td>{{ h.usuario || '—' }}</td>
                                </tr>
                              }
                            </tbody>
                          </table>
                        </div>
                      }
                    }
                  </div>
                </div>
              }
            </div>
            <div class="col-md-3">
              <div class="card bg-light">
                <div class="card-body">
                  <h6 class="font-weight-bold text-muted text-uppercase mb-3">¿Cómo funciona?</h6>
                  <p class="small">
                    Ingresá cuántos pesos colombianos equivale 1 unidad de cada moneda extranjera.
                  </p>
                  <p class="small text-muted">
                    En el portal de proveedores, si el proveedor cotiza en USD, el sistema muestra
                    el subtotal y total equivalente en la moneda por defecto del proveedor.
                  </p>
                  <p class="small text-muted mb-0">
                    El historial registra quién actualizó la tasa, cuándo y desde/hacia qué valor.
                    Actualizá diariamente para reflejar el mercado.
                  </p>
                </div>
              </div>
            </div>
          </div>
        }
      </div>
    </div>
  `,
})
export class TrmComponent implements OnInit {
  tasas: TasaCambio[] = [];
  editValues: Record<string, number> = {};
  usuariosEdit: Record<string, string> = {};
  guardando: Record<string, boolean> = {};
  historial: Record<string, HistorialItem[]> = {};
  historialExpanded: Record<string, boolean> = {};
  cargandoHistorial: Record<string, boolean> = {};
  primerosUsuarios: Record<string, string | null> = {};
  cargando = true;
  error = '';
  exito = '';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<TasaCambio[]>('/api/v1/trm').subscribe({
      next: tasas => {
        this.tasas = tasas;
        for (const t of tasas) {
          this.editValues[t.moneda] = Number(t.tasa_cop);
          this.usuariosEdit[t.moneda] = '';
        }
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar las tasas.';
        this.cargando = false;
      },
    });
  }

  ultimoUsuario(moneda: string): string | null {
    const h = this.historial[moneda];
    return h?.[0]?.usuario ?? null;
  }

  toggleHistorial(moneda: string): void {
    this.historialExpanded[moneda] = !this.historialExpanded[moneda];
    if (this.historialExpanded[moneda] && !this.historial[moneda]) {
      this.cargarHistorial(moneda);
    }
  }

  cargarHistorial(moneda: string): void {
    this.cargandoHistorial[moneda] = true;
    this.http.get<HistorialItem[]>(`/api/v1/trm/${moneda}/historial`).subscribe({
      next: items => {
        this.historial[moneda] = items;
        this.cargandoHistorial[moneda] = false;
      },
      error: () => {
        this.cargandoHistorial[moneda] = false;
      },
    });
  }

  guardar(moneda: string): void {
    const tasa = this.editValues[moneda];
    if (!tasa || tasa <= 0) { this.error = 'La tasa debe ser mayor a cero.'; return; }
    this.guardando[moneda] = true;
    this.error = '';
    this.exito = '';
    const body: any = { tasa_cop: tasa };
    if (this.usuariosEdit[moneda]?.trim()) {
      body.usuario = this.usuariosEdit[moneda].trim();
    }
    this.http.put<TasaCambio>(`/api/v1/trm/${moneda}`, body).subscribe({
      next: updated => {
        const idx = this.tasas.findIndex(t => t.moneda === moneda);
        if (idx >= 0) this.tasas[idx] = updated;
        this.exito = `Tasa ${moneda} actualizada correctamente.`;
        this.guardando[moneda] = false;
        // Recargar historial si está expandido
        if (this.historialExpanded[moneda]) {
          this.cargarHistorial(moneda);
        } else {
          delete this.historial[moneda]; // forzar recarga la próxima vez
        }
        setTimeout(() => { this.exito = ''; }, 4000);
      },
      error: () => {
        this.error = `Error al guardar la tasa ${moneda}.`;
        this.guardando[moneda] = false;
      },
    });
  }
}
