from pydantic import BaseModel


class FunctionData(BaseModel):
    name: str
    arguments: list[dict[str, str]]
    description: str
    return_type: str
    sub_functions: list[str]
