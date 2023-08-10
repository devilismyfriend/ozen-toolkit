from fastapi import APIRouter, status


from stt.models import STTTask
from stt.constants import StatusTask

from stt.serializers import (
    GetSTTTaskSerializerRequest,
    GetSTTTaskSerializerResponse,
    STTTaskSerializerResponse,
    STTTasksSerializerData,
    STTTaskSerializerData,
    CreateSTTTaskSerializerRequest,
    UpdateSTTTaskSerializerRequest
)

router = APIRouter(
    prefix='/stt/v.1',
    tags=['stt.v.1']
)

@router.get('/', 
    response_model=GetSTTTaskSerializerResponse,
    status_code=status.HTTP_200_OK
)
async def get_stt_tasks(
    uuid: str | None = None,
    user_uid: str | None = None,
    name: str | None = None,
    status: StatusTask | None = None,
    created_at_start: str | None = None,
    created_at_end: str | None = None,
    ) -> GetSTTTaskSerializerResponse:
    
    serializer = GetSTTTaskSerializerRequest(
        uuid=uuid,
        user_uid=user_uid,
        name__icontains=name,
        status=status,
        created_at__gte=created_at_start,
        created_at__lte=created_at_end
    )
    
    stt_tasks = await STTTask.filter(**serializer.dict(exclude_none=True)).values()

    return GetSTTTaskSerializerResponse(
        data=STTTasksSerializerData(stt_tasks=stt_tasks)
    )

@router.post('/',
    status_code=status.HTTP_201_CREATED,
    response_model=STTTaskSerializerResponse
)
async def create_stt_task(stt_task: CreateSTTTaskSerializerRequest) -> STTTaskSerializerResponse:
    stt_task = await STTTask.create(**stt_task.dict(exclude_none=True)) 
    return STTTaskSerializerResponse(
        data=STTTaskSerializerData(stt_task=stt_task)
    ) 

@router.post('/{uid}',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=STTTaskSerializerResponse
)
async def update_stt_task(uuid: str, stt_task: UpdateSTTTaskSerializerRequest) -> STTTaskSerializerResponse:
    stt_task = await STTTask.filter(uid=uid).update(**stt_task.dict(exclude_none=True))
    return STTTaskSerializerResponse(
        data=STTTaskSerializerData(stt_task=stt_task)
    ) 

@router.delete('/{uid}',
    response_model=STTTaskSerializerResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def delete_stt_task(uid: str) -> STTTaskSerializerResponse:
    stt_task = await STTTask.filter(uid=uid).delete()
    return STTTaskSerializerResponse(
        data=STTTaskSerializerData(stt_task=stt_task)
    )