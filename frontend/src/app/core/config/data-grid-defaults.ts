import type {
  ExportingEvent,
  dxDataGridOptions,
} from 'devextreme/ui/data_grid';

const GRID_STORAGE_PREFIX = 'ticketGrid';
const GRID_STORAGE_VERSION = 'v2';

function normalizeSegment(value: string): string {
  const normalized = value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');

  return normalized || 'pagina';
}

function getCurrentPageSlug(): string {
  const path = window.location.pathname.replace(/^\/+|\/+$/g, '');
  return normalizeSegment(path || 'dashboard');
}

function formatDatePart(value: number): string {
  return value.toString().padStart(2, '0');
}

function getTimestampSlug(date = new Date()): string {
  return [
    date.getFullYear(),
    formatDatePart(date.getMonth() + 1),
    formatDatePart(date.getDate()),
    formatDatePart(date.getHours()),
    formatDatePart(date.getMinutes()),
  ].join('');
}

function getGridStorageKey(): string {
  return `${GRID_STORAGE_PREFIX}:${GRID_STORAGE_VERSION}:${getCurrentPageSlug()}`;
}

function loadGridState(): Promise<unknown> {
  try {
    const storedState = window.localStorage.getItem(getGridStorageKey());
    return Promise.resolve(storedState ? JSON.parse(storedState) : null);
  } catch {
    return Promise.resolve(null);
  }
}

function saveGridState(gridState: unknown): void {
  try {
    window.localStorage.setItem(getGridStorageKey(), JSON.stringify(gridState));
  } catch {
    // Ignorar errores de cuota o storage deshabilitado; el grid debe seguir usable.
  }
}

function setExportFileName(event: ExportingEvent): void {
  event.fileName ??= `${getCurrentPageSlug()}-${getTimestampSlug()}`;
}

const dataGridDefaults: dxDataGridOptions = {
  hoverStateEnabled: true,
  wordWrapEnabled: true,
  selection: {
    mode: 'multiple',
    showCheckBoxesMode: 'none',
  },
  width: '100%',
  stateStoring: {
    enabled: true,
    type: 'custom',
    customLoad: loadGridState,
    customSave: saveGridState,
  },
  allowColumnReordering: true,
  allowColumnResizing: true,
  columnAutoWidth: false,
  columnChooser: {
    enabled: true,
  },
  columnFixing: {
    enabled: false,
  },
  columnResizingMode: 'widget',
  export: {
    allowExportSelectedData: true,
    enabled: true,
    formats: ['xlsx'],
  },
  filterRow: {
    visible: true,
  },
  headerFilter: {
    visible: true,
  },
  loadPanel: {
    enabled: true,
    text: 'Loading...',
  },
  paging: {
    enabled: false,
  },
  scrolling: {
    mode: 'standard',
    showScrollbar: 'onHover',
  },
  rowAlternationEnabled: true,
  onExporting: setExportFileName,
};

export async function registerDataGridDefaults(): Promise<void> {
  const { default: DataGrid } = await import('devextreme/ui/data_grid');

  DataGrid.defaultOptions<dxDataGridOptions>({
    options: dataGridDefaults,
  });
}
