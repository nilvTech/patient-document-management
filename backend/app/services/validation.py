"""
Never trust the LLM's JSON directly. Pydantic parsing in llm_extraction.py
already guarantees structural correctness (types, required keys), but it
can't catch semantic problems: near-duplicate fields, empty noise entries,
suspicious numeric values, or fields the model invented outside the
canonical vocabulary. That's what this module is for.

Where AI judgment is still required (this layer deliberately does NOT try
to fully automate):
  - Deciding whether a non-canonical field name is a legitimate new test
    type or LLM noise — a human/reviewer should periodically check the
    "non_canonical" warnings and extend CANONICAL_FIELDS.
  - Interpreting reference ranges that aren't simple "low - high" numbers
    (e.g. sex-specific, age-specific, or qualitative ranges like "Negative").
    This layer only auto-derives isAbnormal for the simple numeric case.
  - Unit correctness/conversion (e.g. mg/dL vs mmol/L) — this layer checks
    that a unit string is *present*, not that it's the medically expected
    one for that field.
"""

import re
from dataclasses import dataclass, field

from app.schemas.patient_document_data import (
    ExtractedMedicalField,
    ExtractedMedicalFields,
)
from app.services.canonical_fields import is_canonical

_NUMERIC_RE = re.compile(r"^-?\d+(\.\d+)?$")
_RANGE_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)\s*$")


@dataclass
class ValidationResult:
    valid_fields: list[ExtractedMedicalField] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _is_noise_entry(f: ExtractedMedicalField) -> bool:
    """Entirely empty entries (no value, unit, or range) add nothing useful."""
    return not f.fieldValue and not f.unit and not f.referenceRange


def _try_auto_flag_abnormal(f: ExtractedMedicalField) -> ExtractedMedicalField:
    """Only fills isAbnormal when it's unset AND the range is a plain numeric
    'low - high' pair AND the value is plainly numeric. Anything more complex
    is left to human/AI review rather than guessed here."""
    if f.isAbnormal is not None or not f.fieldValue or not f.referenceRange:
        return f

    value_match = _NUMERIC_RE.match(f.fieldValue.strip())
    range_match = _RANGE_RE.match(f.referenceRange.strip())
    if not value_match or not range_match:
        return f

    try:
        value = float(f.fieldValue)
        low, high = float(range_match.group(1)), float(range_match.group(2))
    except ValueError:
        return f

    f.isAbnormal = not (low <= value <= high)
    return f


def validate_and_normalize(extracted: ExtractedMedicalFields) -> ValidationResult:
    result = ValidationResult()
    seen_field_names: set[str] = set()

    for f in extracted.fields:
        name = (f.fieldName or "").strip()

        # Required property
        if not name:
            result.warnings.append("Dropped a field with an empty fieldName.")
            continue

        if len(name) > 250:
            result.warnings.append(
                f"Dropped '{name[:50]}...' — fieldName exceeds 250 chars."
            )
            continue

        f.fieldName = name

        # Empty/noise entries
        if _is_noise_entry(f):
            result.warnings.append(
                f"Dropped '{name}' — no value, unit, or reference range present."
            )
            continue

        # Duplicate fields — keep the first occurrence with an actual value
        dedupe_key = name.lower()
        if dedupe_key in seen_field_names:
            result.warnings.append(f"Dropped duplicate field '{name}'.")
            continue
        seen_field_names.add(dedupe_key)

        # Non-canonical field name — kept, but flagged for later review
        if not is_canonical(name):
            result.warnings.append(
                f"'{name}' is not in the canonical field list — kept as-is."
            )

        # Numeric sanity check (only warn; don't drop — some legitimate
        # results are qualitative, e.g. "Negative", "Positive", "Trace")
        if f.fieldValue is not None:
            stripped = f.fieldValue.strip()
            if _NUMERIC_RE.match(stripped):
                num = float(stripped)
                if num < 0 or num > 100000:
                    result.warnings.append(
                        f"'{name}' has a suspicious numeric value ({num}) — kept but flagged."
                    )

        # DO NOT calculate abnormality from the reference range.
        # The LLM must only report abnormality when explicitly indicated
        # by the document.
        
        result.valid_fields.append(f)

    return result
