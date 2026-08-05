import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { registerDataGridDefaults } from './app/core/config/data-grid-defaults';

type CssDeclaration = Record<string, string>;

interface TrialPanelStyles {
  containerStyles: CssDeclaration;
  contentStyles: CssDeclaration;
  textStyles: CssDeclaration;
  linkStyles: CssDeclaration;
}

type DxLicenseConstructor = CustomElementConstructor & {
  customStyles?: TrialPanelStyles;
};

type DxLicenseElement = HTMLElement & {
  _containerStyles?: string;
  _contentStyles?: string;
  _spanStyles?: string;
  _linkStyles?: string;
};

// Paleta SISA para el banner de evaluación de DevExtreme.
const SISA_TRIAL_PANEL_STYLES: TrialPanelStyles = {
  containerStyles: {
    'background-color': '#003087',
    'border-bottom': '2px solid #0077c8',
    'padding': '0.35rem 0.75rem',
    'display':'none '
  },
  contentStyles: {
    'background-color': '#003087',
    'padding': '0.1rem 0.75rem',
  },
  textStyles: {
    'color': 'rgba(255, 255, 255, 0.82)',
    'font-size': '0.72rem',
    'font-weight': '500',
  },
  linkStyles: {
    'color': '#bfe6ff',
    'font-size': '0.72rem',
    'font-weight': '600',
  },
};

function toImportantCss(styles: CssDeclaration): string {
  return Object.entries(styles)
    .map(([property, value]) => `${property}: ${value} !important;`)
    .join('');
}

function setDxLicenseClassStyles(constructor: CustomElementConstructor): void {
  (constructor as DxLicenseConstructor).customStyles = SISA_TRIAL_PANEL_STYLES;
}

function patchDxLicenseRegistration(): void {
  const definedDxLicense = customElements.get('dx-license');

  if (definedDxLicense) {
    setDxLicenseClassStyles(definedDxLicense);
    return;
  }

  const defineCustomElement = customElements.define.bind(customElements);

  customElements.define = ((name, constructor, options) => {
    if (name === 'dx-license') {
      setDxLicenseClassStyles(constructor);
    }

    defineCustomElement(name, constructor, options);
  }) as CustomElementRegistry['define'];
}

function updateDxLicenseInstanceStyles(panel: DxLicenseElement): void {
  panel._containerStyles = toImportantCss(SISA_TRIAL_PANEL_STYLES.containerStyles);
  panel._contentStyles = toImportantCss(SISA_TRIAL_PANEL_STYLES.contentStyles);
  panel._spanStyles = toImportantCss(SISA_TRIAL_PANEL_STYLES.textStyles);
  panel._linkStyles = toImportantCss(SISA_TRIAL_PANEL_STYLES.linkStyles);
}

function applyPanelStyles(panel: HTMLElement): void {
  updateDxLicenseInstanceStyles(panel as DxLicenseElement);

  panel.style.setProperty('background-color', '#003087', 'important');
  panel.style.setProperty('border-bottom', '2px solid #0077c8', 'important');
  panel.style.setProperty('padding', '0.35rem 0.75rem', 'important');

  const content = panel.querySelector(':scope > div:first-child') as HTMLElement | null;
  content?.style.setProperty('background-color', '#003087', 'important');
  content?.style.setProperty('padding', '0.1rem 0.75rem', 'important');

  panel.querySelectorAll<HTMLElement>('span').forEach(el => {
    el.style.setProperty('color', 'rgba(255,255,255,0.82)', 'important');
    el.style.setProperty('font-size', '0.72rem', 'important');
    el.style.setProperty('font-weight', '500', 'important');
  });

  panel.querySelectorAll<HTMLElement>('a').forEach(el => {
    el.style.setProperty('color', '#bfe6ff', 'important');
    el.style.setProperty('font-size', '0.72rem', 'important');
    el.style.setProperty('font-weight', '600', 'important');
  });
}

function applyDevExtremeTrialPanelStyles(): void {
  patchDxLicenseRegistration();

  customElements.whenDefined('dx-license').then(() => {
    const DxLicenseClass = customElements.get('dx-license');
    if (DxLicenseClass) {
      setDxLicenseClassStyles(DxLicenseClass);
    }
  });

  let panelObserver: MutationObserver | null = null;
  const applyExistingPanelStyles = (): boolean => {
    const panel = document.querySelector<HTMLElement>('dx-license');
    if (!panel) {
      return false;
    }

    panelObserver?.disconnect();
    requestAnimationFrame(() => applyPanelStyles(panel));
    return true;
  };

  if (applyExistingPanelStyles()) {
    return;
  }

  panelObserver = new MutationObserver(() => {
    applyExistingPanelStyles();
  });
  panelObserver.observe(document.body, { childList: true, subtree: true });
}

applyDevExtremeTrialPanelStyles();

registerDataGridDefaults()
  .then(() => bootstrapApplication(AppComponent, appConfig))
  .catch((err: unknown) => console.error(err));
