import { AfterViewInit, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './sidebar/sidebar.component';
import { NavbarComponent } from './navbar/navbar.component';
import { FooterComponent } from './footer/footer.component';
import { TourService } from '../core/services/tour.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent, NavbarComponent, FooterComponent],
  templateUrl: './layout.component.html',
})
export class LayoutComponent implements AfterViewInit {
  constructor(private tourService: TourService) {}

  ngAfterViewInit(): void {
    window.setTimeout(() => this.tourService.startNavigationTour(), 400);
  }
}
