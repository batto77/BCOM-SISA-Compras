import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  DxDataGridModule,
  DxDataGridComponent,
  DxButtonModule,
  DxTextBoxModule,
  DxSelectBoxModule,
  DxTagBoxModule,
  DxPopupModule,
  DxSwitchModule,
  DxNumberBoxModule,
} from 'devextreme-angular';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { EtiquetasService } from '../../../core/services/etiquetas.service';
import { ParametrosService } from '../../../core/services/parametros.service';
import { Servicio, CategoriaServicio } from '../../../core/models/catalogos.model';
import { Etiqueta } from '../../../core/models/etiquetas.model';
import { TipoServicio, UnidadMedida } from '../../../core/models/parametros.model';

@Component({
  selector: 'app-servicios-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DxDataGridModule,
    DxButtonModule,
    DxTextBoxModule,
    DxSelectBoxModule,
    DxTagBoxModule,
    DxPopupModule,
    DxSwitchModule,
    DxNumberBoxModule,
  ],
  templateUrl: './servicios-list.component.html',
})
export class ServiciosListComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  servicios: Servicio[] = [];
  categoriasServicio: CategoriaServicio[] = [];
  tiposServicio: TipoServicio[] = [];
  unidades: UnidadMedida[] = [];
  etiquetas: Etiqueta[] = [];
  cargando = false;
  error = '';

  popupVisible = false;
  modoEdicion = false;
  servicioActual: Partial<Servicio> & { etiquetas_ids?: number[] } = {};

  constructor(
    private catalogosService: CatalogosService,
    private etiquetasService: EtiquetasService,
    private parametrosService: ParametrosService,
  ) {}

  ngOnInit(): void {
    this.catalogosService.getCategoriasServicio().subscribe({ next: c => { this.categoriasServicio = c; } });
    this.parametrosService.getTiposServicio().subscribe({ next: t => { this.tiposServicio = t; } });
    this.parametrosService.getUnidadesMedida().subscribe({ next: u => { this.unidades = u; } });
    this.etiquetasService.getEtiquetas().subscribe({ next: e => { this.etiquetas = e; } });
    this.cargarServicios();
  }

  cargarServicios(): void {
    this.cargando = true;
    this.error = '';
    this.catalogosService.getServicios().subscribe({
      next: data => { this.servicios = data; this.cargando = false; },
      error: () => {
        this.error = 'No se pudo conectar con el servidor. Verifique que el backend esté activo.';
        this.cargando = false;
      },
    });
  }

  abrirNuevo(): void {
    this.servicioActual = { activo: true, etiquetas: [], etiquetas_ids: [] };
    this.modoEdicion = false;
    this.popupVisible = true;
  }

  abrirEditar(servicio: Servicio): void {
    this.servicioActual = {
      ...servicio,
      etiquetas_ids: (servicio.etiquetas || []).map(e => e.id),
    };
    this.modoEdicion = true;
    this.popupVisible = true;
  }

  guardar(): void {
    if (!this.servicioActual.nombre?.trim()) return;
    const payload = {
      ...this.servicioActual,
      etiquetas: (this.servicioActual.etiquetas_ids || []).map(id => ({ id } as Etiqueta)),
    };
    delete (payload as Record<string, unknown>)['etiquetas_ids'];

    const id = this.servicioActual.id;
    if (this.modoEdicion && id) {
      this.catalogosService.updateServicio(id, payload).subscribe({
        next: () => { this.popupVisible = false; this.cargarServicios(); },
      });
    } else {
      this.catalogosService.createServicio(payload).subscribe({
        next: () => { this.popupVisible = false; this.cargarServicios(); },
      });
    }
  }

  limpiarFiltros(): void {
    this.grid.instance.clearFilter();
  }

  getCategoriaServNombre(id?: number): string {
    if (!id) return '—';
    return this.categoriasServicio.find(c => c.id === id)?.nombre ?? '—';
  }

  getTipoServNombre(id?: number): string {
    if (!id) return '—';
    return this.tiposServicio.find(t => t.id === id)?.nombre ?? '—';
  }

  getUnidadNombre(id?: number): string {
    if (!id) return '—';
    const u = this.unidades.find(u => u.id === id);
    return u ? `${u.nombre} (${u.simbolo})` : '—';
  }
}
