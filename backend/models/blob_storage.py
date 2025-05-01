from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class BlobStorageResponse(BaseModel):
    name: str = Field(..., description="The name of the blob storage entry.")
    url: str = Field(..., description="The URL of the blob storage entry.")

    class Config:
        model_config = ConfigDict(from_attributes=True)

