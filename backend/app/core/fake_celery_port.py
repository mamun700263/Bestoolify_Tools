from fastapi import FastAPI
import os

background_woker_fake = FastAPI()

@background_woker_fake.get("/")
def health():
    return {"status": "worker alive"}