import { Injectable } from '@angular/core';
import { DriveStep, Driver, driver } from 'driver.js';

type TourOutcome = 'completed' | 'skipped';

interface TourDefinition {
  storageKey: string;
  steps: DriveStep[];
}

@Injectable({ providedIn: 'root' })
export class TourService {
  private readonly navigationTour: TourDefinition = {
    storageKey: 'sisa.tour.navigation.v1',
    steps: [
      {
        element: '[data-tour="main-menu"]',
        popover: {
          title: 'Menú principal',
          description: 'Desde aquí puedes acceder a los módulos del proceso de compras.',
          side: 'right',
          align: 'start',
        },
      },
      {
        element: '[data-tour="menu-dashboard"]',
        popover: {
          title: 'Dashboard',
          description: 'Consulta el estado general de oportunidades, cotizaciones y proveedores.',
          side: 'right',
        },
      },
      {
        element: '[data-tour="menu-opportunities"]',
        popover: {
          title: 'Oportunidades',
          description: 'Crea nuevas oportunidades y consulta las que ya se encuentran en gestión.',
          side: 'right',
        },
      },
      {
        element: '[data-tour="menu-quotes"]',
        popover: {
          title: 'Cotizaciones',
          description: 'Revisa las respuestas de proveedores y los comparativos de cada oportunidad.',
          side: 'right',
        },
      },
      {
        element: '[data-tour="menu-suppliers"]',
        popover: {
          title: 'Proveedores',
          description: 'Administra proveedores, su información y sus evaluaciones.',
          side: 'right',
        },
      },
      {
        element: '[data-tour="menu-admin"]',
        popover: {
          title: 'Administración',
          description: 'Configura categorías, etiquetas, parámetros, campos de producto y usuarios.',
          side: 'right',
        },
      },
    ],
  };

  private readonly newOpportunityTour: TourDefinition = {
    storageKey: 'sisa.tour.new-opportunity.v1',
    steps: [
      {
        element: '[data-tour="opportunity-flow"]',
        popover: {
          title: 'Flujo de la oportunidad',
          description: 'El proceso inicia con el encabezado y continúa con ítems, proveedores y envío del RFQ.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '[data-tour="opportunity-title"]',
        popover: {
          title: 'Identifica la oportunidad',
          description: 'Asigna un título corto y reconocible para facilitar su búsqueda y seguimiento.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '[data-tour="opportunity-people"]',
        popover: {
          title: 'Responsables',
          description: 'Registra quién solicita la compra y quién debe aprobarla.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '[data-tour="opportunity-planning"]',
        popover: {
          title: 'Planeación',
          description: 'Define la prioridad, los rubros presupuestales y la fecha requerida.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '[data-tour="opportunity-details"]',
        popover: {
          title: 'Contexto y notas',
          description: 'Describe la necesidad y agrega información interna para el equipo de compras.',
          side: 'top',
          align: 'start',
        },
      },
      {
        element: '[data-tour="opportunity-context"]',
        popover: {
          title: 'Guardado inicial',
          description: 'La oportunidad se guarda primero para generar su número único antes de agregar ítems.',
          side: 'left',
        },
      },
      {
        element: '[data-tour="opportunity-continue"]',
        popover: {
          title: 'Continuar con los ítems',
          description: 'Guarda el encabezado y abre el asistente para agregar productos, servicios y licencias.',
          side: 'top',
          align: 'end',
        },
      },
    ],
  };

  private readonly supplierQuoteTour: TourDefinition = {
    storageKey: 'sisa.tour.supplier-quote.v1',
    steps: [
      {
        element: '[data-tour="supplier-quote-summary"]',
        popover: {
          title: 'Información de la cotización',
          description: 'Confirma la oportunidad, la fecha límite, la prioridad y la versión del RFQ que vas a responder.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '[data-tour="supplier-quote-items"]',
        popover: {
          title: 'Ítems solicitados',
          description: 'Debes responder cada ítem asignado. La tabla calcula automáticamente los subtotales y el total estimado.',
          side: 'top',
          align: 'start',
        },
      },
      {
        element: '[data-tour="supplier-quote-specs"]',
        popover: {
          title: 'Revisa las especificaciones',
          description: 'Usa el triángulo al final de cada fila para desplegar las características y cantidades solicitadas por el comprador.',
          side: 'left',
        },
      },
      {
        element: '[data-tour="supplier-quote-price"]',
        popover: {
          title: 'Precio unitario',
          description: 'Ingresa el precio de una unidad. El sistema lo multiplicará por la cantidad solicitada.',
          side: 'bottom',
        },
      },
      {
        element: '[data-tour="supplier-quote-availability"]',
        popover: {
          title: 'Disponibilidad',
          description: 'Desmarca esta opción cuando no puedas suministrar el ítem. Sus demás campos quedarán deshabilitados.',
          side: 'bottom',
        },
      },
      {
        element: '[data-tour="supplier-quote-delivery"]',
        popover: {
          title: 'Tiempo de entrega',
          description: 'Indica cuántos días necesitas para entregar el producto, servicio o licencia.',
          side: 'bottom',
        },
      },
      {
        element: '[data-tour="supplier-quote-item-notes"]',
        popover: {
          title: 'Observación por ítem',
          description: 'Agrega aclaraciones específicas, restricciones o condiciones relacionadas con ese ítem.',
          side: 'bottom',
        },
      },
      {
        element: '[data-tour="supplier-quote-general-notes"]',
        popover: {
          title: 'Observaciones generales',
          description: 'Puedes registrar condiciones de pago, garantías u otros comentarios aplicables a toda la cotización.',
          side: 'top',
          align: 'start',
        },
      },
      {
        element: '[data-tour="supplier-quote-submit"]',
        popover: {
          title: 'Enviar cotización',
          description: 'Revisa toda la información antes de enviarla. El equipo de compras recibirá tu respuesta para compararla.',
          side: 'top',
          align: 'end',
        },
      },
    ],
  };

  private activeDriver: Driver | null = null;
  private pendingTours: TourDefinition[] = [];

  startNavigationTour(): void {
    this.startTour(this.navigationTour);
  }

  startNewOpportunityTour(): void {
    this.startTour(this.newOpportunityTour);
  }

  startSupplierQuoteTour(): void {
    this.startTour(this.supplierQuoteTour);
  }

  private startTour(tour: TourDefinition): void {
    if (!this.canUseBrowserStorage() || this.hasTourOutcome(tour.storageKey)) {
      return;
    }

    if (this.activeDriver?.isActive()) {
      const isAlreadyPending = this.pendingTours.some(pendingTour => pendingTour.storageKey === tour.storageKey);
      if (!isAlreadyPending) {
        this.pendingTours.push(tour);
      }
      return;
    }

    if (!tour.steps.every(step => this.isTargetVisible(step.element))) {
      return;
    }

    let outcome: TourOutcome = 'skipped';
    const tourDriver = driver({
      steps: tour.steps,
      animate: true,
      smoothScroll: true,
      allowClose: true,
      allowKeyboardControl: true,
      disableActiveInteraction: true,
      overlayColor: '#0f172a',
      overlayOpacity: 0.62,
      overlayClickBehavior: () => {
        outcome = 'skipped';
        tourDriver.destroy();
      },
      stagePadding: 6,
      stageRadius: 6,
      popoverClass: 'sisa-driver-popover',
      popoverOffset: 10,
      showButtons: ['previous', 'next', 'close'],
      showProgress: true,
      progressText: '{{current}} de {{total}}',
      prevBtnText: 'Anterior',
      nextBtnText: 'Siguiente',
      doneBtnText: 'Finalizar',
      onPopoverRender: popover => {
        popover.closeButton.textContent = 'Omitir';
        popover.closeButton.setAttribute('aria-label', 'Omitir recorrido');
      },
      onNextClick: () => {
        if (tourDriver.isLastStep()) {
          outcome = 'completed';
          tourDriver.destroy();
          return;
        }
        tourDriver.moveNext();
      },
      onCloseClick: () => {
        outcome = 'skipped';
        tourDriver.destroy();
      },
      onDestroyed: () => {
        this.saveTourOutcome(tour.storageKey, outcome);
        this.activeDriver = null;
        const nextTour = this.pendingTours.shift();
        if (nextTour) {
          window.setTimeout(() => this.startTour(nextTour));
        }
      },
    });

    this.activeDriver = tourDriver;
    tourDriver.drive();
  }

  private hasTourOutcome(storageKey: string): boolean {
    try {
      const outcome = window.localStorage.getItem(storageKey);
      return outcome === 'completed' || outcome === 'skipped';
    } catch {
      return false;
    }
  }

  private saveTourOutcome(storageKey: string, outcome: TourOutcome): void {
    try {
      window.localStorage.setItem(storageKey, outcome);
    } catch {
      // El recorrido sigue funcionando aunque el navegador bloquee localStorage.
    }
  }

  private canUseBrowserStorage(): boolean {
    return typeof window !== 'undefined' && typeof document !== 'undefined';
  }

  private isTargetVisible(target: DriveStep['element']): boolean {
    if (typeof target !== 'string') {
      return true;
    }

    const element = document.querySelector<HTMLElement>(target);
    return element !== null && element.getClientRects().length > 0;
  }
}
