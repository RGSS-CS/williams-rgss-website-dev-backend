const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname,
  '../backend/management/static/management/js/leaflet_picker.js'), 'utf8');

test('map remeasures when a hidden admin section opens or changes width', () => {
  const mapDiv = { id: 'map_location-0', clientWidth: 0, clientHeight: 0 };
  const field = () => ({ value: '', addEventListener() {}, removeEventListener() {} });
  const elements = { [mapDiv.id]: mapDiv };
  for (const name of ['location', 'location_lat', 'location_lon']) {
    elements['id_location-0-' + name] = field();
  }
  for (const name of ['search_', 'search_btn_', 'search_status_']) {
    elements[name + 'location-0'] = field();
  }
  let ready, resized, observed, disconnected = false, creations = 0;
  const invalidations = [], events = {};
  const map = {
    setView() { return this; },
    on(name, callback) { events[name] = callback; },
    invalidateSize(options) { invalidations.push(options); },
  };
  vm.runInNewContext(source, {
    clearTimeout,
    document: {
      readyState: 'loading',
      createElement: () => ({}),
      getElementById: id => elements[id],
      querySelectorAll: () => [mapDiv, { id: 'map_location-__prefix__' }],
      addEventListener(name, callback) { ready = callback; },
    },
    ResizeObserver: class {
      constructor(callback) { resized = callback; }
      observe(element) { observed = element; }
      disconnect() { disconnected = true; }
    },
    L: {
      map(element) { creations++; element._leaflet_id = creations; return map; },
      tileLayer: () => ({ addTo() {} }),
      marker: () => ({ bindPopup() { return this; }, on() {}, off() {} }),
    },
  });
  ready();
  assert.equal(observed, mapDiv);
  resized();
  assert.equal(invalidations.length, 0);
  mapDiv.clientWidth = 800;
  mapDiv.clientHeight = 420;
  resized();
  mapDiv.clientWidth = 500;
  resized();
  assert.equal(invalidations.length, 2);
  assert.equal(invalidations[0].pan, false);
  ready();
  assert.equal(creations, 1);
  events.unload();
  assert.equal(disconnected, true);
});

function picker({ lat = '', lon = '', name = '' } = {}) {
  const element = (value = '') => ({
    value, events: {},
    addEventListener(type, fn) { this.events[type] = fn; },
    removeEventListener(type) { delete this.events[type]; },
  });
  const fields = {
    'id_location-0-location_lat': element(lat),
    'id_location-0-location_lon': element(lon),
    'id_location-0-location': element(name),
    'map_location-0': { id: 'map_location-0' },
    'search_location-0': element(),
    'search_btn_location-0': element(),
    'search_status_location-0': element(),
  };
  const requests = [], timers = new Map(), markers = [];
  let timerId = 0, popupNodes = 0;
  const map = {
    events: {}, views: [],
    on(type, fn) { this.events[type] = fn; },
    setView(position, zoom) { this.views.push([Array.from(position), zoom]); return this; },
  };
  vm.runInNewContext(source, {
    AbortController,
    document: {
      readyState: 'complete',
      getElementById: id => fields[id],
      querySelectorAll: () => [fields['map_location-0']],
      createElement() { popupNodes++; return {}; },
    },
    setTimeout(fn) { timers.set(++timerId, fn); return timerId; },
    clearTimeout(id) { timers.delete(id); },
    fetch(url, { signal }) {
      return new Promise((resolve, reject) => requests.push({ url, signal, resolve, reject }));
    },
    L: {
      map: () => map,
      tileLayer: () => ({ addTo() {} }),
      marker(position) {
        const marker = {
          events: {}, position, moves: 0, opens: 0, visible: false,
          on(type, fn) { this.events[type] = fn; },
          off() { this.events = {}; },
          addTo() { this.visible = true; return this; },
          bindPopup(content) { this.content = content; return this; },
          setPopupContent(content) { this.content = content; return this; },
          setLatLng(position) { this.moves++; this.position = position; return this; },
          getLatLng() { return { lat: this.position[0], lng: this.position[1] }; },
          openPopup() { this.opens++; return this; },
        };
        markers.push(marker);
        return marker;
      },
    },
  });
  return {
    map, requests, markers, timers, fields,
    get popupNodes() { return popupNodes; },
    get name() { return fields['id_location-0-location'].value; },
    get lat() { return fields['id_location-0-location_lat'].value; },
    get status() { return fields['search_status_location-0'].textContent; },
    get disabled() { return fields['search_btn_location-0'].disabled; },
    click(lat, lng) { map.events.click({ latlng: { lat, lng } }); },
    flush() { const pending = [...timers.values()]; timers.clear(); pending.forEach(fn => fn()); },
    search(query) { fields['search_location-0'].value = query; return fields['search_btn_location-0'].events.click(); },
    async respond(index, data, ok = true) {
      requests[index].resolve({ ok, json: async () => data });
      await new Promise(resolve => setImmediate(resolve));
    },
  };
}

test('saved zero coordinates work and popup text does not become HTML', () => {
  const p = picker({ lat: '0', lon: '0', name: '<img onerror=alert(1)>' });
  assert.deepEqual(p.map.views[0], [[0, 0], 15]);
  assert.equal(p.markers[0].content.textContent, p.name);
  assert.equal(p.lat, '0');
  assert.equal(p.requests.length, 0);
  for (const lat of ['', 'bad', '91', '12junk']) {
    assert.equal(picker({ lat, lon: '10' }).markers[0].visible, false);
  }
});

test('rapid selections render immediately and share one marker, popup and delayed lookup', async () => {
  const p = picker();
  p.click(1, 2);
  p.click(3, 4);
  assert.equal(p.lat, '3.000000');
  assert.equal(p.requests.length, 0);
  assert.equal(p.timers.size, 1);
  assert.equal(p.markers.length, 1);
  assert.equal(p.popupNodes, 1);
  p.flush();
  await p.respond(0, { display_name: 'School' });
  assert.equal(p.name, 'School');
  assert.equal(p.markers[0].moves, 2);
  assert.equal(p.markers[0].opens, 2);
});

test('late reverse and search responses cannot overwrite the latest interaction', async () => {
  const p = picker();
  p.click(1, 2);
  p.flush();
  p.search('Old school');
  p.search('New school');
  assert.equal(p.requests[0].signal.aborted, true);
  assert.equal(p.requests[1].signal.aborted, true);
  await p.respond(1, []);
  assert.equal(p.disabled, true);
  await p.respond(2, [{ lat: '0', lon: '0', display_name: 'New' }]);
  await p.respond(0, { display_name: 'Old' });
  assert.equal(p.name, 'New');
  assert.equal(p.disabled, false);
  p.search('Another');
  p.click(5, 380);
  await p.respond(3, [{ lat: '10', lon: '10', display_name: 'Stale' }]);
  assert.equal(p.name, '5.000000, 20.000000');
});

test('failed or malformed geocoding leaves selected coordinates intact', async () => {
  const p = picker();
  p.click(1, 2);
  p.flush();
  await p.respond(0, {}, false);
  assert.equal(p.name, '1.000000, 2.000000');
  for (const data of [{}, [{ lat: 'bad', lon: '2' }], [{ lat: '91', lon: '2' }]]) {
    p.search('School');
    await p.respond(p.requests.length - 1, data);
    assert.match(p.status, /Search failed/);
    assert.equal(p.disabled, false);
    assert.equal(p.lat, '1.000000');
  }
  p.search('Missing');
  await p.respond(p.requests.length - 1, []);
  assert.equal(p.status, 'No results found.');
  p.search('Offline');
  p.requests.at(-1).reject(new Error('Offline'));
  await new Promise(resolve => setImmediate(resolve));
  assert.match(p.status, /Search failed/);
  assert.equal(p.disabled, false);
});

test('drag and unload cancel pending work and release search listeners', async () => {
  const p = picker();
  p.click(1, 2);
  p.flush();
  const marker = p.markers[0];
  marker.events.dragstart();
  await p.respond(0, { display_name: 'Old' });
  marker.position = [3, 4];
  marker.events.dragend();
  assert.equal(p.lat, '3.000000');
  p.map.events.unload();
  assert.equal(p.timers.size, 0);
  assert.deepEqual(marker.events, {});
  assert.deepEqual(p.fields['search_btn_location-0'].events, {});
  assert.deepEqual(p.fields['search_location-0'].events, {});
  const active = picker();
  active.search('School');
  active.map.events.unload();
  await active.respond(0, [{ lat: '1', lon: '2', display_name: 'Late' }]);
  assert.equal(active.requests[0].signal.aborted, true);
  assert.equal(active.name, '');
});
