## Image processing app
A small web application that allows users to upload images and perform several image processing operations based on their selection.

Usage:
* Upload image
* Select operation
* Click the process button
* And, voila! Your image should be ready.

### Setup instructions
0. Install docker, and node.js
1. Clone the repository
2. Start dockers in both backend and frontend folders
``` 
cd backend
docker-compose up
```
``` 
cd frontend
docker-compose up
```

### Software stack:

#### Frontend:
* Vue.js: Framework for building the web interface (React somehow gives errors while creating new projects)
* Axios: HTTP client for sending requests to the backend
* Docker: Containerize the application

#### Backend:
* FastAPI: Framework for building the backend API
* OpenCV: Image processing
* Docker: Containerize the application

### API Endpoints
#### POST /process/
* Description: Uploads an image file and applies the selected operation.
* Request:
    * file: The image file to process (multipart form-data).
    * operation: The operation to perform (e.g., resize, grayscale).
* Response:
    ```
    {
        "message": "Image processed successfully",
        "image_url": "<url>/processed/<filename>"
    }
    ```
#### POST /dmc-colors/
* Description: Recolors given image using DMC colors
* Request:
    * file: The image file to process (multipart form-data).
* Response:
    ```
    {
        "message": "Image processed successfully",
        "image_url": "<url>/processed/<filename>",
        "dmc_codes": "list[text]",  // unique dmc color codes
        "hex_values": "list[text]"  // hex values of used colors
    }
    ```