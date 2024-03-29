import json

import attrs
import cattrs
import pandas as pd
from attrs import define, field
from pandas import DataFrame, Series
from typing import Dict, List, Optional, Tuple, Type, TypeVar, Union
from .pth import Path
from .dt import *
from . import pth, dt


def create_cattrs_converter():

    def unstructure_datetime(dt: DateTime):
        return dt.timestamp()

    def structure_datetime(timestamp, _):
        return pn.from_timestamp(timestamp)

    converter = cattrs.Converter()
    converter.register_unstructure_hook(DateTime, unstructure_datetime)
    converter.register_structure_hook(DateTime, structure_datetime)
    return converter

converter = create_cattrs_converter()


def int_field(**kwargs):
    return field(default=0, converter=int, **kwargs)

def string_field(**kwargs):
    return field(default='', converter=str, **kwargs)

def bool_field(**kwargs):
    return field(default=False, converter=bool, **kwargs)

def list_field(**kwargs):
    return field(factory=list, **kwargs)

def set_field(**kwargs):
    return field(factory=set, **kwargs)

def dict_field(**kwargs):
    return field(factory=dict, **kwargs)

def float_field(**kwargs):
    return field(default=0.0, converter=float, **kwargs)


M = TypeVar("M", bound='Model')

@define
class Model:
    """
    A base model to inherit from
    """
    
    def to_dict(self) -> Dict:
        """
        Convert instance to a dictionary, no
        type conversion will occur
        """
        return cattrs.unstructure(self)

    def to_json_dict(self) -> Dict:
        """
        Convert this instance to a JSON compatible
        dictionary
        """
        return converter.unstructure(self)

    def to_json_string(self) -> str:
        """
        Convert this instance to a JSON string
        """
        record = self.to_json_dict()
        string = json.dumps(record)
        return string

    def to_json_file(self, path: Union[str, Path], overwrite=True) -> Path:
        """
        Write this instance as a JSON file, returning
        the path it was written to
        """
        path = pth.filepath(path)
        record = self.to_json_dict()
        if path.exists() and not overwrite:
            raise Exception(f'File already exists at "{path}" - use `overwrite=True` to overwrite')

        with path.open('w') as file:
            json.dump(record, file)

        return path

    @classmethod
    def from_dict(cls: Type[M], record) -> M:
        """
        Create an instance of this class from
        the given dictionary
        """
        instance = cattrs.structure(record, cls)
        return instance

    @classmethod
    def from_json_dict(cls: Type[M], record) -> M:
        """
        Create an instance of this class from
        the the given JSON compatible dict
        """
        instance = converter.structure(record, cls)
        return instance        

    @classmethod
    def from_json_string(cls: Type[M], string) -> M:
        """
        Create an instance of this class from
        the given JSON string
        """
        record = json.loads(string)
        instance = cls.from_dict(record)
        return instance

    @classmethod        
    def from_json_file(cls: Type[M], path: Union[str, Path]) -> M:
        """
        Create an instance of this class from 
        the given JSON file
        """
        path = pth.existing_file(path)
        with path.open('r') as file:
            record = json.load(file)
        model = cls.from_json_dict(record)
        return model

    def save(self, path: Union[str, Path], overwrite=True) -> Path:
        """
        Save this class to the given file
        """
        
        t = pn.now()
        path = Path(path)
                        
        # Convert this instance into a dictionary
        record = converter.unstructure(self)
                        
        # Look for DataFrame fields of the class
        df_fields = self._get_fields_of_type(DataFrame)
        if not df_fields:
            path = self.to_json_file(path, overwrite=overwrite)
        else:
            
            path.mkdir(parents=True, exist_ok=overwrite)

            for field in df_fields:
                name = field.name

                # Write the dataframe out to the folder
                df : DataFrame = record[name]
                df_path = path / f'{name}.csv'
                df.to_csv(df_path, index=False)
                
                # Remove it from the record structure
                record.pop(name)
                self._log(f'{name} saved to {df_path} ({df.shape[0]:,} rows, {df.shape[1]:,} cols)')

            # Write the partial model to json
            record_path = path / 'model.json'
            with record_path.open('w') as file:
                json.dump(record, file)
                self._log(f'record saved to {record_path}')

        elapsed = (pn.now() - t).in_words() #type:ignore
        self._log(f'model saved to {path} in {elapsed}')
        return path

    @classmethod
    def load(cls : Type[M], path : Union[Path,str]) -> M:
        """
        Load a Model instance from the given path
        """
                
        path = pth.make(path, check_exists=True)
        t = pn.now()
                
        # Assume only the .json was given
        if path.is_file():
            with path.open('r') as file:
                record = json.load(file)
                instance = cls.from_json_dict(record)
            return instance

        # Load the model json
        record_path = path / 'model.json'
        with record_path.open('r') as file:
            record = json.load(file)

        model = converter.structure(record, cls)
        cls._log(f'record loaded from {record_path}')
                
        # Load the each dataframe field
        for field in cls._get_fields_of_type(DataFrame):
            name = field.name
            df_path = path / f'{name}.csv'
            df = DataFrame()
            if df_path.exists():
                try:
                    df = pd.read_csv(df_path)
                except:
                    pass
            
            cls._log(f'{name} loaded from {df_path} ({df.shape[0]:,} rows x {df.shape[1]:,} cols)')

            # Store it on the model
            setattr(model, name, df)

        elapsed = (pn.now() - t).in_words() #type:ignore
        cls._log(f'model loaded from {path} in {elapsed}')
        return model

    def copy(self : M) -> M:
        """
        Return a deep copy of this model by
        saving and loading from json
        """
        json_string = self.to_json_string()
        model = self.from_json_string(json_string)
        return model

    @classmethod
    def _log(cls: Type[M], *args, **kwargs):
        print(f'{cls.__name__}:', *args, **kwargs)

    @classmethod
    def _get_fields_of_type(cls, type):
        fields = []
        for field in attrs.fields(cls):
            if field.type != type:
                continue
            fields.append(field)
        return fields
