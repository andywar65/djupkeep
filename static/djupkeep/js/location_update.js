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
    L.control.scale().remove();
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
    map.fitBounds(bounds);
});
