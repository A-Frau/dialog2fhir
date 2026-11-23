import os
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from schemas import ExtractionResult, ExtractionMetadata, PatientReport

# 1. Set up
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_PROMPT = (PROJECT_ROOT / "prompts" / "system_en.md").read_text(encoding="utf-8")
output_dir = PROJECT_ROOT / "data" / "output"
load_dotenv(PROJECT_ROOT / ".env")

if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY not found. Check your .env file.")

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
client = Anthropic()

# 2. Function: 1 dialog in, 1 PatientReport out
def extract(dialog_text: str, patient_id: str) -> PatientReport:
    # Extract clinical information from one dialog with LLM.
    response = client.messages.parse(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Extract the clinical information from this dialog:\n\n<dialog>\n{dialog_text}\n</dialog>",
            }
        ],
        output_format=ExtractionResult,
    )

    metadata = ExtractionMetadata(
        model_name=response.model,
        created_at=datetime.now(),
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        stop_reason=response.stop_reason,
    )

    return PatientReport(
        patient_id=patient_id,
        metadata=metadata,
        extraction=response.parsed_output
    )

def save_report(report: PatientReport, output_dir: Path) -> Path:
    # Save PatientReport as a JSON file and return the file path.
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"{report.patient_id}_{report.metadata.model_name}.json"
    output_file = output_dir / file_name
    output_file.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return output_file

if __name__ == "__main__":
    dialog_dir = PROJECT_ROOT / "data" / "synthetic"

    for dialog_file in sorted(dialog_dir.glob("dialog_*.txt")):
        dialog_text = dialog_file.read_text(encoding="utf-8")
        report = extract(dialog_text, patient_id=dialog_file.stem)
        saved_to = save_report(report, output_dir)
        print(f"{dialog_file.name}: {report.metadata.stop_reason} -> {saved_to.name}")