from typing import Optional, List
from sqlmodel import Field, SQLModel
from datetime import datetime
import json

class ResearchSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task: str
    report_content: str  # The full markdown report
    notes_json: str      # JSON string of sources/notes
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def notes(self):
        if not self.notes_json:
            return []
        try:
            return json.loads(self.notes_json)
        except:
            return []
