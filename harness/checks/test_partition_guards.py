import importlib.util
from pathlib import Path
import pandas as pd
import pytest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('guards',ROOT/'skills/model/shared/spatial_analysis/scripts/python/partition_guards.py')
guards=importlib.util.module_from_spec(spec);spec.loader.exec_module(guards)


@pytest.mark.parametrize('coefficients', [[0., 0.], [1., 0.], [0., 1.]])
def test_each_partition_point_requires_positive_support(coefficients):
    points=pd.DataFrame({'id':['a','b'],'longitude':[100.,102.],'latitude':[30.,30.]}).set_index('id')
    weights=pd.DataFrame({'point_id':['a','b'],'source_x':[100.,102.],'source_y':[30.,30.],'weight':coefficients})
    with pytest.raises(ValueError,match='missing_positive_source_support'):
        guards.check_partition(points,['a'],['b'],{'grid':weights},guard_km=75.,radius_km=6371.0088,
            coordinate_basis='angular_lon_lat_aligned_without_verified_datum')

def test_distance_and_shared_nodes():
    points=pd.DataFrame({'id':['a','b'],'longitude':[100.,102.],'latitude':[30.,30.]}).set_index('id')
    weights=pd.DataFrame({'point_id':['a','b'],'source_x':[100.,102.],'source_y':[30.,30.],'weight':[1.,1.]})
    kwargs={'guard_km':75.,'radius_km':6371.0088,'coordinate_basis':'angular_lon_lat_aligned_without_verified_datum'}
    assert guards.check_partition(points,['a'],['b'],{'grid':weights},**kwargs)['passed']
    weights.loc[1,'source_x']=100
    assert not guards.check_partition(points,['a'],['b'],{'grid':weights},**kwargs)['passed']
    weights.loc[1,'source_x']=102;points.loc['b','longitude']=100.1
    assert not guards.check_partition(points,['a'],['b'],{'grid':weights},**kwargs)['passed']
    with pytest.raises(ValueError,match='coordinate_basis'):
        guards.check_partition(points,['a'],['b'],{'grid':weights},**{**kwargs,'coordinate_basis':'EPSG:4326'})
