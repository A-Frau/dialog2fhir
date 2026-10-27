# Schema design

## Goal
Extract structured clinical information from German doctor-patient dialogs
and map it to FHIR, so it can later be sent to Swiss systems such as the
EPD (elektronisches Patientendossier).

The target is FHIR R4, following CH Core (HL7 Switzerland).

## PatientReport fields
One PatientReport is created per dialog.

| Field | Type | Filled by | FHIR CH target |
|---|---|---|---|
| `patient_id` | `str` | our code | CH Core Patient.identifier (local patient ID from the hospital system) |
| `chief_complaint` | one ChiefComplaint (optional) | LLM | CH Core Condition, referenced by Encounter.reasonReference |
| `diagnoses` | list of Diagnosis | LLM | CH Core Condition |
| `home_medications` | list of Medication | LLM | CH Core MedicationStatement |
| `allergies` | list of Allergy | LLM | CH AllergyIntolerance |
| `allergy_status` | fixed choice | LLM | IPS `no-known-allergies` / `no-allergy-info` |
| `vital_signs` | list of VitalSign (most recent set) | LLM | Observation, vital signs profile |

`patient_id` is never extracted by the LLM. A patient ID is not spoken in
the dialog, so an LLM asked for it might make one up (hallucination).

The AHV number and EPR-SPID are not used as patient_id: Swiss law
restricts both, and primary systems may not store them permanently.
The EPR-SPID is only needed when sending data to the EPD.

## Class structure
```
BaseModel
  └── ExtractedEntity        source_text
         ├── VitalSign       (no negation)
         ├── ChiefComplaint  (no negation)
         └── NegatableEntity     + negated
                ├── Diagnosis
                ├── Medication
                └── Allergy
```

Every item stores the exact `source_text` from the dialog, so each value
can be traced back to what was said.

## Negation and missing information
Negation is used where a clinician would document "no" in a history:
"Diabetes: nein", "Antikoagulation: nein", "Allergien: nein". These
pertinent negatives (relevante Negativbefunde) are clinically meaningful,
e.g. "nimmt kein Marcumar" before an intervention.

There are two levels: single **items** and the **list as a whole**.

**Items** state something about one specific finding:

| Dialog | Stored as |
|---|---|
| "allergisch auf Penicillin" | item `Allergy(substance="Penicillin")` |
| "keine Penicillin-Allergie" | item `Allergy(substance="Penicillin", negated=True)` |

**The list status** (`allergy_status`) states something about allergies in
general. These cases name no specific substance, so they are not items:

| Dialog | `allergies` | `allergy_status` | IPS code |
|---|---|---|---|
| "allergisch auf Penicillin" | 1 item | `has_allergies` | (items in list) |
| "keine Allergien bekannt" | empty | `nilknown` | `no-known-allergies` |
| "weiss nicht, ob ich Allergien habe" | empty | `unavailable` | `no-allergy-info` |
| allergies not discussed | empty | `notasked` | `no-allergy-info` |

The status values follow the FHIR List Empty Reasons codes, which keep
"unknown" and "not asked" apart. IPS merges both into `no-allergy-info`.

For diagnoses and medications, v0.1 has only the item level: a finding is
either stated (`negated = False`), explicitly absent (`negated = True`,
e.g. "kein Diabetes") or not mentioned (no item).

Two entities have no negation flag:
- **Chief complaint:** it is the reason for the visit, so it is always
  present. "Keine Brustschmerzen" is a negated symptom, not a chief complaint.
- **Vital signs:** a measurement is either stated or not mentioned.
  "Kein Fieber" is a negated symptom, not a temperature value.

## Vital signs
Only these vital signs are extracted. Each `type` value maps to a FHIR
LOINC code and UCUM unit:

| `type` | Vital sign | LOINC | Unit |
|---|---|---|---|
| `hr` | Heart rate | 8867-4 | /min |
| `rr` | Respiratory rate | 9279-1 | /min |
| `spo2` | Oxygen saturation | 2708-6 | % |
| `temp` | Body temperature | 8310-5 | Cel |
| `sbp` | Systolic blood pressure | 8480-6 | mm[Hg] |
| `dbp` | Diastolic blood pressure | 8462-4 | mm[Hg] |

Blood pressure is stored as two items, `sbp` and `dbp`, with the same
`source_text` (e.g. "Blutdruck 120/80"). This keeps every vital sign the
same shape. When converting to FHIR, both are combined into one blood
pressure Observation (LOINC 85354-9) with a systolic and a diastolic
component.

## Decisions and out of scope (v0.1)
- **FHIR R4**, to match CH Core and the EPD
- **Chief complaint instead of a symptom list:** one main reason for the
  visit, with a clear FHIR target (Condition, referenced by
  Encounter.reasonReference)
- **Patient age (out of scope for v0.1):** age is clinically important,
  especially in emergency care, but FHIR Patient only stores `birthDate`.
  An age stated in the dialog ("ich bin 72") gives no exact date of birth,
  so mapping it would mean inventing data. Options for later: store an
  estimated birth year, or record age as an Observation.
- **Out of scope:** other symptoms, and status fields for medications and
  diagnoses

## Sources
- [CH Core](https://fhir.ch/ig/ch-core/index.html)
- [CH AllergyIntolerance](https://fhir.ch/ig/ch-allergyintolerance/index.html)
- [IPS Absent and Unknown Data](https://hl7.org/fhir/uv/ips/CodeSystem-absent-unknown-uv-ips.html)
- [FHIR R4 List Empty Reasons](https://hl7.org/fhir/R4/valueset-list-empty-reason.html)
- [FHIR R4 Observation Vital Signs](https://hl7.org/fhir/R4/observation-vitalsigns.html)
- [FHIR R4 Encounter](https://hl7.org/fhir/R4/encounter.html)
- [FHIR R4 Condition](https://hl7.org/fhir/R4/condition.html)
- [FHIR R4 Patient](https://hl7.org/fhir/R4/patient.html)
- [eHealth Suisse: Identifikatoren und Nummern im EPD](https://www.e-health-suisse.ch/upload/documents/Factsheet_Identifikatoren_Nummern_EPD.pdf)