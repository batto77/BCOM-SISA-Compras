import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute, Router } from '@angular/router';
import {
  DxTextBoxModule,
  DxSelectBoxModule,
  DxTagBoxModule,
  DxSwitchModule,
  DxButtonModule,
  DxNumberBoxModule,
} from 'devextreme-angular';
import { CatalogosService } from '../../../core/services/catalogos.service';
import { EtiquetasService } from '../../../core/services/etiquetas.service';
import { ParametrosService } from '../../../core/services/parametros.service';
import {
  Producto,
  CategoriaProducto,
  DefinicionCampo,
  ValorEspecificacion,
  ModeloProducto,
} from '../../../core/models/catalogos.model';
import { Etiqueta } from '../../../core/models/etiquetas.model';
import { UnidadMedida } from '../../../core/models/parametros.model';

@Component({
  selector: 'app-producto-form',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DxTextBoxModule,
    DxSelectBoxModule,
    DxTagBoxModule,
    DxSwitchModule,
    DxButtonModule,
    DxNumberBoxModule,
  ],
  templateUrl: './producto-form.component.html',
})
export class ProductoFormComponent implements OnInit {
  modoEdicion = false;
  modoClonar = false;
  productoId: number | null = null;
  cargando = false;
  guardando = false;
  error = '';
  exito = '';

  categorias: CategoriaProducto[] = [];
  etiquetas: Etiqueta[] = [];
  camposCategoria: DefinicionCampo[] = [];
  productosExistentes: Producto[] = [];

  // Modelo principal
  producto: Partial<Producto> = {
    activo: true,
    modo_defecto: 'funcional',
    etiquetas: [],
    especificaciones: [],
    modelos_alternativos: [],
  };

  etiquetasSeleccionadas: number[] = [];
  especificaciones: Record<number, ValorEspecificacion> = {};
  modelos: Partial<ModeloProducto>[] = [];

  constructor(
    private catalogosService: CatalogosService,
    private etiquetasService: EtiquetasService,
    private parametrosService: ParametrosService,
    private route: ActivatedRoute,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.catalogosService.getCategorias().subscribe({ next: c => { this.categorias = c; } });
    this.etiquetasService.getEtiquetas().subscribe({ next: e => { this.etiquetas = e; } });
    this.catalogosService.getProductos().subscribe({ next: p => { this.productosExistentes = p; } });

    const id = this.route.snapshot.paramMap.get('id');
    this.modoClonar = this.route.snapshot.url.some(seg => seg.path === 'clonar');

    if (id) {
      if (this.modoClonar) {
        this.cargarProducto(+id, true);
      } else {
        this.modoEdicion = true;
        this.productoId = +id;
        this.cargarProducto(this.productoId);
      }
    }
  }

  cargarProducto(id: number, paraClonar = false): void {
    this.cargando = true;
    this.catalogosService.getProducto(id).subscribe({
      next: prod => {
        if (prod) {
          this.producto = { ...prod };
          if (paraClonar) {
            this.producto.nombre = `${prod.nombre} (copia)`;
          }
          this.etiquetasSeleccionadas = (prod.etiquetas || []).map(e => e.id);
          this.modelos = (prod.modelos_alternativos || []).map(m => ({ ...m, id: undefined }));
          if (prod.categoria_producto_id) {
            this.cargarCamposCategoria(prod.categoria_producto_id, prod.especificaciones);
          }
        }
        this.cargando = false;
      },
      error: () => { this.error = 'No se pudo cargar el producto.'; this.cargando = false; },
    });
  }

  nombreDuplicado(): boolean {
    const nombre = this.producto.nombre?.trim().toLowerCase();
    if (!nombre) return false;
    return this.productosExistentes.some(
      p => p.nombre.trim().toLowerCase() === nombre && p.id !== this.productoId,
    );
  }

  onCategoriaChange(categoriaId: number): void {
    this.producto.categoria_producto_id = categoriaId;
    this.especificaciones = {};
    this.cargarCamposCategoria(categoriaId);
  }

  cargarCamposCategoria(categoriaId: number, especsPrevias?: ValorEspecificacion[]): void {
    this.catalogosService.getCamposCategoria(categoriaId).subscribe({
      next: campos => {
        this.camposCategoria = campos.filter(c => c.activo).sort((a, b) => a.orden - b.orden);
        // Inicializar especificaciones
        this.especificaciones = {};
        this.camposCategoria.forEach(campo => {
          const prev = especsPrevias?.find(e => e.campo_id === campo.id);
          this.especificaciones[campo.id] = prev ? { ...prev } : { campo_id: campo.id };
        });
      },
    });
  }

  setModo(modo: 'funcional' | 'modelos_especificos'): void {
    this.producto.modo_defecto = modo;
  }

  // --- Modelos alternativos ---

  agregarModelo(): void {
    this.modelos.push({ fabricante: '', modelo: '', es_primario: false, orden: this.modelos.length + 1 });
  }

  eliminarModelo(idx: number): void {
    this.modelos.splice(idx, 1);
  }

  // --- Helpers para specs ---

  getEspecValor(campoId: number): string {
    return (this.especificaciones[campoId]?.valor) ?? '';
  }

  setEspecValor(campoId: number, valor: string): void {
    if (!this.especificaciones[campoId]) {
      this.especificaciones[campoId] = { campo_id: campoId };
    }
    this.especificaciones[campoId].valor = valor;
  }

  getEspecCantidad(campoId: number): number | null {
    return this.especificaciones[campoId]?.cantidad ?? null;
  }

  setEspecCantidad(campoId: number, cantidad: number): void {
    if (!this.especificaciones[campoId]) {
      this.especificaciones[campoId] = { campo_id: campoId };
    }
    this.especificaciones[campoId].cantidad = cantidad;
  }

  getEspecUnidad(campoId: number): number | null {
    return this.especificaciones[campoId]?.unidad_medida_id ?? null;
  }

  setEspecUnidad(campoId: number, unidadId: number): void {
    if (!this.especificaciones[campoId]) {
      this.especificaciones[campoId] = { campo_id: campoId };
    }
    this.especificaciones[campoId].unidad_medida_id = unidadId;
  }

  getEspecBool(campoId: number): boolean {
    return this.especificaciones[campoId]?.valor === 'true';
  }

  setEspecBool(campoId: number, val: boolean): void {
    if (!this.especificaciones[campoId]) {
      this.especificaciones[campoId] = { campo_id: campoId };
    }
    this.especificaciones[campoId].valor = val ? 'true' : 'false';
  }

  esSoftwareOLicencia(): boolean {
    if (!this.producto.categoria_producto_id) return false;
    const cat = this.categorias.find(c => c.id === this.producto.categoria_producto_id);
    return cat?.tipo === 'software' || cat?.tipo === 'licencia';
  }

  // --- Guardar ---

  guardar(): void {
    if (!this.producto.nombre?.trim()) {
      this.error = 'El nombre del producto es obligatorio.';
      return;
    }
    if (this.nombreDuplicado()) {
      this.error = 'Ya existe un producto con ese nombre. Elegí un nombre distinto.';
      return;
    }
    this.guardando = true;
    this.error = '';

    const payload = {
      ...this.producto,
      etiquetas: this.etiquetasSeleccionadas.map(id => ({ id } as Etiqueta)),
      especificaciones: Object.values(this.especificaciones).filter(e => e.valor || e.cantidad || e.unidad_medida_id),
      modelos_alternativos: this.modelos as ModeloProducto[],
    } as Partial<Producto>;

    if (this.modoEdicion && this.productoId) {
      this.catalogosService.updateProducto(this.productoId, payload).subscribe({
        next: result => {
          this.guardando = false;
          if (result) {
            this.exito = 'Producto actualizado correctamente.';
          } else {
            this.error = 'No se pudo guardar. Intente nuevamente.';
          }
        },
        error: () => { this.error = 'Error al guardar.'; this.guardando = false; },
      });
    } else {
      this.catalogosService.createProducto(payload).subscribe({
        next: result => {
          this.guardando = false;
          if (result) {
            this.router.navigate(['/catalogo-productos']);
          } else {
            this.error = 'No se pudo guardar. Intente nuevamente.';
          }
        },
        error: () => { this.error = 'Error al guardar.'; this.guardando = false; },
      });
    }
  }

  cancelar(): void {
    this.router.navigate(['/catalogo-productos']);
  }
}
