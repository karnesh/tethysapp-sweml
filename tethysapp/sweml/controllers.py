from tethys_sdk.layouts import MapLayout
from tethys_sdk.routing import controller
from .app import Sweml as app


#Controller base configurations
BASEMAPS = [
        {'ESRI': {'layer':'NatGeo_World_Map'}},
        {'ESRI': {'layer':'World_Street_Map'}},
        {'ESRI': {'layer':'World_Imagery'}},
        {'ESRI': {'layer':'World_Shaded_Relief'}},
        {'ESRI': {'layer':'World_Topo_Map'}},
        'OpenStreetMap',      
    ]
MAX_ZOOM = 16
MIN_ZOOM = 1
@controller(name="home", app_workspace=True)
class swe(MapLayout):
    app = app
    base_template = 'sweml/base.html'
    map_title = 'SWE'
    map_subtitle = 'SWE 1-km Predictions'
    basemaps = BASEMAPS
    max_zoom = MAX_ZOOM
    min_zoom = MIN_ZOOM