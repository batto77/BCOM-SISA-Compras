import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DxDataGridModule, DxDataGridComponent, DxButtonModule } from 'devextreme-angular';
import { SolicitudesService } from '../../core/services/solicitudes.service';
import { SolicitudCompraOut } from '../../core/models/solicitudes.model';

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

  getEstadoBadgeClass(estado: string): string {
    const clases: Record<string, string> = {
      borrador: 'badge-secondary',
      enviada: 'badge-info',
      en_cotizacion: 'badge-warning',
      aprobada: 'badge-success',
      rechazada: 'badge-danger',
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
}
