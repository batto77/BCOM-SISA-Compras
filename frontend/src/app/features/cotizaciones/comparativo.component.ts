import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DxLoadIndicatorModule } from 'devextreme-angular';

import { CotizacionesService } from '../../core/services/cotizaciones.service';
import {
  ComparativoOut,
  CotizacionOut,
  EvaluacionComparativo,
  EvaluacionResultado,
  EvaluacionCriterio,
  EvaluacionPorItem,
  EvaluacionItemCandidato,
} from '../../core/models/cotizaciones.model';

@Component({
  selector: 'app-comparativo',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, DxLoadIndicatorModule],
  templateUrl: './comparativo.component.html',
})
export class ComparativoComponent implements OnInit {
  datos: ComparativoOut | null = null;
  cargando = false;
  error = '';

  solicitudId = 0;
  justificacion = '';
  guardando = false;
  exito = '';

  // Adjudicación por ítem editada por el usuario: { item_solicitud_id: cotizacion_id | null }
  adjudicacion: Record<number, number | null> = {};

  /** Adjudicación tal como quedó guardada en el servidor, para saber si hay cambios sin guardar. */
  private adjudicacionGuardada: Record<number, number | null> = {};
  estadoOportunidad = '';

  get solicitud() { return this.datos?.solicitud ?? null; }
  get itemsSolicitud() { return this.datos?.items_solicitud ?? []; }
  get evaluacion(): EvaluacionComparativo | null { return this.datos?.evaluacion ?? null; }
  get criterios(): EvaluacionCriterio[] { return this.evaluacion?.criterios ?? []; }
  get criteriosActivos(): EvaluacionCriterio[] { return this.criterios.filter(c => c.activo); }
  get porItem(): EvaluacionPorItem[] { return this.evaluacion?.por_item ?? []; }
  get ganadorSugeridoId(): number | null { return this.evaluacion?.ganador_sugerido_cotizacion_id ?? null; }

  get cotizaciones(): CotizacionOut[] {
    return (this.datos?.cotizaciones ?? []).filter(c => c.estado === 'respondida');
  }

  get cotizacionesRankeadas(): CotizacionOut[] {
    const orden = new Map<number, number>();
    (this.evaluacion?.resultados ?? []).forEach(r => orden.set(r.cotizacion_id, r.puntaje_final));
    return [...this.cotizaciones].sort(
      (a, b) => (orden.get(b.id) ?? -1) - (orden.get(a.id) ?? -1),
    );
  }

  constructor(
    private route: ActivatedRoute,
    private cotizacionesService: CotizacionesService,
  ) {}

  ngOnInit(): void {
    this.solicitudId = Number(this.route.snapshot.paramMap.get('solicitudId'));
    if (this.solicitudId) {
      this.cargar(this.solicitudId);
    }
  }

  cargar(solicitudId: number): void {
    this.cargando = true;
    this.error = '';
    this.cotizacionesService.getComparativo(solicitudId).subscribe({
      next: data => {
        this.datos = data;
        this.justificacion = data?.justificacion_seleccion ?? '';
        // Adjudicación guardada; si no hay, se parte de la sugerida
        const guardada = data?.adjudicacion_items ?? {};
        this.adjudicacion = {};
        this.adjudicacionGuardada = {};
        for (const item of this.itemsSolicitud) {
          const g = guardada[String(item.id)];
          const sug = this.evaluacion?.adjudicacion_sugerida?.[String(item.id)] ?? null;
          this.adjudicacion[item.id] = g != null ? g : (sug ?? null);
          this.adjudicacionGuardada[item.id] = g ?? null;
        }
        this.estadoOportunidad = data?.solicitud?.estado ?? '';
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el comparativo.';
        this.cargando = false;
      },
    });
  }

  // --- Evaluación global ---
  getResultado(cotizacionId: number): EvaluacionResultado | null {
    return this.evaluacion?.resultados.find(r => r.cotizacion_id === cotizacionId) ?? null;
  }
  getSubpuntaje(cotizacionId: number, clave: string): number | null {
    const r = this.getResultado(cotizacionId);
    return r ? ((r.subpuntajes as Record<string, number>)[clave] ?? null) : null;
  }
  getPuntajeFinal(cotizacionId: number): number | null {
    return this.getResultado(cotizacionId)?.puntaje_final ?? null;
  }
  getRankingPos(cotizacionId: number): number {
    return this.cotizacionesRankeadas.findIndex(c => c.id === cotizacionId) + 1;
  }
  esGanadorSugerido(cotizacionId: number): boolean {
    return this.ganadorSugeridoId === cotizacionId;
  }
  barraClass(valor: number | null): string {
    if (valor === null) return 'bg-secondary';
    if (valor >= 75) return 'bg-success';
    if (valor >= 50) return 'bg-info';
    if (valor >= 25) return 'bg-warning';
    return 'bg-danger';
  }

  // --- Adjudicación por ítem ---
  getItemEval(itemSolicitudId: number): EvaluacionPorItem | null {
    return this.porItem.find(p => p.item_solicitud_id === itemSolicitudId) ?? null;
  }
  getCandidato(itemSolicitudId: number, cotizacionId: number): EvaluacionItemCandidato | null {
    return this.getItemEval(itemSolicitudId)?.candidatos.find(c => c.cotizacion_id === cotizacionId) ?? null;
  }
  ofertaItem(itemSolicitudId: number, cotizacionId: number): boolean {
    return !!this.getCandidato(itemSolicitudId, cotizacionId);
  }
  esMejorItem(itemSolicitudId: number, cotizacionId: number): boolean {
    return this.getItemEval(itemSolicitudId)?.mejor_cotizacion_id === cotizacionId;
  }
  esAdjudicado(itemSolicitudId: number, cotizacionId: number): boolean {
    return this.adjudicacion[itemSolicitudId] === cotizacionId;
  }
  adjudicarItem(itemSolicitudId: number, cotizacionId: number): void {
    if (!this.ofertaItem(itemSolicitudId, cotizacionId)) return;
    // Clic sobre el ya adjudicado lo deselecciona
    this.adjudicacion[itemSolicitudId] =
      this.adjudicacion[itemSolicitudId] === cotizacionId ? null : cotizacionId;
  }
  usarSugerencia(): void {
    for (const item of this.itemsSolicitud) {
      this.adjudicacion[item.id] = this.evaluacion?.adjudicacion_sugerida?.[String(item.id)] ?? null;
    }
  }
  adjudicarTodoA(cotizacionId: number): void {
    for (const item of this.itemsSolicitud) {
      this.adjudicacion[item.id] = this.ofertaItem(item.id, cotizacionId) ? cotizacionId : null;
    }
  }
  limpiarAdjudicacion(): void {
    for (const item of this.itemsSolicitud) this.adjudicacion[item.id] = null;
  }

  get itemsAdjudicados(): number {
    return this.itemsSolicitud.filter(i => this.adjudicacion[i.id] != null).length;
  }
  get itemsSinAdjudicar(): number {
    return this.itemsSolicitud.length - this.itemsAdjudicados;
  }

  /** Ítems efectivamente adjudicados según lo último guardado en el servidor. */
  get itemsAdjudicadosGuardados(): number {
    return this.itemsSolicitud.filter(i => this.adjudicacionGuardada[i.id] != null).length;
  }

  /** true si lo que se ve en pantalla difiere de lo guardado (incluye la sugerencia precargada). */
  get hayCambiosSinGuardar(): boolean {
    return this.itemsSolicitud.some(
      i => (this.adjudicacion[i.id] ?? null) !== (this.adjudicacionGuardada[i.id] ?? null),
    );
  }

  /** Estado visual del comparativo: qué tan avanzada está la adjudicación. */
  get estadoAdjudicacion(): 'cancelada' | 'sin_guardar' | 'sin_adjudicar' | 'parcial' | 'completa' {
    if (this.estadoOportunidad === 'cancelada') return 'cancelada';
    if (this.hayCambiosSinGuardar) return 'sin_guardar';
    const guardados = this.itemsAdjudicadosGuardados;
    if (guardados === 0) return 'sin_adjudicar';
    return guardados === this.itemsSolicitud.length ? 'completa' : 'parcial';
  }

  get estadoAdjudicacionTexto(): string {
    const total = this.itemsSolicitud.length;
    switch (this.estadoAdjudicacion) {
      case 'cancelada': return 'Oportunidad cancelada';
      case 'sin_guardar': return 'Cambios sin guardar';
      case 'sin_adjudicar': return 'Sin adjudicar';
      case 'parcial': return `Adjudicación parcial — ${this.itemsAdjudicadosGuardados} de ${total} ítems`;
      case 'completa': return `Adjudicada — ${total} de ${total} ítems`;
    }
  }

  get estadoAdjudicacionClase(): string {
    const clases: Record<string, string> = {
      cancelada: 'alert-dark',
      sin_guardar: 'alert-warning',
      sin_adjudicar: 'alert-secondary',
      parcial: 'alert-info',
      completa: 'alert-success',
    };
    return clases[this.estadoAdjudicacion] ?? 'alert-secondary';
  }

  get estadoAdjudicacionIcono(): string {
    const iconos: Record<string, string> = {
      cancelada: 'fa-ban',
      sin_guardar: 'fa-pen',
      sin_adjudicar: 'fa-hourglass-start',
      parcial: 'fa-adjust',
      completa: 'fa-check-circle',
    };
    return iconos[this.estadoAdjudicacion] ?? 'fa-info-circle';
  }

  get monedaOportunidad(): string {
    return this.evaluacion?.moneda_oportunidad ?? 'COP';
  }

  // Resumen: qué proveedores participan y con cuántos ítems / subtotal (en moneda convertida)
  get resumenPorProveedor(): Array<{ cotizacionId: number; nombre: string; items: number; subtotal_original: number; subtotal_convertido: number; monedas: string[] }> {
    const map = new Map<number, { items: number; subtotal_original: number; subtotal_convertido: number; monedas: Set<string> }>();
    for (const item of this.itemsSolicitud) {
      const cid = this.adjudicacion[item.id];
      if (cid == null) continue;
      const cand = this.getCandidato(item.id, cid);
      const acc = map.get(cid) ?? { items: 0, subtotal_original: 0, subtotal_convertido: 0, monedas: new Set() };
      acc.items += 1;
      acc.subtotal_original += cand?.subtotal_original ?? 0;
      acc.subtotal_convertido += cand?.subtotal_convertido ?? 0;
      if (cand?.moneda_original) acc.monedas.add(cand.moneda_original);
      map.set(cid, acc);
    }
    return [...map.entries()].map(([cotizacionId, v]) => ({
      cotizacionId,
      nombre: this.getProveedorNombre(cotizacionId),
      items: v.items,
      subtotal_original: v.subtotal_original,
      subtotal_convertido: v.subtotal_convertido,
      monedas: [...v.monedas],
    }));
  }
  get totalAdjudicado(): number {
    return this.resumenPorProveedor.reduce((a, r) => a + r.subtotal_convertido, 0);
  }

  getMonedaLabel(moneda: string): string {
    return moneda.toUpperCase();
  }

  getProveedorNombre(cotizacionId: number): string {
    const cot = this.cotizaciones.find(c => c.id === cotizacionId);
    return cot?.proveedor?.razon_social ?? ('Prov. #' + (cot?.proveedor_id ?? ''));
  }

  guardarAdjudicacion(): void {
    this.guardando = true;
    this.error = '';
    this.exito = '';
    this.cotizacionesService
      .adjudicar(this.solicitudId, this.adjudicacion, this.justificacion || undefined)
      .subscribe({
        next: res => {
          this.guardando = false;
          // Lo guardado pasa a ser la nueva referencia, y el estado lo dicta el backend.
          this.adjudicacionGuardada = {};
          for (const item of this.itemsSolicitud) {
            this.adjudicacionGuardada[item.id] = this.adjudicacion[item.id] ?? null;
          }
          if (res?.estado) this.estadoOportunidad = res.estado;
          this.exito = res?.adjudicacion_completa
            ? 'Adjudicación guardada. La oportunidad quedó adjudicada.'
            : 'Adjudicación guardada (parcial): quedan ítems sin adjudicar.';
          setTimeout(() => (this.exito = ''), 5000);
        },
        error: () => {
          this.error = 'No se pudo guardar la adjudicación.';
          this.guardando = false;
        },
      });
  }
}
