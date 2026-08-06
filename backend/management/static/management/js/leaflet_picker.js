(function () {
  "use strict";

  function initMap(widgetId) {
    var latField     = document.getElementById("id_" + widgetId + "-location_lat");
    var lonField     = document.getElementById("id_" + widgetId + "-location_lon");
    var textField    = document.getElementById("id_" + widgetId + "-location");
    var mapDiv       = document.getElementById("map_" + widgetId);
    var searchInput  = document.getElementById("search_" + widgetId);
    var searchBtn    = document.getElementById("search_btn_" + widgetId);
    var searchStatus = document.getElementById("search_status_" + widgetId);

    if (!mapDiv || !latField || !lonField) return;

    // lat/lon are read-only — set only by map interaction, not keyboard
    [latField, lonField].forEach(function (f) {
      f.setAttribute("readonly", "readonly");
      f.style.backgroundColor = "#f5f5f5";
      f.style.cursor = "not-allowed";
    });

    var initLat  = parseFloat(latField.value) || 43.8971; // Dr. G.W. Williams default
    var initLon  = parseFloat(lonField.value) || -79.4470;
    var initZoom = (latField.value && lonField.value) ? 15 : 13;

    var map = L.map(mapDiv).setView([initLat, initLon], initZoom);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    }).addTo(map);

    var marker = null;

    // If there's an existing saved location, place marker with saved name
    if (latField.value && lonField.value) {
      var savedName = (textField && textField.value) ? textField.value : null;
      marker = L.marker([initLat, initLon], { draggable: true })
        .addTo(map)
        .bindPopup(savedName || (initLat.toFixed(6) + ", " + initLon.toFixed(6)))
        .openPopup();
      bindMarkerDrag(marker);
    }

    // Clicking the map reverse-geocodes the point via Nominatim to get a name
    map.on("click", function (e) {
      reverseGeocode(e.latlng.lat, e.latlng.lng, function(name) {
        placeMarker(e.latlng.lat, e.latlng.lng, name);
      });
    });

    function placeMarker(lat, lon, name) {
      var latlng   = L.latLng(lat, lon);
      var latStr   = parseFloat(lat).toFixed(6);
      var lonStr   = parseFloat(lon).toFixed(6);
      var label    = name || (latStr + ", " + lonStr);

      if (marker) {
        marker.setLatLng(latlng);
      } else {
        marker = L.marker(latlng, { draggable: true }).addTo(map);
        bindMarkerDrag(marker);
      }

      marker.bindPopup(label).openPopup();

      latField.value  = latStr;
      lonField.value  = lonStr;
      // Store the human-readable name in the OSMField (location text field)
      if (textField) textField.value = label;

      if (searchStatus) searchStatus.textContent = label;
    }

    function bindMarkerDrag(m) {
      m.on("dragend", function (e) {
        var pos = e.target.getLatLng();
        reverseGeocode(pos.lat, pos.lng, function(name) {
          placeMarker(pos.lat, pos.lng, name);
        });
      });
    }

    // Nominatim reverse geocoding — turns lat/lon into a place name
    // https://nominatim.org/release-docs/latest/api/Reverse/
    function reverseGeocode(lat, lon, callback) {
      fetch(
        "https://nominatim.openstreetmap.org/reverse?format=json&lat=" +
          lat + "&lon=" + lon,
        { headers: { "Accept-Language": "en" } }
      )
        .then(function (r) { return r.json(); })
        .then(function (data) {
          callback(data.display_name || null);
        })
        .catch(function () {
          callback(null);
        });
    }

    // Forward search via Nominatim
    // https://nominatim.org/release-docs/latest/api/Search/
    function doSearch() {
      var query = searchInput.value.trim();
      if (!query) return;

      searchStatus.textContent = "Searching\u2026";
      searchBtn.disabled = true;

      fetch(
        "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" +
          encodeURIComponent(query),
        { headers: { "Accept-Language": "en" } }
      )
        .then(function (r) { return r.json(); })
        .then(function (data) {
          searchBtn.disabled = false;
          if (!data.length) {
            searchStatus.textContent = "No results found.";
            return;
          }
          var result = data[0];
          var lat    = parseFloat(result.lat);
          var lon    = parseFloat(result.lon);
          var name   = result.display_name;

          map.setView([lat, lon], 16);
          placeMarker(lat, lon, name);
        })
        .catch(function () {
          searchBtn.disabled = false;
          searchStatus.textContent = "Search failed. Check your connection.";
        });
    }

    searchBtn.addEventListener("click", doSearch);
    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); doSearch(); }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[id^='map_']").forEach(function (el) {
      initMap(el.id.replace("map_", ""));
    });
  });
})();
