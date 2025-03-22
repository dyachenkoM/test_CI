from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, update

from src.database import AsyncSessionLocal, Base, engine
from src.models import RecipeModel
from src.schemas import RecipeCreateSchema, RecipeSchema


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/recipes/", response_model=list[RecipeSchema])
async def get_recipes(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RecipeModel)
        .order_by(desc(RecipeModel.views), RecipeModel.cooking_time)
        .offset(skip)
        .limit(limit)
    )
    recipes = result.scalars().all()
    return recipes


@app.get("/recipes/{recipe_id}", response_model=RecipeSchema)
async def read_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(
        update(RecipeModel)
        .where(RecipeModel.id == recipe_id)
        .values(views=RecipeModel.views + 1)
    )

    result = await db.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
    db_recipe = result.scalars().first()

    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe


@app.post("/recipes/", response_model=RecipeSchema)
async def create_recipe(recipe: RecipeCreateSchema, db: AsyncSession = Depends(get_db)):
    db_recipe = RecipeModel(**recipe.dict())
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe
