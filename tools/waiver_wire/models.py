# tools/waiver_wire/models.py
# Nova Waiver Wire Tool - Data Models
# Built with Pydantic for type validation and structured output

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# ─────────────────────────────────────────
# LAYER 1: WHO IS THIS PLAYER
# ─────────────────────────────────────────

class PlayerProfile(BaseModel):
    name: str
    team: str
    positions: list[str]
    is_available: bool = True
    injury_status: Optional[str] = None  # DTD, OUT, IL10, IL60
    ownership_pct: Optional[float] = None  # 0.0 to 100.0
# ─────────────────────────────────────────
# LAYER 2: WHAT WILL THEY DO THIS WEEK
# ─────────────────────────────────────────

class WeeklyProjection(BaseModel):
    player_name: str
    week_start: date
    projected_games: int = Field(ge=0, le=7)  # between 0 and 7
    
    # Hitting projections
    projected_hr: float = 0.0
    projected_rbi: float = 0.0
    projected_r: float = 0.0
    projected_sb: float = 0.0
    projected_avg: float = 0.0
    projected_obp: float = 0.0
    
    # Pitching projections
    projected_ip: float = 0.0
    projected_k: float = 0.0
    projected_era: Optional[float] = None
    projected_whip: Optional[float] = None

# ─────────────────────────────────────────
# LAYER 3: HOW DOES NOVA RATE THIS PLAYER
# ─────────────────────────────────────────

class PlayerScore(BaseModel):
    player_name: str
    score_date: date
    
    # The 5 scoring layers
    raw_score: float = Field(ge=0.0, le=10.0)
    context_score: float = Field(ge=0.0, le=10.0)
    risk_score: float = Field(ge=0.0, le=10.0)
    signal_score: float = Field(ge=0.0, le=10.0)
    final_score: float = Field(ge=0.0, le=10.0)
    
    # Nova's reasoning
    summary: str
    top_strengths: list[str]
    top_concerns: list[str]
    
    # Confidence
    confidence: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0
    recommended_action: str  # "ADD", "MONITOR", "IGNORE"

# ─────────────────────────────────────────
# LAYER 4: SHOULD YOU ADD THIS PLAYER
# ─────────────────────────────────────────

class WaiverDecision(BaseModel):
    decision_date: date
    week_start: date
    
    # The full picture connected
    player: PlayerProfile
    projection: WeeklyProjection
    score: PlayerScore
    
    # The actual decision
    decision: str  # "ADD", "MONITOR", "IGNORE"
    priority_rank: int = Field(ge=1)  # 1 = highest priority
    
    # Your league context
    adds_remaining: int = Field(ge=0, le=5)
    il_slots_available: int = Field(ge=0)
    
    # Nova's final word
    reasoning: str
    drop_candidate: Optional[str] = None  # Who to drop for this add
