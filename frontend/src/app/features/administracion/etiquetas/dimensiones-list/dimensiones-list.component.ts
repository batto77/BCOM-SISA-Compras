import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  DxDataGridModule,
  DxDataGridComponent,
  DxPopupModule,
  DxFormModule,
  DxButtonModule,
  DxColorBoxModule,
  DxTextBoxModule,
  DxSwitchModule,
} from 'devextreme-angular';
import { EtiquetasService } from '../../../../core/services/etiquetas.service';
import { Dimension } from '../../../../core/models/etiquetas.model';

@Component({
  selector: 'app-dimensiones-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DxDataGridModule,
    DxPopupModule,
    DxFormModule,
    DxButtonModule,
    DxColorBoxModule,
    DxTextBoxModule,
    DxSwitchModule,
  ],
  templateUrl: './dimensiones-list.component.html',
})
export class DimensionesListComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  dimensiones: Dimension[] = [];
  cargando = false;
  error = '';

  popupVisible = false;
  modoEdicion = false;
  dimensionActual: Partial<Dimension> = {};

  constructor(private etiquetasService: EtiquetasService) {}

  ngOnInit(): void {
    this.cargarDimensiones();
  }

  cargarDimensiones(): void {
    this.cargando = true;
    this.error = '';
    this.etiquetasService.getDimensiones().subscribe({
      next: (data) => {
        this.dimensiones = data;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo conectar con el servidor. Verifique que el backend esté activo.';
        this.cargando = false;
      },
    });
  }

  abrirNueva(): void {
    this.dimensionActual = { activo: true };
    this.modoEdicion = false;
    this.popupVisible = true;
  }

  abrirEditar(dimension: Dimension): void {
    this.dimensionActual = { ...dimension };
    this.modoEdicion = true;
    this.popupVisible = true;
  }

  guardar(): void {
    if (!this.dimensionActual.nombre?.trim()) {
      return;
    }
    if (this.modoEdicion && this.dimensionActual.id) {
      this.etiquetasService.updateDimension(this.dimensionActual.id, this.dimensionActual).subscribe({
        next: (result) => {
          if (result) {
            this.popupVisible = false;
            this.cargarDimensiones();
          }
        },
      });
    } else {
      this.etiquetasService.createDimension(this.dimensionActual).subscribe({
        next: (result) => {
          if (result) {
            this.popupVisible = false;
            this.cargarDimensiones();
          }
        },
      });
    }
  }

  limpiarFiltros(): void {
    this.grid.instance.clearFilter();
  }

  cancelar(): void {
    this.popupVisible = false;
  }

  toggleActivo(dimension: Dimension): void {
    this.etiquetasService.updateDimension(dimension.id, { activo: !dimension.activo }).subscribe({
      next: () => this.cargarDimensiones(),
    });
  }
}
