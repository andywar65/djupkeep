window.addEventListener("map:init", function (event) {
    // Get reference to map
    var map = event.detail.map;
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
    const bounds = [[0, 0], image_size]
    // Add image to map
    L.imageOverlay(image_path, bounds).addTo(map);
    map.fitBounds(bounds);
});
