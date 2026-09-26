(() => {
	"use strict";

	// Edit these settings to change the picker without changing its event handlers.
	const CONFIG = {
		map: {
			defaultPosition: [43.8971, -79.4470],
			defaultZoom: 13,
			savedZoom: 15,
			searchZoom: 16,
			coordinatePrecision: 6,
		},
		tiles: {
			url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
			options: {
				attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
				// OSM needs a Referer; send the origin without exposing admin paths.
				referrerPolicy: "strict-origin-when-cross-origin",
				maxZoom: 19,
			},
		},
		geocoding: {
			baseUrl: "https://nominatim.openstreetmap.org/",
			language: "en",
			reverseDelayMs: 350,
		},
		messages: {
			searching: "Searching\u2026",
			noResults: "No results found.",
			searchFailed: "Search failed. Check your connection.",
		},
	};

	/** Parse a complete coordinate pair, returning null for missing or invalid values. */
	const parsePosition = (latitude, longitude) => {
		const values = [latitude, longitude];
		const hasMissingValue = values.some(value => value == null || String(value).trim() === "");
		if (hasMissingValue) {
			return null;
		}

		const position = values.map(Number);
		const isValid = position.every(Number.isFinite)
			&& Math.abs(position[0]) <= 90
			&& Math.abs(position[1]) <= 180;

		return isValid ? position : null;
	};

	/** Fetch geocoding JSON; callers handle cancellation and user-facing errors. */
	const geocode = async (query, signal) => {
		const response = await fetch(`${CONFIG.geocoding.baseUrl}${query}`, {
			headers: { "Accept-Language": CONFIG.geocoding.language },
			signal,
		});

		if (!response.ok) {
			throw new Error(`Geocoding failed: ${response.status}`);
		}

		return response.json();
	};

	/** Initialize one admin picker, skipping templates and already initialized maps. */
	const initMap = widgetId => {
		if (widgetId.includes("__prefix__")) {
			return;
		}

		const latitudeField = document.getElementById(`id_${widgetId}-location_lat`);
		const longitudeField = document.getElementById(`id_${widgetId}-location_lon`);
		const locationField = document.getElementById(`id_${widgetId}-location`);
		const mapContainer = document.getElementById(`map_${widgetId}`);
		const searchInput = document.getElementById(`search_${widgetId}`);
		const searchButton = document.getElementById(`search_btn_${widgetId}`);
		const searchStatus = document.getElementById(`search_status_${widgetId}`);

		if (!mapContainer || !latitudeField || !longitudeField || mapContainer._leaflet_id) {
			return;
		}

		latitudeField.readOnly = true;
		longitudeField.readOnly = true;

		const savedPosition = parsePosition(latitudeField.value, longitudeField.value);
		const initialPosition = savedPosition || CONFIG.map.defaultPosition;
		const initialZoom = savedPosition ? CONFIG.map.savedZoom : CONFIG.map.defaultZoom;
		const map = L.map(mapContainer).setView(initialPosition, initialZoom);
		const popupContent = document.createElement("span");
		const marker = L.marker(initialPosition, { draggable: true }).bindPopup(popupContent);

		let markerVisible = false;
		let activeRequest = null;
		let reverseTimer = null;
		let resizeObserver = null;

		L.tileLayer(CONFIG.tiles.url, CONFIG.tiles.options).addTo(map);

		/** Update the optional status element using plain text. */
		const setStatus = message => {
			if (searchStatus) {
				searchStatus.textContent = message;
			}
		};

		/** Cancel delayed and in-flight lookups before another interaction takes over. */
		const cancelLookup = () => {
			clearTimeout(reverseTimer);
			reverseTimer = null;
			activeRequest?.abort();
			activeRequest = null;

			if (searchButton) {
				searchButton.disabled = false;
			}
		};

		/** Start a lookup and return its signal for both fetch cancellation and stale-result checks. */
		const beginLookup = () => {
			cancelLookup();
			activeRequest = new AbortController();
			return activeRequest.signal;
		};

		/** Update the stored name and popup text without moving or reopening the marker. */
		const setLabel = label => {
			// Leaflet treats strings as HTML, so reuse a text-only DOM element.
			popupContent.textContent = label;
			marker.setPopupContent(popupContent);

			if (locationField) {
				locationField.value = label;
			}
			setStatus(label);
		};

		/** Reveal or move the single marker; event binding is handled after all handlers exist. */
		const showMarker = position => {
			marker.setLatLng(position);
			if (!markerVisible) {
				marker.addTo(map);
				markerVisible = true;
			}
			marker.openPopup();
		};

		/** Immediately store a selected position and display its name or coordinate fallback. */
		const selectPosition = (position, name) => {
			latitudeField.value = position[0].toFixed(CONFIG.map.coordinatePrecision);
			longitudeField.value = position[1].toFixed(CONFIG.map.coordinatePrecision);

			const coordinateLabel = `${latitudeField.value}, ${longitudeField.value}`;
			const hasName = typeof name === "string" && name.trim() !== "";
			setLabel(hasName ? name : coordinateLabel);
			showMarker(position);
		};

		/** Enrich the current selection with a name, retaining coordinates if the lookup fails. */
		const reverseGeocode = async (position, signal) => {
			try {
				const query = `reverse?format=json&lat=${position[0]}&lon=${position[1]}`;
				const data = await geocode(query, signal);
				const hasName = typeof data?.display_name === "string" && data.display_name.trim() !== "";

				if (!signal.aborted && hasName) {
					setLabel(data.display_name);
				}
			} catch {
				// Coordinates are already saved; a failed name lookup changes nothing.
			} finally {
				if (!signal.aborted) {
					activeRequest = null;
				}
			}
		};

		/** Select a clicked or dragged point immediately, then debounce its name lookup. */
		const selectPoint = point => {
			// Normalize longitudes when the user pans into another world copy.
			const longitude = ((point.lng + 180) % 360 + 360) % 360 - 180;
			const position = parsePosition(point.lat, longitude);
			if (!position) {
				return;
			}

			const signal = beginLookup();
			selectPosition(position);
			reverseTimer = setTimeout(() => {
				reverseTimer = null;
				reverseGeocode(position, signal);
			}, CONFIG.geocoding.reverseDelayMs);
		};

		/** Search for one location and apply it only if no newer interaction has superseded it. */
		const searchLocation = async () => {
			const query = searchInput?.value.trim();
			if (!query) {
				return;
			}

			const signal = beginLookup();
			setStatus(CONFIG.messages.searching);
			if (searchButton) {
				searchButton.disabled = true;
			}

			try {
				const data = await geocode(`search?format=json&limit=1&q=${encodeURIComponent(query)}`, signal);
				if (signal.aborted) {
					return;
				}
				if (!Array.isArray(data)) {
					throw new Error("Invalid search response");
				}
				if (data.length === 0) {
					setStatus(CONFIG.messages.noResults);
					return;
				}

				const result = data[0];
				const position = parsePosition(result?.lat, result?.lon);
				if (!position) {
					throw new Error("Invalid search coordinates");
				}

				selectPosition(position, result.display_name);
				map.setView(position, CONFIG.map.searchZoom);
			} catch {
				if (!signal.aborted) {
					setStatus(CONFIG.messages.searchFailed);
				}
			} finally {
				if (!signal.aborted) {
					activeRequest = null;
					if (searchButton) {
						searchButton.disabled = false;
					}
				}
			}
		};

		/** Search on Enter without submitting the surrounding admin form. */
		const onSearchKeydown = event => {
			if (event.key === "Enter") {
				event.preventDefault();
				searchLocation();
			}
		};

		/** Remeasure visible maps when admin tabs or sidebars change their dimensions. */
		const resizeMap = () => {
			if (mapContainer.clientWidth && mapContainer.clientHeight) {
				map.invalidateSize({ pan: false, debounceMoveend: true });
			}
		};

		/** Release external resources when Leaflet removes the map. */
		const dispose = () => {
			cancelLookup();
			resizeObserver?.disconnect();
			marker.off();
			searchButton?.removeEventListener("click", searchLocation);
			searchInput?.removeEventListener("keydown", onSearchKeydown);
		};

		// Bind events after their dependencies are initialized; rendering never binds handlers.
		marker.on("dragstart", cancelLookup);
		marker.on("dragend", () => selectPoint(marker.getLatLng()));
		map.on("click", event => selectPoint(event.latlng));
		map.on("unload", dispose);
		searchButton?.addEventListener("click", searchLocation);
		searchInput?.addEventListener("keydown", onSearchKeydown);

		if (typeof ResizeObserver !== "undefined") {
			resizeObserver = new ResizeObserver(resizeMap);
			resizeObserver.observe(mapContainer);
		}

		// Preserve saved form values until the user makes a selection.
		if (savedPosition) {
			const coordinateLabel = savedPosition
				.map(value => value.toFixed(CONFIG.map.coordinatePrecision))
				.join(", ");
			popupContent.textContent = locationField?.value || coordinateLabel;
			showMarker(savedPosition);
		}
	};

	/** Initialize the rendered pickers once their form elements are available. */
	const initMaps = () => {
		document.querySelectorAll("[id^='map_']").forEach(element => {
			initMap(element.id.slice(4));
		});
	};

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", initMaps, { once: true });
	} else {
		initMaps();
	}
})();
