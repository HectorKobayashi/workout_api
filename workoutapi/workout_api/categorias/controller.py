from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from fastapi_pagination import LimitOffsetPage, paginate

from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.categorias.models import CategoriaModel
from workout_api.contrib.dependecies import DataBaseDependency
from sqlalchemy.future import select


router = APIRouter()


@router.post(
    '/', 
    summary='criar novo categoria',
    status_code= status.HTTP_201_CREATED,    
    response_model= CategoriaOut 
)
async def post(
    db_session:DataBaseDependency
    , categoria_in: CategoriaIn = Body(...)             
)-> CategoriaOut: 
    try:
        categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())  
        categoria_model = CategoriaModel(**categoria_out.model_dump())
        
        db_session.add(categoria_model)
        await db_session.commit()
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, 
            detail=f'Já existe uma categoria cadastrada com o nome: {categoria_out.nome}.'
        )
    
    return categoria_out


@router.get(
    '/', 
    summary='consultar todas as categorias',
    status_code= status.HTTP_200_OK,    
    response_model= LimitOffsetPage[CategoriaOut] 
)
async def query(db_session:DataBaseDependency)-> LimitOffsetPage[CategoriaOut] : 
    categorias: list[CategoriaOut] = (await db_session.execute(select(CategoriaModel))).scalars().all()
    
    return paginate(categorias)



@router.get(
    '/id/{id}', 
    summary='consultar categoria pelo id',
    status_code= status.HTTP_200_OK,    
    response_model= CategoriaOut
)
async def query(id: UUID4, db_session:DataBaseDependency)-> CategoriaOut : 
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'categoria não encontrada com id: {id}')
    
    return categoria