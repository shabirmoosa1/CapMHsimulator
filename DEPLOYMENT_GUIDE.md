# 🚀 PsySSA NHI Mental Health Simulator - Deployment & Workshop Guide

## Quick Deploy (5 Minutes)

### Option 1: Streamlit Community Cloud (Recommended for Workshop)

1. **Create GitHub Repository**
   ```bash
   # Create new repo on github.com
   # Upload: mh_simulator.py and requirements.txt
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repo
   - Set main file: `mh_simulator.py`
   - Click "Deploy"
   - Share URL with workshop participants!

### Option 2: Local Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run mh_simulator.py

# App opens at http://localhost:8501
```

### Option 3: Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY mh_simulator.py .
EXPOSE 8501
CMD ["streamlit", "run", "mh_simulator.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 📋 Workshop Facilitation Script

### Session: Mental Health Package Design (90 minutes)

#### Opening (5 min)
> "Welcome to our NGT workshop on designing the mental health package for NHI PHC contracting. Today you'll use an interactive simulator to explore trade-offs and build consensus."

#### Tool Introduction (10 min)
> "Open the simulator on your device. Notice:
> - **Sidebar**: All your input controls
> - **Main area**: Real-time calculations and your Feasibility Score
> - **Bottom**: Leaderboard and NGT voting"

#### Guided Exploration (20 min)

**Demo 1: Budget Impact**
> "Start by clicking 'Minimal R80' scenario. Notice your Feasibility Score. Now slide the Capitation Rate to R200. Watch what happens to your budget and coverage. The system rewards reaching more people!"

**Demo 2: The Task-Shift Discovery**
> "Here's the key insight. Slide 'Clinical Psychologists' down to 0.5 FTE. Your score drops. Now slide 'Registered Counsellors' UP to 20. Watch the score jump! The simulator reveals that task-shifting isn't just cost-effective—it's ESSENTIAL for coverage."

**Demo 3: Service Mix**
> "Increase 'Group Interventions' to 25%. Notice how this stretches your sessions further. Groups are leverage!"

#### Individual Design Phase (25 min)
> "Now it's your turn. Design YOUR ideal package. Aim for the highest Feasibility Score. When satisfied, enter your name and click 'Submit to Leaderboard'. We'll celebrate the top scores!"

**Coaching prompts:**
- "If your team cost is RED (>85%), try more counsellors, fewer psychologists"
- "Chase the 'Reach Hero' badge—get utilization above 6%"
- "The 'Task-Shift Champion' badge unlocks at 10:1 counsellor ratio"

#### Group Discussion (15 min)
> "Let's review the leaderboard. [Top scorer], walk us through your design. What trade-offs did you make?"

**Discussion questions:**
1. "What surprised you about the optimal configurations?"
2. "How does this change your view of psychologist roles in PHC?"
3. "What barriers might prevent this task-shifting in practice?"

#### NGT Voting (10 min)
> "Time for consensus. Based on your exploration, vote for the package level PsySSA should advocate for. Click your choice: Minimal (R80), Optimal (R120), or Dream (R200)."

> [After voting] "The results show [X]% support for [winning option]. This is our workshop's collective recommendation!"

#### Wrap-up (5 min)
> "Download your package summary using the Export button. This is YOUR design—bring it to future policy discussions. Key takeaway: Task-shifting to registered counsellors isn't just affordable, it's the ONLY way to achieve meaningful coverage at scale."

---

## 🎮 Key Teaching Moments

### "Aha!" Triggers Built Into the Simulator

1. **Budget Reality Check**
   - When team cost exceeds 85% budget → Red indicator
   - Forces realization: "We can't just hire more psychologists"

2. **Task-Shift Revelation**
   - Score jumps when counsellor:psychologist ratio hits 8:1
   - Badge reward: "Task-Shift Champion"
   - Participants discover the math themselves

3. **Coverage vs Quality Tension**
   - High utilization (>6%) earns "Reach Hero"
   - But fewer sessions per user earns "Efficiency Expert"
   - Forces explicit trade-off discussion

4. **Comparison to National Benchmark**
   - Gauge shows coverage vs 1:80,000 ratio
   - Makes abstract numbers concrete

---

## 🔧 Customization Options

### Adjust Default Values
Edit these in `mh_simulator.py`:

```python
# Line ~100: Default CTC rates
DEFAULT_CTC = {
    "Clinical Psychologist": 900000,  # Change as needed
    ...
}

# Line ~170: Scenario presets
if scenario == "minimal":
    default_pop, default_cap, ... = 80000, 80, ...
```

### Add Your Branding
```python
# Line ~60: Edit colors
--primary-blue: #YOUR_COLOR;
--secondary-green: #YOUR_COLOR;
```

### Pre-populate Leaderboard
```python
# Line ~120
st.session_state.leaderboard = [
    {"name": "Workshop Host", "score": 75, "timestamp": "..."},
    # Add sample entries
]
```

---

## 📱 Mobile Tips

- Simulator is responsive—works on phones
- Share QR code linking to deployed app
- Sidebar auto-collapses on mobile (users tap hamburger menu)

---

## 🎯 Success Metrics

After the workshop, check:
- [ ] 80%+ participants achieved score >60
- [ ] Leaderboard shows diversity of approaches
- [ ] NGT votes show clear consensus
- [ ] Discussion surfaced task-shifting as key lever

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| App won't load | Check requirements.txt installed |
| Charts not showing | Ensure Plotly version ≥5.18 |
| Leaderboard resets | Normal—uses session state (not persistent DB) |
| Mobile sidebar issues | Use latest Streamlit version |

---

**Built for PsySSA | NHI Implementation | February 2026**

Contact: Prof Shabir Moosa, NHI Branch - User & Service Provider Management
