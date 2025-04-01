import geojson
import geopandas as gpd
import requests
from owslib.wfs import WebFeatureService

STATES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
    "BR": "Brasil"
}


class InfodengueMaps:
    def __init__(self):
        self.wfs = None
        self.feature_GDF = None
        self.cities = {}

    def _connect_wfs(self):
        self.wfs = WebFeatureService(
            url="http://info.dengue.mat.br/geoserver/wfs",
            version="2.0.0"
        )
        return self.wfs

    def list_features(self):
        if self.wfs is None:
            self.wfs = self._connect_wfs()
        return list(self.wfs.contents)

    async def get_feature(self, feature_name: str):
        if self.wfs is None:
            self.wfs = self._connect_wfs()
        params = dict(service='WFS', version='2.0.0', request='GetFeature',
                      typeName=feature_name, outputFormat='json')
        r = requests.get(self.wfs.url, params=params)
        map_geojson = geojson.loads(r.content)
        self.feature_GDF = gpd.GeoDataFrame.from_features(map_geojson)
        self.cities = {d['NM_MUN']: d['CD_MUN'] for d in
                       self.feature_GDF[['NM_MUN', 'CD_MUN']].drop_duplicates().to_dict(orient='records')}
        return map_geojson

    def get_city_names(self) -> list:
        return list(self.cities.keys())

    async def get_state_geojson(self, state_code: str):
        feature = await self.get_feature(f"{state_code}_distritos_CD2022")
        return feature

    async def get_city_geojson(self, city_code: str, state_code: str = 'RJ'):
        if self.feature_GDF is None:
            await self.get_featureself.get_feature(f"{state_code}_distritos_CD2022")
        city_geojson = self.feature_GDF[self.feature_GDF['CD_MUN'] == city_code].to_json()
        return geojson.loads(city_geojson)
