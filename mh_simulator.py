"""
🚀 PsySSA NHI Mental Health Cost Simulator
A Gamified NGT Dashboard for Mental Health Package Design
For PsySSA Workshop - February 3, 2026

Author: Built for Prof Shabir Moosa, NHI Branch
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime
import base64
from io import BytesIO

# ============================================================
# PAGE CONFIG & STYLING
# ============================================================
st.set_page_config(
    page_title="PsySSA NHI Mental Health Simulator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for PsySSA branding
st.markdown("""
<style>
    /* Main theme colors - Blues and Greens */
    :root {
        --primary-blue: #1E5F8A;
        --secondary-green: #2E8B57;
        --accent-teal: #20B2AA;
        --light-bg: #F0F8FF;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1E5F8A 0%, #2E8B57 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Score card styling */
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .score-value {
        font-size: 3rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-weight: bold;
        font-size: 0.85rem;
    }
    
    .badge-gold {
        background: linear-gradient(135deg, #f5af19, #f12711);
        color: white;
    }
    
    .badge-silver {
        background: linear-gradient(135deg, #bdc3c7, #2c3e50);
        color: white;
    }
    
    .badge-green {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
    }
    
    .badge-blue {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #1E5F8A;
    }
    
    /* Leaderboard styling */
    .leaderboard-entry {
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Status indicators */
    .status-green { color: #28a745; font-weight: bold; }
    .status-yellow { color: #ffc107; font-weight: bold; }
    .status-red { color: #dc3545; font-weight: bold; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive columns */
    @media (max-width: 768px) {
        .row-widget.stHorizontal {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = [
        {"name": "Dr. Nkosi", "score": 87, "timestamp": "2026-02-03 09:15"},
        {"name": "Prof. Van der Berg", "score": 82, "timestamp": "2026-02-03 09:22"},
        {"name": "Ms. Dlamini", "score": 79, "timestamp": "2026-02-03 09:30"},
    ]

if 'ngt_votes' not in st.session_state:
    st.session_state.ngt_votes = {
        "Minimal (R80)": 0,
        "Optimal (R120)": 0,
        "Comprehensive (R200)": 0
    }

if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# ============================================================
# COST-TO-COMPANY RATES (Editable)
# ============================================================
DEFAULT_CTC = {
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
    <h1>🧠 PsySSA NHI Mental Health Package Simulator</h1>
    <p style="font-size: 1.1rem; margin: 0;">Design Your Ideal PHC Mental Health Package | NGT Workshop Tool</p>
    <p style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">📅 February 3, 2026 | National Health Insurance Implementation</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR - INPUT CONTROLS
# ============================================================
with st.sidebar:
    st.markdown("### 👤 Your Details")
    user_name = st.text_input("Your Name (for Leaderboard)", value=st.session_state.user_name)
    st.session_state.user_name = user_name
    
    st.markdown("---")
    
    # Quick Scenario Buttons
    st.markdown("### ⚡ Quick Scenarios")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("Minimal\nR80", use_container_width=True):
        st.session_state.scenario = "minimal"
    if col2.button("Optimal\nR120", use_container_width=True):
        st.session_state.scenario = "optimal"
    if col3.button("Dream\nR200", use_container_width=True):
        st.session_state.scenario = "dream"
    
    # Apply scenario defaults
    scenario = st.session_state.get('scenario', 'optimal')
    
    if scenario == "minimal":
        default_pop, default_cap, default_util, default_sess = 80000, 80, 3, 4
        default_clin, default_couns, default_reg, default_nurse, default_chw = 0.5, 0.5, 10, 0.5, 4
    elif scenario == "dream":
        default_pop, default_cap, default_util, default_sess = 80000, 200, 6, 6
        default_clin, default_couns, default_reg, default_nurse, default_chw = 1.5, 1.0, 20, 1.5, 6
    else:  # optimal
        default_pop, default_cap, default_util, default_sess = 80000, 120, 4, 5
        default_clin, default_couns, default_reg, default_nurse, default_chw = 1.0, 0.5, 12, 1.0, 4
    
    st.markdown("---")
    
    # Budget Parameters
    st.markdown("### 💰 Budget Parameters")
    
    population = st.slider(
        "Population Covered",
        min_value=50000,
        max_value=100000,
        value=default_pop,
        step=5000,
        format="%d",
        help="Population size for catchment area"
    )
    
    capitation = st.slider(
        "Capitation Rate (R/person/year)",
        min_value=80,
        max_value=200,
        value=default_cap,
        step=10,
        format="R%d"
    )
    
    utilization = st.slider(
        "Expected Utilization (%)",
        min_value=2.0,
        max_value=10.0,
        value=float(default_util),
        step=0.5,
        format="%.1f%%",
        help="% of population accessing services annually"
    )
    
    sessions_per_user = st.slider(
        "Avg Sessions per User",
        min_value=3,
        max_value=8,
        value=default_sess,
        help="Average treatment episodes"
    )
    
    st.markdown("---")
    
    # Service Mix
    st.markdown("### 📋 Service Mix (%)")
    st.caption("Allocate session types (auto-normalizes to 100%)")
    
    screening_raw = st.slider("Screening & Assessment", 10, 30, 15)
    brief_raw = st.slider("Brief Therapy (1-6 sessions)", 40, 70, 55)
    groups_raw = st.slider("Group Interventions", 10, 30, 20)
    crisis_raw = st.slider("Crisis/MDT Referral", 5, 15, 10)
    
    # Normalize to 100%
    total_raw = screening_raw + brief_raw + groups_raw + crisis_raw
    screening_pct = screening_raw / total_raw * 100
    brief_pct = brief_raw / total_raw * 100
    groups_pct = groups_raw / total_raw * 100
    crisis_pct = crisis_raw / total_raw * 100
    
    st.markdown("---")
    
    # Team Composition
    st.markdown("### 👥 Team Composition (FTE)")
    
    clin_psych = st.slider(
        "Clinical Psychologists",
        min_value=0.5,
        max_value=2.0,
        value=default_clin,
        step=0.25,
        format="%.2f FTE"
    )
    
    couns_psych = st.slider(
        "Counselling Psychologists",
        min_value=0.0,
        max_value=1.5,
        value=default_couns,
        step=0.25,
        format="%.2f FTE"
    )
    
    reg_counsellors = st.slider(
        "Registered Counsellors",
        min_value=8,
        max_value=25,
        value=default_reg,
        step=1,
        format="%d FTE"
    )
    
    mh_nurses = st.slider(
        "Mental Health Nurses",
        min_value=0.5,
        max_value=2.0,
        value=default_nurse,
        step=0.25,
        format="%.2f FTE"
    )
    
    chws = st.slider(
        "Community Health Workers",
        min_value=2,
        max_value=8,
        value=default_chw,
        step=1,
        format="%d FTE"
    )
    
    st.markdown("---")
    
    # Editable CTC Table
    st.markdown("### 💵 Cost-to-Company Rates")
    with st.expander("Edit Annual Salaries (R)"):
        ctc_clin = st.number_input("Clinical Psych", value=DEFAULT_CTC["Clinical Psychologist"], step=50000)
        ctc_couns = st.number_input("Counselling Psych", value=DEFAULT_CTC["Counselling Psychologist"], step=50000)
        ctc_reg = st.number_input("Reg Counsellor", value=DEFAULT_CTC["Registered Counsellor"], step=25000)
        ctc_nurse = st.number_input("MH Nurse", value=DEFAULT_CTC["Mental Health Nurse"], step=25000)
        ctc_chw = st.number_input("CHW", value=DEFAULT_CTC["Community Health Worker"], step=10000)

# ============================================================
# CALCULATIONS
# ============================================================
# Total Budget
total_budget = population * capitation

# Team Costs
team_costs = {
    "Clinical Psychologist": clin_psych * ctc_clin,
    "Counselling Psychologist": couns_psych * ctc_couns,
    "Registered Counsellor": reg_counsellors * ctc_reg,
    "Mental Health Nurse": mh_nurses * ctc_nurse,
    "Community Health Worker": chws * ctc_chw
}
total_team_cost = sum(team_costs.values())
team_cost_pct = (total_team_cost / total_budget) * 100 if total_budget > 0 else 0

# Service Calculations
users_covered = int(population * (utilization / 100))
total_sessions = users_covered * sessions_per_user
per_capita_cost = capitation

# Sessions by type
sessions_screening = int(total_sessions * (screening_pct / 100))
sessions_brief = int(total_sessions * (brief_pct / 100))
sessions_groups = int(total_sessions * (groups_pct / 100))
sessions_crisis = int(total_sessions * (crisis_pct / 100))

# Coverage ratio (1:X compared to national 1:80,000)
total_psychs = clin_psych + couns_psych
if total_psychs > 0:
    coverage_ratio = population / total_psychs
else:
    coverage_ratio = float('inf')

# Task-shift ratio (Counsellors : Psychologists)
if total_psychs > 0:
    task_shift_ratio = reg_counsellors / total_psychs
else:
    task_shift_ratio = float('inf')

# ============================================================
# FEASIBILITY SCORE CALCULATION
# ============================================================
def calculate_feasibility_score():
    score = 0
    breakdown = {}
    badges = []
    
    # Budget Fit (40 pts) - Team cost < 75% of budget
    if team_cost_pct < 60:
        budget_score = 40
        badges.append(("🥷 Budget Ninja", "gold"))
    elif team_cost_pct < 75:
        budget_score = 35
    elif team_cost_pct < 85:
        budget_score = 25
    elif team_cost_pct < 95:
        budget_score = 15
    else:
        budget_score = 5
    breakdown["Budget Fit"] = budget_score
    score += budget_score
    
    # Coverage (30 pts) - Utilization > 4%
    if utilization >= 6:
        coverage_score = 30
        badges.append(("🦸 Reach Hero", "green"))
    elif utilization >= 5:
        coverage_score = 25
    elif utilization >= 4:
        coverage_score = 20
    elif utilization >= 3:
        coverage_score = 12
    else:
        coverage_score = 5
    breakdown["Coverage"] = coverage_score
    score += coverage_score
    
    # Task-Shifting (20 pts) - Counsellors > Psychs at 8:1
    if task_shift_ratio >= 10:
        task_score = 20
        badges.append(("⚖️ Task-Shift Champion", "blue"))
    elif task_shift_ratio >= 8:
        task_score = 18
    elif task_shift_ratio >= 6:
        task_score = 14
    elif task_shift_ratio >= 4:
        task_score = 10
    else:
        task_score = 5
    breakdown["Task-Shifting"] = task_score
    score += task_score
    
    # Efficiency (10 pts) - Sessions per user < 6
    if sessions_per_user <= 4:
        eff_score = 10
        badges.append(("⚡ Efficiency Expert", "silver"))
    elif sessions_per_user <= 5:
        eff_score = 8
    elif sessions_per_user <= 6:
        eff_score = 6
    else:
        eff_score = 3
    breakdown["Efficiency"] = eff_score
    score += eff_score
    
    # Bonus: mhGAP alignment check
    if groups_pct >= 15 and mh_nurses >= 1.0:
        badges.append(("📋 mhGAP Aligned", "green"))
    
    return score, breakdown, badges

score, score_breakdown, badges = calculate_feasibility_score()

# ============================================================
# MAIN DASHBOARD - METRICS ROW
# ============================================================
st.markdown("## 📊 Your Package Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Total Budget",
        value=f"R{total_budget/1e6:.1f}M",
        delta=f"R{capitation}/capita"
    )

with col2:
    # Team cost status color
    if team_cost_pct < 70:
        status = "🟢"
    elif team_cost_pct < 85:
        status = "🟡"
    else:
        status = "🔴"
    
    st.metric(
        label=f"👥 Team Cost {status}",
        value=f"R{total_team_cost/1e6:.2f}M",
        delta=f"{team_cost_pct:.1f}% of budget"
    )

with col3:
    st.metric(
        label="🎯 Users Covered",
        value=f"{users_covered:,}",
        delta=f"{utilization:.1f}% utilization"
    )

with col4:
    st.metric(
        label="📅 Total Sessions",
        value=f"{total_sessions:,}",
        delta=f"{sessions_per_user} per user"
    )

# ============================================================
# FEASIBILITY SCORE DISPLAY
# ============================================================
st.markdown("---")

col_score, col_breakdown = st.columns([1, 2])

with col_score:
    # Score color based on value
    if score >= 80:
        score_color = "#28a745"
        grade = "A"
    elif score >= 65:
        score_color = "#17a2b8"
        grade = "B"
    elif score >= 50:
        score_color = "#ffc107"
        grade = "C"
    else:
        score_color = "#dc3545"
        grade = "D"
    
    st.markdown(f"""
    <div class="score-card">
        <h3 style="margin: 0;">🏆 Feasibility Score</h3>
        <div class="score-value" style="color: {score_color};">{score}/100</div>
        <p style="font-size: 1.5rem; margin: 0;">Grade: {grade}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Badges
    if badges:
        st.markdown("#### 🎖️ Badges Earned")
        badge_html = ""
        for badge_name, badge_type in badges:
            badge_html += f'<span class="badge badge-{badge_type}">{badge_name}</span> '
        st.markdown(badge_html, unsafe_allow_html=True)

with col_breakdown:
    st.markdown("#### Score Breakdown")
    
    # Create breakdown chart
    fig_breakdown = go.Figure(go.Bar(
        x=list(score_breakdown.values()),
        y=list(score_breakdown.keys()),
        orientation='h',
        marker_color=['#1E5F8A', '#2E8B57', '#20B2AA', '#6495ED'],
        text=[f"{v}/{'40' if k == 'Budget Fit' else '30' if k == 'Coverage' else '20' if k == 'Task-Shifting' else '10'}" 
              for k, v in score_breakdown.items()],
        textposition='inside'
    ))
    
    fig_breakdown.update_layout(
        height=200,
        margin=dict(l=0, r=20, t=10, b=10),
        xaxis_title="Points",
        showlegend=False,
        xaxis=dict(range=[0, 45])
    )
    
    st.plotly_chart(fig_breakdown, use_container_width=True)

# ============================================================
# CHARTS ROW
# ============================================================
st.markdown("---")
st.markdown("## 📈 Visualizations")

col_pie, col_bar, col_gauge = st.columns(3)

with col_pie:
    st.markdown("#### 👥 Team Mix (by Cost)")
    
    fig_pie = px.pie(
        values=list(team_costs.values()),
        names=list(team_costs.keys()),
        color_discrete_sequence=px.colors.sequential.Blues_r,
        hole=0.4
    )
    fig_pie.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    st.markdown("#### 📋 Service Allocation")
    
    service_data = pd.DataFrame({
        'Service': ['Screening', 'Brief Therapy', 'Groups', 'Crisis/MDT'],
        'Sessions': [sessions_screening, sessions_brief, sessions_groups, sessions_crisis],
        'Percentage': [screening_pct, brief_pct, groups_pct, crisis_pct]
    })
    
    fig_bar = px.bar(
        service_data,
        x='Service',
        y='Sessions',
        color='Service',
        color_discrete_sequence=['#1E5F8A', '#2E8B57', '#20B2AA', '#6495ED'],
        text='Sessions'
    )
    fig_bar.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False
    )
    fig_bar.update_traces(texttemplate='%{text:,}', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_gauge:
    st.markdown("#### 🎯 Coverage vs National (1:80k)")
    
    # Calculate gauge value (lower is better)
    if coverage_ratio == float('inf'):
        gauge_val = 0
    else:
        gauge_val = min(100, (80000 / coverage_ratio) * 100)
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=gauge_val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Coverage Index<br><span style='font-size:0.8em'>Your ratio: 1:{int(coverage_ratio):,}</span>"},
        number={'suffix': "%"},
        gauge={
            'axis': {'range': [None, 150], 'tickwidth': 1},
            'bar': {'color': "#2E8B57"},
            'steps': [
                {'range': [0, 50], 'color': '#ffcccc'},
                {'range': [50, 100], 'color': '#ffffcc'},
                {'range': [100, 150], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    fig_gauge.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# ============================================================
# DETAILED TEAM BREAKDOWN
# ============================================================
st.markdown("---")
st.markdown("## 👥 Team Composition Details")

team_df = pd.DataFrame({
    'Role': list(team_costs.keys()),
    'FTE': [clin_psych, couns_psych, reg_counsellors, mh_nurses, chws],
    'Annual Cost (R)': [f"R{v:,.0f}" for v in team_costs.values()],
    'CTC Rate (R)': [f"R{ctc_clin:,}", f"R{ctc_couns:,}", f"R{ctc_reg:,}", f"R{ctc_nurse:,}", f"R{ctc_chw:,}"]
})

st.dataframe(
    team_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Role": st.column_config.TextColumn("Role", width="large"),
        "FTE": st.column_config.NumberColumn("FTE", format="%.2f"),
        "Annual Cost (R)": st.column_config.TextColumn("Annual Cost"),
        "CTC Rate (R)": st.column_config.TextColumn("CTC Rate")
    }
)

# Key ratios
col_ratio1, col_ratio2, col_ratio3 = st.columns(3)

with col_ratio1:
    st.info(f"**Task-Shift Ratio:** {task_shift_ratio:.1f} Counsellors per Psychologist")

with col_ratio2:
    remaining_budget = total_budget - total_team_cost
    st.success(f"**Remaining Budget:** R{remaining_budget/1e6:.2f}M ({100-team_cost_pct:.1f}%)")

with col_ratio3:
    if total_sessions > 0:
        cost_per_session = total_team_cost / total_sessions
        st.warning(f"**Cost per Session:** R{cost_per_session:.0f}")

# ============================================================
# LEADERBOARD & NGT VOTING
# ============================================================
st.markdown("---")
col_leader, col_vote = st.columns(2)

with col_leader:
    st.markdown("## 🏆 Workshop Leaderboard")
    
    # Sort leaderboard
    sorted_board = sorted(st.session_state.leaderboard, key=lambda x: x['score'], reverse=True)[:5]
    
    for i, entry in enumerate(sorted_board):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏅"
        st.markdown(f"""
        <div class="leaderboard-entry">
            <span>{medal} <strong>{entry['name']}</strong></span>
            <span style="font-size: 1.2rem; font-weight: bold; color: #1E5F8A;">{entry['score']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Submit to leaderboard
    st.markdown("---")
    if st.button("📤 Submit My Score to Leaderboard", type="primary", use_container_width=True):
        if user_name:
            new_entry = {
                "name": user_name,
                "score": score,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.leaderboard.append(new_entry)
            st.success(f"✅ Submitted! {user_name} - Score: {score}")
            st.rerun()
        else:
            st.error("Please enter your name in the sidebar first!")

with col_vote:
    st.markdown("## 🗳️ NGT Consensus Vote")
    st.markdown("*Vote for your preferred package level:*")
    
    # Current votes display
    total_votes = sum(st.session_state.ngt_votes.values())
    
    if total_votes > 0:
        fig_vote = px.bar(
            x=list(st.session_state.ngt_votes.keys()),
            y=list(st.session_state.ngt_votes.values()),
            color=list(st.session_state.ngt_votes.keys()),
            color_discrete_sequence=['#dc3545', '#ffc107', '#28a745']
        )
        fig_vote.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=10, b=10),
            showlegend=False,
            xaxis_title="",
            yaxis_title="Votes"
        )
        st.plotly_chart(fig_vote, use_container_width=True)
    
    # Voting buttons
    col_v1, col_v2, col_v3 = st.columns(3)
    
    if col_v1.button("🔴 Minimal\n(R80)", use_container_width=True):
        st.session_state.ngt_votes["Minimal (R80)"] += 1
        st.rerun()
    
    if col_v2.button("🟡 Optimal\n(R120)", use_container_width=True):
        st.session_state.ngt_votes["Optimal (R120)"] += 1
        st.rerun()
    
    if col_v3.button("🟢 Dream\n(R200)", use_container_width=True):
        st.session_state.ngt_votes["Comprehensive (R200)"] += 1
        st.rerun()
    
    st.markdown(f"**Total Votes:** {total_votes}")

# ============================================================
# EXPORT SECTION
# ============================================================
st.markdown("---")
st.markdown("## 📄 Export Your Package")

def generate_summary():
    """Generate a text summary for export"""
    summary = f"""
╔══════════════════════════════════════════════════════════════════╗
║           PsySSA NHI MENTAL HEALTH PACKAGE SUMMARY               ║
║                    Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}                    ║
╚══════════════════════════════════════════════════════════════════╝

📊 FEASIBILITY SCORE: {score}/100 (Grade {grade})

🎖️ BADGES EARNED: {', '.join([b[0] for b in badges]) if badges else 'None'}

═══════════════════════════════════════════════════════════════════
💰 BUDGET PARAMETERS
═══════════════════════════════════════════════════════════════════
• Population Covered:    {population:,}
• Capitation Rate:       R{capitation} per person per year
• Total Budget:          R{total_budget/1e6:.2f}M
• Expected Utilization:  {utilization:.1f}%
• Users Covered:         {users_covered:,}

═══════════════════════════════════════════════════════════════════
👥 TEAM COMPOSITION
═══════════════════════════════════════════════════════════════════
• Clinical Psychologists:    {clin_psych:.2f} FTE @ R{ctc_clin:,} = R{team_costs['Clinical Psychologist']:,.0f}
• Counselling Psychologists: {couns_psych:.2f} FTE @ R{ctc_couns:,} = R{team_costs['Counselling Psychologist']:,.0f}
• Registered Counsellors:    {reg_counsellors} FTE @ R{ctc_reg:,} = R{team_costs['Registered Counsellor']:,.0f}
• Mental Health Nurses:      {mh_nurses:.2f} FTE @ R{ctc_nurse:,} = R{team_costs['Mental Health Nurse']:,.0f}
• Community Health Workers:  {chws} FTE @ R{ctc_chw:,} = R{team_costs['Community Health Worker']:,.0f}

TOTAL TEAM COST: R{total_team_cost/1e6:.2f}M ({team_cost_pct:.1f}% of budget)
Task-Shift Ratio: {task_shift_ratio:.1f} Counsellors per Psychologist

═══════════════════════════════════════════════════════════════════
📋 SERVICE MIX
═══════════════════════════════════════════════════════════════════
• Screening & Assessment:  {screening_pct:.1f}% ({sessions_screening:,} sessions)
• Brief Therapy:           {brief_pct:.1f}% ({sessions_brief:,} sessions)
• Group Interventions:     {groups_pct:.1f}% ({sessions_groups:,} sessions)
• Crisis/MDT Referral:     {crisis_pct:.1f}% ({sessions_crisis:,} sessions)

TOTAL SESSIONS: {total_sessions:,}
Average Sessions per User: {sessions_per_user}

═══════════════════════════════════════════════════════════════════
📈 KEY METRICS
═══════════════════════════════════════════════════════════════════
• Coverage Ratio:          1:{int(coverage_ratio):,} (National benchmark: 1:80,000)
• Cost per Session:        R{total_team_cost/total_sessions if total_sessions > 0 else 0:.0f}
• Per Capita Spend:        R{capitation}
• Remaining Budget:        R{(total_budget-total_team_cost)/1e6:.2f}M

═══════════════════════════════════════════════════════════════════
🏆 SCORE BREAKDOWN
═══════════════════════════════════════════════════════════════════
• Budget Fit:     {score_breakdown['Budget Fit']}/40 points
• Coverage:       {score_breakdown['Coverage']}/30 points
• Task-Shifting:  {score_breakdown['Task-Shifting']}/20 points
• Efficiency:     {score_breakdown['Efficiency']}/10 points

═══════════════════════════════════════════════════════════════════
                   NHI Implementation Ready | PsySSA 2026
═══════════════════════════════════════════════════════════════════
"""
    return summary

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    summary_text = generate_summary()
    st.download_button(
        label="📥 Download Summary (TXT)",
        data=summary_text,
        file_name=f"MH_Package_{user_name or 'Anonymous'}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True
    )

with col_exp2:
    # JSON export for data portability
    export_data = {
        "user": user_name,
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "grade": grade,
        "badges": [b[0] for b in badges],
        "parameters": {
            "population": population,
            "capitation": capitation,
            "utilization": utilization,
            "sessions_per_user": sessions_per_user
        },
        "team": {
            "clinical_psych_fte": clin_psych,
            "counselling_psych_fte": couns_psych,
            "registered_counsellors": reg_counsellors,
            "mh_nurses": mh_nurses,
            "chws": chws
        },
        "financials": {
            "total_budget": total_budget,
            "team_cost": total_team_cost,
            "team_cost_pct": team_cost_pct
        }
    }
    
    st.download_button(
        label="📊 Download Data (JSON)",
        data=json.dumps(export_data, indent=2),
        file_name=f"MH_Package_Data_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
        use_container_width=True
    )

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧠 <strong>PsySSA NHI Mental Health Package Simulator</strong></p>
    <p style="font-size: 0.85rem;">
        Built for the National Health Insurance Implementation | South Africa<br>
        Workshop: February 3, 2026 | Powered by Streamlit
    </p>
    <p style="font-size: 0.75rem; opacity: 0.7;">
        💡 Key Insight: Task-shifting to registered counsellors enables broader coverage while maintaining quality.<br>
        📋 Reference: WHO mhGAP Guidelines | SA National Mental Health Policy Framework
    </p>
</div>
""", unsafe_allow_html=True)
