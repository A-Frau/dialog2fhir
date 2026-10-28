# Synthetic dialogs

All dialogs in this folder are **fully synthetic**. They do not contain
real patient data. Names, people and cases are invented, and any
resemblance to real persons is coincidental.

## How they were created
The dialogs were drafted with AI assistance (Claude, Anthropic) and
reviewed and edited by a licensed physician for clinical plausibility.

## Setting and language
- Setting: hospital emergency department (Notfallstation) in Switzerland
- Language: Standard German with Swiss vocabulary and spelling
  (e.g. Spital, Hausarzt, no "ß"), as produced when Swiss German speech
  is transcribed by an ASR system
- Colloquial patient phrasing is used on purpose (e.g. "Zucker",
  "Blutverdünner")

## Files
| File | Content |
|---|---|
| `dialog_001.txt` | Typical case, admitted |
| `dialog_002.txt` | Negations and "no known", sent home |
| `dialog_003.txt` | Unclear and missing information, admitted |
| `expected_notes.md` | Expected extraction and deliberate traps |

## Intended use
For developing and testing the extraction pipeline only. Not for
clinical use.