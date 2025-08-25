from pydantic import Field, model_validator
from typing import Self
from maleo.soma.dtos.settings import Settings as BaseSettings
from maleo.soma.enums.service import ServiceKey, ServiceName


class Settings(BaseSettings):
    ICD9_DB_PATH: str = Field(
        "./vectorstores/icd9_chroma_db", description="ICD10 Database Path"
    )
    ICD10_DB_PATH: str = Field(
        "./vectorstores/icd10_chroma_db", description="ICD10 Database Path"
    )

    @model_validator(mode="after")
    def validate_service_key_name(self) -> Self:
        assert (
            self.SERVICE_KEY is ServiceKey.CDS
        ), f"'SERVICE_KEY' must be '{ServiceKey.CDS}'"
        assert (
            self.SERVICE_NAME is ServiceName.CDS
        ), f"'SERVICE_NAME' must be '{ServiceName.CDS}'"

        return self
