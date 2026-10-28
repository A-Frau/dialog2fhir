# Expected extraction

Answer key for the synthetic dialogs, based on docs/schema-design.md.
The ED diagnosis and disposition are not part of the v0.1 schema. They
are listed so they can be checked later, and so we can verify that they
do NOT appear in `diagnoses`.

## dialog_001: typical case

| Field | Expected |
|---|---|
| chief_complaint | Druck auf der Brust |
| diagnoses | Diabetes mellitus, arterielle Hypertonie |
| home_medications | Metformin 500 mg 2x täglich; Concor 5 mg morgens; Aspirin Cardio 100 mg 1x täglich |
| allergies | Penicillin (Ausschlag) |
| allergy_status | `has_allergies` |
| vital_signs | sbp 160, dbp 95, hr 92, spo2 96, temp 36,8, rr 18 |
| ED diagnosis (not in v0.1) | NSTEMI |
| Disposition (not in v0.1) | admitted, cardiology |

## dialog_002: negations, sent home

| Field | Expected |
|---|---|
| chief_complaint | Bauchschmerzen rechts unten |
| diagnoses | Diabetes (negated); Herzkrankheit (negated) |
| home_medications | orale Kontrazeption; Antikoagulation (negated) |
| allergies | (empty) |
| allergy_status | `nilknown` |
| vital_signs | temp 38,4, hr 104, sbp 125, dbp 80, spo2 98 |
| ED diagnosis (not in v0.1) | Gastroenteritis; Appendizitis ruled out |
| Disposition (not in v0.1) | discharged home |

## dialog_003: unclear information, admitted

| Field | Expected |
|---|---|
| chief_complaint | Sturz |
| diagnoses | Herzinsuffizienz; Vorhofflimmern (uncertain) |
| home_medications | (none extractable) |
| allergies | (empty) |
| allergy_status | `unavailable` |
| vital_signs | most recent set only: sbp 110, dbp 70, hr 52 |
| ED diagnosis (not in v0.1) | Bradykardie; Fraktur ruled out |
| Disposition (not in v0.1) | admitted, medicine (monitoring) |

## Traps

| Dialog | Trap | Correct handling |
|---|---|---|
| 001 | Aspirin Cardio dose given in a later answer | Combine into one medication |
| 001 | NSTEMI is the ED diagnosis | Must NOT be in `diagnoses` |
| 001 | Heparin given in the ED | Not a home medication |
| 002 | "keine Blutverdünner" is a drug class | Negated medication; content unclear |
| 002 | Dafalgan taken once / recommended at discharge | Not a home medication |
| 002 | "Blinddarmentzündung ausgeschlossen" | Ruled-out ED diagnosis, not a negated Vorerkrankung |
| 003 | "eine weisse Tablette" without a name | Extract nothing, do not invent a drug |
| 003 | Marcoumar stopped | Not a current medication (schema gap) |
| 003 | "Vorhofflimmern, glaube ich" | Uncertain (schema gap) |
| 003 | Information comes from the daughter | Informant not recorded (schema gap) |
| 003 | Two sets of vital signs | Only the most recent set |
| 003 | Bradykardie, no fracture | ED findings, must NOT be in `diagnoses` |