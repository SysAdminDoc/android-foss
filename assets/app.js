(() => {
	'use strict';

	const APP_VERSION = '0.0.15';
	const PAGE_SIZE = 24;
	const formatter = new Intl.NumberFormat();
	const compactFormatter = new Intl.NumberFormat(undefined, {
		notation: 'compact',
		maximumFractionDigits: 1,
	});
	const requestedLocale = new URL(window.location.href).searchParams.get('lang') || navigator.language || 'en';
	const activeLocale = requestedLocale.toLowerCase().startsWith('es') ? 'es' : 'en';
	const strings = {
		en: {
			showing: (visible, total, filterText) => `Showing ${formatter.format(visible)} of ${formatter.format(total)} matches. ${filterText}.`,
			noResults: filterText => `${filterText}. Try a different search.`,
			noFilters: 'No filters applied',
			activeFilters: count => `${count} active filter${count === 1 ? '' : 's'}`,
			showMore: count => `Show more apps (${formatter.format(count)} remaining)`,
		},
		es: {
			showing: (visible, total, filterText) => `Mostrando ${formatter.format(visible)} de ${formatter.format(total)} resultados. ${filterText}.`,
			noResults: filterText => `${filterText}. Prueba otra búsqueda.`,
			noFilters: 'No hay filtros activos',
			activeFilters: count => `${count} filtro${count === 1 ? '' : 's'} activo${count === 1 ? '' : 's'}`,
			showMore: count => `Mostrar más aplicaciones (${formatter.format(count)} restantes)`,
		},
	};
	const copy = strings[activeLocale];

	const elements = {
		search: document.querySelector('#catalog-search'),
		category: document.querySelector('#filter-category'),
		store: document.querySelector('#filter-store'),
		trust: document.querySelector('#filter-trust'),
		recency: document.querySelector('#filter-recency'),
		host: document.querySelector('#filter-host'),
		discovery: document.querySelector('#filter-discovery'),
		sort: document.querySelector('#filter-sort'),
		clear: document.querySelector('#clear-filters'),
		emptyClear: document.querySelector('#empty-clear'),
		grid: document.querySelector('#catalog-grid'),
		empty: document.querySelector('#empty-state'),
		status: document.querySelector('#status'),
		resultCount: document.querySelector('#result-count'),
		resultSummary: document.querySelector('#result-summary'),
		loadMore: document.querySelector('#load-more'),
		activeQuery: document.querySelector('#active-query'),
		activeQueryText: document.querySelector('#active-query-text'),
		clearSearch: document.querySelector('#clear-search'),
		theme: document.querySelector('#theme-select'),
		metaTheme: document.querySelector('meta[name="theme-color"]'),
		statApps: document.querySelector('#stat-apps'),
		statCategories: document.querySelector('#stat-categories'),
		statLinks: document.querySelector('#stat-links'),
	};

	const state = {
		items: [],
		matches: [],
		visibleLimit: PAGE_SIZE,
	};

	function normalizeUrl(value) {
		return String(value || '').replace(/\/$/, '').toLowerCase();
	}

	function safeExternalUrl(value) {
		try {
			const url = new URL(value);
			return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : '#';
		} catch {
			return '#';
		}
	}

	function unique(values) {
		return [...new Set(values.filter(Boolean))];
	}

	function maxDate(values) {
		const dates = values.filter(value => /^\d{4}-\d{2}-\d{2}$/.test(value || '')).sort();
		return dates.length ? dates.at(-1) : null;
	}

	function daysSince(value) {
		if (!value) return null;
		const parsed = Date.parse(`${value.slice(0, 10)}T00:00:00Z`);
		if (Number.isNaN(parsed)) return null;
		return Math.max(0, Math.floor((Date.now() - parsed) / 86400000));
	}

	function sourcePopularity(entry, popularityData) {
		const sources = popularityData && popularityData.sources ? popularityData.sources : {};
		const exact = sources[entry.sourceUrl] || sources[entry.sourceUrl.replace(/\/$/, '')];
		if (exact) return exact;
		const target = normalizeUrl(entry.sourceUrl);
		return Object.values(sources).find(source => normalizeUrl(source.sourceUrl) === target) || null;
	}

	function trustEntry(entry, trustData) {
		const entries = trustData && trustData.entries ? trustData.entries : {};
		const named = entries[entry.name];
		if (named && normalizeUrl(named.sourceUrl) === normalizeUrl(entry.sourceUrl)) return named;
		return Object.values(entries).find(candidate => normalizeUrl(candidate.sourceUrl) === normalizeUrl(entry.sourceUrl)) || named || null;
	}

	function prepareItem(entry, trustData, popularityData, index) {
		const trust = trustEntry(entry, trustData);
		const packages = trust && Array.isArray(trust.packages) ? trust.packages : [];
		const stores = unique((entry.storeLinks || []).map(link => link.store));
		const packageIds = unique([
			...(entry.storeLinks || []).map(link => link.packageId),
			...packages.map(item => item.packageId),
		]);
		const popularity = sourcePopularity(entry, popularityData);
		const latestUpdate = maxDate(packages.map(item => item.lastUpdated));
		const antiFeatures = unique(packages.flatMap(item => item.antiFeatures || []));
		const sensitivePermissions = unique(packages.flatMap(item => item.sensitivePermissions || []));
		const reproducible = packages.some(item => item.reproducible === true);
		const sourceArchive = packages.some(item => item.sourceArchive === true);
		const noAntiFeatures = packages.length > 0 && packages.every(item => !item.antiFeatures || item.antiFeatures.length === 0);
		const score =
			(stores.length ? 16 : 0) +
			(packages.length ? 12 : 0) +
			(reproducible ? 8 : 0) +
			(latestUpdate ? Math.max(0, 8 - Math.floor((daysSince(latestUpdate) || 0) / 180)) : 0) +
			(popularity && Number.isInteger(popularity.stars) ? Math.min(10, Math.log10(popularity.stars + 1) * 3) : 0);

		return {
			...entry,
			index,
			stores,
			packageIds,
			packages,
			popularity,
			latestUpdate,
			antiFeatures,
			sensitivePermissions,
			reproducible,
			sourceArchive,
			noAntiFeatures,
			score,
			searchText: [
				entry.name,
				entry.category,
				entry.sourceHost,
				entry.sourceUrl,
				...stores,
				...packageIds,
			].join(' ').toLowerCase(),
		};
	}

	function fillSelect(select, values) {
		const fragment = document.createDocumentFragment();
		for (const value of values) {
			const option = document.createElement('option');
			option.value = value;
			option.textContent = value;
			fragment.append(option);
		}
		select.append(fragment);
	}

	function setLabel(control, text) {
		const label = control.closest('label')?.querySelector(':scope > span');
		if (label) label.textContent = text;
	}

	function applyLocale() {
		document.documentElement.lang = activeLocale;
		if (activeLocale !== 'es') return;

		document.querySelector('.skip-link').textContent = 'Saltar a los resultados';
		document.querySelector('.hero-search .sr-only').textContent = 'Buscar en el catálogo';
		elements.search.placeholder = 'Busca aplicaciones, categorías, paquetes o servidores';
		document.querySelector('.theme-field > span').textContent = 'Tema';
		['Oscuro', 'Claro', 'Sistema'].forEach((label, index) => {
			elements.theme.options[index].textContent = label;
		});
		setLabel(elements.category, 'Categoría');
		setLabel(elements.store, 'Tienda');
		setLabel(elements.trust, 'Señal de confianza');
		setLabel(elements.recency, 'Actualización');
		setLabel(elements.sort, 'Orden');
		setLabel(elements.host, 'Servidor de origen');
		setLabel(elements.discovery, 'Señal de descubrimiento');

		const translations = [
			[elements.category, ['Todas las categorías']],
			[elements.store, ['Cualquier tienda', 'F-Droid', 'IzzyOnDroid', 'Sin enlace de tienda']],
			[elements.trust, ['Cualquier señal', 'Sin anti-funciones registradas', 'Reproducibilidad verificada', 'Con anti-funciones', 'Permisos sensibles', 'Archivo de código fuente']],
			[elements.recency, ['Cualquier fecha', 'En los últimos 90 días', 'En el último año', 'En los últimos 2 años', 'Más de 2 años', 'Sin fecha de actualización']],
			[elements.sort, ['Cobertura de señales', 'Nombre', 'Actualización reciente', 'Estrellas del código fuente', 'Categoría']],
			[elements.host, ['Cualquier servidor de origen']],
			[elements.discovery, ['Cualquier señal de descubrimiento', '100+ estrellas del código fuente', '1.000+ estrellas del código fuente', 'Con versión en GitHub', 'Código actualizado en el último año']],
		];
		for (const [select, labels] of translations) {
			labels.forEach((label, index) => {
				if (select.options[index]) select.options[index].textContent = label;
			});
		}

		elements.clear.textContent = 'Limpiar';
		elements.emptyClear.textContent = 'Limpiar filtros';
		document.querySelector('#advanced-filters > summary').textContent = 'Más filtros';
	}

	function matchesTrust(item, value) {
		if (!value) return true;
		if (value === 'anti-features') return item.antiFeatures.length > 0;
		if (value === 'sensitive-permissions') return item.sensitivePermissions.length > 0;
		if (value === 'no-anti-features') return item.noAntiFeatures;
		if (value === 'source-archive') return item.sourceArchive;
		if (value === 'reproducible-verified') return item.reproducible;
		return true;
	}

	function matchesRecency(item, value) {
		if (!value) return true;
		const age = daysSince(item.latestUpdate);
		if (value === 'unknown') return age === null;
		if (value === 'stale') return age !== null && age > 730;
		return age !== null && age <= Number(value);
	}

	function matchesDiscovery(item, value) {
		if (!value) return true;
		const popularity = item.popularity;
		if (!popularity || popularity.available !== true) return false;
		if (value === 'stars100') return Number(popularity.stars) >= 100;
		if (value === 'stars1000') return Number(popularity.stars) >= 1000;
		if (value === 'has-release') return Boolean(popularity.latestReleaseDate);
		if (value === 'source-updated-365') {
			const age = daysSince(popularity.sourcePushed || popularity.sourceUpdated);
			return age !== null && age <= 365;
		}
		return true;
	}

	function compareItems(left, right) {
		const mode = elements.sort.value;
		if (mode === 'name') return left.name.localeCompare(right.name);
		if (mode === 'category') return left.category.localeCompare(right.category) || left.name.localeCompare(right.name);
		if (mode === 'updated') {
			return String(right.latestUpdate || '').localeCompare(String(left.latestUpdate || '')) || left.name.localeCompare(right.name);
		}
		if (mode === 'stars') {
			return Number(right.popularity?.stars || -1) - Number(left.popularity?.stars || -1) || left.name.localeCompare(right.name);
		}
		return right.score - left.score || left.index - right.index;
	}

	function activeFilterCount() {
		return [elements.search, elements.category, elements.store, elements.trust, elements.recency, elements.host, elements.discovery]
			.filter(control => control.value).length;
	}

	function updateSearchUrl() {
		const url = new URL(window.location.href);
		const query = elements.search.value.trim();
		if (query) url.searchParams.set('q', query);
		else url.searchParams.delete('q');
		window.history.replaceState({}, '', url);
	}

	function applyFilters({ resetLimit = true } = {}) {
		if (resetLimit) state.visibleLimit = PAGE_SIZE;
		const query = elements.search.value.trim().toLowerCase();
		state.matches = state.items
			.filter(item => {
				if (query && !item.searchText.includes(query)) return false;
				if (elements.category.value && item.category !== elements.category.value) return false;
				if (elements.store.value === 'none' && item.stores.length) return false;
				if (elements.store.value && elements.store.value !== 'none' && !item.stores.includes(elements.store.value)) return false;
				if (elements.host.value && item.sourceHost !== elements.host.value) return false;
				if (!matchesTrust(item, elements.trust.value)) return false;
				if (!matchesRecency(item, elements.recency.value)) return false;
				if (!matchesDiscovery(item, elements.discovery.value)) return false;
				return true;
			})
			.sort(compareItems);

		updateSearchUrl();
		renderResults();
	}

	function makeElement(tagName, className, text) {
		const node = document.createElement(tagName);
		if (className) node.className = className;
		if (text !== undefined) node.textContent = text;
		return node;
	}

	function makeSignal(text, className = '') {
		return makeElement('span', `signal ${className}`.trim(), text);
	}

	function cardDescription(item) {
		const category = item.category.toLowerCase();
		if (item.stores.length) {
			const storeText = item.stores.length === 1 ? item.stores[0] : item.stores.join(' and ');
			return `Open-source ${category} option with an install link cataloged from ${storeText}.`;
		}
		return `Open-source ${category} project with source code ready to inspect.`;
	}

	function createCard(item) {
		const card = makeElement('article', 'catalog-card');
		card.dataset.name = item.name;
		card.dataset.category = item.category;

		card.append(makeElement('p', 'card-category', item.category));
		card.append(makeElement('h3', '', item.name));
		card.append(makeElement('p', 'card-description', cardDescription(item)));

		const source = makeElement('p', 'card-source');
		source.append(makeElement('strong', '', 'Source: '));
		source.append(document.createTextNode(item.sourceHost || 'External project'));
		card.append(source);

		const signals = makeElement('div', 'card-signals');
		if (item.antiFeatures.length) {
			signals.append(makeSignal(`${item.antiFeatures.length} listed anti-feature${item.antiFeatures.length === 1 ? '' : 's'}`, 'warning'));
		} else if (item.noAntiFeatures) {
			signals.append(makeSignal('No listed anti-features', 'good'));
		}
		if (item.sensitivePermissions.length) {
			signals.append(makeSignal(`${item.sensitivePermissions.length} sensitive permission${item.sensitivePermissions.length === 1 ? '' : 's'}`, 'warning'));
		} else if (item.reproducible) {
			signals.append(makeSignal('Reproducible verified', 'good'));
		}
		if (item.latestUpdate) signals.append(makeSignal(`Updated ${item.latestUpdate}`, 'info'));
		if (item.popularity && Number.isInteger(item.popularity.stars)) {
			signals.append(makeSignal(`${compactFormatter.format(item.popularity.stars)} source stars`));
		}
		if (signals.childElementCount) card.append(signals);

		const actions = makeElement('div', 'card-actions');
		const sourceLink = makeElement('a', 'button source-button', 'View source');
		sourceLink.href = safeExternalUrl(item.sourceUrl);
		sourceLink.rel = 'noreferrer';
		sourceLink.target = '_blank';
		actions.append(sourceLink);

		for (const storeLink of item.storeLinks || []) {
			const link = makeElement('a', 'button store-button', storeLink.store);
			link.href = safeExternalUrl(storeLink.url);
			link.rel = 'noreferrer';
			link.target = '_blank';
			actions.append(link);
		}
		if (actions.childElementCount === 1) sourceLink.classList.add('single-action');
		card.append(actions);
		return card;
	}

	function renderResults() {
		const total = state.matches.length;
		const visible = state.matches.slice(0, state.visibleLimit);
		const fragment = document.createDocumentFragment();
		for (const item of visible) fragment.append(createCard(item));

		elements.grid.replaceChildren(fragment);
		elements.grid.setAttribute('aria-busy', 'false');
		elements.resultCount.textContent = formatter.format(total);
		elements.empty.hidden = total !== 0;
		elements.grid.hidden = total === 0;
		elements.loadMore.hidden = visible.length >= total;
		elements.loadMore.textContent = copy.showMore(total - visible.length);
		const query = elements.search.value.trim();
		elements.activeQuery.hidden = !query;
		elements.activeQueryText.textContent = query;

		const filters = activeFilterCount();
		const filterText = filters ? copy.activeFilters(filters) : copy.noFilters;
		elements.resultSummary.textContent = total
			? copy.showing(visible.length, total, filterText)
			: copy.noResults(filterText);
	}

	function clearFilters() {
		for (const control of [elements.search, elements.category, elements.store, elements.trust, elements.recency, elements.host, elements.discovery]) {
			control.value = '';
		}
		elements.sort.value = 'recommended';
		applyFilters();
		elements.search.focus({ preventScroll: true });
	}

	function showError(message) {
		elements.status.textContent = message;
		elements.status.hidden = false;
		elements.grid.hidden = true;
		elements.grid.setAttribute('aria-busy', 'false');
		elements.resultSummary.textContent = 'Catalog data is unavailable.';
	}

	async function fetchJson(path) {
		const response = await fetch(path, { cache: 'no-store' });
		if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
		return response.json();
	}

	function resolvedTheme(value) {
		if (value !== 'system') return value;
		return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
	}

	function applyTheme(value) {
		const selection = ['dark', 'light', 'system'].includes(value) ? value : 'dark';
		const theme = resolvedTheme(selection);
		document.documentElement.dataset.theme = theme;
		elements.theme.value = selection;
		elements.metaTheme.content = theme === 'light' ? '#f3f8f5' : '#07110f';
		localStorage.setItem('android-foss-theme', selection);
	}

	function registerEvents() {
		for (const control of [elements.category, elements.store, elements.trust, elements.recency, elements.host, elements.discovery, elements.sort]) {
			control.addEventListener('change', () => applyFilters());
		}
		elements.search.addEventListener('input', () => applyFilters());
		elements.search.addEventListener('keydown', event => {
			if (event.key !== 'Enter') return;
			event.preventDefault();
			document.querySelector('#results').scrollIntoView({ behavior: 'smooth' });
		});
		elements.clear.addEventListener('click', clearFilters);
		elements.emptyClear.addEventListener('click', clearFilters);
		elements.clearSearch.addEventListener('click', () => {
			elements.search.value = '';
			applyFilters();
		});
		elements.loadMore.addEventListener('click', () => {
			state.visibleLimit += PAGE_SIZE;
			renderResults();
		});
		elements.theme.addEventListener('change', event => applyTheme(event.target.value));
		window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => {
			if (elements.theme.value === 'system') applyTheme('system');
		});
	}

	async function loadCatalog() {
		try {
			const [catalogData, trustData, popularityData] = await Promise.all([
				fetchJson('catalog.json'),
				fetchJson('catalog-trust.json'),
				fetchJson('catalog-popularity.json'),
			]);
			const entries = Array.isArray(catalogData.entries) ? catalogData.entries : [];
			state.items = entries.map((entry, index) => prepareItem(entry, trustData, popularityData, index));

			const categories = unique(state.items.map(item => item.category)).sort((left, right) => left.localeCompare(right));
			const hosts = unique(state.items.map(item => item.sourceHost)).sort((left, right) => left.localeCompare(right));
			fillSelect(elements.category, categories);
			fillSelect(elements.host, hosts);

			elements.statApps.textContent = formatter.format(entries.length);
			elements.statCategories.textContent = formatter.format(categories.length);
			elements.statLinks.textContent = formatter.format(entries.reduce((count, entry) => count + (entry.storeLinks || []).length, 0));

			const query = new URL(window.location.href).searchParams.get('q');
			if (query) elements.search.value = query;
			applyFilters();
			window.__androidFossCatalog = {
				version: APP_VERSION,
				state,
				applyFilters,
				clearFilters,
			};
		} catch (error) {
			console.error('Catalog load failed:', error);
			showError('The catalog could not be loaded. Refresh the page or open the README list on GitHub.');
		}
	}

	applyLocale();
	applyTheme(localStorage.getItem('android-foss-theme') || 'dark');
	registerEvents();
	loadCatalog();

	if ('serviceWorker' in navigator && (window.location.protocol === 'https:' || window.location.hostname === 'localhost')) {
		window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(error => {
			console.warn('Offline support could not be registered:', error);
		}));
	}
})();
