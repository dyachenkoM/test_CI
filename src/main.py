from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models import RecipeModel
from src.schemas import RecipeSchema, RecipeCreateSchema
from src.database import AsyncSessionLocal, engine, Base


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/recipes/", response_model=list[RecipeSchema])
async def get_recipes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecipeModel).order_by(RecipeModel.views.desc(), RecipeModel.cooking_time).offset(skip).limit(limit))
    recipes = result.scalars().all()
    return recipes


@app.get("/recipes/{recipe_id}", response_model=RecipeSchema)
async def read_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
    db_recipe = result.scalars().first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db_recipe.views += 1
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
