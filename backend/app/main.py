from fastapi import FastAPI
from app.routes import router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Image Processing App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to a list of specific origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
app.mount("/processed", StaticFiles(directory="processed"), name="processed")

@app.get("/")
def read_root():
    return {"message": "Image processing app is running."}