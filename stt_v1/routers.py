from fastapi import APIRouter

from stt_v1.models import STTTask
from stt_v1.serializer import (
    GetSTTTasksSerializer
)

router = APIRouter(
    prefix='/v.1',
    tags=['v.1']
)

@router.get('/')
async def get_stt_tasks(stt_task_filter_params: GetSTTTasksSerializer):
    STTTask.filter() 

@router.post('/')
async def create_stt_task():
    pass 

@router.get('/{uid}')
async def get_stt_task():
    pass 

@router.post('/{uid}')
async def update_stt_task():
    pass 

@router.delete('/{uid}')
async def delete_stt_task():
    pass 
