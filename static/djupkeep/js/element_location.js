window.addEventListener("map:init", function (event) {
    // Get reference to map
    var map = event.detail.map;

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
});
