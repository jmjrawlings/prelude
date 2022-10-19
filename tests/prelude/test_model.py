from pytest import fixture
from attrs import define, field
from src.prelude import *
from pandas import DataFrame

@define
class SampleModel(Model):
    name : str = field(default="")
    id   : int = field(default=0)
    df_a : DataFrame = field(factory=DataFrame)
    df_b : DataFrame = field(factory=DataFrame)
    

@fixture
def model():
    return SampleModel(name='test_model', id=1)


def test_model_roundtrip(model: SampleModel, tmp_path):
    path = model.save(tmp_path / 'model.json')
    new = SampleModel.load(path)