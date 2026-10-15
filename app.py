from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Message": "Welcome to School App! Your deployment is successful."}
