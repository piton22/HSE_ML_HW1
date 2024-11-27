
# main.py

from fastapi import FastAPI, File, UploadFile, Response
from fastapi.encoders import jsonable_encoder
from io import StringIO
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import pickle
import uvicorn
from extract_torque_rpm import extract_torque_rpm

app = FastAPI()

MODEL_NAME = "elastic_pipeline.pickle"


class Item(BaseModel):
    name: str
    year: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: str
    seats: float


class Items(BaseModel):
    objects: List[Item]


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    for col in ['mileage', 'engine', 'max_power']:
        df[col] = df[col].str.extract(r'([\d\.]+)').astype('float')

    train_torque = df['torque'].apply(extract_torque_rpm).to_list()
    df['torque'] = [x[0] for x in train_torque]
    df['rpm'] = [x[1] for x in train_torque]
    return df


def pydantic_model_to_df(model_instance):
    return pd.DataFrame([jsonable_encoder(model_instance)])


@app.post("/predict_item")
async def predict_item(item: Item) -> float:
    try:

        df_input = pydantic_model_to_df(item)

        df = preprocess_data(df_input)

        with open(MODEL_NAME, 'rb') as model_file:
            model_pipeline = pickle.load(model_file)

        preds = model_pipeline.predict(df)
        result = round(float(preds), 0)

        return result

    except Exception as e:
        print(f"Exception occurred: {e}")
        return {"error": f"An error occurred: {e}"}
    

@app.post("/predict_items")
async def predict_items(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        df = preprocess_data(df)

        with open(MODEL_NAME, 'rb') as model_file:
            model_pipeline = pickle.load(model_file)

        preds = model_pipeline.predict(df)

        df['selling_price'] = np.round(preds)
      
        csv_output = df.to_csv(index=False)
        
        return Response(content=csv_output, media_type='text/csv')
    
    except Exception as e:
        return {"error": str(e)}


