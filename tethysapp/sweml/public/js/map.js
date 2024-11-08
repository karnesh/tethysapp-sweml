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

    let key = Math.floor(swe/5)*5+5;
    let color 
    
    switch(key){
        case 0:
            color = 'rgba(0, 0, 0, 0)';
            break;
        case 5:
            color = `rgba(248, 248, 248, ${opacity})`;
            break;
        case 10:
            color = `rgba(221, 221, 248, ${opacity})`;
            break;
        case 15:
            color = `rgba(194, 194, 248, ${opacity})`;
            break;
        case 20:
            color = `rgba(167, 167, 248, ${opacity})`;
            break;
        case 25:
            color = `rgba(140, 140, 248, ${opacity})`;
            break;
        case 30:
            color = `rgba(113, 113, 248, ${opacity})`;
            break;
        case 35:
            color = `rgba(86, 86, 248, ${opacity})`;
            break;
        case 40:
            color = `rgba(59, 59, 248, ${opacity})`;
            break;
        case 45:
            color = `rgba(30, 30, 248, ${opacity})`;
            break;
        case 50:
            color = `rgba(0, 0, 248, ${opacity})`;
            break;
        case 55:
            color = `rgba(140, 140, 248, ${opacity})`;
            break;
        case 60:
            color = 'rgba(0, 0, 0, 0)';
            break;
        case 65:
            color = `rgba(248, 248, 248, ${opacity})`;
            break;
        case 70:
            color = `rgba(221, 221, 248, ${opacity})`;
            break;
        case 75:
            color = `rgba(194, 194, 248, ${opacity})`;
            break;
        case 80:
            color = `rgba(167, 167, 248, ${opacity})`;
            break;
        case 85:
            color = `rgba(140, 140, 248, ${opacity})`;
            break;
        case 90:
            color = `rgba(113, 113, 248, ${opacity})`;
            break;
        case 95:
            color = `rgba(86, 86, 248, ${opacity})`;
            break;
        case 100:
            color = `rgba(59, 59, 248, ${opacity})`;
            break;
    }
    
    return color;
        
    /*
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
    console.log(color_dict.key)
    
    return color_dict.key;
    */
}
