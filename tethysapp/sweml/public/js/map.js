$(function() { //wait for page to load

    var map = TETHYS_MAP_VIEW.getMap();
    var layers = map.getLayers()

    var swe_layer
    layers.forEach(layer => {
        if ("tethys_data" in layer){
            if (layer.tethys_data.layer_name == "SWE") {
                swe_layer = layer;
            }
        }
    });
    
});