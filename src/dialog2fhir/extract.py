from datetime import datetime
import os

from schemas import ExtractionResult, ExtractionMetadata, PatientReport
from dotenv import load_dotenv
from anthropic import Anthropic
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_PROMPT = (PROJECT_ROOT / "prompts" / "system_en.md").read_text(encoding="utf-8")
dialog = (PROJECT_ROOT / "data" / "synthetic" / "dialog_001.txt").read_text(encoding="utf-8")
load_dotenv(PROJECT_ROOT / ".env")
if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY not found. Check your .env file.")
client = Anthropic()

response = client.messages.parse(
    model=os.getenv("ANTHROPIC_MODEL"),
    max_tokens = 4096,
    system = SYSTEM_PROMPT,
    messages = [
        {
            "role" : "user",
            "content" : f"Extract the clinical information from this dialog:\n\n<dialog>\n{dialog}\n</dialog>",
        }
    ],
    output_format=ExtractionResult,
)

metadata = ExtractionMetadata(
    model_name = response.model,
    created_at = datetime.now(),
    input_tokens = response.usage.input_tokens,
    output_tokens = response.usage.output_tokens,
    stop_reason = response.stop_reason,
)

patient_1 = PatientReport(
    patient_id = "TEST-001",
    metadata = metadata,
    extraction = response.parsed_output
)

print(patient_1.model_dump_json(indent=2))