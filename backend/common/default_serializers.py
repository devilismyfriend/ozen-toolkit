from pydantic import BaseModel


class ErrorSerializer(BaseModel):
    error_status: int 
    error_message: str 
