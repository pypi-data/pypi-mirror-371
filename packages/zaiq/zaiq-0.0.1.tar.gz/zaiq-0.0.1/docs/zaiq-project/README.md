# zaiq - AI Capacity Orchestrator

## 📊 Project Status & Session Continuity

**Current Session:** Project Brief Creation with Mary (Business Analyst)  
**Project Name:** zaiq (formerly CDO)  
**Date Started:** 2025-08-22  
**Status:** Initial project briefing in progress

---

## 🎯 Quick Start for Next Session

If you're returning to this project, here's what to do:

1. **Review Current State:**
   - Check `checkpoint-status.md` for exact progress
   - Review completed sections in their respective files
   - Check `next-actions.md` for immediate tasks

2. **Resume with Mary (Analyst):**
   ```
   Use command: /BMad:agents:analyst
   Then say: "Let's continue the zaiq project brief from the checkpoints"
   ```

3. **Or Jump to Specific Work:**
   - For technical architecture: Review `sections/04-technical-considerations.md`
   - For market research: Use `*perform-market-research` command
   - For competitor analysis: Use `*create-competitor-analysis` command

---

## 📁 File Structure

```
docs/zaiq-project/
├── README.md                          # This file - session continuity guide
├── ETYMOLOGY.md                       # The story behind the name 'zaiq'
├── checkpoint-status.md               # Current progress tracker
├── next-actions.md                    # Immediate next steps
├── brief-complete.md                  # Will contain final assembled brief
│
├── sections/                          # Individual brief sections
│   ├── 01-executive-summary.md       # ✅ Created
│   ├── 02-problem-statement.md       # 🔄 In Progress
│   ├── 03-proposed-solution.md       # ⏳ Pending
│   ├── 04-target-users.md            # ⏳ Pending
│   ├── 05-goals-metrics.md           # ⏳ Pending
│   ├── 06-mvp-scope.md               # ⏳ Pending
│   ├── 07-post-mvp-vision.md         # ⏳ Pending
│   ├── 08-technical-considerations.md # ⏳ Pending
│   ├── 09-constraints-assumptions.md  # ⏳ Pending
│   └── 10-risks-questions.md         # ⏳ Pending
│
└── research/                          # Supporting research
    ├── market-analysis.md            # ⏳ To be created
    ├── competitor-analysis.md        # ⏳ To be created
    └── brainstorming-notes.md        # ⏳ To be created
```

---

## 🚀 Project Overview

**Project Name:** zaiq - AI Capacity Orchestrator  
**Type:** Docker-deployable Development Automation Service  
**Stage:** Initial Planning & Discovery

### Core Concept
A service that automates software development by:
1. Accepting git repository + SSH credentials
2. Processing BMAD-structured stories
3. Distributing work to Claude Code instances (Phase 2)
4. Managing story dependencies via DAG visualization
5. (Phase 4) Enabling team time-block sharing
6. (Phase 5) Universal AI provider support

---

## 📋 Key Checkpoints

### Phase 1: Foundation (Current)
- [x] Initial concept definition
- [x] Name selection (zaiq)
- [ ] Complete project brief
- [ ] Market research & validation
- [ ] Technical architecture design
- [ ] MVP scope definition

### Phase 2: Single-User Claude Code MVP (Months 1-3)
- [ ] Create PRD from brief
- [ ] Claude Code API integration
- [ ] BMAD story parsing & execution
- [ ] Basic queue management
- [ ] Git integration with SSH keys
- [ ] CLI interface (`zaiq run story-123`)
- [ ] Docker deployment for individual developers

### Phase 3: Enhanced Single-User (Months 4-6)
- [ ] DAG dependency visualization
- [ ] Web UI for monitoring
- [ ] Multi-repository support
- [ ] Advanced error handling & retry logic
- [ ] Performance optimization

### Phase 4: Multi-User Team Time-Share (Months 7-12)
- [ ] Authentication system
- [ ] Team management & user roles
- [ ] Claude usage credit system
- [ ] Time-block sharing marketplace
- [ ] Usage analytics & reporting
- [ ] Multi-tenant architecture

### Phase 5: AI-Agnostic Platform (Year 2+)
- [ ] Generic AI provider abstraction layer
- [ ] GPT-4/OpenAI integration
- [ ] Gemini/Google AI integration
- [ ] Universal rate limit handling
- [ ] Cross-provider capacity pooling
- [ ] Provider-agnostic story formats
- [ ] Time-block marketplace
- [ ] Multi-tenant architecture

---

## 💡 Key Decisions to Make

1. **Architecture:** Monolithic vs microservices?
2. **Deployment:** Self-host only vs SaaS offering?
3. **Story Format:** Pure BMAD or custom extensions?
4. **DAG Implementation:** Build vs integrate existing tool?
5. **Pricing Model:** Subscription vs usage-based?

---

## 🔄 How to Continue

When you return, Mary (the analyst) will:
1. Check which sections are complete
2. Resume from the last checkpoint
3. Help you make pending decisions
4. Guide you through remaining analysis

Just tell her: "Let's continue the zaiq project" and she'll pick up where we left off.

---

## 📝 Notes Section

Add your thoughts and decisions here as you work through the project:

- **Name chosen:** zaiq - bridges cultures (Singapore zai + Arabic surplus + queue)
- **Why zaiq:** Represents steady distribution of surplus capacity
- **Roadmap:** Single-user Claude → Team time-share → Universal AI orchestrator
- **Phase 2:** Individual Claude Code downtime solution
- **Phase 4:** Team capacity sharing marketplace  
- **Phase 5:** Support all rate-limited AI providers
- 