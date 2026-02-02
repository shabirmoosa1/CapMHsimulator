"""
🧠 Mental Health: FFS vs Capitation Simulator v7
For PsySSA Workshop - February 3, 2026

Author: Prof Shabir Moosa
Department of Family Medicine & PHC, University of Witwatersrand

v7 changes:
1.  All NHI references removed; affiliated to Wits Family Medicine & PHC
2.  'Cost of Sales' → 'Cost of Services' with Rand amount shown
3.  All expenses/incomes displayed MONTHLY (inputs remain annual where natural)
4.  Capitation cost of services = cost/consult × clinic visits (excl CHW)
5.  Email submission removed; replaced with server-side CSV capture
6.  Admin download with password for workshop facilitator
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json, csv, os, re
from datetime import datetime

# ============================================================
# PAGE CONFIG & STYLING
# ============================================================
st.set_page_config(
    page_title="Mental Health Capitation Simulator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        padding: 1.2rem; border-radius: 10px; color: white;
        text-align: center; margin-bottom: 1rem;
    }
    .guide-box {
        background: #e7f3ff; border: 2px solid #1E5F8A;
        border-radius: 10px; padding: 1rem 1.5rem; margin-bottom: 1rem;
        font-size: 0.92rem;
    }
    .ffs-ref-card {
        background: #f8f9fa; border: 2px solid #dee2e6;
        border-radius: 10px; padding: 1rem 1.5rem; margin-bottom: 0.5rem;
    }
    .ffs-ref-card h4 { margin: 0 0 0.5rem 0; color: #495057; }
    .ffs-ref-value { font-size: 1.8rem; font-weight: bold; color: #495057; }
    .ffs-limits { background: #fff3cd; border-radius: 8px; padding: 0.8rem 1.2rem;
        margin-top: 0.5rem; font-size: 0.88rem; color: #664d03; }
    .income-card { padding: 1.5rem; border-radius: 12px; text-align: center; margin: 0.5rem 0; }
    .income-green { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; }
    .income-yellow { background: linear-gradient(135deg, #e6a817 0%, #f0c040 100%); color: #333; }
    .income-red { background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%); color: white; }
    .income-value { font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0; }
    .consult-card { padding: 1.5rem; border-radius: 12px; text-align: center; margin: 0.5rem 0; }
    .consult-green { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; }
    .consult-yellow { background: linear-gradient(135deg, #e6a817 0%, #f0c040 100%); color: #333; }
    .consult-red { background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%); color: white; }
    .consult-value { font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0; }
    .warning-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
    .danger-box { background: #f8d7da; border-left: 4px solid #dc3545; padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
    .success-box { background: #d4edda; border-left: 4px solid #28a745; padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
    .info-box { background: #e7f3ff; border-left: 4px solid #1E5F8A; padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
    .stop-box { background: #2c0b0e; border-left: 6px solid #ff0000; padding: 1.2rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; color: #f8d7da; }
    .flag-box { background: #fef3e2; border: 1px solid #f0ad4e; border-radius: 8px;
        padding: 0.6rem 1rem; margin: 0.3rem 0; font-size: 0.9rem; }
    .coverage-can { background: #d4edda; border-radius: 8px; padding: 1rem; margin: 0.3rem 0; }
    .coverage-cannot { background: #f8d7da; border-radius: 8px; padding: 1rem; margin: 0.3rem 0; }
    .coverage-warn { background: #fff3cd; border-radius: 8px; padding: 1rem; margin: 0.3rem 0; }
    .benchmark-box { background: #f0f4f8; border: 1px solid #c8d6e5; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; font-size: 0.9rem; }
    .assumptions-panel { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 1rem; font-size: 0.82rem; color: #495057; }
    .insight-impact { font-size: 1.05rem; line-height: 1.6; padding: 0.5rem 0; }
    .engaged-green { background: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .engaged-amber { background: #e6a817; color: #333; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .engaged-red { background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .suggest-box { background: #e8f4fd; border-left: 4px solid #17a2b8; padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0; margin: 0.3rem 0; font-size: 0.9rem; }
    .submit-btn {
        display: inline-block; background: linear-gradient(135deg, #1E5F8A 0%, #2E8B57 100%);
        color: white; padding: 0.6rem 1.5rem; border-radius: 8px; font-size: 1rem;
        font-weight: bold; border: none; cursor: pointer; width: 100%;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    @media print {
        body * { display: none !important; }
        body::after {
            content: "Printing is disabled. Please use the Submit button in the simulator.";
            display: block !important; padding: 2rem; font-size: 1.2rem; text-align: center;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
WORKING_DAYS = 250
VISITS_PER_USER = 4
DEFAULT_UTIL = 4.0
DEFAULT_CAP_RATE = 120  # R/person/year
SUBMISSIONS_FILE = "workshop_submissions.csv"
ADMIN_PASSWORD = "PsySSA2026"

PROFESSIONS = {
    "Clinical Psychologist": {
        "default_fee": 1200, "default_consults": 6, "default_costs": 25,
        "scope": "Full diagnostic & therapeutic scope, neuropsych & forensic assessment",
        "daily_capacity": 7, "avg_session_min": 55,
    },
    "Counselling Psychologist": {
        "default_fee": 1000, "default_consults": 7, "default_costs": 25,
        "scope": "Therapeutic interventions & diagnosis; no neuropsych/forensic",
        "daily_capacity": 7, "avg_session_min": 50,
    },
    "Registered Counsellor": {
        "default_fee": 650, "default_consults": 8, "default_costs": 20,
        "scope": "Supportive counselling only — cannot diagnose (HPCSA supervised)",
        "daily_capacity": 9, "avg_session_min": 38,
    },
    "Mental Health Nurse": {
        "default_fee": 450, "default_consults": 12, "default_costs": 15,
        "scope": "Screening, medication support, triage, crisis stabilisation",
        "daily_capacity": 13, "avg_session_min": 25,
    },
    "Psychiatrist": {
        "default_fee": 2200, "default_consults": 15, "default_costs": 30,
        "scope": "Full diagnostic, prescribing, severe mental illness, ECT, hospitalisation",
        "daily_capacity": 18, "avg_session_min": 18,
    }
}

FFS_LIMITATIONS = {
    "Clinical Psychologist": [
        "No prescribing — patients needing medication referred out",
        "No crisis stabilisation (no nursing support)",
        "No community outreach or prevention",
        "Solo: ~6 consults/day, individual sessions only",
    ],
    "Counselling Psychologist": [
        "No prescribing — patients needing medication referred out",
        "No neuropsychological or forensic assessment",
        "No crisis stabilisation",
        "No community outreach; solo individual sessions only",
    ],
    "Registered Counsellor": [
        "⚠️ Cannot legally operate solo (HPCSA requires psychologist supervision)",
        "No diagnosis capability",
        "No prescribing; limited to supportive counselling only",
        "No crisis management",
    ],
    "Mental Health Nurse": [
        "No formal psychological diagnosis or therapy",
        "No prescribing (unless advanced trained)",
        "Limited to screening, triage, and medication monitoring",
        "No psychological assessment capability",
    ],
    "Psychiatrist": [
        "Brief consultations (~18 min) — limited therapy depth",
        "No formal psychological testing (neuropsych, forensic)",
        "No community outreach or prevention",
        "High volume but shallow engagement model",
    ],
}

DEFAULT_TEAM_BY_PROFESSION = {
    "Clinical Psychologist":    {"psych": 0.0,  "clin": 1.0,  "couns": 0.0,  "rc": 0,  "nurse": 0.0},
    "Counselling Psychologist": {"psych": 0.0,  "clin": 0.0,  "couns": 1.0,  "rc": 0,  "nurse": 0.0},
    "Registered Counsellor":    {"psych": 0.0,  "clin": 0.0,  "couns": 0.25, "rc": 1,  "nurse": 0.0},
    "Mental Health Nurse":      {"psych": 0.0,  "clin": 0.0,  "couns": 0.0,  "rc": 0,  "nurse": 1.0},
    "Psychiatrist":             {"psych": 0.25, "clin": 0.0,  "couns": 0.0,  "rc": 0,  "nurse": 0.0},
}

DEFAULT_CTC = {
    "Psychiatrist": 2800000, "Clinical Psychologist": 900000,
    "Counselling Psychologist": 800000, "Registered Counsellor": 450000,
    "Mental Health Nurse": 550000, "Community Health Worker": 150000
}

CHW_ENGAGEMENT_PER_YEAR = 2000
UTILISATION_FLOOR = 1.5
MDT_DUTY_FRACTION = 0.20

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0;">🧠 Mental Health Capitation Simulator</h1>
    <p style="font-size: 1.1rem; margin: 0.3rem 0 0 0;">Fee-for-Service Income vs Capitation Team Model</p>
    <p style="font-size: 0.85rem; opacity: 0.85; margin: 0.3rem 0 0 0;">PsySSA Workshop | 3 February 2026</p>
</div>
""", unsafe_allow_html=True)

# GUIDED BLURB
st.markdown("""
<div class="guide-box">
    <b>How to explore this simulator:</b><br>
    <b>①</b> Review your <b>current FFS practice</b> (fee, consults/day, cost of services) in the left panel<br>
    <b>②</b> Watch <b>"Your Required Consults"</b> — it starts 🔴 RED. Add team members to bring it down to 🟢 GREEN<br>
    <b>③</b> Once GREEN, <b>increase population</b> for greater reach and budget — watch income grow<br>
    <b>④</b> Explore <b>health promotion</b> to extend reach beyond the clinic<br>
    <b>⑤</b> When satisfied, <b>submit your scenario</b> for workshop analysis
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 👤 Your Profile")
    profession = st.selectbox("Your Profession", options=list(PROFESSIONS.keys()), index=0,
        help="Select your current profession for FFS baseline. Team auto-adjusts.")
    prof_data = PROFESSIONS[profession]
    default_team = DEFAULT_TEAM_BY_PROFESSION[profession]

    participant_name = st.text_input("Your Name", help="Required to submit your scenario")

    st.markdown("---")
    st.markdown("## 💼 Your Current FFS Practice")
    ffs_consults = st.slider("Consults per Day", 1, 40, prof_data["default_consults"],
        key=f"ffs_{profession}")
    ffs_fee = st.slider("Average Fee (R)", 100, 3500, prof_data["default_fee"], step=50,
        format="R%d", key=f"fee_{profession}")
    ffs_costs_pct = st.slider("Cost of Services (%)", 0, 100, prof_data["default_costs"],
        help="Room rental, admin, materials as % of turnover", key=f"costs_{profession}")

    # Show Rand amount for cost of services
    _ffs_turnover_mo = ffs_consults * ffs_fee * WORKING_DAYS / 12
    _ffs_cos_mo = _ffs_turnover_mo * (ffs_costs_pct / 100)
    _cost_per_consult = ffs_fee * (ffs_costs_pct / 100)
    st.caption(f"= **R{_ffs_cos_mo:,.0f}/month** (R{_cost_per_consult:,.0f} per consult)")

    st.markdown("---")
    st.markdown("## 🏥 Capitation Scenario")

    # Auto-calculate default population
    default_pop = round(
        prof_data["default_consults"] * WORKING_DAYS
        / (DEFAULT_UTIL / 100 * VISITS_PER_USER)
        / 1000
    ) * 1000
    default_pop = max(1000, min(100000, default_pop))

    st.caption(f"📊 Default population set to match your {prof_data['default_consults']} consults/day demand")
    population = st.slider("Population Covered", 1000, 100000, default_pop, step=1000,
        format="%d", key=f"pop_{profession}")
    capitation = st.slider("Capitation Rate (R/person/year)", 10, 500, DEFAULT_CAP_RATE, step=10,
        format="R%d")
    st.caption(f"= R{capitation/12:.0f}/person/month → Budget **R{population * capitation / 12:,.0f}/month**")
    utilization_rate = st.slider("Utilisation Rate (%)", 1.0, 10.0, DEFAULT_UTIL, step=0.5,
        format="%.1f%%", help="% of population accessing clinical services annually")

    st.markdown("---")
    st.markdown("## 👥 Capitation Team (FTE)")
    st.caption(f"Auto-set for {profession}. Add team members → watch your consults drop from 🔴 to 🟢")
    psychiatrist_fte = st.slider("Psychiatrist (sessional)", 0.0, 2.0, default_team["psych"], step=0.05,
        format="%.2f", help="Only prescriber for psychiatric medication. 0.1-0.25 FTE typical.")
    clin_psych = st.slider("Clinical Psychologists", 0.0, 2.0, default_team["clin"], step=0.25, format="%.2f")
    couns_psych = st.slider("Counselling Psychologists", 0.0, 2.0, default_team["couns"], step=0.25, format="%.2f")
    reg_counsellors = st.slider("Registered Counsellors", 0, 25, default_team["rc"], step=1,
        help="HPCSA: Max 10:1 supervision ratio per psychologist")
    mh_nurses = st.slider("Mental Health Nurses", 0.0, 3.0, default_team["nurse"], step=0.5, format="%.1f")

    st.markdown("---")
    st.markdown("## 🌱 Health Promotion")
    st.caption("Explore after setting up your team above.")
    health_promo = st.slider("Prevention Effort (%)", 0, 100, 0, step=5,
        help="0% = no prevention; higher = more CHWs, reduced utilisation (floor 1.5%).")

    auto_chws = round((health_promo / 100) * (population / 10000), 1)
    chw_ctc_val = DEFAULT_CTC["Community Health Worker"]
    effective_utilization = max(UTILISATION_FLOOR, utilization_rate * (1 - health_promo / 100))
    chw_community_engaged = int(auto_chws * CHW_ENGAGEMENT_PER_YEAR)

    if health_promo > 0:
        st.info(f"📉 Utilisation: {utilization_rate:.1f}% → {effective_utilization:.1f}% (floor {UTILISATION_FLOOR}%)\n\n"
                f"👥 Auto CHWs: {auto_chws:.1f} — engaging ~{chw_community_engaged:,} people/year")
    st.caption(f"🌱 CHWs from health promotion: **{auto_chws:.1f}**")

    st.markdown("---")
    st.markdown("## 💵 Annual Salaries (CTC)")
    with st.expander("Adjust CTC Rates (R)"):
        ctc_psych_md = st.number_input("Psychiatrist CTC", value=DEFAULT_CTC["Psychiatrist"], step=100000)
        ctc_clin = st.number_input("Clinical Psych CTC", value=DEFAULT_CTC["Clinical Psychologist"], step=50000)
        ctc_couns = st.number_input("Counselling Psych CTC", value=DEFAULT_CTC["Counselling Psychologist"], step=50000)
        ctc_reg = st.number_input("Registered Counsellor CTC", value=DEFAULT_CTC["Registered Counsellor"], step=25000)
        ctc_nurse = st.number_input("MH Nurse CTC", value=DEFAULT_CTC["Mental Health Nurse"], step=25000)
        chw_ctc_val = st.number_input("CHW CTC", value=DEFAULT_CTC["Community Health Worker"], step=10000)

# ============================================================
# CALCULATIONS — ALL MONTHLY
# ============================================================

# --- FFS (annual then monthly) ---
ffs_turnover_annual = ffs_consults * ffs_fee * WORKING_DAYS
ffs_cos_annual = ffs_turnover_annual * (ffs_costs_pct / 100)
ffs_income_annual = ffs_turnover_annual - ffs_cos_annual
ffs_annual_consultations = ffs_consults * WORKING_DAYS

ffs_turnover_mo = ffs_turnover_annual / 12
ffs_cos_mo = ffs_cos_annual / 12
ffs_income_mo = ffs_income_annual / 12

cost_per_consult = ffs_fee * (ffs_costs_pct / 100)

# --- Capitation budget (monthly) ---
cap_budget_annual = population * capitation
cap_budget_mo = cap_budget_annual / 12

team_costs = {
    "Psychiatrist": psychiatrist_fte * ctc_psych_md,
    "Clinical Psychologist": clin_psych * ctc_clin,
    "Counselling Psychologist": couns_psych * ctc_couns,
    "Registered Counsellor": reg_counsellors * ctc_reg,
    "Mental Health Nurse": mh_nurses * ctc_nurse,
    "Community Health Worker": auto_chws * chw_ctc_val
}
total_team_cost_annual = sum(team_costs.values())
total_team_cost_mo = total_team_cost_annual / 12

# --- Demand ---
clinical_users = int(population * (effective_utilization / 100))
total_visits_annual = clinical_users * VISITS_PER_USER
visits_per_day = total_visits_annual / WORKING_DAYS
total_visits_mo = total_visits_annual / 12

# --- Capitation Cost of Services (v7: cost/consult × clinic visits, excl CHW) ---
cap_cos_annual = cost_per_consult * total_visits_annual
cap_cos_mo = cap_cos_annual / 12

# --- Capitation income (monthly) ---
cap_income_mo = cap_budget_mo - total_team_cost_mo - cap_cos_mo
cap_income_annual = cap_income_mo * 12

# --- MDT-adjusted clinical capacity ---
your_capacity_raw = prof_data["daily_capacity"]
your_daily_consults = your_capacity_raw * (1 - MDT_DUTY_FRACTION)

profession_fte_map = {
    "Psychiatrist": psychiatrist_fte, "Clinical Psychologist": clin_psych,
    "Counselling Psychologist": couns_psych, "Registered Counsellor": reg_counsellors,
    "Mental Health Nurse": mh_nurses,
}
principal_in_team = profession_fte_map.get(profession, 0) > 0

full_team_capacity = (
    psychiatrist_fte * PROFESSIONS["Psychiatrist"]["daily_capacity"]
    + clin_psych * PROFESSIONS["Clinical Psychologist"]["daily_capacity"]
    + couns_psych * PROFESSIONS["Counselling Psychologist"]["daily_capacity"]
    + reg_counsellors * PROFESSIONS["Registered Counsellor"]["daily_capacity"]
    + mh_nurses * PROFESSIONS["Mental Health Nurse"]["daily_capacity"]
)

team_daily_capacity = full_team_capacity - (prof_data["daily_capacity"] * MDT_DUTY_FRACTION) if principal_in_team else full_team_capacity

# --- YOUR REQUIRED CONSULTS ---
if team_daily_capacity > 0 and principal_in_team:
    your_fraction = your_daily_consults / team_daily_capacity
    your_required_consults = visits_per_day * your_fraction
elif principal_in_team:
    your_required_consults = visits_per_day
else:
    your_required_consults = 0

if your_required_consults > ffs_consults:
    consult_card_class = "consult-red"
    consult_status = "🔴 Above your FFS workload — add team members"
elif your_required_consults > your_daily_consults:
    consult_card_class = "consult-yellow"
    consult_status = f"⚠️ Improving — target is ≤ {your_daily_consults:.1f}/day"
else:
    consult_card_class = "consult-green"
    consult_status = "✅ Sustainable workload — room to grow population"

clinical_ftes = psychiatrist_fte + clin_psych + couns_psych + reg_counsellors + mh_nurses

# --- Average session length ---
total_session_weighted = (
    psychiatrist_fte * PROFESSIONS["Psychiatrist"]["avg_session_min"]
    + clin_psych * PROFESSIONS["Clinical Psychologist"]["avg_session_min"]
    + couns_psych * PROFESSIONS["Counselling Psychologist"]["avg_session_min"]
    + reg_counsellors * PROFESSIONS["Registered Counsellor"]["avg_session_min"]
    + mh_nurses * PROFESSIONS["Mental Health Nurse"]["avg_session_min"]
)
avg_session_min = total_session_weighted / max(1, clinical_ftes) if clinical_ftes > 0 else 0

# --- Population engaged ---
chw_non_overlap_engaged = int(chw_community_engaged * 0.8)
total_population_engaged = clinical_users + chw_non_overlap_engaged
pop_engaged_pct = (total_population_engaged / population * 100) if population > 0 else 0
clinical_contact_pct = (clinical_users / population * 100) if population > 0 else 0

# --- Supervision ---
total_supervisors = clin_psych + couns_psych
supervision_ratio = (reg_counsellors / total_supervisors) if total_supervisors > 0 else (float('inf') if reg_counsellors > 0 else 0)

# --- Derived (monthly) ---
income_diff_mo = cap_income_mo - ffs_income_mo
income_diff_pct = (income_diff_mo / ffs_income_mo * 100) if ffs_income_mo > 0 else 0
team_cost_pct = (total_team_cost_mo / cap_budget_mo * 100) if cap_budget_mo > 0 else 0
cos_pct_of_budget = (cap_cos_mo / cap_budget_mo * 100) if cap_budget_mo > 0 else 0
people_needing_meds = int(clinical_users * 0.6)
engagement_multiplier = total_population_engaged / max(1, ffs_annual_consultations)

# ============================================================
# SERVICE COVERAGE LOGIC
# ============================================================
warnings, dangers, successes = [], [], []
services_can, services_cannot, regulatory_warnings = [], [], []
team_illegal = False

if clin_psych > 0 or couns_psych > 0:
    services_can.append("✅ Mental health diagnosis")
    services_can.append("✅ Psychological therapy (individual)")
if clin_psych > 0:
    services_can.append("✅ Neuropsychological assessment")
    services_can.append("✅ Forensic assessment")
    services_can.append("✅ MDT case review leadership")
    services_can.append("✅ Clinical supervision of counsellors")
if couns_psych > 0 and clin_psych == 0:
    services_can.append("✅ Clinical supervision of counsellors")
if psychiatrist_fte > 0:
    services_can.append("✅ Psychiatric medication prescribing")
    services_can.append("✅ Severe mental illness management")
    services_can.append("✅ Treatment-resistant case management")
if mh_nurses > 0:
    services_can.append("✅ Crisis triage & stabilisation")
    services_can.append("✅ Medication adherence monitoring")
    services_can.append("✅ Routine screening (PHQ-9/GAD-7)")
if reg_counsellors > 0 and total_supervisors > 0:
    services_can.append("✅ Supportive counselling (supervised)")
    services_can.append("✅ Psychoeducation groups")
if auto_chws > 0:
    services_can.append("✅ Community outreach & screening")
    services_can.append("✅ Health promotion & awareness")
    services_can.append("✅ Home-based adherence support")

if psychiatrist_fte == 0:
    services_cannot.append("❌ Medication management (depression, anxiety, psychosis, bipolar)")
    services_cannot.append("❌ Severe / treatment-resistant mental illness")
    services_cannot.append("❌ ECT or medical psychiatric interventions")
if clin_psych == 0 and couns_psych == 0:
    services_cannot.append("❌ Mental health diagnosis (no psychologist)")
    services_cannot.append("❌ Psychological therapy")
    services_cannot.append("❌ MDT clinical leadership")
if clin_psych == 0:
    if couns_psych > 0:
        services_cannot.append("❌ Neuropsychological assessment (needs clin psych)")
        services_cannot.append("❌ Forensic assessment (needs clin psych)")
    elif couns_psych == 0:
        services_cannot.append("❌ Neuropsychological assessment")
        services_cannot.append("❌ Forensic assessment")
if mh_nurses == 0:
    services_cannot.append("❌ Crisis triage & medication support")
    services_cannot.append("❌ Routine PHQ-9/GAD-7 screening")
if auto_chws == 0:
    services_cannot.append("❌ Community outreach & prevention")
if reg_counsellors == 0 and clin_psych == 0 and couns_psych == 0:
    services_cannot.append("❌ Psychoeducation groups")

if reg_counsellors > 0 and total_supervisors == 0:
    regulatory_warnings.append("🔴 <b>HPCSA VIOLATION</b>: Registered Counsellors MUST be supervised by a psychologist.")
    team_illegal = True
if supervision_ratio > 10:
    regulatory_warnings.append(f"🔴 <b>HPCSA VIOLATION</b>: Supervision ratio {supervision_ratio:.1f}:1 exceeds maximum 10:1.")
    team_illegal = True
if auto_chws > 0 and clinical_ftes == 0:
    regulatory_warnings.append("🔴 CHWs cannot deliver clinical services alone.")
    team_illegal = True

# ============================================================
# SAFETY CHECKS
# ============================================================
if psychiatrist_fte == 0:
    dangers.append(f"🔴 <b>NO PSYCHIATRIST — NO MEDICATION</b>: ~{people_needing_meds:,} people needing psychiatric medication have no access. <i>→ Add even 0.05 FTE Psychiatrist in the sidebar.</i>")
if clin_psych == 0 and couns_psych == 0 and reg_counsellors == 0:
    dangers.append("🔴 <b>NO PSYCHOLOGICAL CAPACITY</b>: No psychologists or counsellors. <i>→ Add team members in the sidebar.</i>")
if clin_psych == 0 and couns_psych == 0 and reg_counsellors > 0:
    dangers.append("🔴 <b>UNSUPERVISED COUNSELLORS</b>: HPCSA requires psychologist supervision. <i>→ Add a psychologist in the sidebar.</i>")
if supervision_ratio > 10:
    dangers.append(f"🔴 <b>HPCSA Violation</b>: Supervision ratio {supervision_ratio:.1f}:1 exceeds 10:1. <i>→ Add psychologists or reduce counsellors.</i>")
elif 8 < supervision_ratio <= 10:
    warnings.append(f"⚠️ Supervision ratio {supervision_ratio:.1f}:1 — approaching HPCSA limit of 10:1")
elif reg_counsellors > 0 and total_supervisors > 0 and supervision_ratio <= 8:
    successes.append(f"✓ Supervision ratio {supervision_ratio:.1f}:1 — within HPCSA guidelines")
if mh_nurses == 0 and psychiatrist_fte == 0:
    warnings.append("⚠️ <b>No crisis capacity</b>: No MH Nurse or Psychiatrist for emergencies. <i>→ Consider adding MH Nurse.</i>")
if team_daily_capacity > 0 and visits_per_day > team_daily_capacity:
    overload_pct = ((visits_per_day / team_daily_capacity) - 1) * 100
    dangers.append(f"🔴 <b>Demand exceeds capacity</b>: {visits_per_day:.0f} visits/day needed vs team capacity {team_daily_capacity:.0f}/day ({overload_pct:.0f}% overload). <i>→ Add team members or reduce population.</i>")
elif team_daily_capacity > 0 and visits_per_day > team_daily_capacity * 0.85:
    warnings.append(f"⚠️ Team at {(visits_per_day/team_daily_capacity*100):.0f}% capacity — limited surge room")
if (team_cost_pct + cos_pct_of_budget) > 95:
    dangers.append(f"🔴 <b>Budget overrun</b>: Team ({team_cost_pct:.0f}%) + Cost of Services ({cos_pct_of_budget:.0f}%) exceed budget. <i>→ Reduce FTEs, increase capitation, or reduce cost of services %.</i>")
elif (team_cost_pct + cos_pct_of_budget) > 85:
    warnings.append(f"⚠️ Budget tight: Team + Cost of Services at {team_cost_pct + cos_pct_of_budget:.0f}% of budget")
elif total_team_cost_mo > 0 and (team_cost_pct + cos_pct_of_budget) < 70:
    successes.append(f"✓ Budget healthy: Team + CoS {team_cost_pct + cos_pct_of_budget:.0f}% — room for operations")
if psychiatrist_fte > 0 and (clin_psych > 0 or couns_psych > 0) and mh_nurses > 0:
    successes.append("✓ <b>Comprehensive team</b>: Prescribing + diagnosis + therapy + nursing")
if 6 <= supervision_ratio <= 10:
    successes.append("✓ Effective task-shifting: Leveraging counsellors within safe supervision")

# ============================================================
# VALUE SCORE + SUGGESTIONS
# ============================================================
value_score = 0
income_pts = 30 if cap_income_mo > ffs_income_mo * 1.15 else 22 if cap_income_mo > ffs_income_mo else 15 if cap_income_mo > ffs_income_mo * 0.9 else 5
value_score += income_pts

quality_pts = 40
if psychiatrist_fte == 0: quality_pts -= 15
if clin_psych == 0 and couns_psych == 0: quality_pts -= 12
if team_illegal: quality_pts -= 10
if mh_nurses == 0: quality_pts -= 3
quality_pts = max(0, quality_pts)
value_score += quality_pts

workload_pts = 15 if visits_per_day <= team_daily_capacity * 0.6 else 12 if visits_per_day <= team_daily_capacity * 0.8 else 8 if visits_per_day <= team_daily_capacity else 3
if team_daily_capacity == 0: workload_pts = 0
value_score += workload_pts

access_pts = 15 if pop_engaged_pct >= 10 else 12 if pop_engaged_pct >= 5 else 8 if pop_engaged_pct >= 3 else 5 if pop_engaged_pct >= 1.5 else 2
value_score += access_pts

suggestions = []
if income_pts <= 15:
    suggestions.append("💰 <b>Income</b>: Increase population/capitation rate, or use more lower-cost team members to reduce costs")
if quality_pts < 25:
    if psychiatrist_fte == 0:
        suggestions.append("💊 <b>Prescribing</b>: Add even 0.05–0.10 FTE psychiatrist — unlocks medication access for ~60% of users")
    if clin_psych == 0 and couns_psych == 0:
        suggestions.append("🧠 <b>Diagnosis</b>: Add a psychologist — essential for diagnosis, therapy, and MDT leadership")
    if team_illegal:
        suggestions.append("⚖️ <b>Regulatory</b>: Fix HPCSA violations — check supervision ratios and counsellor oversight")
    if mh_nurses == 0:
        suggestions.append("🏥 <b>Crisis</b>: Add a MH Nurse — enables crisis triage, screening, and medication monitoring")
if workload_pts < 8:
    suggestions.append("📋 <b>Workload</b>: Team is overloaded — add more clinicians or reduce population size")
if access_pts < 8:
    suggestions.append("🌱 <b>Reach</b>: Increase health promotion effort — CHWs extend engagement into the community")

has_coverage_issues = len(services_cannot) > 0
has_safety_issues = len(dangers) > 0
has_impact_issues = (cap_income_mo < ffs_income_mo) or (pop_engaged_pct < 3)

# ============================================================
# MAIN DISPLAY
# ============================================================

if team_illegal:
    st.markdown("""<div class="stop-box"><h3 style="margin:0; color: #ff6b6b;">⛔ TEAM CANNOT LEGALLY OPERATE</h3>
    <p style="margin: 0.5rem 0 0 0;">Current team composition violates HPCSA regulations. Adjust team members in the left panel.</p></div>""", unsafe_allow_html=True)
    for rw in regulatory_warnings:
        st.markdown(f'<div class="danger-box">{rw}</div>', unsafe_allow_html=True)
    st.markdown("---")

# ============================================================
# FFS BASELINE (monthly)
# ============================================================
ffs_limits = FFS_LIMITATIONS.get(profession, [])
limits_html = " · ".join(ffs_limits) if ffs_limits else "No specific limitations noted"
st.markdown(f"""
<div class="ffs-ref-card">
    <h4>💼 Your FFS Baseline — {profession}</h4>
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div><span class="ffs-ref-value">R{ffs_income_mo:,.0f}</span><span style="color: #6c757d;"> /month net income</span></div>
        <div style="color: #6c757d; font-size: 0.9rem;">
            {ffs_consults} consults/day &times; R{ffs_fee} &times; {WORKING_DAYS} days &divide; 12
            &minus; {ffs_costs_pct}% cost of services (R{ffs_cos_mo:,.0f}/mo)
        </div>
    </div>
    <div class="ffs-limits">
        <b>Solo FFS limitations:</b> {limits_html}
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# CAPITATION TEAM MODEL — HERO DASHBOARD (monthly)
# ============================================================
st.markdown("## 🏥 Capitation Team Model")

if principal_in_team:
    st.caption(f"📋 You ({profession}) spend {int(MDT_DUTY_FRACTION*100)}% of time on MDT support, supervision & protocols → "
               f"your optimal capacity: {your_daily_consults:.1f} consults/day (from {your_capacity_raw}/day)")

col_income, col_consults = st.columns([1, 1])

with col_income:
    if cap_income_mo > ffs_income_mo:
        card_class = "income-green"
        comparison_text = f"+R{income_diff_mo:,.0f} ({income_diff_pct:+.1f}%) vs FFS"
    elif cap_income_mo >= 0:
        card_class = "income-yellow"
        comparison_text = f"R{income_diff_mo:,.0f} ({income_diff_pct:.1f}%) below FFS"
    else:
        card_class = "income-red"
        comparison_text = f"R{income_diff_mo:,.0f} — NET LOSS"
    st.markdown(f"""
    <div class="income-card {card_class}">
        <p style="margin:0; font-size: 0.9rem;">Monthly Capitation Income</p>
        <p class="income-value">R{cap_income_mo:,.0f}</p>
        <p style="margin:0; font-size: 0.85rem;">{comparison_text}</p>
        <p style="margin:0.3rem 0 0 0; font-size: 0.8rem; opacity: 0.85;">
            Budget R{cap_budget_mo:,.0f} &minus; Team R{total_team_cost_mo:,.0f}
            &minus; Cost of Services R{cap_cos_mo:,.0f}</p>
    </div>""", unsafe_allow_html=True)

with col_consults:
    st.markdown(f"""
    <div class="consult-card {consult_card_class}">
        <p style="margin:0; font-size: 0.9rem;">Your Required Consults/Day</p>
        <p class="consult-value">{your_required_consults:.1f}</p>
        <p style="margin:0; font-size: 0.85rem;">{consult_status}</p>
        <p style="margin:0.3rem 0 0 0; font-size: 0.8rem; opacity: 0.85;">
            FFS: {ffs_consults}/day &nbsp;|&nbsp; Your capacity: {your_daily_consults:.1f}/day &nbsp;|&nbsp;
            Team: {team_daily_capacity:.0f}/day &nbsp;|&nbsp; Demand: {visits_per_day:.0f}/day</p>
    </div>""", unsafe_allow_html=True)

# Secondary metrics row
m1, m2, m3 = st.columns(3)
with m1:
    eng_cls = "engaged-green" if pop_engaged_pct >= 5 else "engaged-amber" if pop_engaged_pct >= 3 else "engaged-red"
    eng_icon = "✅" if pop_engaged_pct >= 5 else "⚠️" if pop_engaged_pct >= 3 else "🔴"
    st.markdown(f"""<div style="text-align: center;">
        <p style="font-size: 0.85rem; color: #555; margin-bottom: 2px;">Population Engaged</p>
        <p style="font-size: 2rem; font-weight: bold; margin: 0;"><span class="{eng_cls}">{pop_engaged_pct:.1f}%</span></p>
        <p style="font-size: 0.75rem; color: #888; margin-top: 2px;">{eng_icon} {total_population_engaged:,} of {population:,}</p>
    </div>""", unsafe_allow_html=True)
with m2:
    if avg_session_min > 0:
        sq = "Deep" if avg_session_min >= 40 else "Balanced" if avg_session_min >= 25 else "Brief"
        st.markdown(f"""<div style="text-align: center;">
            <p style="font-size: 0.85rem; color: #555; margin-bottom: 2px;">Avg Session Length</p>
            <p style="font-size: 2rem; font-weight: bold; margin: 0;">{avg_session_min:.0f} min</p>
            <p style="font-size: 0.75rem; color: #888; margin-top: 2px;">{sq} engagement</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.metric("Avg Session", "—", help="No clinical staff")
with m3:
    if team_daily_capacity > 0:
        util_pct = (visits_per_day / team_daily_capacity) * 100
        demand_icon = "✅" if util_pct <= 85 else "⚠️" if util_pct <= 100 else "🔴"
        st.markdown(f"""<div style="text-align: center;">
            <p style="font-size: 0.85rem; color: #555; margin-bottom: 2px;">Team Utilisation</p>
            <p style="font-size: 2rem; font-weight: bold; margin: 0;">{util_pct:.0f}%</p>
            <p style="font-size: 0.75rem; color: #888; margin-top: 2px;">{demand_icon} {visits_per_day:.0f} demand / {team_daily_capacity:.0f} capacity</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.metric("Team Utilisation", "—", help="No team capacity")

# ============================================================
# SERVICE COVERAGE
# ============================================================
st.markdown("---")
st.markdown("## 🩺 Service Coverage")
if has_coverage_issues:
    st.markdown(f'<div class="flag-box">⚠️ <b>{len(services_cannot)} service gap(s) detected</b> — adjust team composition in the left panel to address gaps.</div>', unsafe_allow_html=True)

col_can, col_cannot = st.columns(2)
with col_can:
    if services_can:
        st.markdown("<div class='coverage-can'><b>Services Your Team CAN Deliver:</b><br><br>" + "<br>".join(services_can) + "</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='coverage-cannot'><b>⛔ No services can be delivered</b><br>Team has no clinical capacity.</div>", unsafe_allow_html=True)
with col_cannot:
    if services_cannot:
        st.markdown("<div class='coverage-cannot'><b>Services Your Team CANNOT Deliver:</b><br><br>" + "<br>".join(services_cannot) + "</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='coverage-can'><b>✅ Full service coverage</b><br>Comprehensive mental health services.</div>", unsafe_allow_html=True)
    if regulatory_warnings and not team_illegal:
        for rw in regulatory_warnings:
            st.markdown(f"<div class='coverage-warn'>{rw}</div>", unsafe_allow_html=True)

# ============================================================
# IMPACT INSIGHTS (monthly)
# ============================================================
st.markdown("---")
st.markdown("## 💡 Impact Insights")
if has_impact_issues:
    flag_parts = []
    if cap_income_mo < ffs_income_mo:
        flag_parts.append("income below FFS")
    if pop_engaged_pct < 3:
        flag_parts.append("low population engagement")
    st.markdown(f'<div class="flag-box">💡 <b>Areas to improve:</b> {", ".join(flag_parts)}. Adjust team, capitation rate, or health promotion in the left panel.</div>', unsafe_allow_html=True)

insight_cols = st.columns(2)
with insight_cols[0]:
    if cap_income_mo > ffs_income_mo:
        st.markdown(f"""<div class="success-box insight-impact">
            💰 <b>Earn R{income_diff_mo:,.0f} MORE per month</b> while engaging
            <b>{total_population_engaged:,} people/year</b> — a <b>{engagement_multiplier:.1f}× multiplier</b>
            over your {ffs_annual_consultations:,} FFS consultations.</div>""", unsafe_allow_html=True)
    elif cap_income_mo >= 0:
        st.markdown(f"""<div class="warning-box insight-impact">
            💰 You earn <b>R{abs(income_diff_mo):,.0f} less per month</b> than FFS — but engage
            <b>{total_population_engaged:,} people/year</b> ({engagement_multiplier:.1f}× your FFS reach).
            <i>Consider adjusting team composition or capitation rate.</i></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="danger-box insight-impact">
            🚨 <b>Net loss of R{abs(cap_income_mo):,.0f}/month</b>. Team + service costs exceed capitation budget.
            <i>Reduce FTEs, increase population/capitation rate, or lower cost of services %.</i></div>""", unsafe_allow_html=True)

    if psychiatrist_fte == 0:
        st.markdown(f"""<div class="danger-box insight-impact">
            💊 <b>Medication Gap:</b> ~{people_needing_meds:,} people needing psychiatric medication have no access.
            60% of MH conditions require pharmacotherapy. <i>Add even 0.05 FTE psychiatrist.</i></div>""", unsafe_allow_html=True)
    else:
        psych_cap = int(psychiatrist_fte * PROFESSIONS["Psychiatrist"]["daily_capacity"] * WORKING_DAYS)
        st.markdown(f"""<div class="success-box insight-impact">
            💊 <b>Medication covered:</b> Psychiatrist at {psychiatrist_fte:.2f} FTE provides
            ~{psych_cap:,} consultations/year for {people_needing_meds:,} needing pharmacotherapy.</div>""", unsafe_allow_html=True)

with insight_cols[1]:
    if chw_community_engaged > 0:
        st.markdown(f"""<div class="info-box insight-impact">
            🏘️ <b>Capitation Reach:</b> Your team clinically sees <b>{clinical_users:,} people/year</b>,
            plus community outreach engages <b>{chw_non_overlap_engaged:,} more</b> —
            total <b>{total_population_engaged:,}</b> ({engagement_multiplier:.1f}× FFS reach).</div>""", unsafe_allow_html=True)

    if avg_session_min >= 40:
        st.markdown(f"""<div class="success-box insight-impact">
            ⏱️ <b>Deep engagement:</b> Average <b>{avg_session_min:.0f} min</b>
            — therapeutic-depth sessions, not brief med checks.</div>""", unsafe_allow_html=True)
    elif avg_session_min >= 25:
        st.markdown(f"""<div class="info-box insight-impact">
            ⏱️ <b>Balanced sessions:</b> Average <b>{avg_session_min:.0f} min</b> —
            good mix of therapy depth and throughput.</div>""", unsafe_allow_html=True)
    elif avg_session_min > 0:
        st.markdown(f"""<div class="warning-box insight-impact">
            ⏱️ <b>Brief sessions:</b> Average only <b>{avg_session_min:.0f} min</b> —
            high volume but shallow. <i>Consider adding psychologists for depth.</i></div>""", unsafe_allow_html=True)

    if health_promo > 0:
        util_saved = utilization_rate - effective_utilization
        visits_saved = int(population * (util_saved / 100) * VISITS_PER_USER)
        st.markdown(f"""<div class="info-box insight-impact">
            🌱 <b>Prevention saves {visits_saved:,} visits/year</b> ({util_saved:.1f}% reduction).
            {auto_chws:.1f} CHWs reach ~{chw_community_engaged:,} people via screening &amp; psychoeducation.</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="warning-box insight-impact">
            🌱 <b>No prevention investment.</b> Full {utilization_rate:.1f}% utilisation applies.
            <i>Try the Health Promotion slider in the left panel.</i></div>""", unsafe_allow_html=True)

    estimated_prevalence = population * 0.30
    gap_closed_pct = (total_population_engaged / estimated_prevalence * 100) if estimated_prevalence > 0 else 0
    st.markdown(f"""<div class="info-box insight-impact">
        📊 <b>Treatment gap:</b> Of ~{int(estimated_prevalence):,} with lifetime MH conditions,
        your team engages <b>{total_population_engaged:,} ({gap_closed_pct:.1f}%)</b>. SA average: only 9%.</div>""", unsafe_allow_html=True)

# ============================================================
# SAFETY CHECKS
# ============================================================
if dangers or warnings or successes:
    st.markdown("---")
    st.markdown("## ⚠️ Safety Checks")
    if has_safety_issues:
        st.markdown(f'<div class="flag-box">🔴 <b>{len(dangers)} critical issue(s)</b> require attention — see details below and adjust in the left panel.</div>', unsafe_allow_html=True)
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
    sc = "#28a745" if value_score >= 75 else "#e6a817" if value_score >= 55 else "#dc3545"
    sl = "Excellent" if value_score >= 75 else "Moderate" if value_score >= 55 else "Needs Work"
    st.markdown(f"""<div style="background: linear-gradient(135deg, #1E5F8A 0%, #2E8B57 100%);
        padding: 2rem; border-radius: 15px; text-align: center; color: white;">
        <h3 style="margin: 0;">Value Score</h3>
        <p style="font-size: 3.5rem; font-weight: bold; margin: 0.5rem 0; color: {sc};">{value_score}/100</p>
        <p style="margin: 0; opacity: 0.9;">{sl} — Quality ÷ Cost Balance</p></div>""", unsafe_allow_html=True)

with col_breakdown:
    st.markdown("#### Score Breakdown")
    bd = {'Component': ['Income vs FFS (30)', 'Service Coverage (40)', 'Workload Balance (15)', 'Population Engaged (15)'],
          'Points': [income_pts, quality_pts, workload_pts, access_pts], 'Max': [30, 40, 15, 15]}
    fig_bd = go.Figure()
    fig_bd.add_trace(go.Bar(y=bd['Component'], x=bd['Points'], orientation='h', name='Earned',
        marker_color=['#28a745' if p >= m*0.7 else '#e6a817' if p >= m*0.4 else '#dc3545' for p, m in zip(bd['Points'], bd['Max'])],
        text=[f"{p}/{m}" for p, m in zip(bd['Points'], bd['Max'])], textposition='inside'))
    fig_bd.update_layout(height=220, margin=dict(l=0, r=20, t=10, b=10), xaxis=dict(range=[0, 45]), showlegend=False)
    st.plotly_chart(fig_bd, use_container_width=True)

    if suggestions:
        st.markdown("**💡 How to improve your score:**")
        for s in suggestions:
            st.markdown(f'<div class="suggest-box">{s}</div>', unsafe_allow_html=True)

# ============================================================
# COMPARISON CHART (monthly income)
# ============================================================
st.markdown("---")
st.markdown("## 📊 Side-by-Side Comparison")

ffs_services = 1
cap_services = len(services_can)

fig_c = go.Figure()
fig_c.add_trace(go.Bar(name='FFS (Solo)',
    x=['Monthly Income (R)', 'Your Consults/Day', 'People Reached/Year', 'Services Available'],
    y=[ffs_income_mo/1e3, ffs_consults, ffs_annual_consultations/1000, ffs_services],
    marker_color='#6c757d',
    text=[f'R{ffs_income_mo/1e3:.0f}k', f'{ffs_consults}', f'{ffs_annual_consultations/1000:.1f}k', f'{ffs_services}'],
    textposition='outside'))
cbc = '#28a745' if cap_income_mo >= ffs_income_mo else '#e6a817' if cap_income_mo >= 0 else '#dc3545'
fig_c.add_trace(go.Bar(name='Capitation (Team)',
    x=['Monthly Income (R)', 'Your Consults/Day', 'People Reached/Year', 'Services Available'],
    y=[cap_income_mo/1e3, your_required_consults, total_population_engaged/1000, cap_services],
    marker_color=cbc,
    text=[f'R{cap_income_mo/1e3:.0f}k', f'{your_required_consults:.1f}', f'{total_population_engaged/1000:.1f}k', f'{cap_services}'],
    textposition='outside'))
fig_c.update_layout(barmode='group', height=380, margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02), showlegend=True)
st.plotly_chart(fig_c, use_container_width=True)

# ============================================================
# TEAM COST & SERVICE COST BREAKDOWN (monthly)
# ============================================================
st.markdown("---")
st.markdown("## 👥 Cost Breakdown (Monthly)")
col_table, col_pie = st.columns([1, 1])
with col_table:
    fte_map = {"Psychiatrist": psychiatrist_fte, "Clinical Psychologist": clin_psych,
        "Counselling Psychologist": couns_psych, "Registered Counsellor": reg_counsellors,
        "Mental Health Nurse": mh_nurses, "Community Health Worker": auto_chws}
    rows = []
    for k, v in team_costs.items():
        if v > 0:
            v_mo = v / 12
            if k == "Community Health Worker":
                rows.append({'Role': k, 'FTE': fte_map[k], 'Capacity': 'Community', 'Session': '—', 'Monthly Cost': f"R{v_mo:,.0f}"})
            else:
                cap_note = f"{PROFESSIONS[k]['daily_capacity']}/day"
                if k == profession and principal_in_team:
                    cap_note = f"{PROFESSIONS[k]['daily_capacity']}/day (you: {your_daily_consults:.1f})*"
                rows.append({'Role': k, 'FTE': fte_map[k], 'Capacity': cap_note,
                    'Session': f"{PROFESSIONS[k]['avg_session_min']} min", 'Monthly Cost': f"R{v_mo:,.0f}"})
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if principal_in_team:
            st.caption(f"*Your effective capacity after {int(MDT_DUTY_FRACTION*100)}% MDT/supervision time")

    st.markdown(f"""| | |
|---|---|
| **Team Cost** | **R{total_team_cost_mo:,.0f}/month** |
| **Cost of Services** | **R{cap_cos_mo:,.0f}/month** |
| ↳ R{cost_per_consult:,.0f}/consult × {total_visits_mo:,.0f} clinic visits/mo | |
| Budget Available | R{cap_budget_mo:,.0f}/month |
| Team % of Budget | {team_cost_pct:.1f}% |
| CoS % of Budget | {cos_pct_of_budget:.1f}% |
| **Remaining (Your Income)** | **R{cap_income_mo:,.0f}/month** |
| **Team Daily Capacity** | **{team_daily_capacity:.0f} consults/day** |
| **Demand** | **{visits_per_day:.0f} visits/day** |
| **Avg Session Length** | **{avg_session_min:.0f} min** |""")

with col_pie:
    pie_data = {k: v/12 for k, v in team_costs.items() if v > 0}
    pie_data["Cost of Services"] = cap_cos_mo
    if sum(pie_data.values()) > 0:
        fig_p = px.pie(values=list(pie_data.values()), names=list(pie_data.keys()),
            color_discrete_sequence=px.colors.sequential.Teal, hole=0.4)
        fig_p.update_layout(height=340, margin=dict(l=20, r=20, t=30, b=20),
            showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
        st.plotly_chart(fig_p, use_container_width=True)

# ============================================================
# SUBMIT SCENARIO (server-side CSV — no email)
# ============================================================
st.markdown("---")
st.markdown("## 📩 Submit Your Scenario")

summary_text = (
    f"{participant_name or 'Anonymous'} | {profession} | "
    f"FFS R{ffs_income_mo:,.0f}/mo → Cap R{cap_income_mo:,.0f}/mo ({income_diff_pct:+.1f}%) | "
    f"Pop {population:,} @ R{capitation}/yr | Engaged {pop_engaged_pct:.1f}% ({total_population_engaged:,}) | "
    f"Your consults {your_required_consults:.1f}/day (capacity {your_daily_consults:.1f}) | "
    f"Team cap {team_daily_capacity:.0f}/day | "
    f"CoS R{cap_cos_mo:,.0f}/mo | Avg {avg_session_min:.0f}min | Score {value_score}/100 | "
    f"Team: Psych {psychiatrist_fte}, ClinP {clin_psych}, CounsP {couns_psych}, "
    f"RC {reg_counsellors}, MHN {mh_nurses}, CHW {auto_chws:.1f} | "
    f"Promo {health_promo}%"
)

st.markdown("**Your Scenario Summary:**")
st.code(summary_text, language=None)

can_submit = bool(participant_name and participant_name.strip())

if not participant_name:
    st.warning("⚠️ Please enter your **name** in the sidebar to submit.")

if can_submit:
    if st.button("✅ Submit My Scenario", type="primary", use_container_width=True):
        # Build flat row for CSV
        row = {
            "timestamp": datetime.now().isoformat(),
            "name": participant_name.strip(),
            "profession": profession,
            "ffs_fee": ffs_fee,
            "ffs_consults_per_day": ffs_consults,
            "ffs_costs_pct": ffs_costs_pct,
            "ffs_income_monthly": round(ffs_income_mo),
            "population": population,
            "capitation_rate_annual": capitation,
            "utilisation_rate": round(utilization_rate, 1),
            "effective_utilisation": round(effective_utilization, 2),
            "health_promo_pct": health_promo,
            "psychiatrist_fte": psychiatrist_fte,
            "clin_psych_fte": clin_psych,
            "couns_psych_fte": couns_psych,
            "reg_counsellors": reg_counsellors,
            "mh_nurses_fte": mh_nurses,
            "auto_chws": auto_chws,
            "cap_budget_monthly": round(cap_budget_mo),
            "team_cost_monthly": round(total_team_cost_mo),
            "cost_of_services_monthly": round(cap_cos_mo),
            "cap_income_monthly": round(cap_income_mo),
            "income_diff_monthly": round(income_diff_mo),
            "income_diff_pct": round(income_diff_pct, 1),
            "clinical_users": clinical_users,
            "total_population_engaged": total_population_engaged,
            "pop_engaged_pct": round(pop_engaged_pct, 1),
            "your_required_consults": round(your_required_consults, 1),
            "your_daily_capacity": round(your_daily_consults, 1),
            "team_daily_capacity": round(team_daily_capacity),
            "cost_per_consult": round(cost_per_consult),
            "avg_session_min": round(avg_session_min),
            "value_score": value_score,
            "team_illegal": team_illegal,
            "services_available": len(services_can),
            "services_missing": len(services_cannot),
        }
        # Append to CSV
        try:
            file_exists = os.path.exists(SUBMISSIONS_FILE)
            with open(SUBMISSIONS_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
            st.success(f"✅ **Submitted!** Thank you {participant_name}. Your scenario has been recorded for workshop analysis.")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Submission failed: {e}. Please notify the facilitator.")
else:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: #f0f0f0; border-radius: 8px; color: #999;">
        ✅ Submit My Scenario<br>
        <span style="font-size: 0.85rem;">Enter your name in the sidebar to enable</span>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# INTERNATIONAL BENCHMARKS
# ============================================================
st.markdown("---")
tgr = max(0, 100 - (total_population_engaged / max(1, population * 0.3) * 100))
eng_badge = f'<span class="engaged-green">{pop_engaged_pct:.1f}%</span>' if pop_engaged_pct >= 5 else \
    f'<span class="engaged-amber">{pop_engaged_pct:.1f}%</span>' if pop_engaged_pct >= 3 else \
    f'<span class="engaged-red">{pop_engaged_pct:.1f}%</span>'
eng_verdict = "meets WHO target" if pop_engaged_pct >= 5 else "below WHO 5% target" if pop_engaged_pct >= 3 else "critically below WHO target"
st.markdown(f"""<div class="benchmark-box">
    <b>📊 International Benchmarks</b><br><br>
    <b>WHO target:</b> ~5% annual MH service utilisation &nbsp;|&nbsp;
    <b>SA treatment gap:</b> 91% (SASH study, Herman et al. 2009) &nbsp;|&nbsp;
    <b>SA MH budget:</b> ~5% vs 10-12% international norm<br><br>
    <b>Your model:</b> {eng_badge} population engaged — {eng_verdict}
    &nbsp;|&nbsp; Clinical contact: {clinical_contact_pct:.1f}%
    &nbsp;|&nbsp; Treatment gap reduced to <b>{tgr:.0f}%</b>
    &nbsp;|&nbsp; Engagement multiplier: <b>{engagement_multiplier:.1f}×</b> over FFS
</div>""", unsafe_allow_html=True)

# ============================================================
# ASSUMPTIONS & LIMITATIONS
# ============================================================
st.markdown("---")
st.markdown(f"""<div class="assumptions-panel">
    <h4 style="margin-top: 0;">📋 Assumptions</h4>
    <b>Working days:</b> {WORKING_DAYS}/yr &nbsp;|&nbsp;
    <b>Visits per user:</b> {VISITS_PER_USER}/yr avg &nbsp;|&nbsp;
    <b>Utilisation floor:</b> {UTILISATION_FLOOR}% (irreducible chronic demand) &nbsp;|&nbsp;
    <b>Supervision:</b> HPCSA max 10:1 &nbsp;|&nbsp;
    <b>MDT deduction:</b> {int(MDT_DUTY_FRACTION*100)}% of principal user's time for supervision, MDT reviews, protocol development &nbsp;|&nbsp;
    <b>CHW reach:</b> {CHW_ENGAGEMENT_PER_YEAR:,}/CHW/yr (SA WBOT norms); 20% overlap with clinical users deducted &nbsp;|&nbsp;
    <b>Medication need:</b> ~60% of MH users (WHO) &nbsp;|&nbsp;
    <b>MH prevalence:</b> 30% lifetime (SASH study) &nbsp;|&nbsp;
    <b>Cost of Services (capitation):</b> FFS cost/consult × clinical team visits (excl CHW) &nbsp;|&nbsp;
    <b>All figures displayed monthly</b> (annual ÷ 12)
    <br><br>
    <h4 style="margin-top: 0;">⚠️ Limitations</h4>
    <b>6 of 12 PHC roles modelled</b> — excludes PHC doctors, professional nurses, social workers, OTs, clinical associates, lay counsellors, enrolled nurses &nbsp;|&nbsp;
    <b>Individual sessions only</b> — group therapy multiplier not modelled (a group of 8-12 would significantly increase throughput) &nbsp;|&nbsp;
    <b>Service types collapsed</b> — assessment, therapy, crisis, family/couples, and community work all counted as "visits" &nbsp;|&nbsp;
    <b>Static utilisation</b> — no seasonal or epidemic variation &nbsp;|&nbsp;
    <b>CTC estimates</b> — actual rates may differ
</div>""", unsafe_allow_html=True)

# ============================================================
# ADMIN: Workshop Facilitator Download
# ============================================================
st.markdown("---")
with st.expander("🔒 Workshop Admin"):
    admin_pw = st.text_input("Admin Password", type="password", key="admin_pw")
    if admin_pw == ADMIN_PASSWORD:
        if os.path.exists(SUBMISSIONS_FILE):
            with open(SUBMISSIONS_FILE, 'r') as f:
                csv_data = f.read()
            lines = csv_data.strip().split('\n')
            count = len(lines) - 1 if len(lines) > 1 else 0
            st.success(f"📊 **{count} submission(s)** recorded")
            st.download_button("📥 Download All Submissions (CSV)", csv_data,
                file_name=f"workshop_submissions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv")
            st.dataframe(pd.read_csv(SUBMISSIONS_FILE), use_container_width=True)
        else:
            st.info("No submissions yet.")
    elif admin_pw:
        st.error("Incorrect password.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧠 <b>Mental Health Capitation Simulator</b> v7</p>
    <p style="font-size: 0.85rem;">PsySSA Workshop | 3 February 2026</p>
    <p style="font-size: 0.8rem; opacity: 0.8;">Prof Shabir Moosa | Department of Family Medicine &amp; PHC<br>University of the Witwatersrand</p>
</div>""", unsafe_allow_html=True)
