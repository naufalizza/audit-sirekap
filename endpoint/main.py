import sys
invalid_data_folder_path = sys.argv[1]

from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
import os
import re
import uvicorn
from pydantic import BaseModel

integer_compiler = re.compile(r"\d+")
app = FastAPI()

class NonTpsInvalidInfoSummary(BaseModel):
    count: int
    reason: dict[str, int]

class TpsInvalidInfo(BaseModel):
    timestamp: int
    endpoint: str
    sirekap_endpoint: str
    reason: list[str]

class NonTpsInvalidInfo(BaseModel):
    timestamp: int
    summary: NonTpsInvalidInfoSummary
    data: dict[str, int]

class ErrorMessage(BaseModel):
    message: str

def get_400_response():
    return JSONResponse(status_code=400, content={"message": "Bad request"})

def get_404_response():
    return JSONResponse(status_code=404, content={"message": f"Data not found"})

@app.get("/invalid-endpoints", response_model=NonTpsInvalidInfo)
def get_indonesia_invalid_info():
    with open(f"{invalid_data_folder_path}/all.json") as fp:
        data = fp.read()
    return Response(content=data, media_type="application/json")

@app.get("/invalid-endpoints/{prov_id}", response_model=NonTpsInvalidInfo, responses={400: {"model": ErrorMessage}, 404: {"model": ErrorMessage}})
def get_provinsi_invalid_info(prov_id):
    try:
        raise_value_error_if_not_integer(prov_id)
    except ValueError:
        return get_400_response()

    path = f"{invalid_data_folder_path}/{prov_id}/all.json"
    if not os.path.isfile(path):
        return get_404_response()

    with open(path) as fp:
        data = fp.read()
    
    return Response(content=data, media_type="application/json")

@app.get("/invalid-endpoints/{prov_id}/{kota_id}", response_model=NonTpsInvalidInfo, responses={400: {"model": ErrorMessage}, 404: {"model": ErrorMessage}})
def get_kota_invalid_info(prov_id, kota_id):
    try:
        raise_value_error_if_not_integer(prov_id)
        raise_value_error_if_not_integer(kota_id)
    except ValueError:
        return get_400_response()
    
    path = f"{invalid_data_folder_path}/{prov_id}/{kota_id}/all.json"
    if not os.path.isfile(path):
        return get_404_response()

    with open(path) as fp:
        data = fp.read()
    
    return Response(content=data, media_type="application/json")

@app.get("/invalid-endpoints/{prov_id}/{kota_id}/{kec_id}", response_model=NonTpsInvalidInfo, responses={400: {"model": ErrorMessage}, 404: {"model": ErrorMessage}})
def get_kecamatan_invalid_info(prov_id, kota_id, kec_id):
    try:
        raise_value_error_if_not_integer(prov_id)
        raise_value_error_if_not_integer(kota_id)
        raise_value_error_if_not_integer(kec_id)
    except ValueError:
        return get_400_response()

    path = f"{invalid_data_folder_path}/{prov_id}/{kota_id}/{kec_id}/all.json"
    if not os.path.isfile(path):
        return get_404_response()

    with open(path) as fp:
        data = fp.read()
    
    return Response(content=data, media_type="application/json")

@app.get("/invalid-endpoints/{prov_id}/{kota_id}/{kec_id}/{kel_id}", response_model=NonTpsInvalidInfo, responses={400: {"model": ErrorMessage}, 404: {"model": ErrorMessage}})
def get_kelurahan_invalid_info(prov_id, kota_id, kec_id, kel_id):
    try:
        raise_value_error_if_not_integer(prov_id)
        raise_value_error_if_not_integer(kota_id)
        raise_value_error_if_not_integer(kec_id)
        raise_value_error_if_not_integer(kel_id)
    except ValueError:
        return get_400_response()

    path = f"{invalid_data_folder_path}/{prov_id}/{kota_id}/{kec_id}/{kel_id}/all.json"
    if not os.path.isfile(path):
        return get_404_response()

    with open(path) as fp:
        data = fp.read()
    
    return Response(content=data, media_type="application/json")

@app.get("/invalid-endpoints/{prov_id}/{kota_id}/{kec_id}/{kel_id}/{tps_id}", response_model=TpsInvalidInfo, responses={400: {"model": ErrorMessage}, 404: {"model": ErrorMessage}})
def get_tps_invalid_info(prov_id, kota_id, kec_id, kel_id, tps_id):
    try:
        raise_value_error_if_not_integer(prov_id)
        raise_value_error_if_not_integer(kota_id)
        raise_value_error_if_not_integer(kec_id)
        raise_value_error_if_not_integer(kel_id)
        raise_value_error_if_not_integer(tps_id)
    except ValueError:
        return get_400_response()

    path = f"{invalid_data_folder_path}/{prov_id}/{kota_id}/{kec_id}/{kel_id}/{tps_id}.json"
    if not os.path.isfile(path):
        return get_404_response()

    with open(path) as fp:
        data = fp.read()
    
    return Response(content=data, media_type="application/json")

def raise_value_error_if_not_integer(prov_id):
    if not integer_compiler.match(prov_id):
        raise ValueError

uvicorn.run(app)
