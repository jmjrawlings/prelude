from pytest import fixture
from attrs import define, field
from src.prelude import model, pth, Model
from src.prelude.model import M
from typing import Generic, Type, List
from pandas import DataFrame

class ModelTest(Generic[M]):
    type : Type[M]

    @property
    def name(self):
        return self.type.__name__
    
    @classmethod
    def create(cls) -> M:
        return cls.type()
    
    def test_save_model(self, tmp_path):
        model = self.create()
        model.save(tmp_path / self.name)

    def test_copy_model(self):
        model = self.create()
        copy = model.copy()

    def test_serialize_roundtrip(self):
        model = self.create()
        path = model.save(self.name)
        loaded = self.type.load(path)
        assert model == loaded

    
@define
class SimpleModel(Model):
    name : str = field(default="")
    id   : int = field(default=0)


class TestSimpleModel(ModelTest):
    type = SimpleModel


@define
class NestedModel(Model):
    children : List[SimpleModel]
    name : str = field(default="")
    id   : int = field(default=0)

    @classmethod
    def create(cls):
        return cls(
            name='xd',
            id=100,
            children=[
                SimpleModel(name='a'),
                SimpleModel(name='b'),
                SimpleModel(name='c')
            ]
        )


class TestNestedModel(ModelTest):
    type = SimpleModel
