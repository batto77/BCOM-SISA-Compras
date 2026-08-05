import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { CatalogosService } from '../../core/services/catalogos.service';
import { CotizacionesService } from '../../core/services/cotizaciones.service';
import { ParametrosService } from '../../core/services/parametros.service';
import { ProveedorSugerido, ProveedoresService } from '../../core/services/proveedores.service';
import { SolicitudesService } from '../../core/services/solicitudes.service';
import { CategoriaProducto, DefinicionCampo, Servicio } from '../../core/models/catalogos.model';
import { UnidadMedida } from '../../core/models/parametros.model';
import { ItemSolicitudForm, SolicitudCompraOut } from '../../core/models/solicitudes.model';
import { FieldHelpDirective } from '../../shared/directives/field-help.directive';

type PasoCotizacion = 'productos' | 'servicios' | 'licencias' | 'proveedores';
type TipoItemCotizacion = ItemSolicitudForm['tipo'];

interface ItemDraft {
  categoriaId: number | null;
  servicioId: number | null;
  descripcion: string;
  cantidad: number;
  unidadId: number | null;
  especificacionesTexto: string;
  specValues: Record<string, string | number | boolean | null>;
  notas: string;
}

interface EspecificacionGuardada {
  campo_id?: number;
  clave: string;
  nombre?: string;
  tipo_dato?: string;
  valor?: string | number | boolean | null;
  cantidad?: number | null;
  unidad_medida_id?: number | null;
  unidad_nombre?: string;
  unidad_simbolo?: string;
}

interface ProveedorSeleccionable extends ProveedorSugerido {
  seleccionado: boolean;
  itemIds: number[];
}

@Component({
  selector: 'app-cotizacion-asistente',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, FieldHelpDirective],
  templateUrl: './cotizacion-asistente.component.html',
  styleUrl: './cotizacion-asistente.component.scss',
})
export class CotizacionAsistenteComponent implements OnInit {
  solicitud: SolicitudCompraOut | null = null;
  paso: PasoCotizacion = 'productos';
  cargando = true;
  guardando = false;
  error = '';
  exito = '';
  fechaLimiteRFQ = '';

  categorias: CategoriaProducto[] = [];
  camposCategoria: DefinicionCampo[] = [];
  servicios: Servicio[] = [];
  unidades: UnidadMedida[] = [];
  items: ItemSolicitudForm[] = [];
  proveedores: ProveedorSeleccionable[] = [];

  draft: ItemDraft = this.nuevoDraft();
  itemEnEdicion: ItemSolicitudForm | null = null;

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private catalogosService: CatalogosService,
    private cotizacionesService: CotizacionesService,
    private parametrosService: ParametrosService,
    private proveedoresService: ProveedoresService,
    private solicitudesService: SolicitudesService,
  ) {}

  ngOnInit(): void {
    const solicitudId = Number(this.route.snapshot.paramMap.get('solicitudId'));
    if (!solicitudId) {
      this.error = 'Oportunidad no válida.';
      this.cargando = false;
      return;
    }

    forkJoin({
      solicitud: this.solicitudesService.getSolicitud(solicitudId),
      categorias: this.catalogosService.getCategorias(),
      servicios: this.catalogosService.getServicios(),
      unidades: this.parametrosService.getUnidadesMedida(),
    }).subscribe({
      next: ({ solicitud, categorias, servicios, unidades }) => {
        this.solicitud = solicitud;
        this.categorias = categorias.filter(categoria => categoria.activo);
        this.servicios = servicios;
        this.unidades = unidades;
        this.items = (solicitud?.items ?? []).map(item => ({
          id: item.id,
          tipo: item.tipo,
          descripcion: item.descripcion,
          cantidad: item.cantidad,
          unidad_medida_id: item.unidad_medida_id,
          producto_id: item.producto_id,
          categoria_producto_id: item.categoria_producto_id,
          servicio_id: item.servicio_id,
          especificaciones: item.especificaciones,
          notas: item.notas,
          presupuesto_estimado: item.presupuesto_estimado,
          orden: item.orden,
          _productoNombre: item.categoria_producto?.nombre ?? item.producto?.nombre,
          _servicioNombre: item.servicio?.nombre,
          _unidadNombre: item.unidad ? `${item.unidad.nombre} (${item.unidad.simbolo})` : undefined,
        }));
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo cargar la oportunidad.';
        this.cargando = false;
      },
    });
  }

  get categoriasHardware(): CategoriaProducto[] {
    return this.categorias.filter(c => c.tipo === 'hardware');
  }

  get categoriasServicio(): CategoriaProducto[] {
    return this.categorias.filter(c => c.tipo === 'servicio');
  }

  get categoriasLicencia(): CategoriaProducto[] {
    return this.categorias.filter(c => c.tipo === 'software');
  }

  get itemsProducto(): ItemSolicitudForm[] {
    return this.items.filter(item => item.tipo === 'producto');
  }

  get itemsServicio(): ItemSolicitudForm[] {
    return this.items.filter(item => item.tipo === 'servicio');
  }

  get itemsLicencia(): ItemSolicitudForm[] {
    return this.items.filter(item => item.tipo === 'licencia');
  }

  get proveedoresDisponibles(): ProveedorSeleccionable[] {
    return this.proveedores.filter(proveedor => !proveedor.seleccionado);
  }

  get proveedoresSeleccionados(): ProveedorSeleccionable[] {
    return this.proveedores.filter(proveedor => proveedor.seleccionado);
  }

  get totalItems(): number {
    return this.items.length;
  }

  activarPaso(paso: PasoCotizacion): void {
    this.error = '';
    this.exito = '';
    if (paso === 'proveedores') {
      this.prepararProveedores();
      return;
    }
    this.paso = paso;
    this.camposCategoria = [];
    this.draft = this.nuevoDraft();
    this.itemEnEdicion = null;
  }

  seleccionarCatalogo(tipo: TipoItemCotizacion | 'licencia', id: number | null): void {
    this.draft.categoriaId = id;
    this.draft.servicioId = null;
    this.draft.specValues = {};
    this.camposCategoria = [];

    const categoria = this.categorias.find(item => item.id === Number(id));
    this.draft.descripcion = categoria?.nombre ?? '';

    if (id) this.cargarCamposCategoria(Number(id));
  }

  agregarItem(tipo: TipoItemCotizacion): void {
    this.error = '';
    const descripcion = this.draft.descripcion.trim();
    if (!descripcion) {
      this.error = 'La descripción del ítem es requerida.';
      return;
    }
    if (!this.draft.cantidad || this.draft.cantidad <= 0) {
      this.error = 'La cantidad debe ser mayor a cero.';
      return;
    }
    if ((tipo === 'producto' || tipo === 'licencia' || tipo === 'servicio') && !this.validarCamposCategoria()) {
      return;
    }

    const categoria = this.draft.categoriaId
      ? this.categorias.find(item => item.id === Number(this.draft.categoriaId))
      : undefined;
    const unidad = this.draft.unidadId
      ? this.unidades.find(item => item.id === Number(this.draft.unidadId))
      : undefined;

    const itemActualizado: ItemSolicitudForm = {
      id: this.itemEnEdicion?.id,
      tipo,
      descripcion,
      cantidad: Number(this.draft.cantidad),
      unidad_medida_id: this.draft.unidadId ?? undefined,
      categoria_producto_id: (tipo === 'producto' || tipo === 'licencia' || tipo === 'servicio')
        ? this.draft.categoriaId ?? undefined
        : undefined,
      producto_id: undefined,
      servicio_id: undefined,
      especificaciones: (tipo === 'producto' || tipo === 'licencia' || tipo === 'servicio')
        ? this.buildEspecificaciones()
        : this.draft.especificacionesTexto.trim() || undefined,
      notas: this.draft.notas.trim() || undefined,
      presupuesto_estimado: this.itemEnEdicion?.presupuesto_estimado,
      orden: this.itemEnEdicion?.orden ?? this.items.length,
      _productoNombre: categoria?.nombre,
      _servicioNombre: undefined,
      _unidadNombre: unidad ? `${unidad.nombre} (${unidad.simbolo})` : undefined,
    };

    if (this.itemEnEdicion) {
      Object.assign(this.itemEnEdicion, itemActualizado);
      this.exito = 'Ítem actualizado. Guarde el paso para aplicar el cambio al RFQ.';
    } else {
      this.items.push(itemActualizado);
    }

    this.itemEnEdicion = null;
    this.camposCategoria = [];
    this.draft = this.nuevoDraft();
  }

  editarItem(item: ItemSolicitudForm): void {
    this.error = '';
    this.exito = '';
    this.itemEnEdicion = item;
    this.paso = this.getPasoPorTipo(item.tipo);
    this.camposCategoria = [];
    this.draft = {
      categoriaId: item.categoria_producto_id ?? null,
      servicioId: item.servicio_id ?? null,
      descripcion: item.descripcion,
      cantidad: Number(item.cantidad),
      unidadId: item.unidad_medida_id ?? null,
      especificacionesTexto: item.especificaciones ?? '',
      specValues: this.parseEspecificaciones(item.especificaciones),
      notas: item.notas ?? '',
    };

    if (item.categoria_producto_id) {
      this.cargarCamposCategoria(item.categoria_producto_id, this.draft.specValues);
    }
  }

  cancelarEdicionItem(): void {
    this.itemEnEdicion = null;
    this.camposCategoria = [];
    this.draft = this.nuevoDraft();
    this.error = '';
  }

  eliminarItem(item: ItemSolicitudForm): void {
    if (this.itemEnEdicion === item) this.cancelarEdicionItem();
    this.items = this.items.filter(current => current !== item);
    this.reordenarItems();
  }

  moverProveedor(proveedor: ProveedorSeleccionable, seleccionado: boolean): void {
    proveedor.seleccionado = seleccionado;
    if (seleccionado && proveedor.itemIds.length === 0) {
      proveedor.itemIds = this.itemIdsActuales();
    }
  }

  getEspecificacionesResumen(item: ItemSolicitudForm): string {
    if (!item.especificaciones) return 'Sin especificaciones';
    try {
      const specs = JSON.parse(item.especificaciones) as Array<{ nombre: string; valor: unknown }>;
      const readable = specs
        .filter(spec => spec.valor !== null && spec.valor !== '')
        .map(spec => `${spec.nombre}: ${spec.valor === true ? 'Sí' : spec.valor === false ? 'No' : spec.valor}`);
      return readable.length ? readable.join(' · ') : 'Sin especificaciones';
    } catch {
      return item.especificaciones;
    }
  }

  enviarRFQ(): void {
    if (!this.solicitud) return;
    if (this.proveedoresSeleccionados.length === 0) {
      this.error = 'Seleccione al menos un proveedor.';
      return;
    }

    this.guardando = true;
    this.error = '';
    this.guardarItemsSolicitud(() => {
      const asignaciones: Record<number, number[]> = {};
      for (const proveedor of this.proveedoresSeleccionados) {
        asignaciones[proveedor.id] = proveedor.itemIds.length
          ? proveedor.itemIds
          : this.itemIdsActuales();
      }
      this.cotizacionesService.enviarRFQ({
        solicitud_id: this.solicitud!.id,
        proveedor_ids: this.proveedoresSeleccionados.map(proveedor => proveedor.id),
        asignaciones,
        fecha_limite_respuesta: this.fechaLimiteRFQ || undefined,
      }).subscribe({
        next: cotizaciones => {
          this.guardando = false;
          if (!cotizaciones.length) {
            this.error = 'No se pudo enviar la RFQ. Revise proveedores e ítems seleccionados.';
            return;
          }
          this.router.navigate(['/solicitudes', this.solicitud!.id]);
        },
        error: () => {
          this.guardando = false;
          this.error = 'No se pudo enviar la RFQ.';
        },
      });
    });
  }

  guardarItemsYContinuar(paso: PasoCotizacion): void {
    if (paso === 'proveedores') {
      this.prepararProveedores();
      return;
    }
    this.guardarItemsSolicitud(() => {
      this.paso = paso;
      this.draft = this.nuevoDraft();
      this.exito = 'Ítems guardados en la oportunidad.';
    });
  }

  private prepararProveedores(): void {
    if (!this.solicitud) return;
    if (this.items.length === 0) {
      this.error = 'Agregue al menos un ítem antes de seleccionar proveedores.';
      return;
    }
    this.guardarItemsSolicitud(() => {
      this.paso = 'proveedores';
      this.cargarProveedoresSugeridos();
    });
  }

  private cargarProveedoresSugeridos(): void {
    if (!this.solicitud) return;
    this.guardando = true;
    this.proveedoresService.getProveedoresSugeridos(this.solicitud.id).subscribe({
      next: proveedores => {
        const allItemIds = this.itemIdsActuales();
        this.proveedores = proveedores.map(proveedor => ({
          ...proveedor,
          seleccionado: proveedor.sugerido,
          itemIds: proveedor.item_ids_sugeridos?.length ? proveedor.item_ids_sugeridos : allItemIds,
        }));
        this.guardando = false;
      },
      error: () => {
        this.guardando = false;
        this.error = 'No se pudieron cargar los proveedores sugeridos.';
      },
    });
  }

  private guardarItemsSolicitud(done: () => void): void {
    if (!this.solicitud) return;
    if (this.items.length === 0) {
      this.error = 'Agregue al menos un ítem.';
      return;
    }

    this.guardando = true;
    this.error = '';
    this.reordenarItems();
    this.solicitudesService.updateSolicitud(this.solicitud.id, {
      items: this.items.map(item => ({
        id: item.id,
        tipo: item.tipo,
        descripcion: item.descripcion,
        cantidad: item.cantidad,
        unidad_medida_id: item.unidad_medida_id,
        producto_id: item.producto_id,
        categoria_producto_id: item.categoria_producto_id,
        servicio_id: item.servicio_id,
        especificaciones: item.especificaciones,
        notas: item.notas,
        presupuesto_estimado: item.presupuesto_estimado,
        orden: item.orden,
      })),
    }).subscribe({
      next: solicitud => {
        this.guardando = false;
        if (!solicitud) {
          this.error = 'No se pudieron guardar los ítems.';
          return;
        }
        this.solicitud = solicitud;
        this.items = solicitud.items.map(item => ({
          id: item.id,
          tipo: item.tipo,
          descripcion: item.descripcion,
          cantidad: item.cantidad,
          unidad_medida_id: item.unidad_medida_id,
          producto_id: item.producto_id,
          categoria_producto_id: item.categoria_producto_id,
          servicio_id: item.servicio_id,
          especificaciones: item.especificaciones,
          notas: item.notas,
          presupuesto_estimado: item.presupuesto_estimado,
          orden: item.orden,
          _productoNombre: item.categoria_producto?.nombre ?? item.producto?.nombre,
          _servicioNombre: item.servicio?.nombre,
          _unidadNombre: item.unidad ? `${item.unidad.nombre} (${item.unidad.simbolo})` : undefined,
        }));
        done();
      },
      error: () => {
        this.guardando = false;
        this.error = 'No se pudieron guardar los ítems.';
      },
    });
  }

  private itemIdsActuales(): number[] {
    return this.solicitud?.items.map(item => item.id) ?? [];
  }

  private reordenarItems(): void {
    this.items.forEach((item, index) => {
      item.orden = index;
    });
  }

  private nuevoDraft(): ItemDraft {
    return {
      categoriaId: null,
      servicioId: null,
      descripcion: '',
      cantidad: 1,
      unidadId: null,
      especificacionesTexto: '',
      specValues: {},
      notas: '',
    };
  }

  private buildEspecificaciones(): string | undefined {
    if (!this.camposCategoria.length) {
      return undefined;
    }

    const specs: EspecificacionGuardada[] = this.camposCategoria
      .map(campo => {
        const unidadId = campo.tiene_unidad
          ? this.toOptionalNumber(this.draft.specValues[`${campo.clave}_unidad`])
          : undefined;
        const unidad = unidadId
          ? this.unidades.find(item => item.id === unidadId)
          : undefined;

        return {
          campo_id: campo.id,
          clave: campo.clave,
          nombre: campo.nombre,
          tipo_dato: campo.tipo_dato,
          valor: this.draft.specValues[campo.clave],
          cantidad: campo.tiene_cantidad
            ? this.toOptionalNumber(this.draft.specValues[`${campo.clave}_cantidad`])
            : undefined,
          unidad_medida_id: unidadId,
          unidad_nombre: unidad?.nombre,
          unidad_simbolo: unidad?.simbolo,
        };
      })
      .filter(spec =>
        (spec.valor !== null && spec.valor !== '') ||
        spec.cantidad !== undefined ||
        spec.unidad_medida_id !== undefined
      );

    return specs.length ? JSON.stringify(specs) : undefined;
  }

  private cargarCamposCategoria(
    categoriaId: number,
    valoresPrevios: Record<string, string | number | boolean | null> = {},
  ): void {
    this.catalogosService.getCamposCategoria(categoriaId).subscribe({
      next: campos => {
        this.camposCategoria = campos.filter(campo => campo.activo !== false);
        this.draft.specValues = this.camposCategoria.reduce<Record<string, string | number | boolean | null>>(
          (acc, campo) => {
            acc[campo.clave] = valoresPrevios[campo.clave]
              ?? (campo.tipo_dato === 'booleano' ? false : null);
            if (campo.tiene_cantidad) {
              acc[`${campo.clave}_cantidad`] = valoresPrevios[`${campo.clave}_cantidad`] ?? null;
            }
            if (campo.tiene_unidad) {
              acc[`${campo.clave}_unidad`] = valoresPrevios[`${campo.clave}_unidad`]
                ?? campo.unidad_default_id
                ?? null;
            }
            return acc;
          },
          {},
        );
      },
      error: () => {
        this.error = 'No se pudieron cargar los campos de la categoría.';
      },
    });
  }

  private parseEspecificaciones(
    especificaciones?: string,
  ): Record<string, string | number | boolean | null> {
    if (!especificaciones) return {};
    try {
      const specs = JSON.parse(especificaciones) as EspecificacionGuardada[];
      return specs.reduce<Record<string, string | number | boolean | null>>((acc, spec) => {
        if (!spec.clave) return acc;
        acc[spec.clave] = spec.valor ?? null;
        if (spec.cantidad !== undefined) acc[`${spec.clave}_cantidad`] = spec.cantidad;
        if (spec.unidad_medida_id !== undefined) {
          acc[`${spec.clave}_unidad`] = spec.unidad_medida_id;
        }
        return acc;
      }, {});
    } catch {
      return {};
    }
  }

  private getPasoPorTipo(tipo: TipoItemCotizacion): PasoCotizacion {
    if (tipo === 'servicio') return 'servicios';
    if (tipo === 'licencia') return 'licencias';
    return 'productos';
  }

  private toOptionalNumber(value: string | number | boolean | null | undefined): number | undefined {
    if (value === null || value === undefined || value === '') return undefined;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : undefined;
  }

  private validarCamposCategoria(): boolean {
    for (const campo of this.camposCategoria) {
      const value = this.draft.specValues[campo.clave];
      if (campo.es_obligatorio && (value === null || value === '')) {
        this.error = `Complete el campo obligatorio: ${campo.nombre}.`;
        return false;
      }
    }
    return true;
  }
}
