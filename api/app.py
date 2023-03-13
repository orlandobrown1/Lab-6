from fastapi import FastAPI, Request
import motor.motor_asyncio
import pydantic
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

import  datetime 
from datetime import timedelta
import time
import pytz

import requests

app = FastAPI()

origins = [
    "https://orlando-lab6.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://orlandobrown:collegeboy@cluster0.qugvaa8.mongodb.net/?retryWrites=true&w=majority")
db = client.lab_6
states = db["state"]

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str





endpoint = f'https://ecse-sunset-api.onrender.com/api/sunset'

response = requests.get(endpoint)
data = response.json()

sunset = datetime.datetime.strptime(data['sunset'], '%Y-%m-%dT%H:%M:%S.%f').time()
now = datetime.datetime.now(pytz.timezone('Jamaica')).time()


sunset_time = datetime.datetime.strptime(str(sunset),"%H:%M:%S")
now_time = datetime.datetime.strptime(str(now),"%H:%M:%S.%f")

@app.get("/")
async def home():
    return {"LAB 6": "redirect to /api/state"}


@app.put("/api/state")
async def toggle(request: Request): 
  state = await request.json()

  state["light"] = (sunset_time<now_time)
  state["fan"] = (float(state["temperature"]) >= 28.0) 

  obj = await states.find_one({"gate":"new_update"})
  
  if obj:
    await states.update_one({"gate":"new_update"}, {"$set": state})
  else:
    await states.insert_one({**state, "gate": "new_update"})
  new_obj = await states.find_one({"gate":"new_update"}) 
  return new_obj,204



@app.get("/api/state")
async def get_state():
  state = await states.find_one({"gate": "new_update"})
  
  state["fan"] = (float(state["temperature"]) >= 28.0) 
  state["light"] = (sunset_time<now_time)

  if state == None:
    return {"fan": False, "light": False}
  return state