from pydantic import BaseModel

class GetSTTTasksSerializer(BaseModel):
    uid: str 
    name: str | None 