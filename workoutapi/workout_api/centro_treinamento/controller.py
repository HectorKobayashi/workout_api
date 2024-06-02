from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from fastapi_pagination import LimitOffsetPage, paginate

from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependecies import DataBaseDependency
from sqlalchemy.future import select


router = APIRouter()


@router.post(
    '/', 
    summary='criar um novo centro de treinamento',
    status_code= status.HTTP_201_CREATED,    
    response_model= CentroTreinamentoOut 
)
async def post(
    db_session:DataBaseDependency
    , centro_treinamento_in: CentroTreinamentoIn = Body(...)             
)-> CentroTreinamentoOut: 
    try:
        centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())  
        centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())
        
        db_session.add(centro_treinamento_model)
        await db_session.commit()
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, 
            detail=f'Já existe um centro de treinamento cadastrada com o nome: {centro_treinamento_out.nome}.'
        )
    
    return centro_treinamento_out


@router.get(
    '/', 
    summary='consultar todas os centros de treinamento',
    status_code= status.HTTP_200_OK,    
    response_model= LimitOffsetPage[CentroTreinamentoOut] 
)
async def query(db_session:DataBaseDependency)-> LimitOffsetPage[CentroTreinamentoOut] : 
    centro_treinamentos: list[CentroTreinamentoOut] = (await db_session.execute(select(CentroTreinamentoModel))).scalars().all()
    
    return paginate(centro_treinamentos)



@router.get(
    '/id/{id}', 
    summary='consultar centro de treinamento pelo id',
    status_code= status.HTTP_200_OK,    
    response_model= CentroTreinamentoOut
)
async def query(id: UUID4, db_session:DataBaseDependency)-> CentroTreinamentoOut : 
    centro_treinamento: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()
    
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'centro de treinamento não encontrado com id: {id}')
    
    return centro_treinamento