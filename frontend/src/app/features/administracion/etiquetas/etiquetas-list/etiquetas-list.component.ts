import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  DxDataGridModule,
  DxDataGridComponent,
  DxPopupModule,
  DxButtonModule,
  DxColorBoxModule,
  DxTextBoxModule,
  DxSelectBoxModule,
  DxSwitchModule,
} from 'devextreme-angular';
import { EtiquetasService } from '../../../../core/services/etiquetas.service';
import { Etiqueta, Dimension } from '../../../../core/models/etiquetas.model';

@Component({
  selector: 'app-etiquetas-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DxDataGridModule,
    DxPopupModule,
    DxButtonModule,
    DxColorBoxModule,
    DxTextBoxModule,
    DxSelectBoxModule,
    DxSwitchModule,
  ],
  templateUrl: './etiquetas-list.component.html',
})
export class EtiquetasListComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  etiquetas: Etiqueta[] = [];
  dimensiones: Dimension[] = [];
  dimensiones_con_libre: Array<{ id: number | null; nombre: string }> = [];
  cargando = false;
  error = '';

  popupVisible = false;
  modoEdicion = false;
  etiquetaActual: Partial<Etiqueta> = {};

  constructor(private etiquetasService: EtiquetasService) {}

  ngOnInit(): void {
    this.cargarDimensiones();
    this.cargarEtiquetas();
  }

  cargarDimensiones(): void {
    this.etiquetasService.getDimensiones().subscribe({
      next: (data) => {
        this.dimensiones = data;
        this.dimensiones_con_libre = [
          { id: null, nombre: 'Sin categoría' },
          ...data.map(d => ({ id: d.id, nombre: d.nombre })),
        ];
      },
    });
  }

  limpiarFiltros(): void {
    this.grid.instance.clearFilter();
  }

  cargarEtiquetas(): void {
    this.cargando = true;
    this.error = '';
    this.etiquetasService.getEtiquetas().subscribe({
      next: (data) => {
        this.etiquetas = data;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo conectar con el servidor. Verifique que el backend esté activo.';
        this.cargando = false;
      },
    });
  }

  abrirNueva(): void {
    this.etiquetaActual = { activo: true };
    this.modoEdicion = false;
    this.popupVisible = true;
  }

  abrirEditar(etiqueta: Etiqueta): void {
    this.etiquetaActual = { ...etiqueta };
    this.modoEdicion = true;
    this.popupVisible = true;
  }

  guardar(): void {
    if (!this.etiquetaActual.nombre?.trim()) return;
    const payload = { ...this.etiquetaActual };
    if (payload.dimension_id === null) delete payload.dimension_id;

    if (this.modoEdicion && this.etiquetaActual.id) {
      this.etiquetasService.updateEtiqueta(this.etiquetaActual.id, payload).subscribe({
        next: (result) => {
          if (result) { this.popupVisible = false; this.cargarEtiquetas(); }
        },
      });
    } else {
      this.etiquetasService.createEtiqueta(payload).subscribe({
        next: (result) => {
          if (result) { this.popupVisible = false; this.cargarEtiquetas(); }
        },
      });
    }
  }

  cancelar(): void {
    this.popupVisible = false;
  }

  toggleActivo(etiqueta: Etiqueta): void {
    this.etiquetasService.updateEtiqueta(etiqueta.id, { activo: !etiqueta.activo }).subscribe({
      next: () => this.cargarEtiquetas(),
    });
  }

  getNombreDimension(etiqueta: Etiqueta): string {
    if (!etiqueta.dimension_id) return 'Libre';
    const dim = this.dimensiones.find(d => d.id === etiqueta.dimension_id);
    return dim?.nombre ?? 'Libre';
  }

  dimensionCellValue = (etiqueta: Etiqueta): string => this.getNombreDimension(etiqueta);
}
