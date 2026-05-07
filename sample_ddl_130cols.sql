-- ============================================================
-- Sample DDL: SUBJECT_STAGING (Clinical Trial Raw Layer)
-- 130 columns · 1 PK (_PK suffix) · 129 measured columns
-- NOTE: *_id columns intentionally renamed to avoid false PK detection
-- Use this to test the Column Volatility Analyzer
-- ============================================================

CREATE TABLE clinical.SUBJECT_STAGING (

    -- ── Primary Key ──────────────────────────────────────────
    SUBJECT_PK                  STRING        NOT NULL,   -- 1  · Detected as PK (_PK suffix)

    -- ── Study & Site identifiers ─────────────────────────────
    study_code                  STRING,                   -- 2
    protocol_number             STRING,                   -- 3
    site_code                   STRING,                   -- 4
    site_country                STRING,                   -- 5
    site_region                 STRING,                   -- 6
    investigator_code           STRING,                   -- 7
    arm_code                    STRING,                   -- 8
    cohort_label                STRING,                   -- 9
    randomization_flag          STRING,                   -- 10

    -- ── Subject demographics ─────────────────────────────────
    year_of_birth               INTEGER,                  -- 11
    age_at_consent              INTEGER,                  -- 12
    sex                         STRING,                   -- 13
    gender_identity             STRING,                   -- 14
    race                        STRING,                   -- 15
    ethnicity                   STRING,                   -- 16
    nationality                 STRING,                   -- 17
    bmi_baseline                FLOAT,                    -- 18
    height_cm                   FLOAT,                    -- 19
    weight_kg_baseline          FLOAT,                    -- 20

    -- ── Consent & enrollment ─────────────────────────────────
    consent_date                DATE,                     -- 21
    consent_version             STRING,                   -- 22
    enrollment_date             DATE,                     -- 23
    randomization_date          DATE,                     -- 24
    first_dose_date             DATE,                     -- 25
    last_dose_date              DATE,                     -- 26
    study_completion_date       DATE,                     -- 27
    withdrawal_date             DATE,                     -- 28
    withdrawal_reason           STRING,                   -- 29
    early_termination_flag      STRING,                   -- 30

    -- ── Subject status ───────────────────────────────────────
    subject_status              STRING,                   -- 31
    disposition_code            STRING,                   -- 32
    screen_failure_reason       STRING,                   -- 33
    protocol_deviation_flag     STRING,                   -- 34
    protocol_deviation_category STRING,                   -- 35

    -- ── Vital signs (latest values) ──────────────────────────
    systolic_bp_mmhg            FLOAT,                    -- 36
    diastolic_bp_mmhg           FLOAT,                    -- 37
    heart_rate_bpm              FLOAT,                    -- 38
    respiratory_rate            FLOAT,                    -- 39
    body_temp_celsius           FLOAT,                    -- 40
    oxygen_saturation_pct       FLOAT,                    -- 41
    weight_kg_latest            FLOAT,                    -- 42
    bmi_latest                  FLOAT,                    -- 43

    -- ── Lab results ──────────────────────────────────────────
    hba1c_pct                   FLOAT,                    -- 44
    fasting_glucose_mmol        FLOAT,                    -- 45
    creatinine_umol             FLOAT,                    -- 46
    egfr_ml_min                 FLOAT,                    -- 47
    alt_u_l                     FLOAT,                    -- 48
    ast_u_l                     FLOAT,                    -- 49
    alkaline_phosphatase_u_l    FLOAT,                    -- 50
    bilirubin_total_umol        FLOAT,                    -- 51
    albumin_g_l                 FLOAT,                    -- 52
    haemoglobin_g_dl            FLOAT,                    -- 53
    wbc_10e9_l                  FLOAT,                    -- 54
    platelet_count_10e9_l       FLOAT,                    -- 55
    sodium_mmol_l               FLOAT,                    -- 56
    potassium_mmol_l            FLOAT,                    -- 57
    cholesterol_total_mmol      FLOAT,                    -- 58
    ldl_mmol                    FLOAT,                    -- 59
    hdl_mmol                    FLOAT,                    -- 60
    triglycerides_mmol          FLOAT,                    -- 61
    nt_probnp_pg_ml             FLOAT,                    -- 62
    troponin_t_ng_l             FLOAT,                    -- 63
    crp_mg_l                    FLOAT,                    -- 64
    ferritin_ug_l               FLOAT,                    -- 65

    -- ── Diagnosis & medical history ──────────────────────────
    primary_diagnosis_code      STRING,                   -- 66
    primary_diagnosis_date      DATE,                     -- 67
    disease_severity            STRING,                   -- 68
    disease_duration_months     INTEGER,                  -- 69
    comorbidity_diabetes_flag   STRING,                   -- 70
    comorbidity_hypertension_flag STRING,                 -- 71
    comorbidity_ckd_flag        STRING,                   -- 72
    comorbidity_hf_flag         STRING,                   -- 73
    comorbidity_copd_flag       STRING,                   -- 74
    comorbidity_cancer_flag     STRING,                   -- 75
    smoking_status              STRING,                   -- 76
    alcohol_use_status          STRING,                   -- 77
    prior_hospitalization_flag  STRING,                   -- 78
    prior_surgery_flag          STRING,                   -- 79
    prior_surgery_type          STRING,                   -- 80

    -- ── Concomitant medications ──────────────────────────────
    conmed_metformin_flag       STRING,                   -- 81
    conmed_insulin_flag         STRING,                   -- 82
    conmed_statin_flag          STRING,                   -- 83
    conmed_ace_inhibitor_flag   STRING,                   -- 84
    conmed_arb_flag             STRING,                   -- 85
    conmed_beta_blocker_flag    STRING,                   -- 86
    conmed_diuretic_flag        STRING,                   -- 87
    conmed_aspirin_flag         STRING,                   -- 88
    conmed_anticoagulant_flag   STRING,                   -- 89
    conmed_corticosteroid_flag  STRING,                   -- 90

    -- ── Efficacy endpoints ───────────────────────────────────
    primary_endpoint_value      FLOAT,                    -- 91
    primary_endpoint_date       DATE,                     -- 92
    secondary_endpoint_1_value  FLOAT,                    -- 93
    secondary_endpoint_2_value  FLOAT,                    -- 94
    secondary_endpoint_3_value  FLOAT,                    -- 95
    response_category           STRING,                   -- 96
    responder_flag              STRING,                   -- 97
    time_to_response_days       INTEGER,                  -- 98
    progression_free_days       INTEGER,                  -- 99
    overall_survival_days       INTEGER,                  -- 100

    -- ── Adverse events summary ───────────────────────────────
    ae_count_total              INTEGER,                  -- 101
    ae_count_grade3_plus        INTEGER,                  -- 102
    sae_count                   INTEGER,                  -- 103
    ae_leading_to_dc_flag       STRING,                   -- 104
    ae_leading_to_dc_term       STRING,                   -- 105
    dli_flag                    STRING,                   -- 106

    -- ── Dosing & exposure ────────────────────────────────────
    total_doses_administered    INTEGER,                  -- 107
    dose_reductions_count       INTEGER,                  -- 108
    dose_interruptions_count    INTEGER,                  -- 109
    cumulative_dose_mg          FLOAT,                    -- 110
    relative_dose_intensity_pct FLOAT,                    -- 111
    last_known_dose_mg          FLOAT,                    -- 112

    -- ── Patient-reported outcomes ────────────────────────────
    pro_eq5d_score              FLOAT,                    -- 113
    pro_sf36_physical           FLOAT,                    -- 114
    pro_sf36_mental             FLOAT,                    -- 115
    pro_pgic_score              INTEGER,                  -- 116
    pro_fatigue_score           FLOAT,                    -- 117
    pro_pain_score              FLOAT,                    -- 118

    -- ── Biomarkers & genomics ────────────────────────────────
    biomarker_status            STRING,                   -- 119
    biomarker_value_baseline    FLOAT,                    -- 120
    biomarker_value_week12      FLOAT,                    -- 121
    mutation_flag               STRING,                   -- 122
    mutation_type               STRING,                   -- 123
    pdl1_expression_pct         FLOAT,                    -- 124

    -- ── Data provenance ──────────────────────────────────────
    source_system               STRING,                   -- 125
    etl_batch_ref               STRING,                   -- 126
    record_created_at           TIMESTAMP,                -- 127
    record_updated_at           TIMESTAMP,                -- 128
    data_quality_flag           STRING,                   -- 129
    is_latest_version           STRING                    -- 130

);
