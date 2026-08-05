import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import {
  DxLoadIndicatorModule,
  DxNumberBoxModule,
  DxCheckBoxModule,
  DxTextAreaModule,
  DxButtonModule,
  DxSelectBoxModule,
} from 'devextreme-angular';
import {
  PublicService,
  CotizacionPublica,
  ItemRespuesta,
  TasaCambioPublico,
} from '../../core/services/public.service';
import { ParametrosService } from '../../core/services/parametros.service';
import { TourService } from '../../core/services/tour.service';
import {
  EspecificacionVisible,
  parsearEspecificaciones,
} from '../../shared/utils/especificaciones.util';

interface ItemForm {
  item_cotizacion_id: number;
  precio_unitario: number | null;
  tiempo_entrega_dias: number | null;
  disponible: boolean;
  notas: string;
  moneda: string;
}

@Component({
  selector: 'app-cotizar',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    DxLoadIndicatorModule,
    DxNumberBoxModule,
    DxCheckBoxModule,
    DxTextAreaModule,
    DxButtonModule,
    DxSelectBoxModule,
  ],
  templateUrl: './cotizar.component.html',
  styleUrl: './cotizar.component.scss',
})
export class CotizarComponent implements OnInit {
  token = '';
  cotizacion: CotizacionPublica | null = null;
  itemsForm: ItemForm[] = [];
  especificacionesPorItem: Record<number, EspecificacionVisible[]> = {};
  itemsExpandidos = new Set<number>();
  notasProveedor = '';

  cargando = true;
  guardando = false;
  enviado = false;
  error = '';

  fichasTecnicasUrls: Record<number, string> = {};
  fichasSubiendo: Record<number, boolean> = {};
  pdfCotizacionUrl = '';
  pdfCotizacionSubiendo = false;
  uploadError = '';

  tasasCambio: TasaCambioPublico[] = [];
  monedasDisponibles: string[] = ['COP'];
  monedaDefecto = 'COP';

  constructor(
    private route: ActivatedRoute,
    private publicService: PublicService,
    private parametrosService: ParametrosService,
    private tourService: TourService,
  ) {}

  ngOnInit(): void {
    this.token = this.route.snapshot.paramMap.get('token') ?? '';
    if (this.token) {
      this.cargar();
    } else {
      this.error = 'Link inválido.';
      this.cargando = false;
    }
  }

  cargar(): void {
    forkJoin({
      cotizacion: this.publicService.getCotizacionPublica(this.token),
      unidades: this.parametrosService.getUnidadesMedida(),
    }).subscribe({
      next: ({ cotizacion: cot, unidades }) => {
        this.cotizacion = cot;
        this.notasProveedor = cot.notas_proveedor ?? '';
        this.itemsForm = cot.items.map(item => ({
          item_cotizacion_id: item.id,
          precio_unitario: item.precio_unitario ?? null,
          tiempo_entrega_dias: item.tiempo_entrega_dias ?? null,
          disponible: item.disponible,
          notas: item.notas ?? '',
          moneda: item.moneda ?? (cot.proveedor_moneda_defecto ?? 'COP'),
        }));
        this.fichasTecnicasUrls = Object.fromEntries(
          cot.items
            .filter(item => !!item.ficha_tecnica_url)
            .map(item => [item.id, item.ficha_tecnica_url!])
        );
        this.pdfCotizacionUrl = cot.pdf_cotizacion_url ?? '';
        this.tasasCambio = cot.tasas_cambio ?? [];
        const monedaProv = cot.proveedor_moneda_defecto ?? 'COP';
        const monedasProv = cot.proveedor_monedas?.length ? cot.proveedor_monedas : ['COP'];
        this.monedasDisponibles = ['COP', ...this.tasasCambio.map(t => t.moneda)].filter(
          m => monedasProv.includes(m)
        );
        if (!this.monedasDisponibles.length) this.monedasDisponibles = ['COP'];
        this.monedaDefecto = this.monedasDisponibles.includes(monedaProv) ? monedaProv : this.monedasDisponibles[0];
        this.especificacionesPorItem = Object.fromEntries(
          cot.items.map(item => [
            item.id,
            parsearEspecificaciones(item.item_solicitud?.especificaciones, unidades),
          ]),
        );
        this.itemsExpandidos = new Set(
          cot.items
            .filter(item => (this.especificacionesPorItem[item.id]?.length ?? 0) > 0)
            .map(item => item.id),
        );
        this.cargando = false;
        if (cot.estado === 'respondida' && cot.respuesta_version === cot.version_actual) {
          this.enviado = true;
          return;
        }
        window.setTimeout(() => this.tourService.startSupplierQuoteTour(), 300);
      },
      error: err => {
        this.error = err.error?.detail ?? 'No se pudo cargar la cotización. El link puede ser inválido o haber expirado.';
        this.cargando = false;
      },
    });
  }

  getSubtotal(i: number): number {
    const form = this.itemsForm[i];
    if (!form || !form.disponible) return 0;
    const cant = this.cotizacion?.items[i]?.item_solicitud?.cantidad ?? 1;
    return (form.precio_unitario ?? 0) * Number(cant);
  }

  getTasaCop(moneda: string): number {
    if (moneda === 'COP') return 1;
    return Number(this.tasasCambio.find(t => t.moneda === moneda)?.tasa_cop ?? 1);
  }

  getSubtotalCop(i: number): number {
    return this.getSubtotal(i) * this.getTasaCop(this.itemsForm[i]?.moneda ?? 'COP');
  }

  // Convierte el subtotal de un ítem a la moneda por defecto del proveedor
  getSubtotalEnDefecto(i: number): number {
    const cop = this.getSubtotalCop(i);
    const tasaDefecto = this.getTasaCop(this.monedaDefecto);
    return tasaDefecto > 0 ? cop / tasaDefecto : cop;
  }

  getTotalEnDefecto(): number {
    return this.itemsForm.reduce((sum, _, i) => sum + this.getSubtotalEnDefecto(i), 0);
  }

  // True si el ítem está en una moneda distinta a la defecto (necesita mostrar conversión)
  itemNecesitaConversion(i: number): boolean {
    return (this.itemsForm[i]?.moneda ?? 'COP') !== this.monedaDefecto;
  }

  isMultiMoneda(): boolean {
    return this.monedasDisponibles.length > 1 || this.monedasDisponibles[0] !== 'COP';
  }

  getTotalEstimado(): number {
    return this.itemsForm.reduce((sum, _, i) => sum + this.getSubtotal(i), 0);
  }

  getTipoBadge(tipo: string): string {
    const map: Record<string, string> = {
      producto: 'badge-primary',
      servicio: 'badge-info',
      licencia: 'badge-success',
      libre: 'badge-secondary',
    };
    return map[tipo] ?? 'badge-secondary';
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

  getPrioridadBadge(prioridad: string): string {
    const map: Record<string, string> = {
      urgente: 'badge-danger',
      alta: 'badge-warning',
      normal: 'badge-primary',
      baja: 'badge-secondary',
    };
    return map[prioridad] ?? 'badge-secondary';
  }

  onFichaSeleccionada(event: Event, itemId: number): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !this.token) return;
    this.fichasSubiendo[itemId] = true;
    this.uploadError = '';
    this.publicService.uploadFichaTecnica(this.token, itemId, file).subscribe({
      next: res => {
        this.fichasTecnicasUrls[itemId] = res.url;
        this.fichasSubiendo[itemId] = false;
      },
      error: () => {
        this.fichasSubiendo[itemId] = false;
        this.uploadError = 'Error al subir la ficha técnica. Verificá que sea un PDF válido.';
      },
    });
    input.value = '';
  }

  onPdfCotizacionSeleccionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !this.token) return;
    this.pdfCotizacionSubiendo = true;
    this.uploadError = '';
    this.publicService.uploadPdfCotizacion(this.token, file).subscribe({
      next: res => {
        this.pdfCotizacionUrl = res.url;
        this.pdfCotizacionSubiendo = false;
      },
      error: () => {
        this.pdfCotizacionSubiendo = false;
        this.uploadError = 'Error al subir el PDF. Verificá que sea un archivo válido.';
      },
    });
    input.value = '';
  }

  enviar(): void {
    if (!this.cotizacion || this.guardando) return;
    this.guardando = true;
    this.error = '';

    const items: ItemRespuesta[] = this.itemsForm.map(f => ({
      item_cotizacion_id: f.item_cotizacion_id,
      precio_unitario: f.precio_unitario,
      tiempo_entrega_dias: f.tiempo_entrega_dias,
      disponible: f.disponible,
      notas: f.notas || null,
      moneda: f.moneda || 'COP',
    }));

    this.publicService.responderCotizacion(this.token, {
      items,
      notas_proveedor: this.notasProveedor || undefined,
    }).subscribe({
      next: () => {
        this.guardando = false;
        this.enviado = true;
      },
      error: err => {
        this.guardando = false;
        this.error = err.error?.detail ?? 'Error al enviar. Intente nuevamente.';
      },
    });
  }
}
