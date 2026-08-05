import { Routes } from '@angular/router';
import { LayoutComponent } from './layout/layout.component';

export const routes: Routes = [
  // Ruta pública — portal del proveedor (sin layout interno)
  {
    path: 'cotizar/:token',
    loadComponent: () =>
      import('./features/public/cotizar.component').then(m => m.CotizarComponent),
  },
  {
    path: '',
    component: LayoutComponent,
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
      },
      {
        path: 'solicitudes',
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/solicitudes/solicitudes.component').then(m => m.SolicitudesComponent),
          },
          {
            path: 'nueva',
            loadComponent: () =>
              import('./features/solicitudes/solicitud-wizard.component').then(m => m.SolicitudWizardComponent),
          },
          {
            path: ':id',
            loadComponent: () =>
              import('./features/solicitudes/solicitud-detail.component').then(m => m.SolicitudDetailComponent),
          },
        ],
      },
      {
        path: 'cotizaciones',
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/cotizaciones/cotizaciones.component').then(m => m.CotizacionesComponent),
          },
          {
            path: 'comparativo/:solicitudId',
            loadComponent: () =>
              import('./features/cotizaciones/comparativo.component').then(m => m.ComparativoComponent),
          },
          {
            path: 'asistente/:solicitudId',
            loadComponent: () =>
              import('./features/cotizaciones/cotizacion-asistente.component').then(m => m.CotizacionAsistenteComponent),
          },
          {
            path: ':id/versiones',
            loadComponent: () =>
              import('./features/cotizaciones/cotizacion-versiones.component').then(m => m.CotizacionVersionesComponent),
          },
          {
            path: ':id',
            loadComponent: () =>
              import('./features/cotizaciones/cotizacion-detail.component').then(m => m.CotizacionDetailComponent),
          },
        ],
      },
      {
        path: 'ordenes-compra',
        loadComponent: () =>
          import('./features/ordenes-compra/ordenes-compra.component').then(m => m.OrdenesCompraComponent),
      },

      // --- Administración ---
      {
        path: 'administracion',
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/administracion/administracion.component').then(m => m.AdministracionComponent),
          },
          {
            path: 'etiquetas/dimensiones',
            loadComponent: () =>
              import('./features/administracion/etiquetas/dimensiones-list/dimensiones-list.component')
                .then(m => m.DimensionesListComponent),
          },
          {
            path: 'etiquetas/tags',
            loadComponent: () =>
              import('./features/administracion/etiquetas/etiquetas-list/etiquetas-list.component')
                .then(m => m.EtiquetasListComponent),
          },
          {
            path: 'parametros',
            loadComponent: () =>
              import('./features/administracion/parametros/parametros.component')
                .then(m => m.ParametrosComponent),
          },
          {
            path: 'catalogo-campos',
            loadComponent: () =>
              import('./features/administracion/catalogo-campos/categorias-list/categorias-list.component')
                .then(m => m.CategoriasListComponent),
          },
          {
            path: 'auditoria',
            loadComponent: () =>
              import('./features/administracion/auditoria/auditoria.component')
                .then(m => m.AuditoriaComponent),
          },
          {
            path: 'campos-oportunidad',
            loadComponent: () =>
              import('./features/administracion/campos-oportunidad/campos-oportunidad.component')
                .then(m => m.CamposOportunidadComponent),
          },
          {
            path: 'trm',
            loadComponent: () =>
              import('./features/administracion/trm/trm.component')
                .then(m => m.TrmComponent),
          },
          {
            path: 'criterios-evaluacion',
            loadComponent: () =>
              import('./features/administracion/criterios-evaluacion/criterios-evaluacion.component')
                .then(m => m.CriteriosEvaluacionComponent),
          },
        ],
      },

      // --- Proveedores ---
      {
        path: 'proveedores',
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/proveedores/proveedores-list/proveedores-list.component')
                .then(m => m.ProveedoresListComponent),
          },
          {
            path: 'nuevo',
            loadComponent: () =>
              import('./features/proveedores/proveedor-form/proveedor-form.component')
                .then(m => m.ProveedorFormComponent),
          },
          {
            path: ':id/editar',
            loadComponent: () =>
              import('./features/proveedores/proveedor-form/proveedor-form.component')
                .then(m => m.ProveedorFormComponent),
          },
        ],
      },

      // --- Catálogo de productos ---
      {
        path: 'catalogo-productos',
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/catalogo-productos/productos-list/productos-list.component')
                .then(m => m.ProductosListComponent),
          },
          {
            path: 'nuevo',
            loadComponent: () =>
              import('./features/catalogo-productos/producto-form/producto-form.component')
                .then(m => m.ProductoFormComponent),
          },
          {
            path: ':id/editar',
            loadComponent: () =>
              import('./features/catalogo-productos/producto-form/producto-form.component')
                .then(m => m.ProductoFormComponent),
          },
        ],
      },

      // --- Catálogo de servicios ---
      {
        path: 'catalogo-servicios',
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/catalogo-servicios/servicios-list/servicios-list.component')
                .then(m => m.ServiciosListComponent),
          },
        ],
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
