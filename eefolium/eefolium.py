""" This module extends the folium Map class. It is designed to be used in Google Colab, as Google Colab currently does not support ipyleaflet.
"""

import ee
import folium
from folium import plugins
from .common import *
from .conversion import *


# More WMS basemaps can be found at https://viewer.nationalmap.gov/services/
ee_basemaps = {
    "ROADMAP": folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Maps",
        overlay=True,
        control=True,
    ),
    "SATELLITE": folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite",
        overlay=True,
        control=True,
    ),
    "TERRAIN": folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Terrain",
        overlay=True,
        control=True,
    ),
    "HYBRID": folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite",
        overlay=True,
        control=True,
    ),
    "ESRI": folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Satellite",
        overlay=True,
        control=True,
    ),
    "Esri Ocean": folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Ocean",
        overlay=True,
        control=True,
    ),
    "Esri Satellite": folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Satellite",
        overlay=True,
        control=True,
    ),
    "Esri Standard": folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Standard",
        overlay=True,
        control=True,
    ),
    "Esri Terrain": folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Terrain",
        overlay=True,
        control=True,
    ),
    "Esri Transportation": folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Transportation",
        overlay=True,
        control=True,
    ),
    "Esri Topo World": folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Topo World",
        overlay=True,
        control=True,
    ),
    "Esri National Geographic": folium.TileLayer(
        tiles="http://services.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri National Geographic",
        overlay=True,
        control=True,
    ),
    "Esri Shaded Relief": folium.TileLayer(
        tiles="https://services.arcgisonline.com/arcgis/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Shaded Relief",
        overlay=True,
        control=True,
    ),
    "Esri Physical Map": folium.TileLayer(
        tiles="https://services.arcgisonline.com/arcgis/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Physical Map",
        overlay=True,
        control=True,
    ),
    "Bing VirtualEarth": folium.TileLayer(
        tiles="http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1",
        attr="Microsoft",
        name="Bing VirtualEarth",
        overlay=True,
        control=True,
    ),
    "3DEP Elevation": folium.WmsTileLayer(
        url="https://elevation.nationalmap.gov/arcgis/services/3DEPElevation/ImageServer/WMSServer?",
        layers="3DEPElevation:None",
        attr="USGS",
        name="3DEP Elevation",
        overlay=True,
        control=True,
    ),
    "NAIP Imagery": folium.WmsTileLayer(
        url="https://services.nationalmap.gov/arcgis/services/USGSNAIPImagery/ImageServer/WMSServer?",
        layers="0",
        attr="USGS",
        name="NAIP Imagery",
        overlay=True,
        control=True,
    ),
}


class Map(folium.Map):
    """The Map class inherits from folium.Map. By default, the Map will add Google Maps as the basemap. Set add_google_map = False to use OpenStreetMap as the basemap.

    Returns:
        object: folium map object.
    """

    def __init__(self, **kwargs):

        import logging

        logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

        if "use_ee" not in kwargs.keys():
            kwargs["use_ee"] = True

        if kwargs["use_ee"]:
            ee_initialize()

        if "ee_initialize" not in kwargs.keys():
            kwargs["ee_initialize"] = True

        if kwargs["ee_initialize"]:
            ee_initialize()

        # Default map center location and zoom level
        latlon = [40, -100]
        zoom = 4

        # Interchangeable parameters between ipyleaflet and folium
        if "center" in kwargs.keys():
            kwargs["location"] = kwargs["center"]
            kwargs.pop("center")
        if "location" in kwargs.keys():
            latlon = kwargs["location"]
        else:
            kwargs["location"] = latlon

        if "zoom" in kwargs.keys():
            kwargs["zoom_start"] = kwargs["zoom"]
            kwargs.pop("zoom")
        if "zoom_start" in kwargs.keys():
            zoom = kwargs["zoom_start"]
        else:
            kwargs["zoom_start"] = zoom

        if "add_google_map" not in kwargs.keys():
            kwargs["add_google_map"] = True
        if "plugin_LatLngPopup" not in kwargs.keys():
            kwargs["plugin_LatLngPopup"] = True
        if "plugin_Fullscreen" not in kwargs.keys():
            kwargs["plugin_Fullscreen"] = True
        if "plugin_Draw" not in kwargs.keys():
            kwargs["plugin_Draw"] = False
        if "Draw_export" not in kwargs.keys():
            kwargs["Draw_export"] = True
        if "plugin_MiniMap" not in kwargs.keys():
            kwargs["plugin_MiniMap"] = False
        if "plugin_LayerControl" not in kwargs.keys():
            kwargs["plugin_LayerControl"] = False

        super().__init__(**kwargs)

        if kwargs.get("add_google_map"):
            ee_basemaps["ROADMAP"].add_to(self)
        if kwargs.get("plugin_LatLngPopup"):
            folium.LatLngPopup().add_to(self)
        if kwargs.get("plugin_Fullscreen"):
            plugins.Fullscreen().add_to(self)
        if kwargs.get("plugin_Draw"):
            plugins.Draw(export=kwargs.get("Draw_export")).add_to(self)
        if kwargs.get("plugin_MiniMap"):
            plugins.MiniMap().add_to(self)
        if kwargs.get("plugin_LayerControl"):
            folium.LayerControl().add_to(self)

        self.fit_bounds([latlon, latlon], max_zoom=zoom)

    def setOptions(self, mapTypeId="HYBRID", styles={}, types=[]):
        """Adds Google basemap to the map.

        Args:
            mapTypeId (str, optional): A mapTypeId to set the basemap to. Can be one of "ROADMAP", "SATELLITE", "HYBRID" or "TERRAIN" to select one of the standard Google Maps API map types. Defaults to 'HYBRID'.
            styles ([type], optional): A dictionary of custom MapTypeStyle objects keyed with a name that will appear in the map's Map Type Controls. Defaults to None.
            types ([type], optional): A list of mapTypeIds to make available. If omitted, but opt_styles is specified, appends all of the style keys to the standard Google Maps API map types.. Defaults to None.
        """
        try:
            ee_basemaps[mapTypeId].add_to(self)
        except:
            print(
                "Basemap can only be one of the following: {}".format(
                    ", ".join(ee_basemaps.keys())
                )
            )

    set_options = setOptions

    def add_basemap(self, basemap="HYBRID"):
        """Adds a basemap to the map.

        Args:
            basemap (str, optional): Can be one of string from ee_basemaps. Defaults to 'HYBRID'.
        """
        try:
            ee_basemaps[basemap].add_to(self)
        except:
            print(
                "Basemap can only be one of the following: {}".format(
                    ", ".join(ee_basemaps.keys())
                )
            )

    def add_layer(
        self, ee_object, vis_params={}, name="Layer untitled", shown=True, opacity=1.0
    ):
        """Adds a given EE object to the map as a layer.

        Args:
            ee_object (Collection|Feature|Image|MapId): The object to add to the map.
            vis_params (dict, optional): The visualization parameters. Defaults to {}.
            name (str, optional): The name of the layer. Defaults to 'Layer untitled'.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
            opacity (float, optional): The layer's opacity represented as a number between 0 and 1. Defaults to 1.
        """
        image = None

        if (
            not isinstance(ee_object, ee.Image)
            and not isinstance(ee_object, ee.ImageCollection)
            and not isinstance(ee_object, ee.FeatureCollection)
            and not isinstance(ee_object, ee.Feature)
            and not isinstance(ee_object, ee.Geometry)
        ):
            err_str = "\n\nThe image argument in 'addLayer' function must be an instace of one of ee.Image, ee.Geometry, ee.Feature or ee.FeatureCollection."
            raise AttributeError(err_str)

        if (
            isinstance(ee_object, ee.geometry.Geometry)
            or isinstance(ee_object, ee.feature.Feature)
            or isinstance(ee_object, ee.featurecollection.FeatureCollection)
        ):
            features = ee.FeatureCollection(ee_object)

            width = 2

            if "width" in vis_params:
                width = vis_params["width"]

            color = "000000"

            if "color" in vis_params:
                color = vis_params["color"]

            image_fill = features.style(**{"fillColor": color}).updateMask(
                ee.Image.constant(0.5)
            )
            image_outline = features.style(
                **{"color": color, "fillColor": "00000000", "width": width}
            )

            image = image_fill.blend(image_outline)
        elif isinstance(ee_object, ee.image.Image):
            image = ee_object
        elif isinstance(ee_object, ee.imagecollection.ImageCollection):
            image = ee_object.mosaic()

        map_id_dict = ee.Image(image).getMapId(vis_params)
        folium.raster_layers.TileLayer(
            tiles=map_id_dict["tile_fetcher"].url_format,
            attr="Google Earth Engine",
            name=name,
            overlay=True,
            control=True,
            show=shown,
            opacity=opacity,
        ).add_to(self)

    addLayer = add_layer

    def set_center(self, lon, lat, zoom=10):
        """Centers the map view at a given coordinates with the given zoom level.

        Args:
            lon (float): The longitude of the center, in degrees.
            lat (float): The latitude of the center, in degrees.
            zoom (int, optional): The zoom level, from 1 to 24. Defaults to 10.
        """
        self.fit_bounds([[lat, lon], [lat, lon]], max_zoom=zoom)

    setCenter = set_center

    def center_object(self, ee_object, zoom=10):
        """Centers the map view on a given object.

        Args:
            ee_object (Element|Geometry): An Earth Engine object to center on - a geometry, image or feature.
            zoom (int, optional): The zoom level, from 1 to 24. Defaults to 10.
        """
        lat = 0
        lon = 0
        bounds = [[lat, lon], [lat, lon]]
        if isinstance(ee_object, ee.geometry.Geometry):
            centroid = ee_object.centroid()
            lon, lat = centroid.getInfo()["coordinates"]
            bounds = [[lat, lon], [lat, lon]]
        elif isinstance(ee_object, ee.featurecollection.FeatureCollection):
            centroid = ee_object.geometry().centroid()
            lon, lat = centroid.getInfo()["coordinates"]
            bounds = [[lat, lon], [lat, lon]]
        elif isinstance(ee_object, ee.image.Image):
            geometry = ee_object.geometry()
            coordinates = geometry.getInfo()["coordinates"][0]
            bounds = [coordinates[0][::-1], coordinates[2][::-1]]
        elif isinstance(ee_object, ee.imagecollection.ImageCollection):
            geometry = ee_object.geometry()
            coordinates = geometry.getInfo()["coordinates"][0]
            bounds = [coordinates[0][::-1], coordinates[2][::-1]]
        else:
            bounds = [[0, 0], [0, 0]]

        self.fit_bounds(bounds, max_zoom=zoom)

    centerObject = center_object

    def set_control_visibility(
        self, layerControl=True, fullscreenControl=True, latLngPopup=True
    ):
        """Sets the visibility of the controls on the map.

        Args:
            layerControl (bool, optional): Whether to show the control that allows the user to toggle layers on/off. Defaults to True.
            fullscreenControl (bool, optional): Whether to show the control that allows the user to make the map full-screen. Defaults to True.
            latLngPopup (bool, optional): Whether to show the control that pops up the Lat/lon when the user clicks on the map. Defaults to True.
        """
        if layerControl:
            folium.LayerControl().add_to(self)
        if fullscreenControl:
            plugins.Fullscreen().add_to(self)
        if latLngPopup:
            folium.LatLngPopup().add_to(self)

    setControlVisibility = set_control_visibility

    def add_layer_control(self):
        """Adds layer basemap to the map."""
        folium.LayerControl().add_to(self)

    addLayerControl = add_layer_control

    def add_wms_layer(
        self,
        url,
        layers,
        name=None,
        attribution="",
        overlay=True,
        control=True,
        shown=True,
        format="image/png",
    ):
        """Add a WMS layer to the map.

        Args:
            url (str): The URL of the WMS web service.
            layers (str): Comma-separated list of WMS layers to show.
            name (str, optional): The layer name to use on the layer control. Defaults to None.
            attribution (str, optional): The attribution of the data layer. Defaults to ''.
            overlay (str, optional): Allows overlay. Defaults to True.
            control (str, optional): Adds the layer to the layer control. Defaults to True.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
            format (str, optional): WMS image format (use ‘image/png’ for layers with transparency). Defaults to 'image/jpeg'.
        """
        try:
            folium.raster_layers.WmsTileLayer(
                url=url,
                layers=layers,
                attr=attribution,
                name=name,
                overlay=overlay,
                control=control,
                show=shown,
            ).add_to(self)
        except:
            print("Failed to add the specified WMS TileLayer.")

    def add_tile_layer(
        self,
        tiles="OpenStreetMap",
        name=None,
        attribution="",
        overlay=True,
        control=True,
        shown=True,
        opacity=1.0,
        API_key=None,
    ):
        """Add a XYZ tile layer to the map.

        Args:
            tiles (str): The URL of the XYZ tile service.
            name (str, optional): The layer name to use on the layer control. Defaults to None.
            attribution (str, optional): The attribution of the data layer. Defaults to ''.
            overlay (str, optional): Allows overlay. Defaults to True.
            control (str, optional): Adds the layer to the layer control. Defaults to True.
            shown (bool, optional): A flag indicating whether the layer should be on by default. Defaults to True.
            opacity (float, optional): Sets the opacity for the layer.
            API_key (str, optional): – API key for Cloudmade or Mapbox tiles. Defaults to True.
        """

        try:
            folium.raster_layers.TileLayer(
                tiles=tiles,
                name=name,
                attr=attribution,
                overlay=overlay,
                control=control,
                show=shown,
                opacity=opacity,
                API_key=API_key,
            ).add_to(self)
        except:
            print("Failed to add the specified TileLayer.")

    def publish(
        self,
        name=None,
        headline="Untitled",
        visibility="PUBLIC",
        overwrite=True,
        open=True,
    ):
        """Publish the map to datapane.com

        Args:
            name (str, optional): The URL of the map. Defaults to None.
            headline (str, optional): Title of the map. Defaults to 'Untitled'.
            visibility (str, optional): Visibility of the map. It can be one of the following: PUBLIC, PRIVATE, ORG. Defaults to 'PUBLIC'.
            overwrite (bool, optional): Whether to overwrite the existing map with the same name. Defaults to True.
            open (bool, optional): Whether to open the map. Defaults to True.
        """
        import webbrowser

        try:
            import datapane as dp
        except Exception as e:
            print(
                "The datapane Python package is not installed. You need to install and authenticate datapane first."
            )
            webbrowser.open_new_tab(
                "https://docs.datapane.com/tutorials/tut-getting-started"
            )
            return

        import datapane as dp

        # import logging
        # logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

        if name is None:
            name = "folium_" + random_string(6)

        visibility = visibility.upper()
        if visibility not in ["PUBLIC", "PRIVATE", "ORG"]:
            visibility = "PRIVATE"

        if overwrite:
            delete_dp_report(name)

        report = dp.Report(dp.Plot(self))
        report.publish(name=name, headline=headline, visibility=visibility, open=open)


def delete_dp_report(name):
    """Deletes a datapane report.

    Args:
        name (str): Name of the report to delete.
    """
    try:
        import datapane as dp

        reports = dp.Report.list()
        items = list(reports)
        names = list(map(lambda item: item["name"], items))
        if name in names:
            report = dp.Report.get(name)
            url = report.blocks[0]["url"]
            # print('Deleting {}...'.format(url))
            dp.Report.delete(dp.Report.by_id(url))
    except Exception as e:
        print(e)
        return


def delete_dp_reports():
    """Deletes all datapane reports."""
    try:
        import datapane as dp

        reports = dp.Report.list()
        for item in reports:
            print(item["name"])
            report = dp.Report.get(item["name"])
            url = report.blocks[0]["url"]
            print("Deleting {}...".format(url))
            dp.Report.delete(dp.Report.by_id(url))
    except Exception as e:
        print(e)
        return
