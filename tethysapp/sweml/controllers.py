from tethys_sdk.layouts import MapLayout
from tethys_sdk.routing import controller
from .app import Sweml as app


# Controller base configurations
basemaps = [
        {'ESRI': {'layer':'NatGeo_World_Map'}},
        {'ESRI': {'layer':'World_Street_Map'}},
        {'ESRI': {'layer':'World_Imagery'}},
        {'ESRI': {'layer':'World_Shaded_Relief'}},
        {'ESRI': {'layer':'World_Topo_Map'}},
        'OpenStreetMap',      
    ]
max_zoom = 16
min_zoom = 1


@controller(name="home", app_workspace=True)
class swe(MapLayout):
    app = app
    base_template = 'sweml/base.html'
    map_title = 'SWE'
    map_subtitle = 'SWE 1-km Predictions'
    basemaps = basemaps
    max_zoom = max_zoom
    min_zoom = min_zoom