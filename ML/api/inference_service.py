"""
FastAPI Web Service for ERP Document Classification.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
import os, tempfile, shutil
from api.schemas import ClassificationRequest, ClassificationResponse
from ml.inference.predict import predict_document
from ml.inference.model_loader import load_trained_artifacts
from ml.training.ensemble_model import SoftVotingEnsemble
from ml.training.calibrator_model import MultiClassCalibrator

app = FastAPI(title="ERP Document Classifier API", version="1.0.0")

# Preload artifacts at startup
artifacts = None

def get_artifacts():
    global artifacts
    if artifacts is None:
        artifacts = load_trained_artifacts()
    return artifacts

@app.on_event("startup")
def startup_event():
    try:
        get_artifacts()
    except Exception as e:
        print(f"Warning: Could not pre-load model artifacts at startup: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ERP Document Classifier", "version": "1.0.0"}

@app.post("/predict", response_model=ClassificationResponse)
def predict_path(request: ClassificationRequest):
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    
    try:
        res = predict_document(request.file_path, get_artifacts())
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/upload", response_model=ClassificationResponse)
async def predict_file(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        res = predict_document(tmp_path, get_artifacts())
        os.remove(tmp_path)
        return res
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))
