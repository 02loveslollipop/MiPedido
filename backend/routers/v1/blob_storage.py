from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from models.blob_storage import BlobStorageResponse
from database.repositories.blob_storage import BlobStorage
from utils.admin_auth import get_current_admin, AdminTokenData
from utils.admin_logger import log_admin_operation  # Import the logging utility
import traceback
from typing import List, Annotated

router = APIRouter(
    prefix="/blob",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload", response_model=BlobStorageResponse, status_code=status.HTTP_201_CREATED)
async def upload_blob_storage(file: Annotated[UploadFile, File()], current_admin: AdminTokenData = Depends(get_current_admin)):
    
    try:
        #check contetent type
        if file.content_type not in ["image/jpeg", "image/png", "application/pdf", "application/octet-stream"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only JPEG, PNG, and PDF files are allowed.")
        
        # Check file size (5MB limit)
        if file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds the limit of 5MB.")
        
        
        url = await BlobStorage.upload_blob(upload_file=file)
        
        # Log the admin operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="upload_blob",
            target_type="blob_storage",
            target_id=url,
            details={
                "file_name": file.filename,
                "file_size": file.size,
                "content_type": file.content_type,
                "status": "success"
            }
        )
            
        
        return BlobStorageResponse(
            name=file.filename,
            url=url
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        # Log the error and raise an HTTP exception
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
    
@router.delete("/delete/", status_code=status.HTTP_200_OK, response_model=dict)
async def delete_blob_storage(blob_url: str, current_admin: AdminTokenData = Depends(get_current_admin)):
    
    try:
        
        print(blob_url)
        
        if not blob_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Blob URL is required")

        if blob_url.startswith("https://") is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid blob URL format")
        
        await BlobStorage.delete_blob(blob_url=blob_url)
        
        # Log the admin operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="delete_blob",
            target_type="blob_storage",
            target_id=blob_url,
            details={
                "status": "success"
            }
        )
        
        return {"message": "Blob deleted successfully"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        # Log the error and raise an HTTP exception
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e