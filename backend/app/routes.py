from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.image_processor import process_image, convert_to_dmc
import os
router = APIRouter()

@router.post("/process/")
async def process_image_route(file: UploadFile = File(...), operation: str = Form(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    check_filesize(file)

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
    finally:
        # Delete temporary file
        os.remove(temp_file)

@router.post("/dmc-colors/")
async def convert_to_dmc_colors_route(file: UploadFile = File(...), max_colors: int = Form(...), image_width: int = Form(...), use_grid_filter: bool = Form(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    check_filesize(file)

    # Save uploaded image temporarily
    contents = await file.read()
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as f:
        f.write(contents)

    try:
        dmc_image_path, dmc_codes, hex_values, color_counts = convert_to_dmc(temp_file, n_colors=max_colors, image_width=image_width, use_grid_filter=use_grid_filter)
        return {
            "message": "Image converted to DMC colors successfully",
            "image_url": f"http://127.0.0.1:8000/{dmc_image_path}",
            "dmc_codes": dmc_codes,
            "hex_values": hex_values,
            "color_counts": color_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Delete temporary file
        os.remove(temp_file)

@router.post("/custom-dmc-colors/")
async def convert_to_custom_dmc_colors_route(file: UploadFile = File(...), dmc_colors: str = Form(...), max_colors: int = Form(...), image_width: int = Form(...), use_grid_filter: bool = Form(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    check_filesize(file)

    # Save uploaded image temporarily
    contents = await file.read()
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as f:
        f.write(contents)
    selected_dmc_colors = dmc_colors.split(",")
    print(selected_dmc_colors)
    try:
        dmc_image_path, dmc_codes, hex_values, color_counts = convert_to_dmc(temp_file, selected_dmc_colors, max_colors, image_width, use_grid_filter)
        return {
            "message": "Image converted to custom DMC colors successfully",
            "image_url": f"http://127.0.0.1:8000/{dmc_image_path}",
            "dmc_codes": dmc_codes,
            "hex_values": hex_values,
            "color_counts": color_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Delete temporary file
        os.remove(temp_file)

def check_filesize(file: UploadFile):
    if file.size > 50 * 1024 * 1024:  # 50 MB
        raise HTTPException(status_code=400, detail="File size too large. Please upload an image smaller than 50 MB.")
