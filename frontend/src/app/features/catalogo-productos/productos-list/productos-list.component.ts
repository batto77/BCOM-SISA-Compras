import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DxDataGridModule, DxDataGridComponent } from 'devextreme-angular';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { Producto } from '../../../core/models/catalogos.model';

@Component({
  selector: 'app-productos-list',
  standalone: true,
  imports: [CommonModule, RouterLink, DxDataGridModule],
  templateUrl: './productos-list.component.html',
})
export class ProductosListComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  productos: Producto[] = [];
  cargando = false;
  error = '';

  constructor(private catalogosService: CatalogosService) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando = true;
    this.error = '';
    this.catalogosService.getProductos().subscribe({
      next: data => { this.productos = data; this.cargando = false; },
      error: () => {
        this.error = 'No se pudo conectar con el servidor.';
        this.cargando = false;
      },
    });
  }

  limpiarFiltros(): void {
    this.grid.instance.clearFilter();
  }

  getEtiquetasTexto(producto: Producto): string {
    return (producto.etiquetas || []).map(et => et.nombre).join(', ');
  }
}
