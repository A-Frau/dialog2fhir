"""Pydantic schemas for a patient report extracted from a German doctor-patient dialog.

The report contains:
- patient_id: local patient ID from the hospital system (set by our code,
  not extracted by the LLM)
- chief_complaint: main reason for the visit, if stated
- diagnoses: list of known diagnoses
- home_medications: list of medications the patient takes at home
- allergies: list of allergies and intolerances
- allergy_status: whether allergies are present, none known, unknown to the
  patient, or not discussed in the dialog
- vital_signs: the most recent set of vital signs mentioned in the dialog

Every extracted item stores the exact source text from the dialog.
Diagnoses, medications and allergies also have a negation flag for
explicitly absent findings, e.g. "kein Diabetes".

See docs/schema-design.md for the FHIR CH mapping and design decisions.
"""
from typing import Literal

from pydantic import BaseModel

class ExtractedEntity(BaseModel):
    source_text: str

class NegatableEntity(ExtractedEntity):
    negated: bool = False

class ChiefComplaint(ExtractedEntity):
    complaint: str

class VitalSign(ExtractedEntity):
    type: Literal["sbp", "dbp", "spo2", "hr", "rr", "temp"]
    value: str
    unit: str

class Diagnosis(NegatableEntity):
    diagnosis: str

class Medication(NegatableEntity):
    medication: str
    dose: str | None = None
    frequency: str | None = None

class Allergy(NegatableEntity):
    substance: str
    reaction: str | None = None

class PatientReport(BaseModel):
    patient_id: str
    chief_complaint: ChiefComplaint | None = None
    vital_signs: list[VitalSign] = []
    diagnoses: list[Diagnosis] = []
    home_medications: list[Medication] = []
    allergies: list[Allergy] = []
    allergy_status: Literal["has_allergies", "nilknown", "unavailable", "notasked"] = "notasked"

if __name__ == "__main__":
    report = PatientReport(
        patient_id="TEST-001",
        chief_complaint=ChiefComplaint(
            complaint="Brustschmerzen", source_text="Brustschmerzen seit 2 Stunden"
        ),
        vital_signs=[
            VitalSign(type="hr", value="88", unit="/min", source_text="Puls 88"),
            VitalSign(type="sbp", value="120", unit="mmHg", source_text="Blutdruck 120/80"),
            VitalSign(type="dbp", value="80", unit="mmHg", source_text="Blutdruck 120/80"),
        ],
        diagnoses=[
            Diagnosis(diagnosis="Diabetes mellitus Typ 2", source_text="Diabetes seit 10 Jahren"),
            Diagnosis(diagnosis="Koronare Herzkrankheit", negated=True, source_text="keine Herzkrankheit bekannt"),
        ],
        home_medications=[
            Medication(medication="Metformin", dose="500 mg", frequency="2x täglich", source_text="Metformin 500 zweimal am Tag"),
        ],
        allergies=[
            Allergy(substance="Penicillin", reaction="Hautausschlag", source_text="allergisch auf Penicillin, gibt Ausschlag"),
        ],
        allergy_status="has_allergies",
    )
    print(report.model_dump_json(indent=2))






