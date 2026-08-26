import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  DxDataGridModule,
  DxDataGridComponent,
  DxButtonModule,
} from 'devextreme-angular';

import { CotizacionesService } from '../../core/services/cotizaciones.service';
import { CotizacionOut } from '../../core/models/cotizaciones.model';

@Component({
  selector: 'app-cotizaciones',
  standalone: true,
  imports: [CommonModule, RouterLink, DxDataGridModule, DxButtonModule],
  templateUrl: './cotizaciones.component.html',
})
export class CotizacionesComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  cotizaciones: CotizacionOut[] = [];
  cargando = false;
  error = '';
  recordatorioMsg = '';
  recordatorioError = '';
  enviandoRecordatorio: Record<number, boolean> = {};

  constructor(private cotizacionesService: CotizacionesService) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando = true;
    this.error = '';
    this.cotizacionesService.getCotizaciones({ limit: 100 }).subscribe({
      next: data => {
        this.cotizaciones = data.items;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo conectar con el servidor.';
        this.cargando = false;
      },
    });
  }

  limpiarFiltros(): void {
    this.grid.instance.clearFilter();
  }

  getEstadoBadgeClass(estado: string): string {
    const clases: Record<string, string> = {
      invitada: 'badge-warning',
      respondida: 'badge-success',
      descartada: 'badge-secondary',
    };
    return clases[estado] ?? 'badge-secondary';
  }

  /**
   * Estado mostrado en la grilla. La adjudicación no vive en la cotización sino
   * en la oportunidad, así que se antepone cuando corresponde: saber que una
   * cotización ganó importa más que saber que fue respondida.
   */
  getEstadoTexto(cot: CotizacionOut): string {
    return cot.adjudicada ? 'adjudicada' : cot.estado;
  }

  getEstadoClase(cot: CotizacionOut): string {
    return cot.adjudicada ? 'badge-primary' : this.getEstadoBadgeClass(cot.estado);
  }

  getEstadoAyuda(cot: CotizacionOut): string {
    if (cot.adjudicada) {
      return `Se le adjudicaron ${cot.items_adjudicados} ítem(s) de esta oportunidad`;
    }
    return '';
  }

  enviarRecordatorio(cotizacionId: number): void {
    if (this.enviandoRecordatorio[cotizacionId]) return;
    this.enviandoRecordatorio[cotizacionId] = true;
    this.recordatorioMsg = '';
    this.recordatorioError = '';
    this.cotizacionesService.enviarRecordatorio(cotizacionId).subscribe({
      next: res => {
        this.enviandoRecordatorio[cotizacionId] = false;
        const email = res.email ?? 'sin email configurado';
        this.recordatorioMsg = `Recordatorio registrado para ${res.proveedor ?? 'proveedor'} (${email}).`;
        setTimeout(() => { this.recordatorioMsg = ''; }, 6000);
      },
      error: err => {
        this.enviandoRecordatorio[cotizacionId] = false;
        this.recordatorioError = err?.error?.detail ?? 'No se pudo enviar el recordatorio.';
        setTimeout(() => { this.recordatorioError = ''; }, 5000);
      },
    });
  }
}
