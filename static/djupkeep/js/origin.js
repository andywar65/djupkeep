window.addEventListener("map:init", function (event) {
    var map = event.detail.map; // Get reference to map
    map.options.crs = L.CRS.Simple;
    let image_path = JSON.parse(document.getElementById("image_path").textContent);
    let image_size = JSON.parse(document.getElementById("image_size").textContent);
    let bounds = [[0,0], image_size];
    let image = L.imageOverlay(image_path, bounds).addTo(map);
    map.fitBounds(bounds);
});
