import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

interface NavItem {
  label: string;
  icon: string;
  route?: string;
  tourId?: string;
  children?: NavItem[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './sidebar.component.html',
})
export class SidebarComponent {
  menuItems: NavItem[] = [
    {
      label: 'Dashboard',
      icon: 'fas fa-tachometer-alt',
      route: '/dashboard',
      tourId: 'menu-dashboard',
    },
    {
      label: 'Oportunidades',
      icon: 'fas fa-file-alt',
      tourId: 'menu-opportunities',
      children: [
        { label: 'Nueva oportunidad', icon: 'far fa-circle', route: '/solicitudes/nueva' },
        { label: 'Mis oportunidades', icon: 'far fa-circle', route: '/solicitudes' },
      ],
    },
    {
      label: 'Cotizaciones',
      icon: 'fas fa-tags',
      tourId: 'menu-quotes',
      children: [
        { label: 'Mis cotizaciones', icon: 'far fa-circle', route: '/cotizaciones' },
      ],
    },
    {
      label: 'Proveedores',
      icon: 'fas fa-truck',
      tourId: 'menu-suppliers',
      children: [
        { label: 'Lista de proveedores', icon: 'far fa-circle', route: '/proveedores' },
        { label: 'Nuevo proveedor', icon: 'far fa-circle', route: '/proveedores/nuevo' },
        { label: 'Evaluaciones', icon: 'far fa-circle', route: '/proveedores/evaluaciones' },
      ],
    },
    {
      label: 'Administración',
      icon: 'fas fa-cog',
      tourId: 'menu-admin',
      children: [
        { label: 'Inicio', icon: 'far fa-circle', route: '/administracion' },
        { label: 'Categorías', icon: 'far fa-circle', route: '/administracion/etiquetas/dimensiones' },
        { label: 'Etiquetas', icon: 'far fa-circle', route: '/administracion/etiquetas/tags' },
        { label: 'Parámetros', icon: 'far fa-circle', route: '/administracion/parametros' },
        { label: 'Campos de producto', icon: 'far fa-circle', route: '/administracion/catalogo-campos' },
        { label: 'Campos de oportunidad', icon: 'far fa-circle', route: '/administracion/campos-oportunidad' },
        { label: 'TRM / Tasas de cambio', icon: 'far fa-circle', route: '/administracion/trm' },
        { label: 'Pesos del comparativo', icon: 'far fa-circle', route: '/administracion/criterios-evaluacion' },
        { label: 'Auditoría', icon: 'far fa-circle', route: '/administracion/auditoria' },
        { label: 'Usuarios y roles', icon: 'far fa-circle', route: '/administracion/usuarios' },
      ],
    },
  ];

  openGroups = new Set<string>();

  toggleGroup(label: string): void {
    if (this.openGroups.has(label)) {
      this.openGroups.delete(label);
    } else {
      this.openGroups.add(label);
    }
  }

  isOpen(label: string): boolean {
    return this.openGroups.has(label);
  }
}
