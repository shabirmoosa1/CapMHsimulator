"""
🧠 NHI Mental Health: FFS vs Capitation Simulator
Simplified Version for Health Professionals
For PsySSA Workshop - February 3, 2026

Author: Built for Prof Shabir Moosa, NHI Branch
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
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

# Custom CSS - Clean Professional Style
st.markdown("""
<style>
    :root {
        --primary-blue: #1E5F8A;
        --secondary-green: #28a745;
        --warning-red: #dc3545;
        --neutral-gray: #6c757d;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1E5F8A 0%, #2E8B57 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
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
    
    .comparison-better {
        color: #28a745;
        font-weight: bold;
    }
    
    .comparison-worse {
        color: #dc3545;
        font-weight: bold;
    }
    
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
    
    .badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-weight: bold;
        font-size: 0.85rem;
    }
    
    .badge-gold { background: linear-gradient(135deg, #f5af19, #f12711); color: white; }
    .badge-green { background: linear-gradient(135deg, #11998e, #38ef7d); color: white; }
    .badge-blue { background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; }
    
    .assumptions-panel {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        font-size: 0.85rem;
        color: #495057;
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
        "ctc": 900000,
        "can_supervise": True,
        "scope": "Full diagnostic & therapeutic scope"
    },
    "Counselling Psychologist": {
        "default_fee": 1000,
        "default_patients": 7,
        "default_costs": 25,
        "ctc": 800000,
        "can_supervise": True,
        "scope": "Therapeutic interventions, no neuro/forensic"
    },
    "Educational Psychologist": {
        "default_fee": 1100,
        "default_patients": 5,
        "default_costs": 30,
        "ctc": 850000,
        "can_supervise": True,
        "scope": "Learning & developmental assessments"
    },
    "Registered Counsellor": {
        "default_fee": 650,
        "default_patients": 8,
        "default_costs": 20,
        "ctc": 450000,
        "can_supervise": False,
        "scope": "Supportive counselling, no diagnosis"
    },
    "Mental Health Nurse": {
        "default_fee": 450,
        "default_patients": 12,
        "default_costs": 15,
        "ctc": 550000,
        "can_supervise": False,
        "scope": "Screening, medication support, triage"
    }
}

# Team CTC rates
TEAM_CTC = {
    "Clinical Psychologist": 900000,
    "Counselling Psychologist": 800000,
    "Registered Counsellor": 450000,
    "Mental Health Nurse": 550000,
    "Community Health Worker": 120000
}

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🧠 NHI Mental Health Simulator</h1>
    <p style="font-size: 1.1rem; margin: 0;">Compare Your FFS Income vs Capitation Team Model</p>
    <p style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">February 2026 | National Health Insurance</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR - INPUTS
# ============================================================
with st.sidebar:
    st.markdown("## 👤 Your Profile")
    
    # Profession Selection
    profession = st.selectbox(
        "Your Profession",
        options=list(PROFESSIONS.keys()),
        index=0,
        help="Select your current profession for FFS baseline"
    )
    
    prof_data = PROFESSIONS[profession]
    
    st.markdown("---")
    
    # ========== FFS SECTION ==========
    st.markdown("## 💼 Your Current FFS Practice")
    
    ffs_patients = st.slider(
        "Patients per Day",
        min_value=1,
        max_value=40,
        value=prof_data["default_patients"],
        help="Average number of patients you see daily"
    )
    
    ffs_fee = st.slider(
        "Average Fee (R)",
        min_value=100,
        max_value=2500,
        value=prof_data["default_fee"],
        step=50,
        format="R%d"
    )
    
    ffs_costs_pct = st.slider(
        "Cost of Sales (%)",
        min_value=0,
        max_value=100,
        value=prof_data["default_costs"],
        help="Room rental, admin, materials as % of turnover"
    )
    
    st.markdown("---")
    
    # ========== CAPITATION SECTION ==========
    st.markdown("## 🏥 Capitation Scenario")
    
    population = st.slider(
        "Population Covered",
        min_value=1000,
        max_value=100000,
        value=80000,
        step=1000,
        format="%d"
    )
    
    capitation = st.slider(
        "Capitation Rate (R/person/year)",
        min_value=10,
        max_value=500,
        value=120,
        step=10,
        format="R%d"
    )
    
    utilization_base = st.slider(
        "Base Utilization (%)",
        min_value=1.0,
        max_value=10.0,
        value=4.0,
        step=0.5,
        format="%.1f%%",
        help="% of population accessing services annually"
    )
    
    st.markdown("---")
    
    # ========== HEALTH PROMOTION ==========
    st.markdown("## 🌱 Health Promotion Effort")
    
    health_promo = st.slider(
        "Prevention Investment (%)",
        min_value=0,
        max_value=50,
        value=10,
        step=5,
        help="Higher investment reduces utilization over time"
    )
    
    # Calculate utilization reduction (5-10% reduction per 10% effort)
    utilization_reduction = health_promo * 0.075  # 7.5% reduction per 10% effort (midpoint of 5-10%)
    effective_utilization = utilization_base * (1 - utilization_reduction / 100)
    
    if health_promo > 0:
        st.info(f"📉 Utilization reduced: {utilization_base:.1f}% → {effective_utilization:.1f}%")
    
    st.markdown("---")
    
    # ========== TEAM COMPOSITION ==========
    st.markdown("## 👥 Capitation Team (FTE)")
    
    clin_psych = st.slider(
        "Clinical Psychologists",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.25,
        format="%.2f"
    )
    
    couns_psych = st.slider(
        "Counselling Psychologists",
        min_value=0.0,
        max_value=2.0,
        value=0.5,
        step=0.25,
        format="%.2f"
    )
    
    reg_counsellors = st.slider(
        "Registered Counsellors",
        min_value=0,
        max_value=25,
        value=10,
        step=1,
        help="HPCSA: Max 10:1 supervision ratio"
    )
    
    mh_nurses = st.slider(
        "Mental Health Nurses",
        min_value=0.0,
        max_value=3.0,
        value=1.0,
        step=0.5,
        format="%.1f"
    )
    
    chws = st.slider(
        "Community Health Workers",
        min_value=0,
        max_value=10,
        value=4,
        step=1
    )
    
    st.markdown("---")
    
    # Edit CTC rates
    st.markdown("## 💵 Edit Annual Salaries")
    with st.expander("Adjust CTC Rates (R)"):
        ctc_clin = st.number_input("Clinical Psych CTC", value=TEAM_CTC["Clinical Psychologist"], step=50000)
        ctc_couns = st.number_input("Counselling Psych CTC", value=TEAM_CTC["Counselling Psychologist"], step=50000)
        ctc_reg = st.number_input("Registered Counsellor CTC", value=TEAM_CTC["Registered Counsellor"], step=25000)
        ctc_nurse = st.number_input("MH Nurse CTC", value=TEAM_CTC["Mental Health Nurse"], step=25000)
        ctc_chw = st.number_input("CHW CTC", value=TEAM_CTC["Community Health Worker"], step=10000)

# ============================================================
# CALCULATIONS
# ============================================================

# FFS Calculations
working_days = 250
ffs_turnover = ffs_patients * ffs_fee * working_days
ffs_costs = ffs_turnover * (ffs_costs_pct / 100)
ffs_income = ffs_turnover - ffs_costs

# Capitation Calculations
cap_total_budget = population * capitation

# Team costs
team_costs = {
    "Clinical Psychologist": clin_psych * ctc_clin,
    "Counselling Psychologist": couns_psych * ctc_couns,
    "Registered Counsellor": reg_counsellors * ctc_reg,
    "Mental Health Nurse": mh_nurses * ctc_nurse,
    "Community Health Worker": chws * ctc_chw
}
total_team_cost = sum(team_costs.values())

# Other costs (admin, consumables) - estimate 15% of remaining budget
remaining_after_team = cap_total_budget - total_team_cost
other_costs = max(0, remaining_after_team * 0.15)

cap_total_costs = total_team_cost + other_costs
cap_income = cap_total_budget - cap_total_costs

# Service metrics
users_covered = int(population * (effective_utilization / 100))
visits_per_user = 4  # Standard assumption
total_visits = users_covered * visits_per_user
visits_per_day = total_visits / working_days

# Supervision ratios
total_supervisors = clin_psych + couns_psych
if total_supervisors > 0:
    supervision_ratio = reg_counsellors / total_supervisors
else:
    supervision_ratio = float('inf') if reg_counsellors > 0 else 0

# Income comparison
income_difference = cap_income - ffs_income
income_difference_pct = (income_difference / ffs_income * 100) if ffs_income > 0 else 0

# Workload comparison
ffs_workload = ffs_patients
cap_workload = visits_per_day / max(1, (clin_psych + couns_psych + reg_counsellors + mh_nurses)) if (clin_psych + couns_psych + reg_counsellors + mh_nurses) > 0 else visits_per_day

# ============================================================
# COMPETENCY WARNINGS
# ============================================================
warnings = []
dangers = []
successes = []

# HPCSA Supervision ratio check (max 10:1)
if supervision_ratio > 10:
    dangers.append(f"🔴 **HPCSA Violation:** Supervision ratio {supervision_ratio:.1f}:1 exceeds maximum 10:1. Add more psychologists or reduce counsellors.")
elif supervision_ratio > 8:
    warnings.append(f"⚠️ **Supervision stretched:** Ratio {supervision_ratio:.1f}:1 approaching HPCSA limit of 10:1")
elif reg_counsellors > 0 and total_supervisors > 0:
    successes.append(f"✓ Supervision ratio {supervision_ratio:.1f}:1 within HPCSA guidelines")

# No supervisors but have counsellors
if reg_counsellors > 0 and total_supervisors == 0:
    dangers.append("🔴 **No supervision:** Registered Counsellors require psychologist supervision. Add Clinical or Counselling Psychologists.")

# No crisis capacity
if mh_nurses == 0 and clin_psych == 0:
    warnings.append("⚠️ **Limited crisis capacity:** Consider adding MH Nurse or Clinical Psychologist for emergencies")

# CHW alone cannot deliver clinical services
if chws > 0 and (clin_psych + couns_psych + reg_counsellors + mh_nurses) == 0:
    dangers.append("🔴 **CHWs cannot work alone:** Community Health Workers require clinical supervision and cannot deliver therapy")

# Budget overrun
team_cost_pct = (total_team_cost / cap_total_budget * 100) if cap_total_budget > 0 else 0
if team_cost_pct > 95:
    dangers.append(f"🔴 **Budget overrun:** Team costs ({team_cost_pct:.0f}%) exceed available budget")
elif team_cost_pct > 85:
    warnings.append(f"⚠️ **Budget tight:** Team costs at {team_cost_pct:.0f}% of budget. Little room for consumables/admin.")
elif team_cost_pct < 70:
    successes.append(f"✓ Budget healthy: Team costs {team_cost_pct:.0f}% leaving room for operations")

# Task shifting success
if supervision_ratio >= 6 and supervision_ratio <= 10:
    successes.append("✓ Good task-shifting: Leveraging counsellors effectively within safe supervision")

# ============================================================
# BADGES
# ============================================================
badges = []

if cap_income > ffs_income * 1.1:
    badges.append(("💰 Income Winner", "gold"))
    
if team_cost_pct < 65:
    badges.append(("🎯 Budget Master", "green"))

if 6 <= supervision_ratio <= 10:
    badges.append(("⚖️ Task-Shift Pro", "blue"))

if health_promo >= 20 and effective_utilization < utilization_base * 0.85:
    badges.append(("🌱 Prevention Champion", "green"))

if cap_workload < ffs_workload * 0.7:
    badges.append(("😌 Workload Winner", "blue"))

# ============================================================
# MAIN DISPLAY
# ============================================================

# Two Column Layout: FFS vs Capitation
col_ffs, col_cap = st.columns(2)

with col_ffs:
    st.markdown("### 💼 Your FFS Practice")
    st.markdown(f"**Profession:** {profession}")
    st.markdown(f"*{prof_data['scope']}*")
    
    st.markdown(f"""
    <div class="income-card income-neutral">
        <p style="margin:0; font-size: 0.9rem;">Annual FFS Income</p>
        <p class="income-value">R{ffs_income:,.0f}</p>
        <p style="margin:0; font-size: 0.85rem;">
            {ffs_patients} pts/day × R{ffs_fee} × 250 days<br>
            minus {ffs_costs_pct}% costs
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("Daily Workload", f"{ffs_patients} patients")
    st.metric("Annual Reach", f"{ffs_patients * working_days:,} consultations")

with col_cap:
    st.markdown("### 🏥 Capitation Team Model")
    st.markdown(f"**Population:** {population:,} | **Rate:** R{capitation}/person/year")
    
    # Color based on comparison
    if cap_income > ffs_income:
        card_class = "income-green"
        comparison_text = f"+R{income_difference:,.0f} ({income_difference_pct:+.1f}%)"
    elif cap_income < ffs_income:
        card_class = "income-red"
        comparison_text = f"R{income_difference:,.0f} ({income_difference_pct:.1f}%)"
    else:
        card_class = "income-neutral"
        comparison_text = "Same as FFS"
    
    st.markdown(f"""
    <div class="income-card {card_class}">
        <p style="margin:0; font-size: 0.9rem;">Annual Capitation Income</p>
        <p class="income-value">R{cap_income:,.0f}</p>
        <p style="margin:0; font-size: 0.85rem;">
            vs FFS: {comparison_text}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("Team Workload", f"{cap_workload:.1f} pts/day each")
    st.metric("Population Reach", f"{users_covered:,} users/year")

# ============================================================
# COMPARISON VISUALIZATION
# ============================================================
st.markdown("---")
st.markdown("## 📊 Side-by-Side Comparison")

col_chart, col_insights = st.columns([2, 1])

with col_chart:
    # Create comparison bar chart
    comparison_data = pd.DataFrame({
        'Metric': ['Annual Income', 'Daily Workload', 'Annual Reach'],
        'FFS': [ffs_income, ffs_patients, ffs_patients * working_days],
        'Capitation': [cap_income, cap_workload, users_covered]
    })
    
    # Income comparison
    fig_income = go.Figure()
    
    fig_income.add_trace(go.Bar(
        name='FFS',
        x=['Income (R)', 'Workload (pts/day)', 'Reach (users/yr)'],
        y=[ffs_income/1000000, ffs_patients, (ffs_patients * working_days)/1000],
        marker_color='#6c757d',
        text=[f'R{ffs_income/1000000:.2f}M', f'{ffs_patients}', f'{(ffs_patients * working_days)/1000:.1f}k'],
        textposition='outside'
    ))
    
    fig_income.add_trace(go.Bar(
        name='Capitation',
        x=['Income (R)', 'Workload (pts/day)', 'Reach (users/yr)'],
        y=[cap_income/1000000, cap_workload, users_covered/1000],
        marker_color='#28a745' if cap_income >= ffs_income else '#dc3545',
        text=[f'R{cap_income/1000000:.2f}M', f'{cap_workload:.1f}', f'{users_covered/1000:.1f}k'],
        textposition='outside'
    ))
    
    fig_income.update_layout(
        barmode='group',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis_title="Value (millions/units/thousands)",
        showlegend=True
    )
    
    st.plotly_chart(fig_income, use_container_width=True)

with col_insights:
    st.markdown("### 💡 Key Insights")
    
    # Income insight
    if cap_income > ffs_income:
        st.markdown(f"""
        <div class="success-box">
            <strong>Income:</strong> Capitation earns <span class="comparison-better">R{income_difference:,.0f} MORE</span> per year
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="danger-box">
            <strong>Income:</strong> Capitation earns <span class="comparison-worse">R{abs(income_difference):,.0f} LESS</span> per year
        </div>
        """, unsafe_allow_html=True)
    
    # Workload insight
    workload_change = ((cap_workload - ffs_patients) / ffs_patients * 100) if ffs_patients > 0 else 0
    if cap_workload < ffs_patients:
        st.markdown(f"""
        <div class="success-box">
            <strong>Workload:</strong> <span class="comparison-better">{abs(workload_change):.0f}% lighter</span> with team support
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="warning-box">
            <strong>Workload:</strong> {workload_change:.0f}% heavier - consider more team members
        </div>
        """, unsafe_allow_html=True)
    
    # Reach insight
    reach_multiple = users_covered / (ffs_patients * working_days) if (ffs_patients * working_days) > 0 else 0
    st.markdown(f"""
    <div class="info-box">
        <strong>Reach:</strong> Serve <span style="color: #1E5F8A; font-weight: bold;">{reach_multiple:.1f}x more people</span> with capitation
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# COMPETENCY WARNINGS SECTION
# ============================================================
if dangers or warnings or successes:
    st.markdown("---")
    st.markdown("## ⚠️ Competency & Safety Checks")
    
    for danger in dangers:
        st.markdown(f'<div class="danger-box">{danger}</div>', unsafe_allow_html=True)
    
    for warning in warnings:
        st.markdown(f'<div class="warning-box">{warning}</div>', unsafe_allow_html=True)
    
    for success in successes:
        st.markdown(f'<div class="success-box">{success}</div>', unsafe_allow_html=True)

# ============================================================
# BADGES SECTION
# ============================================================
if badges:
    st.markdown("---")
    st.markdown("## 🏆 Achievements")
    badge_html = ""
    for badge_name, badge_type in badges:
        badge_html += f'<span class="badge badge-{badge_type}">{badge_name}</span> '
    st.markdown(badge_html, unsafe_allow_html=True)

# ============================================================
# VALUE SCORE
# ============================================================
st.markdown("---")
st.markdown("## 📈 Value Score")

col_score, col_breakdown = st.columns([1, 2])

with col_score:
    # Calculate value score
    value_score = 0
    
    # Income component (40 pts)
    if cap_income > ffs_income * 1.15:
        income_pts = 40
    elif cap_income > ffs_income:
        income_pts = 30
    elif cap_income > ffs_income * 0.9:
        income_pts = 20
    else:
        income_pts = 10
    value_score += income_pts
    
    # Quality/Safety (30 pts)
    quality_pts = 30
    if len(dangers) > 0:
        quality_pts = 5
    elif len(warnings) > 0:
        quality_pts = 20
    value_score += quality_pts
    
    # Workload (15 pts)
    if cap_workload < ffs_patients * 0.6:
        workload_pts = 15
    elif cap_workload < ffs_patients * 0.8:
        workload_pts = 12
    elif cap_workload < ffs_patients:
        workload_pts = 8
    else:
        workload_pts = 3
    value_score += workload_pts
    
    # Reach (15 pts)
    if reach_multiple > 5:
        reach_pts = 15
    elif reach_multiple > 3:
        reach_pts = 12
    elif reach_multiple > 1.5:
        reach_pts = 8
    else:
        reach_pts = 4
    value_score += reach_pts
    
    # Display score
    if value_score >= 80:
        score_color = "#28a745"
    elif value_score >= 60:
        score_color = "#ffc107"
    else:
        score_color = "#dc3545"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E5F8A 0%, #2E8B57 100%); 
                padding: 2rem; border-radius: 15px; text-align: center; color: white;">
        <h3 style="margin: 0;">Value Score</h3>
        <p style="font-size: 3.5rem; font-weight: bold; margin: 0.5rem 0; color: {score_color};">
            {value_score}/100
        </p>
        <p style="margin: 0; opacity: 0.9;">Quality ÷ Cost Balance</p>
    </div>
    """, unsafe_allow_html=True)

with col_breakdown:
    st.markdown("#### Score Breakdown")
    
    breakdown_data = {
        'Component': ['Income vs FFS', 'Quality & Safety', 'Workload Balance', 'Population Reach'],
        'Points': [income_pts, quality_pts, workload_pts, reach_pts],
        'Max': [40, 30, 15, 15]
    }
    
    fig_breakdown = go.Figure()
    
    # Add earned points
    fig_breakdown.add_trace(go.Bar(
        y=breakdown_data['Component'],
        x=breakdown_data['Points'],
        orientation='h',
        name='Earned',
        marker_color=['#28a745' if p >= m*0.7 else '#ffc107' if p >= m*0.4 else '#dc3545' 
                      for p, m in zip(breakdown_data['Points'], breakdown_data['Max'])],
        text=[f"{p}/{m}" for p, m in zip(breakdown_data['Points'], breakdown_data['Max'])],
        textposition='inside'
    ))
    
    fig_breakdown.update_layout(
        height=200,
        margin=dict(l=0, r=20, t=10, b=10),
        xaxis=dict(range=[0, 45]),
        showlegend=False
    )
    
    st.plotly_chart(fig_breakdown, use_container_width=True)

# ============================================================
# TEAM COST BREAKDOWN
# ============================================================
st.markdown("---")
st.markdown("## 👥 Team Cost Breakdown")

col_table, col_pie = st.columns([1, 1])

with col_table:
    team_df = pd.DataFrame({
        'Role': [k for k, v in team_costs.items() if v > 0],
        'FTE': [
            clin_psych if k == "Clinical Psychologist" else
            couns_psych if k == "Counselling Psychologist" else
            reg_counsellors if k == "Registered Counsellor" else
            mh_nurses if k == "Mental Health Nurse" else
            chws
            for k, v in team_costs.items() if v > 0
        ],
        'Annual Cost': [f"R{v:,.0f}" for k, v in team_costs.items() if v > 0]
    })
    
    if not team_df.empty:
        st.dataframe(team_df, use_container_width=True, hide_index=True)
    
    st.markdown(f"""
    | **Total Team Cost** | **R{total_team_cost:,.0f}** |
    |---|---|
    | Budget Available | R{cap_total_budget:,.0f} |
    | Team % of Budget | {team_cost_pct:.1f}% |
    | Remaining for Ops | R{cap_total_budget - total_team_cost:,.0f} |
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
# ASSUMPTIONS PANEL
# ============================================================
st.markdown("---")
st.markdown(f"""
<div class="assumptions-panel">
    <h4 style="margin-top: 0;">📋 Assumptions</h4>
    <ul style="margin-bottom: 0;">
        <li><strong>Working days:</strong> 250 per year</li>
        <li><strong>Visits per user:</strong> 4 average (adjustable utilization affects user count)</li>
        <li><strong>Supervision ratio:</strong> HPCSA maximum 10 Registered Counsellors per Psychologist</li>
        <li><strong>Health promotion:</strong> {health_promo}% effort reduces utilization by ~{utilization_reduction:.1f}%</li>
        <li><strong>CTC rates:</strong> Private sector estimates (editable in sidebar)</li>
        <li><strong>Other costs:</strong> 15% of remaining budget for admin/consumables</li>
        <li><strong>No facility costs included</strong> - assumes existing infrastructure</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧠 <strong>NHI Mental Health: FFS vs Capitation Simulator</strong></p>
    <p style="font-size: 0.85rem;">
        PsySSA Workshop | February 3, 2026<br>
        National Health Insurance Implementation | South Africa
    </p>
    <p style="font-size: 0.75rem; opacity: 0.7;">
        💡 Key Insight: Task-shifting with proper supervision enables broader reach while maintaining quality and improving income.
    </p>
</div>
""", unsafe_allow_html=True)
