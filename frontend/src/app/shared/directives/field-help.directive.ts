import { DOCUMENT } from '@angular/common';
import {
  Directive,
  ElementRef,
  HostBinding,
  HostListener,
  Inject,
  Input,
  OnDestroy,
  Renderer2,
} from '@angular/core';

@Directive({
  selector: '.field-help',
  standalone: true,
})
export class FieldHelpDirective implements OnDestroy {
  private tooltipText = '';
  private tooltipElement: HTMLElement | null = null;
  private removeWindowListeners: Array<() => void> = [];

  @HostBinding('attr.tabindex') readonly tabIndex = 0;
  @HostBinding('attr.title') readonly nativeTitle = null;

  @HostBinding('attr.aria-label')
  get ariaLabel(): string | null {
    return this.tooltipText ? `Ayuda: ${this.tooltipText}` : null;
  }

  @Input('title')
  set title(value: string | null | undefined) {
    this.tooltipText = value?.trim() ?? '';
    if (this.tooltipElement) {
      this.tooltipElement.textContent = this.tooltipText;
      this.positionTooltip();
    }
  }

  constructor(
    private readonly elementRef: ElementRef<HTMLElement>,
    private readonly renderer: Renderer2,
    @Inject(DOCUMENT) private readonly document: Document,
  ) {}

  @HostListener('mouseenter')
  @HostListener('focus')
  show(): void {
    if (!this.tooltipText || this.tooltipElement) return;

    const tooltip = this.renderer.createElement('div') as HTMLElement;
    this.renderer.addClass(tooltip, 'field-help-tooltip');
    this.renderer.setAttribute(tooltip, 'role', 'tooltip');
    this.renderer.setProperty(tooltip, 'textContent', this.tooltipText);
    this.renderer.appendChild(this.document.body, tooltip);
    this.tooltipElement = tooltip;
    this.positionTooltip();

    this.removeWindowListeners = [
      this.renderer.listen('window', 'resize', () => this.positionTooltip()),
      this.renderer.listen('window', 'scroll', () => this.positionTooltip()),
    ];
  }

  @HostListener('mouseleave')
  @HostListener('blur')
  hide(): void {
    this.destroyTooltip();
  }

  @HostListener('click', ['$event'])
  toggle(event: MouseEvent): void {
    event.preventDefault();
    event.stopPropagation();
    if (this.tooltipElement) {
      this.hide();
    } else {
      this.show();
    }
  }

  @HostListener('keydown.escape')
  closeFromKeyboard(): void {
    this.hide();
  }

  ngOnDestroy(): void {
    this.destroyTooltip();
  }

  private positionTooltip(): void {
    if (!this.tooltipElement) return;

    const triggerRect = this.elementRef.nativeElement.getBoundingClientRect();
    const tooltipRect = this.tooltipElement.getBoundingClientRect();
    const viewportPadding = 8;
    const gap = 8;

    let left = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
    left = Math.max(
      viewportPadding,
      Math.min(left, window.innerWidth - tooltipRect.width - viewportPadding),
    );

    let top = triggerRect.top - tooltipRect.height - gap;
    if (top < viewportPadding) {
      top = triggerRect.bottom + gap;
    }

    this.renderer.setStyle(this.tooltipElement, 'left', `${Math.round(left)}px`);
    this.renderer.setStyle(this.tooltipElement, 'top', `${Math.round(top)}px`);
  }

  private destroyTooltip(): void {
    for (const removeListener of this.removeWindowListeners) {
      removeListener();
    }
    this.removeWindowListeners = [];

    if (this.tooltipElement) {
      this.renderer.removeChild(this.document.body, this.tooltipElement);
      this.tooltipElement = null;
    }
  }
}
