from pydantic import BaseModel

class TPFileUploadRequest(BaseModel):
    file_path: str
    content_type: str