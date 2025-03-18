from pydantic import BaseModel


class RecipeBase(BaseModel):
    name: str
    cooking_time: int
    ingredients: str
    description: str


class RecipeCreateSchema(RecipeBase):
    pass


class RecipeSchema(RecipeBase):
    id: int
    views: int

    class Config:
        from_attributes = True
