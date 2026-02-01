"""
🧠 NHI Mental Health: FFS vs Capitation Simulator v3
For PsySSA Workshop - February 3, 2026

Author: Built for Prof Shabir Moosa, NHI Branch
National Department of Health, South Africa

Changes in v3:
- Psychiatrist added (optional, 0.05 FTE increments)
- Educational Psychologist removed
- HPCSA scope-of-practice service coverage matrix
- Quality floor: "Team cannot legally operate" warnings
- Health promotion 0-100% with auto-CHW calculation
- CHW auto-calculated (removed from manual sliders)
- Badges/Achievements removed
- FFS as compact reference panel at top
- Income: yellow (below FFS), red (loss), green (above)
- "Population access %" replaces "reach"
- "Daily visits" replaces workload labels
- Submission collection for workshop
- International benchmarks
- Impact-framed insights
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
from datetime import datetime

# ============================================================
# PAGE CONFIG & STYLING
# ============================================================
st.set_page_config(
    page_title="NHI Mental Health Simulator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary-blue: #1E5F8A;
        --secondary-green: #28a745;
        --warning-yellow: #e6a817;
        --warning-red: #dc3545;
        --neutral-gray: #6c757d;
    }

    .main-header {
        background: linear-gradient(135deg, #1E5F8A 0%, #2E8B57 100%);
        padding: 1.2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }

    .ffs-ref-card {
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
    }

    .ffs-ref-card h4 { margin: 0 0 0.5rem 0; color: #495057; }
    .ffs-ref-value { font-size: 1.8rem; font-weight: bold; color: #495057; }

    .income-card {
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
    }

    .income-green {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
    }

    .income-yellow {
        background: linear-gradient(135deg, #e6a817 0%, #f0c040 100%);
        color: #333;
    }

    .income-red {
        background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);
        color: white;
    }

    .income-neutral {
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        color: white;
    }

    .income-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .comparison-better { color: #28a745; font-weight: bold; }
    .comparison-worse { color: #dc3545; font-weight: bold; }

    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }

    .danger-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }

    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }

    .info-box {
        background: #e7f3ff;
        border-left: 4px solid #1E5F8A;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }

    .stop-box {
        background: #2c0b0e;
        border-left: 6px solid #ff0000;
        padding: 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
        color: #f8d7da;
    }

    .coverage-can {
        background: #d4edda;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.3rem 0;
    }

    .coverage-cannot {
        background: #f8d7da;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.3rem 0;
    }

    .coverage-warn {
        background: #fff3cd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.3rem 0;
    }

    .benchmark-box {
        background: #f0f4f8;
        border: 1px solid #c8d6e5;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }

    .assumptions-panel {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        font-size: 0.85rem;
        color: #495057;
    }

    .insight-impact {
        font-size: 1.05rem;
        line-height: 1.6;
        padding: 0.5rem 0;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# PROFESSION DATA (FFS Baselines)
# ============================================================
PROFESSIONS = {
    "Clinical Psychologist": {
        "default_fee": 1200,
        "default_patients": 6,
        "default_costs": 25,
        "scope": "Full diagnostic & therapeutic scope, neuropsych & forensic assessment"
    },
    "Counselling Psychologist": {
        "default_fee": 1000,
        "default_patients": 7,
        "default_costs": 25,
        "scope": "Therapeutic interventions & diagnosis; no neuropsych/forensic"
    },
    "Registered Counsellor": {
        "default_fee": 650,
        "default_patients": 8,
        "default_costs": 20,
        "scope": "Supportive counselling only — cannot diagnose (HPCSA supervised)"
    },
    "Mental Health Nurse": {
        "default_fee": 450,
        "default_patients": 12,
        "default_costs": 15,
        "scope": "Screening, medication support, triage, crisis stabilisation"
    },
    "Psychiatrist": {
        "default_fee": 2200,
        "default_patients": 15,
        "default_costs": 30,
        "scope": "Full diagnostic, prescribing, severe mental illness, ECT, hospitalisation"
    }
}

# Default Team CTC rates
DEFAULT_CTC = {
    "Psychiatrist": 2800000,
    "Clinical Psychologist": 900000,
    "Counselling Psychologist": 800000,
    "Registered Counsellor": 450000,
    "Mental Health Nurse": 550000,
    "Community Health Worker": 150000
}

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0;">🧠 NHI Mental Health Simulator</h1>
    <p style="font-size: 1.1rem; margin: 0.3rem 0 0 0;">Fee-for-Service Income vs Capitation Team Model</p>
    <p style="font-size: 0.85rem; opacity: 0.85; margin: 0.3rem 0 0 0;">PsySSA Workshop | 3 February 2026 | National Health Insurance</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR - ALL INPUTS
# ============================================================
with st.sidebar:
    st.markdown("## 👤 Your Profile")

    profession = st.selectbox(
        "Your Profession",
        options=list(PROFESSIONS.keys()),
        index=0,
        help="Select your current profession for FFS baseline"
    )
    prof_data = PROFESSIONS[profession]

    participant_name = st.text_input(
        "Your Name (optional)",
        help="For submission collection"
    )

    st.markdown("---")

    # ========== FFS SECTION ==========
    st.markdown("## 💼 Your Current FFS Practice")

    ffs_patients = st.slider(
        "Patients per Day",
        min_value=1, max_value=40,
        value=prof_data["default_patients"],
        help="Average number of patients you see daily"
    )

    ffs_fee = st.slider(
        "Average Fee (R)",
        min_value=100, max_value=3500,
        value=prof_data["default_fee"],
        step=50, format="R%d"
    )

    ffs_costs_pct = st.slider(
        "Cost of Sales (%)",
        min_value=0, max_value=100,
        value=prof_data["default_costs"],
        help="Room rental, admin, materials as % of turnover"
    )

    st.markdown("---")

    # ========== CAPITATION SECTION ==========
    st.markdown("## 🏥 Capitation Scenario")

    population = st.slider(
        "Population Covered",
        min_value=1000, max_value=100000,
        value=80000, step=1000, format="%d"
    )

    capitation = st.slider(
        "Capitation Rate (R/person/year)",
        min_value=10, max_value=500,
        value=120, step=10, format="R%d"
    )

    utilization_base = st.slider(
        "Base Utilisation (%)",
        min_value=1.0, max_value=10.0,
        value=4.0, step=0.5, format="%.1f%%",
        help="% of population accessing services annually"
    )

    st.markdown("---")

    # ========== HEALTH PROMOTION ==========
    st.markdown("## 🌱 Health Promotion Investment")

    health_promo = st.slider(
        "Prevention Effort (%)",
        min_value=0, max_value=100,
        value=10, step=5,
        help="0% = no prevention; 100% = maximum investment. Auto-adds CHWs and reduces utilisation linearly."
    )

    # Auto-calculate CHWs: 1 CHW per 10,000 pop at 100%
    auto_chws = round((health_promo / 100) * (population / 10000), 1)
    chw_ctc_val = DEFAULT_CTC["Community Health Worker"]

    # Linear utilization reduction: at 100% effort, utilization approaches 0
    effective_utilization = utilization_base * (1 - health_promo / 100)

    if health_promo > 0:
        st.info(
            f"📉 Utilisation: {utilization_base:.1f}% → {effective_utilization:.1f}%\n\n"
            f"👥 Auto CHWs: {auto_chws:.1f} (at R{chw_ctc_val:,}/yr each)"
        )

    st.markdown("---")

    # ========== TEAM COMPOSITION ==========
    st.markdown("## 👥 Capitation Team (FTE)")

    psychiatrist_fte = st.slider(
        "Psychiatrist (sessional)",
        min_value=0.0, max_value=2.0,
        value=0.0, step=0.05, format="%.2f",
        help="Only prescriber for psychiatric medication. 0.1-0.25 FTE typical for sessional."
    )

    clin_psych = st.slider(
        "Clinical Psychologists",
        min_value=0.0, max_value=2.0,
        value=1.0, step=0.25, format="%.2f"
    )

    couns_psych = st.slider(
        "Counselling Psychologists",
        min_value=0.0, max_value=2.0,
        value=0.5, step=0.25, format="%.2f"
    )

    reg_counsellors = st.slider(
        "Registered Counsellors",
        min_value=0, max_value=25,
        value=10, step=1,
        help="HPCSA: Max 10:1 supervision ratio per psychologist"
    )

    mh_nurses = st.slider(
        "Mental Health Nurses",
        min_value=0.0, max_value=3.0,
        value=1.0, step=0.5, format="%.1f"
    )

    st.caption(f"🌱 CHWs auto-calculated from health promotion: **{auto_chws:.1f}**")

    st.markdown("---")

    # Edit CTC rates
    st.markdown("## 💵 Annual Salaries (CTC)")
    with st.expander("Adjust CTC Rates (R)"):
        ctc_psych_md = st.number_input("Psychiatrist CTC", value=DEFAULT_CTC["Psychiatrist"], step=100000)
        ctc_clin = st.number_input("Clinical Psych CTC", value=DEFAULT_CTC["Clinical Psychologist"], step=50000)
        ctc_couns = st.number_input("Counselling Psych CTC", value=DEFAULT_CTC["Counselling Psychologist"], step=50000)
        ctc_reg = st.number_input("Registered Counsellor CTC", value=DEFAULT_CTC["Registered Counsellor"], step=25000)
        ctc_nurse = st.number_input("MH Nurse CTC", value=DEFAULT_CTC["Mental Health Nurse"], step=25000)
        chw_ctc_val = st.number_input("CHW CTC", value=DEFAULT_CTC["Community Health Worker"], step=10000)


# ============================================================
# CALCULATIONS
# ============================================================

# FFS
working_days = 250
ffs_turnover = ffs_patients * ffs_fee * working_days
ffs_costs = ffs_turnover * (ffs_costs_pct / 100)
ffs_income = ffs_turnover - ffs_costs

# Capitation
cap_total_budget = population * capitation

team_costs = {
    "Psychiatrist": psychiatrist_fte * ctc_psych_md,
    "Clinical Psychologist": clin_psych * ctc_clin,
    "Counselling Psychologist": couns_psych * ctc_couns,
    "Registered Counsellor": reg_counsellors * ctc_reg,
    "Mental Health Nurse": mh_nurses * ctc_nurse,
    "Community Health Worker": auto_chws * chw_ctc_val
}
total_team_cost = sum(team_costs.values())

remaining_after_team = cap_total_budget - total_team_cost
other_costs = max(0, remaining_after_team * 0.15)
cap_total_costs = total_team_cost + other_costs
cap_income = cap_total_budget - cap_total_costs

# Service metrics
users_covered = int(population * (effective_utilization / 100))
visits_per_user = 4
total_visits = users_covered * visits_per_user
visits_per_day = total_visits / working_days

# Population access %
pop_access_pct = (users_covered / population * 100) if population > 0 else 0

# Clinical FTEs (excludes CHWs)
clinical_ftes = psychiatrist_fte + clin_psych + couns_psych + reg_counsellors + mh_nurses
cap_daily_visits = visits_per_day / max(1, clinical_ftes) if clinical_ftes > 0 else visits_per_day

# Supervision
total_supervisors = clin_psych + couns_psych
supervision_ratio = (reg_counsellors / total_supervisors) if total_supervisors > 0 else (float('inf') if reg_counsellors > 0 else 0)

# Comparisons
income_difference = cap_income - ffs_income
income_difference_pct = (income_difference / ffs_income * 100) if ffs_income > 0 else 0
team_cost_pct = (total_team_cost / cap_total_budget * 100) if cap_total_budget > 0 else 0

# Medication estimate (~60% of MH users need pharmacotherapy)
people_needing_meds = int(users_covered * 0.6)

# ============================================================
# COMPETENCY & SERVICE COVERAGE ANALYSIS
# ============================================================
warnings = []
dangers = []
successes = []
services_can = []
services_cannot = []
regulatory_warnings = []
team_illegal = False

# --- What CAN be delivered ---
if clin_psych > 0 or couns_psych > 0:
    services_can.append("✅ Mental health diagnosis")
if clin_psych > 0 or couns_psych > 0:
    services_can.append("✅ Psychological therapy (individual & group)")
if clin_psych > 0:
    services_can.append("✅ Neuropsychological assessment")
    services_can.append("✅ Forensic assessment")
if psychiatrist_fte > 0:
    services_can.append("✅ Psychiatric medication prescribing")
    services_can.append("✅ Severe mental illness treatment")
    services_can.append("✅ Treatment-resistant case management")
if mh_nurses > 0:
    services_can.append("✅ Crisis triage & stabilisation")
    services_can.append("✅ Medication adherence monitoring")
if reg_counsellors > 0 and total_supervisors > 0:
    services_can.append("✅ Supportive counselling (supervised)")
    services_can.append("✅ Psychoeducation & prevention")
if auto_chws > 0:
    services_can.append("✅ Community outreach & screening")
    services_can.append("✅ Health promotion & awareness")

# --- What CANNOT be delivered ---
if psychiatrist_fte == 0:
    services_cannot.append("❌ Medication management (depression, anxiety, psychosis, bipolar)")
    services_cannot.append("❌ Severe / treatment-resistant mental illness")
    services_cannot.append("❌ Hospitalisation pathway for acute psychiatric emergencies")
    services_cannot.append("❌ ECT or medical psychiatric interventions")

if clin_psych == 0 and couns_psych == 0:
    services_cannot.append("❌ Mental health diagnosis (no psychologist)")
    services_cannot.append("❌ Psychological therapy")

if clin_psych == 0:
    if couns_psych > 0:
        services_cannot.append("❌ Neuropsychological assessment (needs clinical psychologist)")
        services_cannot.append("❌ Forensic assessment (needs clinical psychologist)")
    else:
        services_cannot.append("❌ Neuropsychological assessment")
        services_cannot.append("❌ Forensic assessment")

if mh_nurses == 0:
    services_cannot.append("❌ Crisis triage & medication support")

# --- Regulatory checks ---
if reg_counsellors > 0 and total_supervisors == 0:
    regulatory_warnings.append("🔴 <b>HPCSA VIOLATION</b>: Registered Counsellors MUST be supervised by a psychologist. Current team cannot legally operate.")
    team_illegal = True

if supervision_ratio > 10:
    regulatory_warnings.append(f"🔴 <b>HPCSA VIOLATION</b>: Supervision ratio {supervision_ratio:.1f}:1 exceeds maximum 10:1.")
    team_illegal = True

if auto_chws > 0 and clinical_ftes == 0:
    regulatory_warnings.append("🔴 CHWs cannot deliver clinical services alone. No clinical team members present.")
    team_illegal = True

# --- Competency warnings ---
if psychiatrist_fte == 0:
    dangers.append(
        f"🔴 <b>NO PSYCHIATRIST — NO MEDICATION</b>: ~{people_needing_meds:,} people "
        f"needing psychiatric medication have no access to prescribing. "
        "This includes depression, anxiety disorders, psychosis, bipolar, and treatment-resistant conditions."
    )

if clin_psych == 0 and couns_psych == 0 and reg_counsellors == 0:
    dangers.append("🔴 <b>NO PSYCHOLOGICAL CAPACITY</b>: No psychologists or counsellors — team cannot deliver any psychological intervention.")

if clin_psych == 0 and couns_psych == 0 and reg_counsellors > 0:
    dangers.append("🔴 <b>UNSUPERVISED COUNSELLORS</b>: HPCSA requires psychologist supervision. Team cannot legally operate.")

if supervision_ratio > 10:
    dangers.append(f"🔴 <b>HPCSA Violation</b>: Supervision ratio {supervision_ratio:.1f}:1 exceeds maximum 10:1. Add psychologists or reduce counsellors.")
elif supervision_ratio > 8 and supervision_ratio <= 10:
    warnings.append(f"⚠️ Supervision ratio {supervision_ratio:.1f}:1 — approaching HPCSA limit of 10:1")
elif reg_counsellors > 0 and total_supervisors > 0 and supervision_ratio <= 8:
    successes.append(f"✓ Supervision ratio {supervision_ratio:.1f}:1 — within HPCSA guidelines")

if mh_nurses == 0 and psychiatrist_fte == 0:
    warnings.append("⚠️ <b>No crisis capacity</b>: No MH Nurse or Psychiatrist for psychiatric emergencies")

if team_cost_pct > 95:
    dangers.append(f"🔴 <b>Budget overrun</b>: Team costs ({team_cost_pct:.0f}%) exceed available budget")
elif team_cost_pct > 85:
    warnings.append(f"⚠️ Budget tight: Team costs at {team_cost_pct:.0f}% of budget")
elif team_cost_pct < 70 and total_team_cost > 0:
    successes.append(f"✓ Budget healthy: Team costs {team_cost_pct:.0f}% — room for operations")

if psychiatrist_fte > 0 and (clin_psych > 0 or couns_psych > 0) and mh_nurses > 0:
    successes.append("✓ <b>Comprehensive team</b>: Prescribing + diagnosis + therapy + nursing support")

if 6 <= supervision_ratio <= 10:
    successes.append("✓ Effective task-shifting: Leveraging counsellors within safe supervision")


# ============================================================
# QUALITY SCORE (recalibrated)
# ============================================================
value_score = 0

# Income component (30 pts)
if cap_income > ffs_income * 1.15:
    income_pts = 30
elif cap_income > ffs_income:
    income_pts = 22
elif cap_income > ffs_income * 0.9:
    income_pts = 15
else:
    income_pts = 5
value_score += income_pts

# Service coverage (40 pts — biggest weight)
quality_pts = 40
if psychiatrist_fte == 0:
    quality_pts -= 15
if clin_psych == 0 and couns_psych == 0:
    quality_pts -= 12
if team_illegal:
    quality_pts -= 10
if mh_nurses == 0:
    quality_pts -= 3
quality_pts = max(0, quality_pts)
value_score += quality_pts

# Workload (15 pts)
if cap_daily_visits < ffs_patients * 0.6:
    workload_pts = 15
elif cap_daily_visits < ffs_patients * 0.8:
    workload_pts = 12
elif cap_daily_visits < ffs_patients:
    workload_pts = 8
else:
    workload_pts = 3
value_score += workload_pts

# Access (15 pts)
if pop_access_pct >= 5:
    access_pts = 15
elif pop_access_pct >= 3:
    access_pts = 10
elif pop_access_pct >= 1.5:
    access_pts = 6
else:
    access_pts = 2
value_score += access_pts


# ============================================================
# MAIN DISPLAY
# ============================================================

# ---------- QUALITY FLOOR ----------
if team_illegal:
    st.markdown("""
    <div class="stop-box">
        <h3 style="margin:0; color: #ff6b6b;">⛔ TEAM CANNOT LEGALLY OPERATE</h3>
        <p style="margin: 0.5rem 0 0 0;">
            Current team composition violates HPCSA regulations.
            Adjust team members in the sidebar before this configuration can be used.
        </p>
    </div>
    """, unsafe_allow_html=True)
    for rw in regulatory_warnings:
        st.markdown(f'<div class="danger-box">{rw}</div>', unsafe_allow_html=True)
    st.markdown("---")

# ---------- FFS REFERENCE CARD (compact, at top) ----------
st.markdown(f"""
<div class="ffs-ref-card">
    <h4>💼 Your FFS Baseline — {profession}</h4>
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <span class="ffs-ref-value">R{ffs_income:,.0f}</span>
            <span style="color: #6c757d;"> /year net income</span>
        </div>
        <div style="color: #6c757d; font-size: 0.9rem;">
            {ffs_patients} pts/day &times; R{ffs_fee} &times; 250 days &minus; {ffs_costs_pct}% costs
            &nbsp;|&nbsp; {ffs_patients * working_days:,} consultations/year
            &nbsp;|&nbsp; <em>{prof_data['scope']}</em>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- CAPITATION MODEL ----------
st.markdown("## 🏥 Capitation Team Model")

col_income, col_metrics = st.columns([1, 1])

with col_income:
    if cap_income > ffs_income:
        card_class = "income-green"
        comparison_text = f"+R{income_difference:,.0f} ({income_difference_pct:+.1f}%) vs FFS"
    elif cap_income >= 0:
        card_class = "income-yellow"
        comparison_text = f"R{income_difference:,.0f} ({income_difference_pct:.1f}%) below FFS"
    else:
        card_class = "income-red"
        comparison_text = f"R{income_difference:,.0f} — NET LOSS"

    st.markdown(f"""
    <div class="income-card {card_class}">
        <p style="margin:0; font-size: 0.9rem;">Annual Capitation Income</p>
        <p class="income-value">R{cap_income:,.0f}</p>
        <p style="margin:0; font-size: 0.85rem;">{comparison_text}</p>
        <p style="margin:0.3rem 0 0 0; font-size: 0.8rem; opacity: 0.85;">
            Budget R{cap_total_budget:,.0f} &minus; Team R{total_team_cost:,.0f} &minus; Ops R{other_costs:,.0f}
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_metrics:
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(
            "Daily Visits",
            f"{cap_daily_visits:.1f}",
            delta=f"{cap_daily_visits - ffs_patients:+.1f} vs FFS",
            delta_color="inverse"
        )
    with m2:
        st.metric(
            "Population Access",
            f"{pop_access_pct:.1f}%",
            help="% of covered population accessing services annually"
        )
    with m3:
        st.metric(
            "Users Served",
            f"{users_covered:,}",
            delta=f"{users_covered - ffs_patients * working_days:+,} vs FFS"
        )

    # Benchmarks
    treatment_gap_remaining = max(0, 100 - (users_covered / max(1, population * 0.3) * 100))
    st.markdown(f"""
    <div class="benchmark-box">
        <b>📊 International Benchmarks</b><br>
        WHO target: ~5% annual MH utilisation &nbsp;|&nbsp;
        SA treatment gap: 91% (SASH study) &nbsp;|&nbsp;
        SA MH budget: 5% of health spend (vs 10-12% recommended)<br>
        Your model: <b>{pop_access_pct:.1f}%</b> access
        {"— ✅ meets WHO target" if pop_access_pct >= 5 else " — ⚠️ below WHO 5% target" if pop_access_pct >= 2 else " — 🔴 critically below WHO target"}
        &nbsp;|&nbsp; Treatment gap reduced to <b>{treatment_gap_remaining:.0f}%</b>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SERVICE COVERAGE MATRIX
# ============================================================
st.markdown("---")
st.markdown("## 🩺 Service Coverage & Competency")

col_can, col_cannot = st.columns(2)

with col_can:
    if services_can:
        can_html = "<div class='coverage-can'><b>Services Your Team CAN Deliver:</b><br><br>"
        for s in services_can:
            can_html += f"{s}<br>"
        can_html += "</div>"
        st.markdown(can_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="coverage-cannot">
            <b>⛔ No services can be delivered</b><br>
            Team has no clinical capacity.
        </div>
        """, unsafe_allow_html=True)

with col_cannot:
    if services_cannot:
        cannot_html = "<div class='coverage-cannot'><b>Services Your Team CANNOT Deliver:</b><br><br>"
        for s in services_cannot:
            cannot_html += f"{s}<br>"
        cannot_html += "</div>"
        st.markdown(cannot_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="coverage-can">
            <b>✅ Full service coverage</b><br>
            Team can deliver comprehensive mental health services.
        </div>
        """, unsafe_allow_html=True)

    if regulatory_warnings and not team_illegal:
        for rw in regulatory_warnings:
            st.markdown(f"<div class='coverage-warn'>{rw}</div>", unsafe_allow_html=True)


# ============================================================
# IMPACT INSIGHTS
# ============================================================
st.markdown("---")
st.markdown("## 💡 Impact Insights")

insight_cols = st.columns(2)

with insight_cols[0]:
    # Income insight
    if cap_income > ffs_income:
        st.markdown(f"""
        <div class="success-box insight-impact">
            💰 <b>Earn R{income_difference:,.0f} MORE</b> per year while serving
            <b>{users_covered - ffs_patients * working_days:,} more people</b> than your FFS practice.
        </div>
        """, unsafe_allow_html=True)
    elif cap_income >= 0:
        st.markdown(f"""
        <div class="warning-box insight-impact">
            💰 You earn <b>R{abs(income_difference):,.0f} less</b> than FFS — but serve
            <b>{users_covered:,} users</b> vs {ffs_patients * working_days:,} FFS consultations.
            Consider adjusting capitation rate or team composition.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="danger-box insight-impact">
            🚨 <b>Net loss of R{abs(cap_income):,.0f}</b>. Team costs exceed capitation budget.
            Reduce team size, increase capitation rate, or increase population.
        </div>
        """, unsafe_allow_html=True)

    # Medication gap
    if psychiatrist_fte == 0:
        st.markdown(f"""
        <div class="danger-box insight-impact">
            💊 <b>Medication Gap:</b> ~{people_needing_meds:,} people needing psychiatric medication
            have nowhere to go. 60% of mental health conditions require pharmacotherapy.
            <br><i>Add even 0.1 FTE psychiatrist for sessional prescribing.</i>
        </div>
        """, unsafe_allow_html=True)
    else:
        psych_capacity = int(psychiatrist_fte * 15 * working_days)
        st.markdown(f"""
        <div class="success-box insight-impact">
            💊 <b>Medication covered:</b> Psychiatrist at {psychiatrist_fte:.2f} FTE provides
            ~{psych_capacity:,} medication consultations/year for
            {people_needing_meds:,} people needing pharmacotherapy.
        </div>
        """, unsafe_allow_html=True)

with insight_cols[1]:
    # Workload
    workload_change = ((cap_daily_visits - ffs_patients) / ffs_patients * 100) if ffs_patients > 0 else 0
    if cap_daily_visits < ffs_patients:
        st.markdown(f"""
        <div class="success-box insight-impact">
            ⚖️ <b>{abs(workload_change):.0f}% lighter workload</b> per clinician — team-based care
            distributes the load across {clinical_ftes:.1f} FTE clinical staff.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="warning-box insight-impact">
            ⚖️ Workload <b>{workload_change:.0f}% heavier</b> than FFS.
            Consider adding more team members or reducing utilisation expectations.
        </div>
        """, unsafe_allow_html=True)

    # Health promotion
    if health_promo > 0:
        utilisation_saved = utilization_base - effective_utilization
        visits_saved = int(population * (utilisation_saved / 100) * visits_per_user)
        st.markdown(f"""
        <div class="info-box insight-impact">
            🌱 <b>Prevention saves {visits_saved:,} visits/year</b> ({utilisation_saved:.1f}% utilisation reduction).
            {auto_chws:.1f} CHWs auto-deployed for community outreach at R{auto_chws * chw_ctc_val:,.0f}/year.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="warning-box insight-impact">
            🌱 <b>No prevention investment</b>. Full {utilization_base:.1f}% utilisation applies.
            Health promotion reduces demand and adds CHW capacity.
        </div>
        """, unsafe_allow_html=True)

    # Treatment gap
    estimated_prevalence = population * 0.30
    gap_closed_pct = (users_covered / estimated_prevalence * 100) if estimated_prevalence > 0 else 0
    st.markdown(f"""
    <div class="info-box insight-impact">
        📊 <b>Treatment gap:</b> Of ~{int(estimated_prevalence):,} people with lifetime MH conditions,
        your team reaches <b>{users_covered:,} ({gap_closed_pct:.1f}%)</b>.
        SA average: only 9% get treatment.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SAFETY CHECKS
# ============================================================
if dangers or warnings or successes:
    st.markdown("---")
    st.markdown("## ⚠️ Safety Checks")

    for d in dangers:
        st.markdown(f'<div class="danger-box">{d}</div>', unsafe_allow_html=True)
    for w in warnings:
        st.markdown(f'<div class="warning-box">{w}</div>', unsafe_allow_html=True)
    for s in successes:
        st.markdown(f'<div class="success-box">{s}</div>', unsafe_allow_html=True)


# ============================================================
# VALUE SCORE
# ============================================================
st.markdown("---")
st.markdown("## 📈 Value Score")

col_score, col_breakdown = st.columns([1, 2])

with col_score:
    if value_score >= 75:
        score_color = "#28a745"
        score_label = "Excellent"
    elif value_score >= 55:
        score_color = "#e6a817"
        score_label = "Moderate"
    else:
        score_color = "#dc3545"
        score_label = "Needs Work"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E5F8A 0%, #2E8B57 100%);
                padding: 2rem; border-radius: 15px; text-align: center; color: white;">
        <h3 style="margin: 0;">Value Score</h3>
        <p style="font-size: 3.5rem; font-weight: bold; margin: 0.5rem 0; color: {score_color};">
            {value_score}/100
        </p>
        <p style="margin: 0; opacity: 0.9;">{score_label} — Quality &divide; Cost Balance</p>
    </div>
    """, unsafe_allow_html=True)

with col_breakdown:
    st.markdown("#### Score Breakdown")

    breakdown_data = {
        'Component': ['Income vs FFS (30)', 'Service Coverage (40)', 'Workload Balance (15)', 'Population Access (15)'],
        'Points': [income_pts, quality_pts, workload_pts, access_pts],
        'Max': [30, 40, 15, 15]
    }

    fig_breakdown = go.Figure()
    fig_breakdown.add_trace(go.Bar(
        y=breakdown_data['Component'],
        x=breakdown_data['Points'],
        orientation='h',
        name='Earned',
        marker_color=['#28a745' if p >= m * 0.7 else '#e6a817' if p >= m * 0.4 else '#dc3545'
                      for p, m in zip(breakdown_data['Points'], breakdown_data['Max'])],
        text=[f"{p}/{m}" for p, m in zip(breakdown_data['Points'], breakdown_data['Max'])],
        textposition='inside'
    ))

    fig_breakdown.update_layout(
        height=220,
        margin=dict(l=0, r=20, t=10, b=10),
        xaxis=dict(range=[0, 45]),
        showlegend=False
    )
    st.plotly_chart(fig_breakdown, use_container_width=True)


# ============================================================
# COMPARISON CHART
# ============================================================
st.markdown("---")
st.markdown("## 📊 Side-by-Side Comparison")

fig_compare = go.Figure()

fig_compare.add_trace(go.Bar(
    name='FFS',
    x=['Income (R)', 'Daily Visits', 'Users/Year'],
    y=[ffs_income / 1_000_000, ffs_patients, (ffs_patients * working_days) / 1000],
    marker_color='#6c757d',
    text=[f'R{ffs_income / 1_000_000:.2f}M', f'{ffs_patients}', f'{(ffs_patients * working_days) / 1000:.1f}k'],
    textposition='outside'
))

cap_bar_color = '#28a745' if cap_income >= ffs_income else '#e6a817' if cap_income >= 0 else '#dc3545'
fig_compare.add_trace(go.Bar(
    name='Capitation',
    x=['Income (R)', 'Daily Visits', 'Users/Year'],
    y=[cap_income / 1_000_000, cap_daily_visits, users_covered / 1000],
    marker_color=cap_bar_color,
    text=[f'R{cap_income / 1_000_000:.2f}M', f'{cap_daily_visits:.1f}', f'{users_covered / 1000:.1f}k'],
    textposition='outside'
))

fig_compare.update_layout(
    barmode='group',
    height=350,
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    showlegend=True
)
st.plotly_chart(fig_compare, use_container_width=True)


# ============================================================
# TEAM COST BREAKDOWN
# ============================================================
st.markdown("---")
st.markdown("## 👥 Team Cost Breakdown")

col_table, col_pie = st.columns([1, 1])

with col_table:
    fte_map = {
        "Psychiatrist": psychiatrist_fte,
        "Clinical Psychologist": clin_psych,
        "Counselling Psychologist": couns_psych,
        "Registered Counsellor": reg_counsellors,
        "Mental Health Nurse": mh_nurses,
        "Community Health Worker": auto_chws
    }

    team_df = pd.DataFrame({
        'Role': [k for k, v in team_costs.items() if v > 0],
        'FTE': [fte_map[k] for k, v in team_costs.items() if v > 0],
        'Annual Cost': [f"R{v:,.0f}" for k, v in team_costs.items() if v > 0]
    })

    if not team_df.empty:
        st.dataframe(team_df, use_container_width=True, hide_index=True)

    st.markdown(f"""
    | | |
    |---|---|
    | **Total Team Cost** | **R{total_team_cost:,.0f}** |
    | Budget Available | R{cap_total_budget:,.0f} |
    | Team % of Budget | {team_cost_pct:.1f}% |
    | Operational Costs | R{other_costs:,.0f} |
    | **Remaining (Your Income)** | **R{cap_income:,.0f}** |
    """)

with col_pie:
    if total_team_cost > 0:
        pie_data = {k: v for k, v in team_costs.items() if v > 0}
        fig_pie = px.pie(
            values=list(pie_data.values()),
            names=list(pie_data.keys()),
            color_discrete_sequence=px.colors.sequential.Teal,
            hole=0.4
        )
        fig_pie.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ============================================================
# SUBMISSION COLLECTION
# ============================================================
st.markdown("---")
st.markdown("## 📋 Save Your Scenario")

submission_data = {
    "timestamp": datetime.now().isoformat(),
    "name": participant_name,
    "profession": profession,
    "ffs_income": round(ffs_income),
    "ffs_patients_per_day": ffs_patients,
    "ffs_fee": ffs_fee,
    "population": population,
    "capitation_rate": capitation,
    "utilisation_base": utilization_base,
    "health_promo_pct": health_promo,
    "effective_utilisation": round(effective_utilization, 2),
    "auto_chws": auto_chws,
    "team": {
        "psychiatrist_fte": psychiatrist_fte,
        "clin_psych_fte": clin_psych,
        "couns_psych_fte": couns_psych,
        "reg_counsellors": reg_counsellors,
        "mh_nurses_fte": mh_nurses,
        "chws_auto": auto_chws
    },
    "results": {
        "cap_income": round(cap_income),
        "income_vs_ffs": round(income_difference),
        "income_vs_ffs_pct": round(income_difference_pct, 1),
        "users_covered": users_covered,
        "pop_access_pct": round(pop_access_pct, 1),
        "daily_visits_per_clinician": round(cap_daily_visits, 1),
        "value_score": value_score,
        "team_cost_pct": round(team_cost_pct, 1),
        "team_illegal": team_illegal,
        "services_available": len(services_can),
        "services_missing": len(services_cannot)
    }
}

col_sub1, col_sub2 = st.columns(2)

with col_sub1:
    st.download_button(
        label="⬇️ Download My Scenario (JSON)",
        data=json.dumps(submission_data, indent=2),
        file_name=f"mh_scenario_{participant_name or 'anon'}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
        help="Save your scenario parameters and results"
    )

with col_sub2:
    summary_line = (
        f"{participant_name or 'Anonymous'} | {profession} | "
        f"FFS R{ffs_income:,.0f} -> Cap R{cap_income:,.0f} ({income_difference_pct:+.1f}%) | "
        f"Pop {population:,} @ R{capitation} | Access {pop_access_pct:.1f}% | "
        f"Score {value_score}/100 | "
        f"Team: Psych {psychiatrist_fte}, ClinP {clin_psych}, CounsP {couns_psych}, "
        f"RC {reg_counsellors}, MHN {mh_nurses}, CHW {auto_chws:.1f}"
    )
    st.code(summary_line, language=None)
    st.caption("Copy the above summary to share your scenario")


# ============================================================
# ASSUMPTIONS PANEL
# ============================================================
st.markdown("---")
st.markdown(f"""
<div class="assumptions-panel">
    <h4 style="margin-top: 0;">📋 Assumptions & Sources</h4>
    <ul style="margin-bottom: 0;">
        <li><b>Working days:</b> 250 per year</li>
        <li><b>Visits per user:</b> 4 average per year</li>
        <li><b>Supervision:</b> HPCSA maximum 10 Registered Counsellors per Psychologist</li>
        <li><b>Health promotion:</b> {health_promo}% effort reduces utilisation linearly ({utilization_base:.1f}% &rarr; {effective_utilization:.1f}%); auto-adds {auto_chws:.1f} CHWs</li>
        <li><b>Medication need:</b> ~60% of MH service users require pharmacotherapy (WHO/Lancet Commission)</li>
        <li><b>MH prevalence:</b> 30% lifetime (SA Stress &amp; Health Study, Herman et al. 2009)</li>
        <li><b>Treatment gap:</b> 91% among those who cannot afford private care (Herman et al. 2009)</li>
        <li><b>WHO benchmark:</b> ~5% annual MH service utilisation for comprehensive coverage</li>
        <li><b>SA MH budget:</b> ~5% of total health expenditure vs 10-12% international recommendation</li>
        <li><b>CTC rates:</b> Private/NHI sector estimates (editable in sidebar)</li>
        <li><b>Operational costs:</b> 15% of remaining budget for admin/consumables</li>
        <li><b>No facility costs included</b> &mdash; assumes existing NHI-contracted infrastructure</li>
    </ul>
</div>
""", unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧠 <b>NHI Mental Health: FFS vs Capitation Simulator</b> v3</p>
    <p style="font-size: 0.85rem;">
        PsySSA Workshop | 3 February 2026<br>
        National Health Insurance | South Africa
    </p>
    <p style="font-size: 0.8rem; opacity: 0.8;">
        Built for Prof Shabir Moosa | NHI Branch: User &amp; Service Provider Management<br>
        National Department of Health
    </p>
</div>
""", unsafe_allow_html=True)
