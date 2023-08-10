from pydantic import BaseModel, field_validator, FieldValidationInfo
from typing import Optional
from common.default_serializers import ErrorSerializer
from stt.constants import StatusTask

class GetSTTTaskSerializerRequest(BaseModel):
    uuid: str | None = None
    user_uid: str | None = None
    name: str | None = None
    status: StatusTask | None = None
    created_at_start: str | None = None
    created_at_end: str | None = None
    
    
class GetSTTTaskSerializer(BaseModel):
    uid: str
    user_uid: str 
    name: str 
    status: str
    percentage_of_transcribe: int 
    created_at: str
    audio_url: str 
    text: str

class STTTasksSerializerData(BaseModel):
    stt_tasks: Optional[list[GetSTTTaskSerializer]]

class STTTaskSerializerData(BaseModel):
    stt_task: GetSTTTaskSerializer

class GetSTTTaskSerializerResponse(BaseModel):
    data: Optional[STTTasksSerializerData] = None 
    errors: Optional[list[ErrorSerializer]] = None 
    
class STTTaskSerializerResponse(BaseModel):
    data: Optional[STTTaskSerializerData] = None 
    errors: Optional[list[ErrorSerializer]] = None 
      
class CreateSTTTaskSerializerRequest(BaseModel):
    user_uid: str | None = None 
    name: str | None = None
    audio_url: str
    
class UpdateSTTTaskSerializerRequest(BaseModel):
    name: str | None = None
    text: str | None = None
