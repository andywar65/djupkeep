window.addEventListener("map:init", function (event) {
    var map = event.detail.map; // Get reference to map
    map.options.crs = L.CRS.Simple;
});
