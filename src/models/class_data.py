from pydantic import BaseModel, Field

class ClassData(BaseModel):
    name: str
    description: str
    inherited: list[str]
    constructor_args: list[dict[str, str]]
    public_functions: list[str]
    decorators: list[str]
