"""Lightweight ontology loading and validation."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from autodev_rag.config import SCHEMA_PATH


class EntitySchema(BaseModel):
    description: str = ""
    fields: list[str] = Field(default_factory=list)


class RelationSchema(BaseModel):
    name: str
    source: str
    target: str


class Ontology(BaseModel):
    entities: dict[str, EntitySchema] = Field(default_factory=dict)
    relations: list[RelationSchema] = Field(default_factory=list)

    def validate_entity_type(self, entity_type: str) -> bool:
        return entity_type in self.entities

    def get_relation_names(self) -> list[str]:
        return [relation.name for relation in self.relations]


def load_ontology(path: str | Path = SCHEMA_PATH) -> Ontology:
    path = Path(path)
    with path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}
    return Ontology.model_validate(raw)


def validate_entity_type(entity_type: str, path: str | Path = SCHEMA_PATH) -> bool:
    return load_ontology(path).validate_entity_type(entity_type)


def get_relation_names(path: str | Path = SCHEMA_PATH) -> list[str]:
    return load_ontology(path).get_relation_names()

