let opacity = 0.8;

const color_dict = {
    0: 'rgba(0, 0, 0, 0)',
    2.5: `rgba(248, 248, 248, ${opacity})`,
    5: `rgba(221, 221, 248, ${opacity})`,
    7.5: `rgba(194, 194, 248, ${opacity})`,
    10: `rgba(167, 167, 248, ${opacity})`,
    12.5: `rgba(140, 140, 248, ${opacity})`,
    15: `rgba(113, 113, 248, ${opacity})`,
    17.5: `rgba(86, 86, 248, ${opacity})`,
    20: `rgba(59, 59, 248, ${opacity})`,
    22.5: `rgba(30, 30, 248, ${opacity})`,
    25: `rgba(0, 0, 248, ${opacity})`,
    27.5: `rgba(81, 40, 137, ${opacity})`,
    30: `rgba(100, 45, 144, ${opacity})`,
    32.5: `rgba(119, 51, 151, ${opacity})`,
    35: `rgba(139, 56, 159, ${opacity})`,
    37.5: `rgba(158, 62, 166, ${opacity})`,
    40: `rgba(177, 67, 173, ${opacity})`,
    42.5: `rgba(197, 73, 181, ${opacity})`,
    45: `rgba(216, 78, 188, ${opacity})`,
    47.5: `rgba(235, 84, 195, ${opacity})`,
    50: `rgba(255, 90, 204, ${opacity})`
};


$(function() { // Wait for the page to load

    var map = TETHYS_MAP_VIEW.getMap();
    var layers = map.getLayers();

    var swe_layer;
    layers.forEach(layer => {
        if ("tethys_data" in layer){
            if (layer.tethys_data.layer_name.includes("SWE")) {
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

    let key = Math.floor(swe / 2.5) * 2.5 + 2.5;
    console.log(swe, key)
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
    let labelValues = [0, 10, 20, 30, 40, 50]; // Adjust label positions as needed
    for (let value of labelValues) {
        let label = document.createElement('div');
        label.innerText = `${value} in`;
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
        let percentage = (key / 50) * 100; // Assuming max value is 100
        gradientColors.push(`${color} ${percentage}%`);
    }

    // Create linear gradient CSS string
    let gradientString = `linear-gradient(to right, ${gradientColors.join(', ')})`;
    return gradientString;
}
