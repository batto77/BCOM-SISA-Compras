import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DxDataGridModule, DxDataGridComponent, DxButtonModule } from 'devextreme-angular';
import { SolicitudesService } from '../../core/services/solicitudes.service';
import { SolicitudCompraOut } from '../../core/models/solicitudes.model';
import {
  getPrioridadBadgeClass,
  getPrioridadAyuda,
  getPrioridadNombre,
} from '../../shared/utils/prioridades.util';

@Component({
  selector: 'app-solicitudes',
  standalone: true,
  imports: [CommonModule, RouterLink, DxDataGridModule, DxButtonModule],
  templateUrl: './solicitudes.component.html',
})
export class SolicitudesComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  solicitudes: SolicitudCompraOut[] = [];
  cargando = false;
  error = '';

  constructor(private solicitudesService: SolicitudesService) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando = true;
    this.error = '';
    this.solicitudesService.getSolicitudes().subscribe({
      next: data => {
        this.solicitudes = data;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo conectar con el servidor. Verifique que el backend esté activo.';
        this.cargando = false;
      },
    });
  }

  limpiarFiltros(): void {
    this.grid.instance.clearFilter();
  }

  getRubrosTexto(solicitud: SolicitudCompraOut): string {
    if (solicitud.rubros?.length) {
      return solicitud.rubros.map(rubro => rubro.nombre).join(', ');
    }
    return solicitud.rubro?.nombre ?? '—';
  }

  /** Texto plano de los proveedores adjudicados: permite filtrar, ordenar y agrupar. */
  getAdjudicadoTexto(solicitud: SolicitudCompraOut): string {
    return (solicitud.adjudicado_a ?? []).map(a => a.razon_social).join(', ');
  }

  getItemsCount(solicitud: SolicitudCompraOut): number {
    return solicitud.items?.length ?? 0;
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
}
