import geopandas as gpd
import requests
import geojson
from pyproj import CRS
from owslib.wfs import WebFeatureService

class InfodengueMaps:
    def __init__(self):
        self.wfs = None

    def _connect_wfs(self):
        return WebFeatureService(
            url="http://info.dengue.mat.br/geoserver/wfs",
            version="2.0.0"
        )
    def list_features(self):
        if self.wfs is None:
            self.wfs = self._connect_wfs()
        return list(self.wfs.contents)

    def get_feature(self, feature_name: str):
        if self.wfs is None:
            self.wfs = self._connect_wfs()
        params = dict(service='WFS', version='2.0.0', request='GetFeature',
                      typeName=feature_name, outputFormat='json')
        r = requests.get(self.wfs.url, params=params)
        return geojson.loads(r.content)