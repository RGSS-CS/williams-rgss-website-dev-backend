const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname,
  '../backend/management/static/management/js/leaflet_picker.js'), 'utf8');

test('map remeasures when a hidden admin section opens or changes width', () => {
  const mapDiv = { id: 'map_location-0', clientWidth: 0, clientHeight: 0 };
  const field = () => ({ value: '', style: {}, setAttribute() {}, addEventListener() {} });
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
    document: {
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
