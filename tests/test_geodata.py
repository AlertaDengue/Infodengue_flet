from geodata.wfs import Infodengue
from owslib.wfs import WebFeatureService

def test_Infodengue():
    infodengue = Infodengue()
    assert infodengue.wfs.url == "http://info.dengue.mat.br/geoserver/wfs"
    assert infodengue.wfs.version == "2.0.0"

def test_list_features():
    infodengue = Infodengue()
    assert 'brasil_censo_gpkg:AC_bairros_CD2022' in  infodengue.list_features()

def test_get_feature():
    infodengue = Infodengue()
    feat = infodengue.get_feature('REGIC2018_Internacional_Cidades')
    assert 'crs' in feat.keys()