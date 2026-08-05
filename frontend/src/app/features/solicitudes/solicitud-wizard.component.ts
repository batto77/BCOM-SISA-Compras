import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import {
  DxButtonModule,
  DxCheckBoxModule,
  DxDateBoxModule,
  DxLoadIndicatorModule,
  DxNumberBoxModule,
  DxSelectBoxModule,
  DxTagBoxModule,
  DxTextAreaModule,
  DxTextBoxModule,
} from 'devextreme-angular';
import { forkJoin } from 'rxjs';

import { ParametrosService } from '../../core/services/parametros.service';
import { SolicitudesService } from '../../core/services/solicitudes.service';
import { TourService } from '../../core/services/tour.service';
import { CamposSolicitudService, CampoSolicitud } from '../../core/services/campos-solicitud.service';
import { EvaluacionService, CriterioEvaluacion } from '../../core/services/evaluacion.service';
import { RubroPresupuestal } from '../../core/models/parametros.model';
import { SolicitudCompraCreate } from '../../core/models/solicitudes.model';
import { FieldHelpDirective } from '../../shared/directives/field-help.directive';

@Component({
  selector: 'app-solicitud-wizard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DxButtonModule,
    DxCheckBoxModule,
    DxDateBoxModule,
    DxLoadIndicatorModule,
    DxNumberBoxModule,
    DxSelectBoxModule,
    DxTagBoxModule,
    DxTextAreaModule,
    DxTextBoxModule,
    FieldHelpDirective,
  ],
  templateUrl: './solicitud-wizard.component.html',
})
export class SolicitudWizardComponent implements OnInit {
  guardando = false;
  cargando = true;
  error = '';
  errorNumero = '';

  numero = '';
  titulo = '';
  descripcion = '';
  solicitanteNombre = '';
  aprobador = '';
  rubroIds: number[] = [];
  fechaRequerida = new Date();
  prioridad: SolicitudCompraCreate['prioridad'] = 'normal';
  notas = '';

  readonly numeroPattern = /^DAV-\d{7}$/;

  rubros: RubroPresupuestal[] = [];
  camposDinamicos: CampoSolicitud[] = [];
  valoresCampos: Record<string, any> = {};

  // --- Pesos de evaluación del comparativo (por oportunidad) ---
  criteriosEval: CriterioEvaluacion[] = [];
  pesosEval: Record<string, number> = {};

  get sumaPesos(): number {
    return this.criteriosEval.reduce((a, c) => a + (Number(this.pesosEval[c.clave]) || 0), 0);
  }
  get pesosValidos(): boolean {
    return Math.round(this.sumaPesos) === 100;
  }
  restablecerPesos(): void {
    for (const c of this.criteriosEval) this.pesosEval[c.clave] = Number(c.peso_default);
  }
  prioridadOptions = [
    { id: 'urgente', nombre: 'Urgente' },
    { id: 'alta', nombre: 'Alta' },
    { id: 'normal', nombre: 'Normal' },
    { id: 'baja', nombre: 'Baja' },
  ];

  constructor(
    private parametrosService: ParametrosService,
    private solicitudesService: SolicitudesService,
    private router: Router,
    private tourService: TourService,
    private camposSolicitudService: CamposSolicitudService,
    private evaluacionService: EvaluacionService,
  ) {}

  ngOnInit(): void {
    forkJoin({
      rubros: this.parametrosService.getRubros(),
      campos: this.camposSolicitudService.getCampos(true),
      criterios: this.evaluacionService.getCriterios(),
    }).subscribe({
      next: ({ rubros, campos, criterios }) => {
        this.rubros = rubros;
        this.camposDinamicos = campos;
        this.valoresCampos = {};
        for (const c of campos) {
          this.valoresCampos[String(c.id)] = c.tipo_dato === 'booleano' ? false : '';
        }
        this.criteriosEval = (criterios || []).filter(c => c.activo);
        this.restablecerPesos();
        this.finishLoading();
      },
      error: () => {
        this.finishLoading();
      },
    });
  }

  private finishLoading(): void {
    this.cargando = false;
    window.setTimeout(() => this.tourService.startNewOpportunityTour(), 250);
  }

  onNumeroChange(value: string): void {
    this.numero = value;
    if (value && !this.numeroPattern.test(value)) {
      this.errorNumero = 'Formato incorrecto. Ejemplo: DAV-1234567';
    } else {
      this.errorNumero = '';
    }
  }

  guardarYAgregarItems(): void {
    if (this.guardando) return;
    if (!this.titulo.trim()) {
      this.error = 'El título de la oportunidad es requerido.';
      return;
    }
    if (!this.solicitanteNombre.trim()) {
      this.error = 'El nombre del solicitante es requerido.';
      return;
    }
    if (this.numero && !this.numeroPattern.test(this.numero)) {
      this.error = 'El número DAV tiene formato incorrecto. Ejemplo: DAV-1234567';
      return;
    }
    if (this.criteriosEval.length && !this.pesosValidos) {
      this.error = `Los pesos del comparativo deben sumar 100% (actual: ${this.sumaPesos}%).`;
      return;
    }

    this.guardando = true;
    this.error = '';

    const camposExtraFiltrados: Record<string, any> = {};
    for (const campo of this.camposDinamicos) {
      const val = this.valoresCampos[String(campo.id)];
      if (val !== '' && val !== null && val !== undefined) {
        camposExtraFiltrados[String(campo.id)] = val;
      }
    }

    const payload: SolicitudCompraCreate = {
      numero: this.numero.trim() || undefined,
      campos_extra: Object.keys(camposExtraFiltrados).length > 0 ? camposExtraFiltrados : undefined,
      titulo: this.titulo.trim(),
      descripcion: this.descripcion.trim() || undefined,
      solicitante_nombre: this.solicitanteNombre.trim(),
      aprobador: this.aprobador.trim() || undefined,
      rubro_id: this.rubroIds[0],
      rubro_ids: this.rubroIds,
      fecha_requerida: this.fechaRequerida.toISOString().split('T')[0],
      prioridad: this.prioridad,
      notas: this.notas.trim() || undefined,
      pesos_evaluacion: this.criteriosEval.length
        ? this.criteriosEval.reduce((acc, c) => {
            acc[c.clave] = Number(this.pesosEval[c.clave]) || 0;
            return acc;
          }, {} as Record<string, number>)
        : undefined,
      items: [],
    };

    this.solicitudesService.createSolicitud(payload).subscribe({
      next: solicitud => {
        this.guardando = false;
        if (!solicitud) {
          this.error = 'No se pudo crear la oportunidad. Verificá los datos.';
          return;
        }
        this.router.navigate(['/cotizaciones/asistente', solicitud.id]);
      },
      error: (err) => {
        this.guardando = false;
        if (err?.status === 409) {
          this.error = err?.error?.detail ?? 'Ya existe una oportunidad con ese número DAV.';
        } else {
          this.error = 'No se pudo crear la oportunidad. Verificá los datos.';
        }
      },
    });
  }

  cancelar(): void {
    this.router.navigate(['/solicitudes']);
  }
}
