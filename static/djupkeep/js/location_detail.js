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

    // Delete all default layers
    map.eachLayer(function (layer) {
        map.removeLayer(layer);
    });
    // Set new CRS
    map.options.crs = L.CRS.Simple;
    map.options.zoomSnap = 0.1;
    // Get image attributes
    const image_path = JSON.parse(document.getElementById("image_path").textContent);
    const image_size = JSON.parse(document.getElementById("image_size").textContent);
    const origin = JSON.parse(document.getElementById("origin_coords").textContent);
    const unit = JSON.parse(document.getElementById("unit_coords").textContent);
    const meters = JSON.parse(document.getElementById("length_meters").textContent);
    // Get drawing bounds
    function get_bounds(image_size, origin) {
        if (origin !== "" ) {
            return [[-origin[1], -origin[0]], [image_size[1]-origin[1], image_size[0]-origin[0]]];
        } else {
            return [[0, 0], [image_size[1], image_size[0]]];
        }
    };
    const bounds = get_bounds(image_size, origin);
    map.fitBounds(bounds);

    const layer_control = L.control.layers(null).addTo(map);

    function getCollections() {
      // remove all layers from layer control and from map
      map.eachLayer(function (layer) {
        layer_control.removeLayer(layer);
        map.removeLayer(layer);
      });
      // Add image to map
        L.imageOverlay(image_path, bounds).addTo(map);
        // Add units
        if (unit !== "" ) {
            let length = Math.sqrt(Math.pow(unit[0], 2) + Math.pow(unit[1], 2))
            for (let i = 1; i < (image_size[0]-origin[0])/length; i++) {
                L.polyline([[-origin[1], i*length], [(image_size[1]-origin[1]), i*length]], {weight: 1}).bindPopup("X=m "+(i*meters).toString()).addTo(map);
            }
            for (let i = -1; i > (-origin[0])/length; i--) {
                L.polyline([[-origin[1], i*length], [(image_size[1]-origin[1]), i*length]], {weight: 1}).bindPopup("X=m "+(i*meters).toString()).addTo(map);
            }
            for (let i = 1; i < (image_size[1]-origin[1])/length; i++) {
                L.polyline([[i*length, -origin[0]], [i*length, (image_size[0]-origin[0])]], {weight: 1}).bindPopup("Y=m "+(i*meters).toString()).addTo(map);
            }
            for (let i = -1; i > (-origin[1])/length; i--) {
                L.polyline([[i*length, -origin[0]], [i*length, (image_size[0]-origin[0])]], {weight: 1}).bindPopup("Y=m "+(i*meters).toString()).addTo(map);
            }
        }
        // Add axis
        if (origin !== "" ) {
            L.polyline([[-origin[1], 0], [(image_size[1]-origin[1]), 0]], {color: "red"}).bindPopup("X=0").addTo(map);
            L.polyline([[0, -origin[0]], [0, (image_size[0]-origin[0])]], {color: "red"}).bindPopup("Y=0").addTo(map);
        }
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
        let category = marker.properties.popupContent.layer
        L.geoJson(marker, {onEachFeature: onEachFeature}).addTo(window[category]);
      }
    }

    getCollections()

    addEventListener("refreshCollections", function(evt){
      getCollections();
    })
  }
