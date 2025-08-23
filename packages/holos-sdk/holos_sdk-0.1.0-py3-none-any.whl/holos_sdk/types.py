from pydantic import BaseModel, Field
from typing import Optional, List, Union
import uuid


# TaskPlan schema for tracing task planning data
class TaskPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task plan")
    goal: str = Field(..., description="The goal or objective of this task plan")
    depend_plans: List[Union[str, 'TaskPlan']] = Field(default_factory=list, description="Dependent plans or sub-tasks")
    task_id: Optional[str] = Field(None, description="Associated task ID")
