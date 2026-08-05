import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import {
  DxNumberBoxModule,
  DxCheckBoxModule,
  DxTextAreaModule,
  DxButtonModule,
  DxLoadIndicatorModule,
  DxTextBoxModule,
  DxSelectBoxModule,
} from 'devextreme-angular';

import { CotizacionesService } from '../../core/services/cotizaciones.service';
import { CotizacionOut, ItemCotizacionForm } from '../../core/models/cotizaciones.model';
import { ParametrosService } from '../../core/services/parametros.service';
import {
  EspecificacionVisible,
  parsearEspecificaciones,
} from '../../shared/utils/especificaciones.util';

@Component({
  selector: 'app-cotizacion-detail',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DxNumberBoxModule,
    DxCheckBoxModule,
    DxTextAreaModule,
    DxButtonModule,
    DxLoadIndicatorModule,
    DxTextBoxModule,
    DxSelectBoxModule,
  ],
  templateUrl: './cotizacion-detail.component.html',
  styleUrl: './cotizacion-detail.component.scss',
})
export class CotizacionDetailComponent implements OnInit {
  cotizacion: CotizacionOut | null = null;
  cargando = false;
  guardando = false;
  error = '';
  mensaje = '';

  modoEdicion = false;
  itemsForm: ItemCotizacionForm[] = [];
  especificacionesPorItem: Record<number, EspecificacionVisible[]> = {};
  itemsExpandidos = new Set<number>();
  notas_proveedor = '';

  // Campos dinámicos por categoría
  camposDinamicos: any[] = [];
  valoresEspecificacion: Record<string, any> = {};
  categoriaSeleccionada: any = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private cotizacionesService: CotizacionesService,
    private parametrosService: ParametrosService,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.cargar(id);
    }
  }

  cargar(id: number): void {
    this.cargando = true;
    this.error = '';
    forkJoin({
      cotizacion: this.cotizacionesService.getCotizacion(id),
      unidades: this.parametrosService.getUnidadesMedida(),
    }).subscribe({
      next: ({ cotizacion: cot, unidades }) => {
        this.cotizacion = cot;
        this.notas_proveedor = cot?.notas_proveedor ?? '';
        this.especificacionesPorItem = Object.fromEntries(
          (cot?.items ?? []).map(item => [
            item.id,
            parsearEspecificaciones(item.item_solicitud?.especificaciones, unidades),
          ]),
        );
        this.inicializarForm();
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo cargar la cotización.';
        this.cargando = false;
      },
    });
  }

  inicializarForm(): void {
    if (!this.cotizacion) return;
    this.itemsForm = this.cotizacion.items.map(item => ({
      item_solicitud_id: item.item_solicitud_id,
      precio_unitario: item.precio_unitario ?? undefined,
      tiempo_entrega_dias: item.tiempo_entrega_dias ?? undefined,
      disponible: item.disponible,
      notas: item.notas ?? undefined,
      orden: item.orden,
      valores_especificacion: item.valores_especificacion ?? undefined,
    }));
    // Reset campos dinámicos al re-inicializar el formulario
    this.camposDinamicos = [];
    this.valoresEspecificacion = {};
    this.categoriaSeleccionada = null;
  }

  onCategoriaSelect(catId: number): void {
    this.cotizacionesService.getCamposCategoria(catId).subscribe({
      next: (response) => {
        this.categoriaSeleccionada = response.categoria;
        this.camposDinamicos = response.campos;
        this.valoresEspecificacion = {};
      },
    });
  }

  activarEdicion(): void {
    this.inicializarForm();
    this.modoEdicion = true;
  }

  cancelarEdicion(): void {
    this.inicializarForm();
    this.notas_proveedor = this.cotizacion?.notas_proveedor ?? '';
    this.modoEdicion = false;
  }

  guardar(): void {
    if (!this.cotizacion) return;
    this.guardando = true;
    this.error = '';

    // Incluir valores_especificacion en el ítem activo si hay campos dinámicos
    if (this.camposDinamicos.length > 0) {
      const idxActivo = this.itemsForm.findIndex(item => item.item_solicitud_id != null);
      if (idxActivo >= 0) {
        this.itemsForm[idxActivo].valores_especificacion = this.valoresEspecificacion;
      }
    }

    this.cotizacionesService
      .updateCotizacion(this.cotizacion.id, {
        estado: 'respondida',
        notas_proveedor: this.notas_proveedor || undefined,
        items: this.itemsForm,
      })
      .subscribe({
        next: actualizada => {
          this.cotizacion = actualizada;
          this.notas_proveedor = actualizada?.notas_proveedor ?? '';
          this.inicializarForm();
          this.modoEdicion = false;
          this.guardando = false;
          this.mensaje = 'Respuesta guardada correctamente.';
          setTimeout(() => (this.mensaje = ''), 3000);
        },
        error: () => {
          this.error = 'No se pudo guardar la respuesta.';
          this.guardando = false;
        },
      });
  }

  descartar(): void {
    if (!this.cotizacion) return;
    if (!confirm('¿Descartar esta cotización? Esta acción no se puede deshacer.')) return;

    this.cotizacionesService
      .updateCotizacion(this.cotizacion.id, { estado: 'descartada' })
      .subscribe({
        next: () => {
          this.router.navigate(['/cotizaciones']);
        },
      });
  }

  getTotalEstimado(): number {
    if (!this.cotizacion) return 0;
    return this.cotizacion.items.reduce((acc, item) => {
      const precio = item.precio_unitario ?? 0;
      const cantidad = item.item_solicitud?.cantidad ?? 1;
      return acc + precio * cantidad;
    }, 0);
  }

  getTotalForm(): number {
    if (!this.cotizacion) return 0;
    return this.itemsForm.reduce((acc, item, idx) => {
      const precio = item.precio_unitario ?? 0;
      const cantidad = this.cotizacion!.items[idx]?.item_solicitud?.cantidad ?? 1;
      return acc + precio * cantidad;
    }, 0);
  }

  getSubtotal(idx: number): number {
    const precio = this.modoEdicion
      ? (this.itemsForm[idx]?.precio_unitario ?? 0)
      : (this.cotizacion?.items[idx]?.precio_unitario ?? 0);
    const cantidad = this.cotizacion?.items[idx]?.item_solicitud?.cantidad ?? 1;
    return precio * cantidad;
  }

  getTipoBadgeClass(tipo: string): string {
    const clases: Record<string, string> = {
      producto: 'badge-primary',
      servicio: 'badge-info',
      licencia: 'badge-success',
      libre: 'badge-secondary',
    };
    return clases[tipo] ?? 'badge-secondary';
  }

  alternarEspecificaciones(itemId: number): void {
    if (this.itemsExpandidos.has(itemId)) {
      this.itemsExpandidos.delete(itemId);
      return;
    }
    this.itemsExpandidos.add(itemId);
  }

  tieneEspecificaciones(itemId: number): boolean {
    return (this.especificacionesPorItem[itemId]?.length ?? 0) > 0;
  }

  estaExpandido(itemId: number): boolean {
    return this.itemsExpandidos.has(itemId);
  }

  getEstadoBadgeClass(estado: string): string {
    const clases: Record<string, string> = {
      invitada: 'badge-warning',
      respondida: 'badge-success',
      descartada: 'badge-secondary',
    };
    return clases[estado] ?? 'badge-secondary';
  }
}
