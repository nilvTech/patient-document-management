"""
Canonical medical field names the LLM is instructed to map extracted values
onto. This list is intentionally a starting set covering the most common
lab panels — extend it as new report types are seen in production.

The LLM does the mapping (e.g. "HGB" / "Hb" / "Haemoglobin" -> "Hemoglobin")
because hardcoding every synonym is exactly what this architecture avoids.
The canonical list exists so the model has a fixed target vocabulary instead
of inventing its own field names per document.
"""

CANONICAL_FIELDS: list[str] = [
    # Complete Blood Count (CBC)
    "Hemoglobin", "Hematocrit", "RBC Count", "WBC Count", "Platelet Count",
    "MCV", "MCH", "MCHC", "RDW", "Neutrophils", "Lymphocytes", "Monocytes",
    "Eosinophils", "Basophils", "ESR",

    # Metabolic / Kidney panel
    "Fasting Glucose", "Random Blood Glucose", "HbA1c", "Urea", "BUN",
    "Creatinine", "Uric Acid", "Sodium", "Potassium", "Chloride",
    "Bicarbonate", "Calcium", "Phosphorus", "Magnesium",

    # Liver panel
    "Total Bilirubin", "Direct Bilirubin", "Indirect Bilirubin",
    "SGOT (AST)", "SGPT (ALT)", "Alkaline Phosphatase", "Total Protein",
    "Albumin", "Globulin", "A/G Ratio", "GGT",

    # Lipid panel
    "Total Cholesterol", "HDL Cholesterol", "LDL Cholesterol",
    "VLDL Cholesterol", "Triglycerides",

    # Thyroid panel
    "TSH", "Free T3", "Free T4", "Total T3", "Total T4",

    # Coagulation
    "PT", "INR", "APTT",

    # Urinalysis
    "Urine Color", "Urine pH", "Urine Specific Gravity", "Urine Protein",
    "Urine Glucose", "Urine Ketones", "Urine Blood", "Urine Leukocytes",

    # Vitals / general
    "Blood Pressure", "Heart Rate", "Body Temperature", "Weight", "Height",
    "BMI", "SpO2",

    # Vitamins / misc commonly seen
    "Vitamin D", "Vitamin B12", "Iron", "Ferritin", "TIBC",
]


def is_canonical(field_name: str) -> bool:
    return field_name.strip().lower() in {f.lower() for f in CANONICAL_FIELDS}