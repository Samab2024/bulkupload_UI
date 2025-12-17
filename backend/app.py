from fastapi import FastAPI, UploadFile, File, Form
from core.bulk_runner import run_bulk_upload
import os
import uuid


app = FastAPI()


UPLOAD_DIR = "storage/uploads"
LOG_DIR = "storage/logs"


os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


@app.post("/bulk-upload")
async def bulk_upload(
region: str = Form(...),
profile: str = Form(...),
file: UploadFile = File(...)
):
run_id = str(uuid.uuid4())
csv_path = os.path.join(UPLOAD_DIR, f"{run_id}_{file.filename}")


with open(csv_path, "wb") as f:
f.write(await file.read())


result = run_bulk_upload(region, profile, csv_path, run_id, LOG_DIR)


return {"run_id": run_id, "result": result}
