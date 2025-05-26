from fastapi import FastAPI
import uvicorn
from app.engine import Engine
from app.query_handlers import ISSHandler, IPHandler
from app.service import compute_loop

app = FastAPI()
engine = Engine()

@app.get("/latest")
def get_latest():
    return engine.get_latest()

def start():
    engine.register("iss", ISSHandler(), refresh_interval=5)
    engine.register("ip", IPHandler(), refresh_interval=15)
    compute_loop(engine)

if __name__ == "__main__":
    start()
    uvicorn.run(app, host="127.0.0.1", port=8000)