import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import {
  DxTagBoxModule,
  DxDateBoxModule,
  DxTextAreaModule,
  DxPopupModule,
  DxButtonModule,
  DxDataGridModule,
  DxLoadIndicatorModule,
} from 'devextreme-angular';

import { SolicitudesService } from '../../core/services/solicitudes.service';
import { CotizacionesService } from '../../core/services/cotizaciones.service';
import { ProveedoresService } from '../../core/services/proveedores.service';
import { ParametrosService } from '../../core/services/parametros.service';
import { SolicitudCompraOut } from '../../core/models/solicitudes.model';
import { CotizacionOut, EnviarRFQRequest } from '../../core/models/cotizaciones.model';
import { Proveedor } from '../../core/models/proveedores.model';
import {
  EspecificacionVisible,
  parsearEspecificaciones,
} from '../../shared/utils/especificaciones.util';
import {
  getPrioridadBadgeClass,
  getPrioridadAyuda,
  getPrioridadNombre,
} from '../../shared/utils/prioridades.util';

@Component({
  selector: 'app-solicitud-detail',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DxTagBoxModule,
    DxDateBoxModule,
    DxTextAreaModule,
    DxPopupModule,
    DxButtonModule,
    DxDataGridModule,
    DxLoadIndicatorModule,
  ],
  templateUrl: './solicitud-detail.component.html',
  styleUrl: './solicitud-detail.component.scss',
})
export class SolicitudDetailComponent implements OnInit {
  solicitud: SolicitudCompraOut | null = null;
  cotizaciones: CotizacionOut[] = [];
  proveedoresDisponibles: Proveedor[] = [];
  especificacionesPorItem: Record<number, EspecificacionVisible[]> = {};
  notaAnalistaPorItem: Record<number, string> = {};
  itemsExpandidos = new Set<number>();

  cargando = false;
  error = '';

  // Popup enviar RFQ
  popupEnviarVisible = false;
  proveedoresSeleccionados: number[] = [];
  fechaLimiteRFQ: Date | null = null;
  notasRFQ = '';
  enviando = false;

  // Popup cancelar oportunidad (la observación es obligatoria)
  popupCancelarVisible = false;
  motivoCancelacion = '';
  errorCancelar = '';
  cancelando = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private solicitudesService: SolicitudesService,
    private cotizacionesService: CotizacionesService,
    private proveedoresService: ProveedoresService,
    private parametrosService: ParametrosService,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.cargar(id);
    }
  }

  cargar(id?: number): void {
    const solicitudId = id ?? this.solicitud?.id;
    if (!solicitudId) return;

    this.cargando = true;
    this.error = '';

    forkJoin({
      solicitud: this.solicitudesService.getSolicitud(solicitudId),
      unidades: this.parametrosService.getUnidadesMedida(),
    }).subscribe({
      next: ({ solicitud: sol, unidades }) => {
        this.solicitud = sol;
        this.especificacionesPorItem = Object.fromEntries(
          (sol?.items ?? []).map(item => [
            item.id,
            parsearEspecificaciones(item.especificaciones, unidades),
          ]),
        );
        this.notaAnalistaPorItem = Object.fromEntries(
          (sol?.items ?? []).map(item => [item.id, (item.notas ?? '').trim()]),
        );
        this.itemsExpandidos = new Set(
          (sol?.items ?? [])
            .filter(item =>
              (this.especificacionesPorItem[item.id]?.length ?? 0) > 0
              || !!this.notaAnalistaPorItem[item.id],
            )
            .map(item => item.id),
        );
        this.cargando = false;
        this.cargarCotizaciones(solicitudId);
      },
      error: () => {
        this.error = 'No se pudo cargar la oportunidad.';
        this.cargando = false;
      },
    });
  }

  cargarCotizaciones(solicitudId: number): void {
    this.cotizacionesService.getCotizacionesBySolicitud(solicitudId).subscribe({
      next: cots => (this.cotizaciones = cots),
    });
  }

  onFechaLimiteChange(value: Date | null): void {
    this.fechaLimiteRFQ = value;
  }

  abrirEnviarRFQ(): void {
    this.proveedoresSeleccionados = [];
    this.fechaLimiteRFQ = null;
    this.notasRFQ = '';

    this.proveedoresService.getProveedores({ estado: 'activo' }).subscribe({
      next: provs => (this.proveedoresDisponibles = provs),
    });

    this.popupEnviarVisible = true;
  }

  enviarRFQ(): void {
    if (!this.solicitud || this.proveedoresSeleccionados.length === 0) return;

    this.enviando = true;

    const req: EnviarRFQRequest = {
      solicitud_id: this.solicitud.id,
      proveedor_ids: this.proveedoresSeleccionados,
      fecha_limite_respuesta: this.fechaLimiteRFQ
        ? this.fechaLimiteRFQ.toISOString().split('T')[0]
        : undefined,
      notas_internas: this.notasRFQ || undefined,
    };

    this.cotizacionesService.enviarRFQ(req).subscribe({
      next: nuevas => {
        this.enviando = false;
        this.popupEnviarVisible = false;
        this.cotizaciones = [...this.cotizaciones, ...nuevas];
        if (this.solicitud) {
          this.solicitud = { ...this.solicitud, estado: 'en_cotizacion' };
        }
      },
      error: () => {
        this.enviando = false;
        this.error = 'No se pudo enviar el RFQ. Intente nuevamente.';
      },
    });
  }

  getCotizacionEstadoBadge(estado: string): string {
    const clases: Record<string, string> = {
      invitada: 'badge-warning',
      respondida: 'badge-success',
      descartada: 'badge-secondary',
    };
    return clases[estado] ?? 'badge-secondary';
  }

  getPrioridadBadgeClass(prioridad: string): string {
    return getPrioridadBadgeClass(prioridad);
  }

  /** Texto de ayuda para el tooltip: "Crítico — Operación totalmente interrumpida". */
  getPrioridadAyuda(prioridad: string): string {
    return getPrioridadAyuda(prioridad);
  }

  getPrioridadNombre(prioridad: string): string {
    return getPrioridadNombre(prioridad);
  }

  getTipoBadgeClass(tipo: string): string {
    const clases: Record<string, string> = {
      producto: 'badge-primary',
      servicio: 'badge-info',
      licencia: 'badge-success',
      libre: 'badge-secondary',
    };
    return clases[tipo] ?? 'badge-secondary';
  }

  alternarEspecificaciones(itemId: number): void {
    if (this.itemsExpandidos.has(itemId)) {
      this.itemsExpandidos.delete(itemId);
      return;
    }
    this.itemsExpandidos.add(itemId);
  }

  tieneEspecificaciones(itemId: number): boolean {
    return (this.especificacionesPorItem[itemId]?.length ?? 0) > 0;
  }

  tieneNotaAnalista(itemId: number): boolean {
    return !!this.notaAnalistaPorItem[itemId];
  }

  /**
   * Un ítem sin especificaciones estructuradas (p. ej. una licencia) igual
   * debe poder desplegarse si tiene nota, o la nota queda invisible.
   */
  tieneDetalle(itemId: number): boolean {
    return this.tieneEspecificaciones(itemId) || this.tieneNotaAnalista(itemId);
  }

  estaExpandido(itemId: number): boolean {
    return this.itemsExpandidos.has(itemId);
  }

  get pasoActual(): number {
    const pasos: Record<string, number> = {
      borrador: 1,
      enviada: 2,
      en_cotizacion: 3,
      adjudicada: 4,
      aprobada: 4,   // histórico: reemplazado por 'adjudicada'
      rechazada: 4,
      cancelada: 4,
    };
    return pasos[this.solicitud?.estado ?? 'borrador'] ?? 1;
  }

  get estaCancelada(): boolean {
    return this.solicitud?.estado === 'cancelada';
  }

  getEstadoBadgeClass(estado: string): string {
    const clases: Record<string, string> = {
      borrador: 'badge-secondary',
      enviada: 'badge-info',
      en_cotizacion: 'badge-warning',
      adjudicada: 'badge-success',
      aprobada: 'badge-success',   // histórico: reemplazado por 'adjudicada'
      rechazada: 'badge-danger',
      cancelada: 'badge-dark',
    };
    return clases[estado] ?? 'badge-secondary';
  }

  get puedeCancelar(): boolean {
    return !!this.solicitud && !this.estaCancelada;
  }

  abrirCancelar(): void {
    this.motivoCancelacion = '';
    this.errorCancelar = '';
    this.popupCancelarVisible = true;
  }

  confirmarCancelar(): void {
    const motivo = this.motivoCancelacion.trim();
    if (!motivo) {
      this.errorCancelar = 'La observación es obligatoria para cancelar la oportunidad.';
      return;
    }
    if (!this.solicitud) return;

    this.cancelando = true;
    this.errorCancelar = '';
    this.cotizacionesService.cancelarOportunidad(this.solicitud.id, motivo).subscribe({
      next: res => {
        this.cancelando = false;
        this.popupCancelarVisible = false;
        if (this.solicitud) {
          this.solicitud.estado = res.estado;
          this.solicitud.motivo_cancelacion = res.motivo_cancelacion;
          this.solicitud.fecha_cancelacion = res.fecha_cancelacion ?? undefined;
        }
      },
      error: err => {
        this.cancelando = false;
        this.errorCancelar = err?.error?.detail ?? 'No se pudo cancelar la oportunidad.';
      },
    });
  }

  reabrir(): void {
    if (!this.solicitud) return;
    this.cancelando = true;
    this.cotizacionesService.reabrirOportunidad(this.solicitud.id).subscribe({
      next: res => {
        this.cancelando = false;
        if (this.solicitud) {
          this.solicitud.estado = res.estado;
          this.solicitud.motivo_cancelacion = undefined;
          this.solicitud.fecha_cancelacion = undefined;
        }
      },
      error: () => {
        this.cancelando = false;
        this.error = 'No se pudo reabrir la oportunidad.';
      },
    });
  }

  get puedeMostrarComparativo(): boolean {
    return this.cotizaciones.length >= 2;
  }
}
