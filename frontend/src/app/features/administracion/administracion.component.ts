import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

interface AccesoAdmin {
  titulo: string;
  descripcion: string;
  icono: string;
  ruta: string;
  color: string;
}

@Component({
  selector: 'app-administracion',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './administracion.component.html',
})
export class AdministracionComponent {
  accesos: AccesoAdmin[] = [
    {
      titulo: 'Categorías',
      descripcion: 'Grupos de clasificación para etiquetas (ej: Área, Prioridad)',
      icono: 'fas fa-layer-group',
      ruta: '/administracion/etiquetas/dimensiones',
      color: 'primary',
    },
    {
      titulo: 'Etiquetas',
      descripcion: 'Etiquetas para clasificar proveedores y productos',
      icono: 'fas fa-tags',
      ruta: '/administracion/etiquetas/tags',
      color: 'info',
    },
    {
      titulo: 'Parámetros del sistema',
      descripcion: 'Unidades de medida, rubros presupuestales y plantillas ANS',
      icono: 'fas fa-sliders-h',
      ruta: '/administracion/parametros',
      color: 'warning',
    },
    {
      titulo: 'Campos de producto',
      descripcion: 'Categorías de producto y sus campos de especificaciones técnicas',
      icono: 'fas fa-puzzle-piece',
      ruta: '/administracion/catalogo-campos',
      color: 'success',
    },
    {
      titulo: 'Usuarios y roles',
      descripcion: 'Gestión de usuarios y permisos del sistema',
      icono: 'fas fa-users-cog',
      ruta: '/administracion/usuarios',
      color: 'secondary',
    },
  ];
}
