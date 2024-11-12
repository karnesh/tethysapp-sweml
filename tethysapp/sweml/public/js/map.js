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
     
    features = swe_layer.getSource().getFeatures();
    
    for (let feature of features) {
        let color = setFeatureColor(feature)
        let style = new ol.style.Style({
            fill: new ol.style.Fill({
                color: color,
            }),
        })
        feature.setStyle(style);
    }
});

function setFeatureColor(feature) {
    let swe = feature.A.SWE;
    let opacity = 0.8;
    
    const color_dict = {
        0: 'rgba(0, 0, 0, 0)',
        5: `rgba(248, 248, 248, ${opacity})`,
        10: `rgba(221, 221, 248, ${opacity})`,
        15: `rgba(194, 194, 248, ${opacity})`,
        20: `rgba(167, 167, 248, ${opacity})`,
        25: `rgba(140, 140, 248, ${opacity})`,
        30: `rgba(113, 113, 248, ${opacity})`,
        35: `rgba(86, 86, 248, ${opacity})`,
        40: `rgba(59, 59, 248, ${opacity})`,
        45: `rgba(30, 30, 248, ${opacity})`,
        50: `rgba(0, 0, 248, ${opacity})`,
        55: `rgba(33, 102, 172, ${opacity})`,
        60: `rgba(33, 102, 172, ${opacity})`,
        65: `rgba(33, 102, 172, ${opacity})`,
        70: `rgba(33, 102, 172, ${opacity})`,
        75: `rgba(33, 102, 172, ${opacity})`,
        80: `rgba(33, 102, 172, ${opacity})`,
        85: `rgba(33, 102, 172, ${opacity})`,
        90: `rgba(33, 102, 172, ${opacity})`,
        95: `rgba(33, 102, 172, ${opacity})`,
        100: `rgba(33, 102, 172, ${opacity})`
    };
    let key = Math.floor(swe/5)*5+5;
    
    return color_dict[key];
}

/*
$(function() {  // Wait for page to load
    // Map Click Event Handler
    TETHYS_MAP_VIEW.mapClicked(function(coords) {
        let popup_content = document.querySelector("#properties-popup-content");
        let lat_lon = ol.proj.transform(coords, 'EPSG:3857', 'EPSG:4326');
        let rounded_lat = Math.round(lat_lon[1] * 100) / 100;
        let rounded_lon = Math.round(lat_lon[0] * 100) / 100;
        popup_content.innerHTML = `<b>Coordinates:</b><p>${rounded_lat}, ${rounded_lon}</p>`;
        MAP_LAYOUT.get_plot();
        MAP_LAYOUT.show_plot();
        })
});
*/
