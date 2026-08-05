import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DxNumberBoxModule, DxButtonModule, DxLoadIndicatorModule } from 'devextreme-angular';

import { EvaluacionService, CriterioEvaluacion } from '../../../core/services/evaluacion.service';

@Component({
  selector: 'app-criterios-evaluacion',
  standalone: true,
  imports: [CommonModule, RouterLink, DxNumberBoxModule, DxButtonModule, DxLoadIndicatorModule],
  template: `
    <div class="content-header">
      <div class="container-fluid">
        <div class="row mb-2">
          <div class="col-sm-6"><h1 class="m-0">Pesos del comparativo</h1></div>
          <div class="col-sm-6">
            <ol class="breadcrumb float-sm-right">
              <li class="breadcrumb-item"><a routerLink="/dashboard">Inicio</a></li>
              <li class="breadcrumb-item"><a routerLink="/administracion">Administración</a></li>
              <li class="breadcrumb-item active">Pesos del comparativo</li>
            </ol>
          </div>
        </div>
      </div>
    </div>

    <div class="content">
      <div class="container-fluid">
        @if (cargando) {
          <div class="text-center py-5"><dx-load-indicator [visible]="true"></dx-load-indicator></div>
        } @else {
          @if (error) { <div class="alert alert-danger">{{ error }}</div> }
          @if (exito) { <div class="alert alert-success">{{ exito }}</div> }

          <div class="row">
            <div class="col-md-8">
              <div class="card">
                <div class="card-header">
                  <h3 class="card-title">Valores base de los criterios de evaluación</h3>
                </div>
                <div class="card-body">
                  <table class="table table-sm align-middle">
                    <thead class="thead-light">
                      <tr>
                        <th>Criterio</th>
                        <th style="width:160px;">Peso base</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      @for (c of criterios; track c.clave) {
                        <tr>
                          <td>
                            <strong>{{ c.nombre }}</strong>
                            <div class="text-muted small">{{ c.descripcion }}</div>
                          </td>
                          <td>
                            <dx-number-box
                              [(value)]="pesos[c.clave]"
                              [min]="0" [max]="100" [step]="5"
                              format="#0'%'"
                              [showSpinButtons]="true"
                            ></dx-number-box>
                          </td>
                          <td class="text-muted small"><code>{{ c.clave }}</code></td>
                        </tr>
                      }
                      <tr class="font-weight-bold" [class.text-success]="pesosValidos" [class.text-danger]="!pesosValidos">
                        <td class="text-right">Total</td>
                        <td>{{ suma }}%</td>
                        <td>
                          @if (!pesosValidos) { <span class="small"><i class="fas fa-exclamation-triangle mr-1"></i>Debe sumar 100%</span> }
                          @else { <span class="small"><i class="fas fa-check mr-1"></i>OK</span> }
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <button class="btn btn-primary" [disabled]="guardando || !pesosValidos" (click)="guardar()">
                    @if (guardando) { <span class="spinner-border spinner-border-sm mr-1"></span> }
                    <i class="fas fa-save mr-1"></i>Guardar pesos base
                  </button>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card bg-light">
                <div class="card-body">
                  <h6 class="font-weight-bold text-muted text-uppercase mb-3">¿Cómo funciona?</h6>
                  <p class="small">
                    Estos son los pesos <strong>por defecto</strong> con los que arranca cada nueva oportunidad.
                  </p>
                  <p class="small text-muted">
                    Al crear una oportunidad podés ajustar los pesos solo para ese caso, sin afectar estos valores base.
                  </p>
                  <p class="small text-muted mb-0">
                    Los pesos deben sumar 100%. Se usan en el comparativo para calcular el ranking global de proveedores.
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
export class CriteriosEvaluacionComponent implements OnInit {
  criterios: CriterioEvaluacion[] = [];
  pesos: Record<string, number> = {};
  cargando = true;
  guardando = false;
  error = '';
  exito = '';

  constructor(private evaluacionService: EvaluacionService) {}

  get suma(): number {
    return this.criterios.reduce((a, c) => a + (Number(this.pesos[c.clave]) || 0), 0);
  }
  get pesosValidos(): boolean {
    return Math.round(this.suma) === 100;
  }

  ngOnInit(): void {
    this.evaluacionService.getCriterios().subscribe({
      next: crit => {
        this.criterios = crit.filter(c => c.activo);
        for (const c of this.criterios) this.pesos[c.clave] = Number(c.peso_default);
        this.cargando = false;
      },
      error: () => { this.error = 'No se pudieron cargar los criterios.'; this.cargando = false; },
    });
  }

  guardar(): void {
    if (!this.pesosValidos) return;
    this.guardando = true;
    this.error = '';
    this.exito = '';
    const payload: Record<string, number> = {};
    for (const c of this.criterios) payload[c.clave] = Number(this.pesos[c.clave]) || 0;
    this.evaluacionService.actualizarPesos(payload).subscribe({
      next: crit => {
        this.criterios = crit.filter(c => c.activo);
        this.exito = 'Pesos base actualizados correctamente.';
        this.guardando = false;
        setTimeout(() => (this.exito = ''), 4000);
      },
      error: err => {
        this.error = err.error?.detail ?? 'No se pudieron guardar los pesos.';
        this.guardando = false;
      },
    });
  }
}
