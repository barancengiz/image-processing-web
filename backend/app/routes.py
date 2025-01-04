from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.image_processor import process_image, convert_to_dmc

router = APIRouter()

@router.post("/process/")
async def process_image_route(file: UploadFile = File(...), operation: str = Form(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    # Save uploaded image temporarily
    contents = await file.read()
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as f:
        f.write(contents)

    # Process image
    try:
        output_filename = process_image(temp_file, operation)
        return {
            "message": "Image processed successfully", 
            "image_url": f"http://127.0.0.1:8000/{output_filename}"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Delete temporary file
    os.remove(temp_file)

@router.post("/dmc-colors/")
async def convert_to_dmc_colors_route(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    # Save uploaded image temporarily
    contents = await file.read()
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as f:
        f.write(contents)

    try:
        dmc_image_path, dmc_colors_used = convert_to_dmc(temp_file)
        return {
            "message": "Image converted to DMC colors successfully",
            "image_url": f"http://127.0.0.1:8000/{dmc_image_path}",
            "dmc_colors": dmc_colors_used,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Delete temporary file
    os.remove(temp_file)