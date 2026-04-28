from pydantic import BaseModel, Field
from typing import Optional

class PolicyRecord(BaseModel):
    Topic: str
    Content: str
    PolicyType: Optional[str] = Field(default="N/A")
    AcordCode: Optional[str] = Field(default="N/A")
    CoveragePeriod: Optional[str] = Field(default="N/A")
    ProcessArea: Optional[str] = Field(default="N/A")