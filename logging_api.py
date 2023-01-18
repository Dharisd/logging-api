from typing import Union
import uuid
import pymongo
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List

import pydantic
from bson.objectid import ObjectId
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str
from datetime import datetime, timedelta



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*",
]



@app.get("/")
async def main():
    return {"message": "Hello World"}



USERNAME = "root"
PASSWORD = "bruh345"


client = pymongo.MongoClient(
    f"mongodb://{USERNAME}:{PASSWORD}@localhost:27017/",
)
db = client["vehicledata"]
col = db["vehiclepasses"]


class VehiclePass(BaseModel):
    type: str
    speed: float
    timestamp: float
    img_data:str




app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/store-pass/")
async def create_item(request: Request,payload: VehiclePass,status_code=200):
    return_status = {"message":"failed"}

    print(await request.body())

    try:
        payload_dict = payload.dict()
        inserted = col.insert_one(payload_dict)
    except Exception as e:
        return_status["message"] = f"{e}"
    
    if inserted:
        return_status["message"] = "success"
    
    return return_status





#return last 50 passes 
@app.get("/get-passes/")
def get_passes(request: Request, img: bool = False, orderby: str = "timestamp" ):

    outdata = {
        "message":"success",
        "data":[]
    }
    try:
        
        if orderby == "speed":
            pass_output = list(db["vehiclepasses"].find({},{"img_data":0},limit=50).sort("speed",-1))
        if img:
            pass_output = list(db["vehiclepasses"].find(limit=50).sort("timestamp",-1))
        else:
            pass_output = list(db["vehiclepasses"].find({},{"img_data":0},limit=50).sort("timestamp",-1))
        
        outdata["data"] = pass_output
    
    except Exception as e:
        outdata["message"] = f"{e}"
  
    return outdata


#return last 50 passes 
""" this is safe from filtering issues as """
@app.get("/get-stats/")
def get_passes(request: Request, time_window: int = 60):
    """
    total last hour
    total by type 
    permin graph
    """

    outdata = {
        "message":"success",
        "data": {
            "total": 0,
            "distinct_classes":0,
            "average_speed":0,
            "total_by_type":{},
            "per_min_graph":[]
        }
    }
    try:

        #get total in an hour
        last_hour_date_time = datetime.now() - timedelta(minutes= time_window)
        last_hour_date_time = last_hour_date_time.timestamp()
        current_timestamp = datetime.now().timestamp()

        t_query = col.find({"timestamp": {"$gt": last_hour_date_time}})
        total_pass_count = t_query.count()
        distinct_classes = len(t_query.distinct("type"))
        
        outdata["data"]["total"] = total_pass_count
        outdata["data"]["distinct_classes"] = distinct_classes

        #get average speed
        speed_list = []
        for p_speed in t_query:
            speed_list.append(p_speed["speed"])

        outdata["data"]["average_speed"] = sum(speed_list)/total_pass_count

        #get all unique classes of detctions
        total_by_type = {}
        for v_type in col.find().distinct("type"):
           
            t_query = col.find({
                "timestamp": {"$gt": last_hour_date_time},
                "type":v_type,
                }).count()

            total_by_type[v_type] = t_query
        
        outdata["data"]["total_by_type"] = total_by_type

        #get permin graph
        # need just a series of vlaues like 2 3 6 4
        w_value = 60 #techincally the range in seconds 
        start_ts = last_hour_date_time
        c_ts = start_ts
        windows = []
        ts_windows = []
        per_window = []
        #create the windows 
        windows.append(start_ts)

        while w_value + c_ts < current_timestamp:
            c_ts += w_value
            windows.append(c_ts)

        #filter using the windows
        for i in range(0,len(windows)):
            if i != len(windows) -1 :
                v_count = col.find(
                    {
                        "timestamp": {"$gt": windows[i],"$lte": windows[i+1]},
                    }).count()

            else:
                v_count = col.find(
                    {
                        "timestamp": {"$gt": windows[i]},
                    }).count()

            per_window.append([windows[i],v_count])

        outdata["data"]["per_min_graph"] = per_window
        

    except Exception as e:
            outdata["message"] = f"{e}"

    return outdata




    



