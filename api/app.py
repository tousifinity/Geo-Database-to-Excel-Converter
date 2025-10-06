import os
import tempfile
import shutil
import zipfile
import fiona
import geopandas as gpd
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
import io
import asyncio

app = FastAPI()

# Allow all origins for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dictionary to track progress per upload_id
progress = {}


@app.post("/convert")
async def convert(file: UploadFile = File(...), upload_id: str = Form(...)):
    """
    Convert uploaded zipped .gdb folder to Excel and return as ZIP
    """
    progress[upload_id] = 0
    tmpdir = tempfile.mkdtemp()
    try:
        # Save uploaded zip
        zip_path = os.path.join(tmpdir, file.filename)
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Extract zip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Find .gdb folder
        gdb_path = None
        for root, dirs, files in os.walk(tmpdir):
            for d in dirs:
                if d.endswith(".gdb"):
                    gdb_path = os.path.join(root, d)
                    break
            if gdb_path:
                break

        if not gdb_path:
            return {"error": "No .gdb folder found in zip."}

        layers = fiona.listlayers(gdb_path)
        total_layers = len(layers)
        memory_zip = io.BytesIO()

        with zipfile.ZipFile(memory_zip, "w") as zipf:
            for i, layer_name in enumerate(layers, start=1):
                gdf = gpd.read_file(gdb_path, layer=layer_name)

                # Convert timezone-aware datetime columns to naive
                for col in gdf.columns:
                    if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                        if getattr(gdf[col].dt, "tz", None):
                            gdf[col] = gdf[col].dt.tz_localize(None)

                safe_name = "".join(
                    c if c.isalnum() else "_" for c in layer_name)
                out_path = os.path.join(tmpdir, f"{safe_name}.xlsx")
                gdf.to_excel(out_path, index=False)
                zipf.write(out_path, f"{safe_name}.xlsx")

                # Update progress, capping at 99%
                current_progress = int(i / total_layers * 100)
                progress[upload_id] = min(current_progress, 90)

                # Delay for visibility (can be removed for production speed)
                await asyncio.sleep(1.0)

        memory_zip.seek(0)
        # progress[upload_id] is NOT set to 100 here! The frontend will handle the final step.
        return StreamingResponse(
            memory_zip,
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment; filename=exports.zip"}
        )

    finally:
        # Clean up the temp directory, this will run AFTER the file is fully streamed
        shutil.rmtree(tmpdir)
        # Optionally set final progress here for robustness, although the frontend handles it
        progress[upload_id] = 100


@app.get("/progress/{upload_id}")
async def get_progress(upload_id: str):
    """
    Return current progress for a given upload_id
    """
    return {"progress": progress.get(upload_id, 0)}
