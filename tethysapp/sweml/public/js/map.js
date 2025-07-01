let opacity = 0.8;

const color_dict = {
    0: 'rgba(0, 0, 0, 0)',
    3: `rgba(248, 248, 248, ${opacity})`,
    6: `rgba(221, 221, 248, ${opacity})`,
    9: `rgba(194, 194, 248, ${opacity})`,
    12: `rgba(167, 167, 248, ${opacity})`,
    15: `rgba(140, 140, 248, ${opacity})`,
    18: `rgba(113, 113, 248, ${opacity})`,
    21: `rgba(86, 86, 248, ${opacity})`,
    24: `rgba(59, 59, 248, ${opacity})`,
    27: `rgba(30, 30, 248, ${opacity})`,
    30: `rgba(0, 0, 248, ${opacity})`,
    33: `rgba(81, 40, 137, ${opacity})`,
    36: `rgba(100, 45, 144, ${opacity})`,
    39: `rgba(119, 51, 151, ${opacity})`,
    42: `rgba(139, 56, 159, ${opacity})`,
    45: `rgba(158, 62, 166, ${opacity})`,
    48: `rgba(177, 67, 173, ${opacity})`,
    51: `rgba(197, 73, 181, ${opacity})`,
    54: `rgba(216, 78, 188, ${opacity})`,
    57: `rgba(235, 84, 195, ${opacity})`,
    60: `rgba(255, 90, 204, ${opacity})`
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
    
    if (swe_layer){
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
    }

});

function setFeatureColor(feature) {
    
    let swe = feature.get('SWE');

    let key = Math.floor(swe / 3) * 3 + 3;
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
    let labelValues = [0, 10, 20, 30, 40, 50, 60]; // Adjust label positions as needed
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
        let percentage = (key / 60) * 100; // Assuming max value is 60
        gradientColors.push(`${color} ${percentage}%`);
    }

    // Create linear gradient CSS string
    let gradientString = `linear-gradient(to right, ${gradientColors.join(', ')})`;
    return gradientString;
}
    
function regionSelectionVisibility(){
    let model_id = document.getElementById("model_id").value;
    let region_id = document.getElementById("region-id-div");
    if (model_id === "SWEML_regionalv1.0"){
        region_id.style.display = "block";
    } else{
        region_id.style.display = "none";
    }
}