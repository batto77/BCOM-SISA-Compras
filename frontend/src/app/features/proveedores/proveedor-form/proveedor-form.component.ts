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
import { ProveedoresService } from '../../../core/services/proveedores.service';
import { EtiquetasService } from '../../../core/services/etiquetas.service';
import {
  Proveedor,
  ContactoProveedor,
  EmailContacto,
  TelefonoContacto,
} from '../../../core/models/proveedores.model';
import { Etiqueta } from '../../../core/models/etiquetas.model';

const PAISES = [
  'Colombia', 'Estados Unidos', 'España', 'Alemania', 'China', 'México', 'Brasil', 'Otro',
];

const IDIOMA_POR_PAIS: Record<string, 'ES' | 'EN'> = {
  'Colombia': 'ES',
  'España': 'ES',
  'México': 'ES',
  'Brasil': 'ES',
  'Estados Unidos': 'EN',
  'Alemania': 'EN',
  'China': 'EN',
  'Otro': 'ES',
};

@Component({
  selector: 'app-proveedor-form',
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
  templateUrl: './proveedor-form.component.html',
})
export class ProveedorFormComponent implements OnInit {
  modoEdicion = false;
  proveedorId: number | null = null;
  cargando = false;
  guardando = false;
  error = '';
  exito = '';

  paises = PAISES;
  tiposPersona = [
    { value: 'juridica', label: 'Jurídica' },
    { value: 'natural',  label: 'Natural'  },
  ];
  monedasOptions = ['COP', 'USD', 'EUR'];
  etiquetas: Etiqueta[] = [];

  get monedasDefectoOptions(): string[] {
    return (this.proveedor.monedas ?? []).length > 0
      ? (this.proveedor.monedas ?? [])
      : this.monedasOptions;
  }
  idiomasOptions = [
    { id: 'ES', nombre: 'Español (ES)' },
    { id: 'EN', nombre: 'Inglés (EN)' },
  ];
  estadosOptions = [
    { id: 'activo', nombre: 'Activo' },
    { id: 'inactivo', nombre: 'Inactivo' },
  ];
  tiposEmail = [
    { id: 'comercial', nombre: 'Comercial' },
    { id: 'tecnico', nombre: 'Técnico' },
    { id: 'facturacion', nombre: 'Facturación' },
  ];
  tiposTelefono = [
    { id: 'celular', nombre: 'Celular' },
    { id: 'fijo', nombre: 'Fijo' },
    { id: 'whatsapp', nombre: 'WhatsApp' },
  ];

  // Modelo del formulario
  proveedor: Partial<Proveedor> = {
    pais: 'Colombia',
    idioma: 'ES',
    estado: 'activo',
    contactos: [],
    etiquetas: [],
  };

  etiquetasSeleccionadas: number[] = [];

  // --- Calificación (estrellas 0–10) ---
  readonly estrellas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  calificacionHover = 0;

  setCalificacion(n: number): void {
    // Clic en la estrella que ya es el valor actual → baja 1 (permite corregir / llegar a 0)
    this.proveedor.calificacion = this.proveedor.calificacion === n ? n - 1 : n;
  }

  estrellaLlena(n: number): boolean {
    const ref = this.calificacionHover || (this.proveedor.calificacion ?? 0);
    return n <= ref;
  }
  contactos: Array<Partial<ContactoProveedor> & {
    expandido: boolean;
    emails: Array<Partial<EmailContacto>>;
    telefonos: Array<Partial<TelefonoContacto>>;
  }> = [];

  constructor(
    private proveedoresService: ProveedoresService,
    private etiquetasService: EtiquetasService,
    private route: ActivatedRoute,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.etiquetasService.getEtiquetas().subscribe({ next: e => { this.etiquetas = e; } });

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.modoEdicion = true;
      this.proveedorId = +id;
      this.cargarProveedor(this.proveedorId);
    }
  }

  cargarProveedor(id: number): void {
    this.cargando = true;
    this.proveedoresService.getProveedor(id).subscribe({
      next: prov => {
        if (prov) {
          // Guardamos solo los campos escalares del proveedor (sin etiquetas ni contactos)
          const { etiquetas: _e, contactos: _c, ...provBase } = prov as any;
          this.proveedor = { ...provBase };
          // Los IDs de etiquetas se manejan en etiquetasSeleccionadas
          this.etiquetasSeleccionadas = (prov.etiquetas || [])
            .map(e => e.id)
            .filter((id): id is number => id !== undefined);
          this.contactos = (prov.contactos || []).map(c => ({
            ...c,
            expandido: true,
            emails: [...(c.emails || [])],
            telefonos: [...(c.telefonos || [])],
          }));
        }
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el proveedor.';
        this.cargando = false;
      },
    });
  }

  onPaisChange(pais: string): void {
    this.proveedor.pais = pais;
    this.proveedor.idioma = IDIOMA_POR_PAIS[pais] ?? 'ES';
  }

  // --- Contactos ---

  agregarContacto(): void {
    this.contactos.push({
      nombre: '',
      cargo: '',
      es_principal: this.contactos.length === 0,
      activo: true,
      expandido: true,
      emails: [],
      telefonos: [],
    });
  }

  eliminarContacto(idx: number): void {
    this.contactos.splice(idx, 1);
  }

  toggleContacto(idx: number): void {
    this.contactos[idx].expandido = !this.contactos[idx].expandido;
  }

  // --- Emails ---

  agregarEmail(idx: number): void {
    this.contactos[idx].emails.push({
      email: '',
      tipo: 'comercial',
      es_principal: this.contactos[idx].emails.length === 0,
    });
  }

  eliminarEmail(contactoIdx: number, emailIdx: number): void {
    this.contactos[contactoIdx].emails.splice(emailIdx, 1);
  }

  // --- Teléfonos ---

  agregarTelefono(idx: number): void {
    this.contactos[idx].telefonos.push({
      numero: '',
      tipo: 'celular',
    });
  }

  eliminarTelefono(contactoIdx: number, telIdx: number): void {
    this.contactos[contactoIdx].telefonos.splice(telIdx, 1);
  }

  // --- Guardar ---

  guardar(): void {
    if (!this.proveedor.razon_social?.trim()) {
      this.error = 'La razón social es obligatoria.';
      return;
    }
    this.guardando = true;
    this.error = '';

    // Construir contactos con la estructura que el backend espera (emails y telefonos anidados)
    const contactosPayload = this.contactos.map(c => ({
      id: c.id,                            // undefined si es nuevo → backend lo crea
      nombre: c.nombre,
      cargo: c.cargo,
      es_principal: c.es_principal,
      activo: c.activo,
      emails: c.emails.map(e => ({
        id: e.id,                          // undefined si es nuevo
        email: e.email,
        tipo: e.tipo,
        es_principal: e.es_principal,
      })),
      telefonos: c.telefonos.map(t => ({
        id: t.id,
        numero: t.numero,
        tipo: t.tipo,
        extension: t.extension,
      })),
    }));

    // IMPORTANTE: enviar etiqueta_ids (lista de IDs), NO el array de objetos Etiqueta
    // El backend ProveedorCreate/ProveedorUpdate espera etiqueta_ids: number[]
    const payload = {
      ...this.proveedor,
      etiqueta_ids: this.etiquetasSeleccionadas,
      contactos: contactosPayload,
    };
    // Limpiar campo etiquetas (objetos) para que no confunda al backend
    delete (payload as any)['etiquetas'];

    if (this.modoEdicion && this.proveedorId) {
      this.proveedoresService.updateProveedor(this.proveedorId, payload as Partial<Proveedor>).subscribe({
        next: result => {
          this.guardando = false;
          if (result) {
            this.exito = 'Proveedor actualizado correctamente.';
            // Recargar para reflejar IDs asignados a nuevos contactos/emails
            this.cargarProveedor(this.proveedorId!);
          } else {
            this.error = 'No se pudo guardar. Intente nuevamente.';
          }
        },
        error: () => { this.error = 'Error al guardar.'; this.guardando = false; },
      });
    } else {
      this.proveedoresService.createProveedor(payload as Partial<Proveedor>).subscribe({
        next: result => {
          this.guardando = false;
          if (result) {
            this.router.navigate(['/proveedores']);
          } else {
            this.error = 'No se pudo guardar. Intente nuevamente.';
          }
        },
        error: () => { this.error = 'Error al guardar.'; this.guardando = false; },
      });
    }
  }

  cancelar(): void {
    this.router.navigate(['/proveedores']);
  }
}
