"""Schémas Pydantic — reflètent exactement le JSON attendu par le frontend Angular."""
from pydantic import BaseModel, ConfigDict, Field


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str


class LoginOut(BaseModel):
    token: str
    user: UserOut


class ImageOut(BaseModel):
    # Le frontend lit image.id, image.path et image.isAnnotated (camelCase).
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    path: str
    isAnnotated: bool = Field(validation_alias="is_annotated", serialization_alias="isAnnotated")


class BatchImagesOut(BaseModel):
    current_batch: int
    total_batches: int
    images: list[ImageOut]


class UndefinedImagesOut(BaseModel):
    images: list[ImageOut]


class AnnotationIn(BaseModel):
    image_id: int
    grade: str
    stade: str


class BatchAnnotationsIn(BaseModel):
    annotations: list[AnnotationIn]


class AnnotationUpdateIn(BaseModel):
    grade: str
    stade: str


class AnnotationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    grade: str
    stade: str
    user: UserOut
    image: ImageOut


class BatchAnnotationsOut(BaseModel):
    annotations: list[AnnotationOut]
