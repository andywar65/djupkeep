function map_init(map, options) {

    function onEachFeature(feature, layer) {
      if (feature.properties && feature.properties.popupContent) {
        layer.bindPopup(feature.properties.popupContent.content, {minWidth: 256});
      }
    }

    function setLineStyle(feature) {
      if (feature.properties.popupContent.linetype) {
        return {"color": feature.properties.popupContent.color, "weight": 3 };
      } else {
        return {"color": feature.properties.popupContent.color, "weight": 3, dashArray: "10, 10" };
      }
    }

    const base_map = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 23,
      });

    const mapbox_token = JSON.parse(document.getElementById("mapbox_token").textContent);

    const sat_map = L.tileLayer("https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}",
      {
        attribution: 'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 23,
        tileSize: 512,
        zoomOffset: -1,
        id: "mapbox/satellite-v9",
        accessToken: mapbox_token
      });

    const layer_control = L.control.layers(null).addTo(map);
    const locationGroup = L.layerGroup().addTo(map);

    function getCollections() {
      // add eventually inactive base layers so they can be removed
      base_map.addTo(map);
      sat_map.addTo(map);
      // remove all layers from layer control and from map
      map.eachLayer(function (layer) {
        layer_control.removeLayer(layer);
        map.removeLayer(layer);
      });
      // add base layers back to map and layer control
      base_map.addTo(map);
      locationGroup.addTo(map);
      layer_control.addBaseLayer(base_map, "Base");
      layer_control.addBaseLayer(sat_map, "Satellite");
      // add other layers to map and layer control
      collection = JSON.parse(document.getElementById("layer_data").textContent);
      if (collection !== null) {
        for (layer_name of collection) {
          window[layer_name] = L.layerGroup().addTo(map);
          layer_control.addOverlay(window[layer_name], layer_name);
        }
      }
      // add objects to layers
      collection = JSON.parse(document.getElementById("marker_data").textContent);
      for (marker of collection.features) {
        let layer = marker.properties.popupContent.layer
        L.geoJson(marker, {onEachFeature: onEachFeature}).addTo(window[layer]);
      }
      // map.fitBounds(L.geoJson(collection).getBounds(), {padding: [30,30]});
      collection = JSON.parse(document.getElementById("line_data").textContent);
      if (collection !== null) {
        for (line of collection.features) {
          let name = line.properties.popupContent.layer
          L.geoJson(line, {style: setLineStyle, onEachFeature: onEachFeature}).addTo(map);
        }
      }
      map.fitBounds(L.geoJson(collection).getBounds(), {padding: [10,10]});
      collection = JSON.parse(document.getElementById("block_data").textContent);
      if (collection !== null) {
        for (block of collection.features) {
          let name = block.properties.popupContent.layer
          L.geoJson(block, {style: setLineStyle, onEachFeature: onEachFeature}).addTo(map);
        }
      }
    }

    getCollections()

    addEventListener("refreshCollections", function(evt){
      getCollections();
    })

    function userFound(e) {
      let content = "You are here (accuracy " + e.accuracy + " meters)!";
      L.marker( e.latlng ).bindPopup(content).addTo(locationGroup);
      L.circle(e.latlng, e.accuracy).addTo(locationGroup);
      // map.panTo(e.latlng, map.getZoom());
      collection = JSON.parse(document.getElementById("marker_data").textContent);
      map.fitBounds([e.latlng, L.geoJson(collection).getBounds()],
        {padding: [50,50]});
    }

    function userNotFound(e) {
        alert(e.message);
    }

    function locateUser() {
      locationGroup.clearLayers();
      map.locate().on('locationfound', userFound).on('locationerror', userNotFound);
    }

    document.getElementById("locate-user").addEventListener("click", locateUser);
  }
