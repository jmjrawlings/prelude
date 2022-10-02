# %%
%pip install attrs cattrs pandas pendulum

# %%
from typing import List, Tuple, Optional, Union
from pandas import DataFrame, Series
from pendulum import DateTime, Date
import pendulum as pn
from attrs import define, field
from pathlib import Path
import pandas as pd
import json
import attrs
import cattrs

converter = cattrs.Converter()
converter.register_unstructure_hook(DateTime, lambda dt: dt.timestamp())
converter.register_structure_hook(DateTime, lambda ts, _: pn.from_timestamp(ts))

# %%
@define
class Model:
    id         : int       = field(default=0)
    name       : str       = field(default='')
    created_at : DateTime  = field(factory=pn.now)
    df_a       : DataFrame = field(factory=DataFrame)
    df_b       : DataFrame = field(factory=DataFrame)
        
    def save(self, path: Path) -> Path:
        """
        Save this model to disk
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        t = pn.now()
        
        # Convert this instance into a dictionary
        record = converter.unstructure(self)
                        
        # Look for DataFrame fields of the class 
        for fieldname in Model.get_dataframe_fields():
            # Write the dataframe out to the folder
            df : DataFrame = record[fieldname]
            csv_path = path / f'{fieldname}.csv'
            df.to_csv(csv_path, index=False)
            
            # Remove it from the record structure
            record.pop(fieldname)
            print(f'model: "{self.name}" wrote "{fieldname}" with {df.shape[0]:,} rows to {csv_path}')

        # Write the partial model to json
        json_path = path / 'model.json'
        with json_path.open('w') as file:
            json.dump(record, file)

        print(f'model: "{self.name}" wrote json to {json_path}')

        elapsed = (pn.now() - t).in_words()
        print(f'model: "{self.name}" saved to {path} in {elapsed}')
        return path

    @classmethod
    def load(cls, path : Path) -> "Model":
        """
        Load a Model instance from disk
        """
        
        path = Path(path)
        assert path.is_dir(), f'Path must be a directory'
        t = pn.now()
        
        # Load the model json
        json_path = path / 'model.json'
        with json_path.open('r') as file:
            record = json.load(file)

        model = converter.structure(record, cls)
        print(f'model: "{model.name}" read json from {json_path}')
        
        # Load the dataframes
        for fieldname in Model.get_dataframe_fields():
            # Write the dataframe out to the folder
            csv_path = path / f'{fieldname}.csv'
            df = pd.read_csv(csv_path)

            print(f'model: "{model.name}" read "{fieldname}" with {df.shape[0]} rows from {csv_path}')

            # Store it on the model
            setattr(model, fieldname, df)

        elapsed = (pn.now() - t).in_words()

        print(f'model: "{model.name}" loaded from {path} in {elapsed}')
        # Create the model from record
        return model


    def copy(self):
        """
        Return a deep copy of this model by saving
        to disk and loading from disk
        """
        from tempfile import mkdtemp
        temp_dir = mkdtemp()
        path = self.save(temp_dir)
        model = self.load(path)
        return model

    @classmethod
    def get_dataframe_fields(cls):
        fields = []
        for field in attrs.fields(cls):
            if field.type != DataFrame:
                continue
            fields.append(field.name)
        return fields
           
    
    def __str__(self):
        return f'Model "{self.name} with A({self.df_a.shape[0]} rows) and B({self.df_b.shape[0]} rows)'

    def __repr__(self):
        return f'<{self!s}>'

# %%
def create_model(id, name):
    df_a = DataFrame(dict(a=[1,2,3], b=[2,3,4]))
    df_b = DataFrame(dict(c=[1,2,3], d=[2,3,4]))
    model = Model(
        id=id,
        name=name,
        df_a=df_a,
        df_b=df_b
    )
    print(f'created {model!r}')
    return model




# %%

# Create a sample model
model1 = create_model(1, 'model1')
# Save it to disk
path = model1.save('model1')
# Load it from disk
model2 = Model.load(path)
# Models are different objects
assert id(model1) != id(model2)
# Compare dataframes
for field in Model.get_dataframe_fields():
    df1 = getattr(model1, field)
    df2 = getattr(model2, field)

    # They are different objects
    assert id(df1) != id(df2)

    # But the same values
    assert df1.equals(df2)

# Edit the model and save
model2.name = 'model2'
model2.df_a['a'] = 1
model2.save('model2')

# Make a deep copy
model3 = model2.copy()


# %%
