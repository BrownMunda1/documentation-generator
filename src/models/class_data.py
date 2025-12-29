from pydantic import BaseModel


class ClassData(BaseModel):
    name: str
    description: str
    inherited: list[str]
    constructor_args: list[dict[str, str]]
    public_functions: list[str]
    decorators: list[str]
