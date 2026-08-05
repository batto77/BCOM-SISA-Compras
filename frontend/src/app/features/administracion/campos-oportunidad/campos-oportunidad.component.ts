import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  DxDataGridModule,
  DxDataGridComponent,
  DxPopupModule,
  DxTextBoxModule,
  DxSelectBoxModule,
  DxCheckBoxModule,
  DxTagBoxModule,
  DxButtonModule,
  DxNumberBoxModule,
} from 'devextreme-angular';
import { CamposSolicitudService, CampoSolicitud } from '../../../core/services/campos-solicitud.service';

@Component({
  selector: 'app-campos-oportunidad',
  standalone: true,
  imports: [
    CommonModule, RouterLink, DxDataGridModule, DxPopupModule,
    DxTextBoxModule, DxSelectBoxModule, DxCheckBoxModule, DxTagBoxModule, DxButtonModule, DxNumberBoxModule,
  ],
  template: `
    <div class="content-header">
      <div class="container-fluid">
        <div class="row mb-2">
          <div class="col-sm-6"><h1 class="m-0">Campos de oportunidad</h1></div>
          <div class="col-sm-6">
            <ol class="breadcrumb float-sm-right">
              <li class="breadcrumb-item"><a routerLink="/dashboard">Inicio</a></li>
              <li class="breadcrumb-item"><a routerLink="/administracion">Administración</a></li>
              <li class="breadcrumb-item active">Campos de oportunidad</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
    <div class="content">
      <div class="container-fluid">
        <div class="card">
          <div class="card-header d-flex align-items-center">
            <h3 class="card-title flex-grow-1">Campos dinámicos configurados</h3>
            <button class="btn btn-primary btn-sm" (click)="abrirNuevo()">
              <i class="fas fa-plus mr-1"></i>Nuevo campo
            </button>
          </div>
          <div class="card-body p-0">
            <dx-data-grid
              #grid
              [dataSource]="campos"
              [showBorders]="false"
              [rowAlternationEnabled]="true"
              [columnAutoWidth]="true"
            >
              <dxo-toolbar>
                <dxi-item location="before" template="btnLimpiar"></dxi-item>
                <dxi-item name="searchPanel"></dxi-item>
              </dxo-toolbar>
              <dxo-search-panel [visible]="true" placeholder="Buscar..."></dxo-search-panel>
              <div *dxTemplate="let _ of 'btnLimpiar'">
                <button class="btn btn-sm btn-outline-secondary" (click)="grid.instance.clearFilter()">
                  <i class="fas fa-eraser mr-1"></i>Limpiar filtros
                </button>
              </div>
              <dxo-filter-row [visible]="true"></dxo-filter-row>

              <dxi-column dataField="orden" caption="Orden" [width]="70"></dxi-column>
              <dxi-column dataField="nombre" caption="Nombre" [minWidth]="150"></dxi-column>
              <dxi-column dataField="tipo_dato" caption="Tipo" [width]="110"></dxi-column>
              <dxi-column dataField="obligatorio" caption="Obligatorio" [width]="110" dataType="boolean"></dxi-column>
              <dxi-column dataField="activo" caption="Activo" [width]="90" dataType="boolean"></dxi-column>
              <dxi-column caption="Acciones" [width]="110" cellTemplate="accionesTpl" [allowFiltering]="false" [allowSorting]="false"></dxi-column>
              <div *dxTemplate="let c of 'accionesTpl'">
                <button class="btn btn-xs btn-outline-primary mr-1" (click)="abrirEdicion(c.data)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-xs btn-outline-danger" (click)="eliminar(c.data.id)">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </dx-data-grid>
          </div>
        </div>
      </div>
    </div>

    <!-- Popup para crear/editar -->
    <dx-popup
      [visible]="showPopup"
      (visibleChange)="showPopup = $event"
      [title]="editandoId ? 'Editar campo' : 'Nuevo campo'"
      [width]="480"
      [height]="'auto'"
      [showCloseButton]="true"
    >
      <div *dxTemplate="let data of 'content'" class="p-3">
        @if (errorPopup) {
          <div class="alert alert-danger mb-3">{{ errorPopup }}</div>
        }
        <div class="form-group">
          <label class="small font-weight-bold text-muted text-uppercase">Nombre *</label>
          <dx-text-box [(value)]="form.nombre" placeholder="Ej: Centro de costos"></dx-text-box>
        </div>
        <div class="form-group">
          <label class="small font-weight-bold text-muted text-uppercase">Descripción (tooltip)</label>
          <dx-text-box [(value)]="form.descripcion" placeholder="Explicación del campo..."></dx-text-box>
        </div>
        <div class="row">
          <div class="col-6">
            <div class="form-group">
              <label class="small font-weight-bold text-muted text-uppercase">Tipo de dato</label>
              <dx-select-box
                [items]="tiposOptions"
                displayExpr="label"
                valueExpr="value"
                [(value)]="form.tipo_dato"
              ></dx-select-box>
            </div>
          </div>
          <div class="col-6">
            <div class="form-group">
              <label class="small font-weight-bold text-muted text-uppercase">Orden</label>
              <dx-number-box [(value)]="form.orden" [min]="0" [showSpinButtons]="true"></dx-number-box>
            </div>
          </div>
        </div>
        @if (form.tipo_dato === 'lista') {
          <div class="form-group">
            <label class="small font-weight-bold text-muted text-uppercase">Opciones de lista</label>
            <dx-tag-box
              [value]="form.opciones ?? []"
              (valueChange)="form.opciones = $any($event)"
              [acceptCustomValue]="true"
              placeholder="Escribí una opción y presioná Enter..."
            ></dx-tag-box>
          </div>
        }
        <div class="d-flex gap-3 mb-3">
          <dx-check-box [(value)]="form.obligatorio" text="Obligatorio"></dx-check-box>
          <dx-check-box [(value)]="form.activo" text="Activo" class="ml-3"></dx-check-box>
        </div>
        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-light mr-2" (click)="showPopup = false">Cancelar</button>
          <button class="btn btn-primary" [disabled]="guardando" (click)="guardar()">
            @if (guardando) { <span class="spinner-border spinner-border-sm mr-1"></span> }
            Guardar
          </button>
        </div>
      </div>
    </dx-popup>
  `,
})
export class CamposOportunidadComponent implements OnInit {
  @ViewChild('grid') grid!: DxDataGridComponent;

  campos: CampoSolicitud[] = [];
  showPopup = false;
  editandoId: number | null = null;
  guardando = false;
  errorPopup = '';

  form: {
    nombre: string;
    descripcion: string;
    tipo_dato: CampoSolicitud['tipo_dato'];
    opciones: string[];
    obligatorio: boolean;
    activo: boolean;
    orden: number;
  } = this.emptyForm();

  tiposOptions = [
    { value: 'texto', label: 'Texto' },
    { value: 'numero', label: 'Número' },
    { value: 'fecha', label: 'Fecha' },
    { value: 'booleano', label: 'Sí / No' },
    { value: 'lista', label: 'Lista de opciones' },
  ];

  constructor(private service: CamposSolicitudService) {}

  ngOnInit(): void { this.cargar(); }

  cargar(): void {
    this.service.getCampos().subscribe(c => { this.campos = c; });
  }

  emptyForm() {
    return { nombre: '', descripcion: '', tipo_dato: 'texto' as CampoSolicitud['tipo_dato'], opciones: [] as string[], obligatorio: false, activo: true, orden: 0 };
  }

  abrirNuevo(): void {
    this.editandoId = null;
    this.form = this.emptyForm();
    this.errorPopup = '';
    this.showPopup = true;
  }

  abrirEdicion(campo: CampoSolicitud): void {
    this.editandoId = campo.id;
    this.form = {
      nombre: campo.nombre,
      descripcion: campo.descripcion ?? '',
      tipo_dato: campo.tipo_dato,
      opciones: [...(campo.opciones ?? [])],
      obligatorio: campo.obligatorio,
      activo: campo.activo,
      orden: campo.orden,
    };
    this.errorPopup = '';
    this.showPopup = true;
  }

  guardar(): void {
    if (!this.form.nombre?.trim()) { this.errorPopup = 'El nombre es requerido.'; return; }
    this.guardando = true;
    const obs = this.editandoId
      ? this.service.updateCampo(this.editandoId, this.form)
      : this.service.createCampo(this.form);
    obs.subscribe({
      next: () => {
        this.guardando = false;
        this.showPopup = false;
        this.cargar();
      },
      error: () => { this.guardando = false; this.errorPopup = 'Error al guardar.'; },
    });
  }

  eliminar(id: number): void {
    if (!confirm('¿Eliminar este campo?')) return;
    this.service.deleteCampo(id).subscribe(() => this.cargar());
  }
}
