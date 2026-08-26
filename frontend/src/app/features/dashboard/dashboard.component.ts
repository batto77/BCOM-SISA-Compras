import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DashboardResumen } from '../../core/models/dashboard.model';
import { DashboardService } from '../../core/services/dashboard.service';
import {
  getPrioridadBadgeClass,
  getPrioridadAyuda,
  getPrioridadNombre,
} from '../../shared/utils/prioridades.util';

interface DashboardCard {
  titulo: string;
  valor: number;
  icono: string;
  color: string;
  ruta: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  resumen: DashboardResumen | null = null;
  cargando = true;
  error = '';

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando = true;
    this.error = '';
    this.dashboardService.getResumen().subscribe({
      next: resumen => {
        this.resumen = resumen;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar las estadísticas del sistema.';
        this.cargando = false;
      },
    });
  }

  get tarjetas(): DashboardCard[] {
    return [
      {
        titulo: 'Oportunidades activas',
        valor: this.resumen?.oportunidades_activas ?? 0,
        icono: 'fas fa-file-alt',
        color: 'warning',
        ruta: '/solicitudes',
      },
      {
        titulo: 'Cotizaciones pendientes',
        valor: this.resumen?.cotizaciones_pendientes ?? 0,
        icono: 'fas fa-clock',
        color: 'info',
        ruta: '/cotizaciones',
      },
      {
        titulo: 'Respuestas recibidas',
        valor: this.resumen?.cotizaciones_respondidas ?? 0,
        icono: 'fas fa-check-circle',
        color: 'primary',
        ruta: '/cotizaciones',
      },
      {
        titulo: 'Proveedores activos',
        valor: this.resumen?.proveedores_activos ?? 0,
        icono: 'fas fa-truck',
        color: 'success',
        ruta: '/proveedores',
      },
    ];
  }

  get estadosOportunidad(): Array<{ estado: string; cantidad: number }> {
    return Object.entries(this.resumen?.oportunidades_por_estado ?? {})
      .map(([estado, cantidad]) => ({ estado, cantidad }))
      .sort((a, b) => b.cantidad - a.cantidad);
  }

  getEstadoBadgeClass(estado: string): string {
    const clases: Record<string, string> = {
      borrador: 'badge-secondary',
      enviada: 'badge-info',
      en_cotizacion: 'badge-primary',
      adjudicada: 'badge-success',
      aprobada: 'badge-success',   // histórico: reemplazado por 'adjudicada'
      rechazada: 'badge-danger',
      cancelada: 'badge-dark',
    };
    return clases[estado] ?? 'badge-secondary';
  }

  getEstadoLabel(estado: string): string {
    const etiquetas: Record<string, string> = {
      borrador: 'Borrador',
      enviada: 'Enviada',
      en_cotizacion: 'En cotización',
      adjudicada: 'Adjudicada',
      aprobada: 'Aprobada',
      rechazada: 'Rechazada',
      cancelada: 'Cancelada',
    };
    return etiquetas[estado] ?? estado;
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
