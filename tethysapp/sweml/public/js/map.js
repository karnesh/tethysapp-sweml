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


$(function() { // Wait for the page to load

    var map = TETHYS_MAP_VIEW.getMap();
    var layers = map.getLayers();

    var swe_layer;
    layers.forEach(layer => {
        if ("tethys_data" in layer){
            if (layer.tethys_data.layer_name == "SWE") {
                swe_layer = layer;
            }
        }
    });
     
    var features = swe_layer.getSource().getFeatures();
    
    for (let feature of features) {
        let color = setFeatureColor(feature);
        let style = new ol.style.Style({
            fill: new ol.style.Fill({
                color: color,
            }),
        });
        feature.setStyle(style);
    }

    // Call the function to create the legend
    createLegend();

});

function setFeatureColor(feature) {
    
    let swe = feature.get('SWE');

    let key = Math.floor(swe / 5) * 5 + 5;
    
    return color_dict[key];
}

function createLegend() {
    // Create legend container
    let legendDiv = document.getElementById('legend');

    // Add title to legend
    let legendTitle = document.createElement('div');
    legendTitle.innerHTML = 'Snow Water Equivalent (SWE)';
    legendTitle.id = 'legend-title';
    legendDiv.appendChild(legendTitle);

    // Create color ramp
    let colorRamp = document.createElement('div');
    colorRamp.id = 'legend-color-ramp';
    colorRamp.style.background = createColorGradient(color_dict);
    legendDiv.appendChild(colorRamp);

    // Create labels container
    let labelsDiv = document.createElement('div');
    labelsDiv.id = 'legend-labels';

    // Create labels
    let labelValues = [5, 20, 40, 60, 80, 100]; // Adjust label positions as needed
    for (let value of labelValues) {
        let label = document.createElement('div');
        label.innerText = `${value} mm`;
        labelsDiv.appendChild(label);
    }

    legendDiv.appendChild(labelsDiv);

    // Add legend to the map container
    document.getElementById('map_view').appendChild(legendDiv);
}

function createColorGradient(color_dict) {
    let keys = Object.keys(color_dict).sort((a, b) => a - b);
    let gradientColors = [];

    for (let key of keys) {
        let color = color_dict[key];
        let percentage = (key / 100) * 100; // Assuming max value is 100
        gradientColors.push(`${color} ${percentage}%`);
    }

    // Create linear gradient CSS string
    let gradientString = `linear-gradient(to right, ${gradientColors.join(', ')})`;
    return gradientString;
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
