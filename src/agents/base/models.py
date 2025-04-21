from pydantic import BaseModel, Field
from typing import List


class TaskHandlerOutput(BaseModel):
    queries: List[str] = Field(description="The list of queries to be executed")
