from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.image_processor import process_image

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
        # processed_image_url = f"http://127.0.0.1:8000/{output_filename}"
        return {"message": "Image processed successfully", "file_path": output_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
