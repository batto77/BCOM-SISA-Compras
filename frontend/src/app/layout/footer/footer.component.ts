import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  template: `
    <footer class="main-footer">
      <strong>SISA &copy; {{ year }}</strong>
      &mdash; Sistema de Gestión de Compras y Abastecimiento
      <div class="float-right d-none d-sm-inline-block">
        <b>v1.0.0</b>
      </div>
    </footer>
  `,
})
export class FooterComponent {
  year = new Date().getFullYear();
}
