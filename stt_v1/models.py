from enum import StrEnum, auto

from tortoise import fields, models

class STTTask(models.Model):
    
    class StatusTask(StrEnum):
        CREATED = auto()
        FINISHED = auto()
    
    uid = fields.UUIDField(pk=True)
    user_uid = fields.UUIDField(null=True)
    name = fields.TextField(null=False)
    
    status = fields.CharField(default=StatusTask.CREATED.value, null=False, max_length=20)
    
    percentage_of_transcribe = fields.IntField(null=False, min=0, max=100)
    
    audio_url = fields.TextField(null=False)
    text = fields.TextField(null=True)
    
    created_at = fields.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'uid: {self.uid}, status {self.status}, percentage of transcribe {self.percentage_of_transcribe}'