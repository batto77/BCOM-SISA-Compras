import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DxDataGridModule, DxDataGridComponent } from 'devextreme-angular';
import { ProveedoresService } from '../../../core/services/proveedores.service';
import { Proveedor } from '../../../core/models/proveedores.model';
import { Etiqueta } from '../../../core/models/etiquetas.model';

@Component({
  selector: 'app-proveedores-list',
  standalone: true,
  imports: [CommonModule, RouterLink, DxDataGridModule],
  templateUrl: './proveedores-list.component.html',
})
export class ProveedoresListComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  proveedores: Proveedor[] = [];
  cargando = false;
  error = '';
  readonly estrellas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

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
}
