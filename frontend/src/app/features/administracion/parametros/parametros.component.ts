import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  DxDataGridModule,
  DxButtonModule,
  DxTextBoxModule,
  DxNumberBoxModule,
  DxSwitchModule,
  DxSelectBoxModule,
  DxPopupModule,
} from 'devextreme-angular';
import { ParametrosService } from '../../../core/services/parametros.service';
import {
  UnidadMedida,
  RubroPresupuestal,
  PlantillaANS,
} from '../../../core/models/parametros.model';

type TabActiva = 'unidades' | 'rubros' | 'ans';

@Component({
  selector: 'app-parametros',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DxDataGridModule,
    DxButtonModule,
    DxTextBoxModule,
    DxNumberBoxModule,
    DxSwitchModule,
    DxSelectBoxModule,
    DxPopupModule,
  ],
  templateUrl: './parametros.component.html',
})
export class ParametrosComponent implements OnInit {
  tabActiva: TabActiva = 'unidades';
  cargando = false;
  error = '';
  // Referencia al grid activo (cambia al cambiar de tab)
  private gridInstance: any = null;

  // Datos
  unidades: UnidadMedida[] = [];
  rubros: RubroPresupuestal[] = [];
  plantillasANS: PlantillaANS[] = [];

  // Popup genérico
  popupVisible = false;
  modoEdicion = false;
  itemActual: Record<string, unknown> = {};

  constructor(private parametrosService: ParametrosService) {}

  ngOnInit(): void {
    this.cargarTab('unidades');
  }

  seleccionarTab(tab: TabActiva): void {
    this.tabActiva = tab;
    this.cargarTab(tab);
  }

  cargarTab(tab: TabActiva): void {
    this.cargando = true;
    this.error = '';
    switch (tab) {
      case 'unidades':
        this.parametrosService.getUnidadesMedida().subscribe({
          next: d => { this.unidades = d; this.cargando = false; },
          error: () => { this.setError(); },
        });
        break;
      case 'rubros':
        this.parametrosService.getRubros().subscribe({
          next: d => { this.rubros = d; this.cargando = false; },
          error: () => { this.setError(); },
        });
        break;
      case 'ans':
        this.parametrosService.getPlantillasANS().subscribe({
          next: d => { this.plantillasANS = d; this.cargando = false; },
          error: () => { this.setError(); },
        });
        break;
    }
  }

  setError(): void {
    this.error = 'No se pudo conectar con el servidor. Verifique que el backend esté activo.';
    this.cargando = false;
  }

  abrirNuevo(): void {
    this.itemActual = this.getDefaults();
    this.modoEdicion = false;
    this.popupVisible = true;
  }

  abrirEditar(item: Record<string, unknown>): void {
    this.itemActual = { ...item };
    this.modoEdicion = true;
    this.popupVisible = true;
  }

  getDefaults(): Record<string, unknown> {
    switch (this.tabActiva) {
      case 'unidades': return { activo: true };
      case 'rubros': return { activo: true };
      case 'ans': return { horas: 24 };
    }
  }

  guardar(): void {
    const id = this.itemActual['id'] as number | undefined;
    switch (this.tabActiva) {
      case 'unidades':
        if (this.modoEdicion && id) {
          this.parametrosService.updateUnidadMedida(id, this.itemActual as Partial<UnidadMedida>)
            .subscribe({ next: () => { this.popupVisible = false; this.cargarTab('unidades'); } });
        } else {
          this.parametrosService.createUnidadMedida(this.itemActual as Partial<UnidadMedida>)
            .subscribe({ next: () => { this.popupVisible = false; this.cargarTab('unidades'); } });
        }
        break;
      case 'rubros':
        if (this.modoEdicion && id) {
          this.parametrosService.updateRubro(id, this.itemActual as Partial<RubroPresupuestal>)
            .subscribe({ next: () => { this.popupVisible = false; this.cargarTab('rubros'); } });
        } else {
          this.parametrosService.createRubro(this.itemActual as Partial<RubroPresupuestal>)
            .subscribe({ next: () => { this.popupVisible = false; this.cargarTab('rubros'); } });
        }
        break;
      case 'ans':
        if (this.modoEdicion && id) {
          this.parametrosService.updatePlantillaANS(id, this.itemActual as Partial<PlantillaANS>)
            .subscribe({ next: () => { this.popupVisible = false; this.cargarTab('ans'); } });
        } else {
          this.parametrosService.createPlantillaANS(this.itemActual as Partial<PlantillaANS>)
            .subscribe({ next: () => { this.popupVisible = false; this.cargarTab('ans'); } });
        }
        break;
    }
  }

  onGridInit(e: any): void {
    this.gridInstance = e.component;
  }

  limpiarFiltros(): void {
    this.gridInstance?.clearFilter();
  }

  cancelar(): void {
    this.popupVisible = false;
  }

  formatoPesos(value: number | undefined): string {
    if (value == null) return '—';
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(value);
  }

  get tituloPopup(): string {
    const base = this.modoEdicion ? 'Editar' : 'Nuevo';
    switch (this.tabActiva) {
      case 'unidades': return `${base} unidad de medida`;
      case 'rubros': return `${base} rubro presupuestal`;
      case 'ans': return `${base} plantilla ANS`;
    }
  }
}
