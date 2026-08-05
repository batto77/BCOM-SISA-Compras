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
  itemsExpandidos = new Set<number>();

  cargando = false;
  error = '';

  // Popup enviar RFQ
  popupEnviarVisible = false;
  proveedoresSeleccionados: number[] = [];
  fechaLimiteRFQ: Date | null = null;
  notasRFQ = '';
  enviando = false;

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
        this.itemsExpandidos = new Set(
          (sol?.items ?? [])
            .filter(item => (this.especificacionesPorItem[item.id]?.length ?? 0) > 0)
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
    const clases: Record<string, string> = {
      urgente: 'badge-danger',
      alta: 'badge-warning',
      normal: 'badge-primary',
      baja: 'badge-secondary',
    };
    return clases[prioridad] ?? 'badge-secondary';
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

  estaExpandido(itemId: number): boolean {
    return this.itemsExpandidos.has(itemId);
  }

  get pasoActual(): number {
    const pasos: Record<string, number> = {
      borrador: 1,
      enviada: 2,
      en_cotizacion: 3,
      aprobada: 4,
      rechazada: 4,
    };
    return pasos[this.solicitud?.estado ?? 'borrador'] ?? 1;
  }

  get puedeMostrarComparativo(): boolean {
    return this.cotizaciones.length >= 2;
  }
}
