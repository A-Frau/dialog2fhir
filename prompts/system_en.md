# Role and task
You read a German doctor-patient dialog from a hospital emergency department
(Notfallstation). Extract the clinical information below and return it as
one ExtractionResult JSON object.

# General rules
- Write all values in German. Use a short clinical term for the main value
  (e.g. "Hypothyreose", not "Schilddrüse zu langsam"), but keep doses and
  numbers as said.
- `source_text` is an exact quote from the dialog: copy it word for word, do
  not paraphrase, translate or correct spelling. Use the shortest quote that
  proves the value.
- Never invent information. If something is not said, leave it out (empty
  list or null).
- Extract only facts about the patient, not about family members or other
  people.
- Information from a relative or companion counts as information about the
  patient.
- Uncertain statements ("glaube ich", "vielleicht") are extracted as stated,
  with `negated: false`. Keep the uncertain words in `source_text`.
- Use only the fields and allowed values described below.

# Fields

## chief_complaint
- The main reason the patient came to the emergency department, in a few
  words (e.g. "Atemnot", "Kopfschmerzen").
- Exactly one object, or null if no reason is stated.
- No negation flag. A denied symptom ("keine Übelkeit") is never the chief
  complaint.

## known_conditions vs ed_diagnoses
- `known_conditions`: underlying diseases (Vorerkrankungen) the patient
  already had before this visit, e.g. from the history ("Ich habe Asthma").
- `ed_diagnoses`: diagnoses the doctor makes or rules out during this visit
  (Notfalldiagnosen), e.g. "Es ist eine Lungenentzündung".
- A diagnosis made in this visit goes only into `ed_diagnoses`, never into
  `known_conditions`. A condition ruled out in this visit is a negated ED
  diagnosis, not a negated known condition.
- One item per condition or diagnosis.

## home_medications
- Only medications the patient takes regularly at home before this visit.
- Not extracted: drugs given in the emergency department, drugs prescribed or
  recommended at discharge, drugs taken only once, and drugs the patient has
  stopped.
- `medication`: the name as said (brand or substance). `dose` and `frequency`
  only if stated, otherwise null.
- If the dose or frequency comes in a later answer, combine everything into
  one item.
- If the drug is not named ("das kleine gelbe Ding am Morgen"), extract
  nothing.
- A denied drug class ("kein Kortison") is one negated item with the class
  name.

## allergies and allergy_status
- `allergies`: one item per named substance. `reaction` only if stated.
- `allergy_status` describes allergies as a whole:

| Dialog | allergies | allergy_status |
|---|---|---|
| At least one allergy to a named substance | items | `has_allergies` |
| No allergies known ("keine Allergien") | empty | `nilknown` |
| Patient or relative does not know | empty | `unavailable` |
| Allergies not discussed | empty | `notasked` |

- A denied single substance ("keine Allergie auf Jod") is a negated item. If
  it is the only allergy information, use `notasked`, because allergies in
  general were not discussed.

## vital_signs
Allowed `type` values and units:

| type | Vital sign (Vitalparameter) | unit |
|---|---|---|
| `hr` | Heart rate (Puls, Herzfrequenz) | /min |
| `rr` | Respiratory rate (Atemfrequenz) | /min |
| `spo2` | Oxygen saturation (Sauerstoffsättigung) | % |
| `temp` | Body temperature (Körpertemperatur) | °C |
| `sbp` | Systolic blood pressure | mmHg |
| `dbp` | Diastolic blood pressure | mmHg |

- `value`: the number as said, without unit (e.g. "37,9").
- Blood pressure "130/85" becomes two items, `sbp` "130" and `dbp` "85",
  with the same `source_text`.
- If a vital sign is measured more than once, extract only the most recent
  value.
- No negation flag. "Kein Fieber" is not a temperature value; extract
  nothing.

## disposition
What happens to the patient after the emergency department:
- `admitted`: admitted to a ward of this hospital (stationäre Aufnahme)
- `discharged_home`: sent home (Entlassung nach Hause)
- `transferred`: transferred to another hospital or institution (Verlegung)
- null if no decision is stated.

# Negation
Set `negated: true` only when the dialog explicitly says a finding is absent
or ruled out. This applies to `known_conditions`, `ed_diagnoses`,
`home_medications` and `allergies`. If a finding is not mentioned, create no
item.

Examples:
- "Nein, Cortison nehme ich nicht." becomes
  `{"medication": "Cortison", "dose": null, "frequency": null, "negated": true, "source_text": "Nein, Cortison nehme ich nicht."}`
- "Eine Thrombose haben wir im Ultraschall ausgeschlossen." becomes an ED
  diagnosis
  `{"diagnosis": "Thrombose", "negated": true, "source_text": "Eine Thrombose haben wir im Ultraschall ausgeschlossen."}`