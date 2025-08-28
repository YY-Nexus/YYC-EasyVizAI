from dataclasses import dataclass, asdict
from typing import Any, Dict
import time, uuid
from app.core.events.publisher import publish_event

@dataclass
class ReportSectionReadyEvent:
    task_id: str
    section_id: str
    artifact_ref: str

    def to_message(self) -> Dict[str, Any]:
        return {
            "id": f"evt_{uuid.uuid4()}",
            "type": "report.section.ready",
            "ts": int(time.time()),
            "data": asdict(self),
        }

def emit_report_section_ready(task_id: str, section_id: str, artifact_ref: str):
    evt = ReportSectionReadyEvent(task_id, section_id, artifact_ref)
    publish_event(evt.to_message())