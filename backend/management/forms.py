from django import forms
from django.utils.html import format_html
from .models import Location


class LeafletPickerWidget(forms.TextInput):
    """
    Renders a persistent full-width Leaflet map with:
    - Nominatim place search bar
    - Click-to-place / draggable marker
    - Read-only lat/lon fields (set only by map interaction)

    widget_id is set per-inline-prefix so multiple instances don't clash.
    """

    def __init__(self, widget_id="location", *args, **kwargs):
        self.widget_id = widget_id
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        # Render the hidden location input (still submitted in POST for osm_field)
        text_html = super().render(name, value, attrs, renderer)

        map_html = format_html(
            """
            {text_input}
            <div class="leaflet-picker-wrap">
              <div class="leaflet-picker-search">
                <input type="text"
                       id="search_{wid}"
                       placeholder="Search the school name (e.g. Dr. G.W. Williams Secondary School)"
                       autocomplete="off" />
                <button type="button" id="search_btn_{wid}">Search</button>
              </div>
              <div class="leaflet-picker-status" id="search_status_{wid}"></div>
              <div id="map_{wid}" class="leaflet-picker-map"></div>
              <p class="leaflet-picker-hint">
                Click the map or drag the marker to set the school location.
              </p>
            </div>
            """,
            text_input=text_html,
            wid=self.widget_id
        )
        return map_html

    @property
    def media(self):
        return forms.Media(
            css={"all": [
                "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
                "management/css/leaflet_picker.css"
            ]},
            js=[
                "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
                "management/js/leaflet_picker.js"
            ]
        )


class LocationAdminForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ("location", "location_lat", "location_lon")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use the form prefix as the widget ID so the JS can find the
        # correct lat/lon sibling fields even in a formset context.
        prefix = kwargs.get("prefix") or "location"
        self.fields["location"].widget = LeafletPickerWidget(widget_id=prefix)
        # lat/lon labels shown in hidden fields — clean them up
        self.fields["location_lat"].label = "Latitude"
        self.fields["location_lon"].label = "Longitude"
