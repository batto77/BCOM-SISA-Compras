import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DxDataGridModule, DxDataGridComponent, DxPopupModule } from 'devextreme-angular';
import { ProveedoresService, ImportacionProveedoresResultado } from '../../../core/services/proveedores.service';
import { Proveedor } from '../../../core/models/proveedores.model';
import { Etiqueta } from '../../../core/models/etiquetas.model';

@Component({
  selector: 'app-proveedores-list',
  standalone: true,
  imports: [CommonModule, RouterLink, DxDataGridModule, DxPopupModule],
  templateUrl: './proveedores-list.component.html',
})
export class ProveedoresListComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  proveedores: Proveedor[] = [];
  cargando = false;
  error = '';
  readonly estrellas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  importando = false;
  importError = '';
  resultadoImportacion: ImportacionProveedoresResultado | null = null;
  popupResultadoVisible = false;

  constructor(private proveedoresService: ProveedoresService) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando = true;
    this.error = '';
    this.proveedoresService.getProveedores().subscribe({
      next: data => { this.proveedores = data; this.cargando = false; },
      error: () => {
        this.error = 'No se pudo conectar con el servidor. Verifique que el backend esté activo.';
        this.cargando = false;
      },
    });
  }

  limpiarFiltros(): void {
    this.grid.instance.clearFilter();
  }

  getEtiquetasProveedor(proveedor: Proveedor): Etiqueta[] {
    return proveedor.etiquetas || [];
  }

  getEtiquetasTexto(proveedor: Proveedor): string {
    return (proveedor.etiquetas || []).map(et => et.nombre).join(', ');
  }

  descargarPlantilla(): void {
    this.proveedoresService.descargarPlantilla().subscribe({
      next: blob => {
        if (!blob) {
          this.error = 'No se pudo descargar la plantilla.';
          return;
        }
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'plantilla_proveedores.xlsx';
        a.click();
        window.URL.revokeObjectURL(url);
      },
    });
  }

  onArchivoSeleccionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = '';
    if (!file) return;

    this.importando = true;
    this.importError = '';
    this.resultadoImportacion = null;

    this.proveedoresService.importarProveedores(file).subscribe({
      next: resultado => {
        this.importando = false;
        if (!resultado) {
          this.importError = 'No se pudo procesar el archivo. Verificá el formato e intentá nuevamente.';
          return;
        }
        this.resultadoImportacion = resultado;
        this.popupResultadoVisible = true;
        if (resultado.creados > 0) {
          this.cargar();
        }
      },
      error: () => {
        this.importando = false;
        this.importError = 'No se pudo procesar el archivo. Verificá el formato e intentá nuevamente.';
      },
    });
  }
}
