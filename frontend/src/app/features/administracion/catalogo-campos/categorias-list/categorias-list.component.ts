import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  DxDataGridModule,
  DxDataGridComponent,
  DxPopupModule,
  DxButtonModule,
  DxTextBoxModule,
  DxSelectBoxModule,
  DxSwitchModule,
  DxNumberBoxModule,
  DxTagBoxModule,
} from 'devextreme-angular';
import { CatalogosService } from '../../../../core/services/catalogos.service';
import { ParametrosService } from '../../../../core/services/parametros.service';
import { CategoriaProducto, DefinicionCampo } from '../../../../core/models/catalogos.model';
import { UnidadMedida } from '../../../../core/models/parametros.model';

@Component({
  selector: 'app-categorias-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DxDataGridModule,
    DxPopupModule,
    DxButtonModule,
    DxTextBoxModule,
    DxSelectBoxModule,
    DxSwitchModule,
    DxNumberBoxModule,
    DxTagBoxModule,
  ],
  templateUrl: './categorias-list.component.html',
})
export class CategoriasListComponent implements OnInit {
  @ViewChild('gridCategorias') gridCategorias!: DxDataGridComponent;
  @ViewChild('gridCampos') gridCampos!: DxDataGridComponent;

  categorias: CategoriaProducto[] = [];
  categoriaSeleccionada: CategoriaProducto | null = null;
  campos: DefinicionCampo[] = [];
  unidades: UnidadMedida[] = [];

  cargando = false;
  cargandoCampos = false;
  error = '';

  // Popup campo
  popupCampoVisible = false;
  modoEdicionCampo = false;
  campoActual: Partial<DefinicionCampo> = {};

  // Popup categoría
  popupCategoriaVisible = false;
  modoEdicionCategoria = false;
  categoriaActual: Partial<CategoriaProducto> = {};

  tiposDato = ['texto', 'numero', 'booleano'];
  tiposCategoria = [
    { id: 'hardware', nombre: 'Hardware' },
    { id: 'software', nombre: 'Software' },
    { id: 'licencia', nombre: 'Licencia' },
    { id: 'servicio', nombre: 'Servicio' },
  ];

  constructor(
    private catalogosService: CatalogosService,
    private parametrosService: ParametrosService,
  ) {}

  ngOnInit(): void {
    this.cargarCategorias();
    this.parametrosService.getUnidadesMedida().subscribe({
      next: u => { this.unidades = u; },
    });
  }

  cargarCategorias(): void {
    this.cargando = true;
    this.catalogosService.getCategorias().subscribe({
      next: data => {
        this.categorias = data;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo conectar con el servidor.';
        this.cargando = false;
      },
    });
  }

  limpiarFiltrosCampos(): void {
    this.gridCampos?.instance?.clearFilter();
  }

  limpiarFiltrosCategorias(): void {
    this.gridCategorias?.instance?.clearFilter();
  }

  seleccionarCategoria(cat: CategoriaProducto): void {
    this.categoriaSeleccionada = cat;
    this.cargandoCampos = true;
    this.catalogosService.getCamposCategoria(cat.id).subscribe({
      next: data => {
        this.campos = data;
        this.cargandoCampos = false;
      },
      error: () => { this.cargandoCampos = false; },
    });
  }

  // --- Categoría ---

  abrirNuevaCategoria(): void {
    this.categoriaActual = { activo: true };
    this.modoEdicionCategoria = false;
    this.popupCategoriaVisible = true;
  }

  abrirEditarCategoria(categoria: CategoriaProducto): void {
    this.categoriaActual = { ...categoria };
    this.modoEdicionCategoria = true;
    this.popupCategoriaVisible = true;
  }

  guardarCategoria(): void {
    if (!this.categoriaActual.nombre?.trim()) return;
    const id = this.categoriaActual.id;
    if (this.modoEdicionCategoria && id) {
      this.catalogosService.updateCategoria(id, this.categoriaActual).subscribe({
        next: categoria => {
          if (!categoria) {
            this.error = 'No se pudo actualizar la categoría.';
            return;
          }
          this.popupCategoriaVisible = false;
          this.cargarCategorias();
        },
      });
    } else {
      this.catalogosService.createCategoria(this.categoriaActual).subscribe({
        next: categoria => {
          if (!categoria) {
            this.error = 'No se pudo crear la categoría. Revise el nombre y el tipo.';
            return;
          }
          this.popupCategoriaVisible = false;
          this.cargarCategorias();
          this.seleccionarCategoria(categoria);
        },
      });
    }
  }

  // --- Campo ---

  abrirNuevoCampo(): void {
    if (!this.categoriaSeleccionada) return;
    this.campoActual = {
      activo: true,
      es_obligatorio: false,
      es_campo_base: false,
      tiene_cantidad: false,
      tiene_unidad: false,
      tipo_dato: 'texto',
      orden: (this.campos.length + 1),
      opciones_unidad: [],
    };
    this.modoEdicionCampo = false;
    this.popupCampoVisible = true;
  }

  abrirEditarCampo(campo: DefinicionCampo): void {
    this.campoActual = { ...campo, opciones_unidad: [...(campo.opciones_unidad || [])] };
    this.modoEdicionCampo = true;
    this.popupCampoVisible = true;
  }

  guardarCampo(): void {
    if (!this.categoriaSeleccionada || !this.campoActual.nombre?.trim()) return;
    const catId = this.categoriaSeleccionada.id;
    const campoId = this.campoActual.id;
    if (this.modoEdicionCampo && campoId) {
      this.catalogosService.updateCampo(catId, campoId, this.campoActual).subscribe({
        next: () => { this.popupCampoVisible = false; this.seleccionarCategoria(this.categoriaSeleccionada!); },
      });
    } else {
      this.catalogosService.createCampo(catId, this.campoActual).subscribe({
        next: () => { this.popupCampoVisible = false; this.seleccionarCategoria(this.categoriaSeleccionada!); },
      });
    }
  }

  toggleActivoCampo(campo: DefinicionCampo): void {
    if (!this.categoriaSeleccionada) return;
    this.catalogosService.updateCampo(this.categoriaSeleccionada.id, campo.id, { activo: !campo.activo }).subscribe({
      next: () => this.seleccionarCategoria(this.categoriaSeleccionada!),
    });
  }

  autoSlug(nombre: string): void {
    if (!this.modoEdicionCampo) {
      this.campoActual.clave = nombre
        .toLowerCase()
        .normalize('NFD').replace(/[̀-ͯ]/g, '')
        .replace(/\s+/g, '_')
        .replace(/[^a-z0-9_]/g, '');
    }
  }

  getTipoBadgeClass(tipo: string): string {
    switch (tipo) {
      case 'texto': return 'badge-primary';
      case 'numero': return 'badge-warning';
      case 'booleano': return 'badge-info';
      default: return 'badge-secondary';
    }
  }

  getUnidadesIds(campo: Partial<DefinicionCampo>): number[] {
    return (campo.opciones_unidad || []).map(u => u.id);
  }

  onOpcionesUnidadChange(ids: number[]): void {
    this.campoActual.opciones_unidad = ids
      .map(id => this.unidades.find(u => u.id === id))
      .filter((u): u is UnidadMedida => u !== undefined);
  }
}
