from fastapi import UploadFile
from fastapi import HTTPException
from random import randbytes
import vercel_blob

class BlobStorage:
    
    @staticmethod
    async def upload_blob(upload_file: UploadFile, blob_name: str = None) -> str:
        try:
            if blob_name is None:
                blob_name = randbytes(16).hex() + "_" + upload_file.filename
            
            res = vercel_blob.put(blob_name, upload_file.file.read())
            
            url = res["url"]
            #url = res["downloadUrl"]
            if url is None:
                raise Exception("Blob storage upload failed")
            return url
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    async def delete_blob(blob_url: str) -> bool:
        try:
            vercel_blob.delete([blob_url])
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
        