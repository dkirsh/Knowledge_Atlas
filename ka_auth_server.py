#!/usr/bin/env python3
"""
Knowledge Atlas Lightweight Auth Server
========================================
FastAPI + SQLite backend providing real JWT authentication for ATLAS.

Endpoints
---------
POST /auth/register          – create account (auto-approved for COGS 160)
POST /auth/login             – returns access + refresh JWT
POST /auth/refresh           – exchange refresh token for new access token
POST /auth/forgot-password   – generates reset token (printed to console / stored in DB)
POST /auth/reset-password    – validates token, sets new password
GET  /auth/me                – returns current user info (requires Bearer token)
POST /auth/github-username   – store student's GitHub username (requires Bearer token)
GET  /api/assignments        – returns student's assigned questions (requires Bearer token)
GET  /api/questions          – list all available research questions

Running
-------
    python3 ka_auth_server.py
    # Server starts on http://localhost:8765
    # CORS allows http://localhost and file:// origins (for local dev)

Notes
-----
- SQLite DB: ka_auth.db (created automatically in same directory as this file)
- JWT secret: auto-generated on first run, stored in ka_auth_secret.txt
- Password reset "email": reset link is printed to console (no SMTP needed for local dev)
- HTTPS: not used in local dev; do not deploy this as-is to a public server
"""

import os, sys, sqlite3, secrets, hashlib, time, json, re, smtplib, ssl
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import urlparse

# ── Third-party (install: pip3 install fastapi uvicorn python-jose[cryptography] passlib[bcrypt])
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError

# ════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════
BASE_DIR   = Path(__file__).parent
DB_PATH    = Path(os.getenv("KA_DB_PATH", str(BASE_DIR / "data" / "ka_auth.db")))
SECRET_FILE = Path(os.getenv("KA_SECRET_FILE", str(BASE_DIR / "data" / "ka_auth_secret.txt")))
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES  = 60
REFRESH_TOKEN_EXPIRE_DAYS    = 30
RESET_TOKEN_EXPIRE_MINUTES   = 60
PUBLIC_SITE_URL = os.getenv("KA_PUBLIC_SITE_URL", "https://xrlab.ucsd.edu/ka").rstrip("/")
SMTP_HOST = os.getenv("KA_SMTP_HOST", "")
SMTP_PORT = int(os.getenv("KA_SMTP_PORT", "465"))
SMTP_USER = os.getenv("KA_SMTP_USER", "")
SMTP_PASSWORD = os.getenv("KA_SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("KA_SMTP_FROM", SMTP_USER or "no-reply@ucsd.edu")
SMTP_USE_SSL = os.getenv("KA_SMTP_SSL", "1").lower() not in ("0", "false", "no")
SMTP_USE_STARTTLS = os.getenv("KA_SMTP_STARTTLS", "0").lower() in ("1", "true", "yes")


def _origin_from_url(url: str) -> str | None:
    parsed = urlparse((url or "").strip())
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def _build_allowed_origins() -> list[str]:
    configured = os.getenv("KA_CORS_ORIGINS", "").strip()
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]

    origins: list[str] = []
    public_origin = _origin_from_url(PUBLIC_SITE_URL)
    if public_origin:
        origins.append(public_origin)

    origins.extend([
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8765",
        "http://127.0.0.1:8765",
        "null",
    ])

    deduped: list[str] = []
    seen: set[str] = set()
    for origin in origins:
        if origin and origin not in seen:
            seen.add(origin)
            deduped.append(origin)
    return deduped


ALLOWED_CORS_ORIGINS = _build_allowed_origins()

# Load or generate JWT secret
def _get_secret() -> str:
    if SECRET_FILE.exists():
        return SECRET_FILE.read_text().strip()
    s = secrets.token_hex(48)
    SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
    SECRET_FILE.write_text(s)
    print(f"[KA-AUTH] Generated new JWT secret → {SECRET_FILE}")
    return s

SECRET_KEY = _get_secret()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)
ARTICLE_MODULE_LOADED = False
ARTICLE_MODULE_BACKEND = "unavailable"


def _hash_token(token: str) -> str:
    return "sha256$" + hashlib.sha256(token.encode("utf-8")).hexdigest()


def _mask_email(email: str) -> str:
    local, _, domain = (email or "").partition("@")
    if not domain:
        return "[redacted]"
    if len(local) <= 2:
        masked_local = local[:1] + "*"
    else:
        masked_local = local[:1] + "*" * (len(local) - 2) + local[-1:]
    return f"{masked_local}@{domain}"


def _find_reset_token_row(db: sqlite3.Connection, presented_token: str):
    hashed = _hash_token(presented_token)
    return db.execute(
        """
        SELECT * FROM reset_tokens
        WHERE token IN (?, ?) AND used=0
        ORDER BY CASE WHEN token=? THEN 0 ELSE 1 END
        LIMIT 1
        """,
        (hashed, presented_token, hashed),
    ).fetchone()


def _find_refresh_token_row(db: sqlite3.Connection, presented_token: str):
    hashed = _hash_token(presented_token)
    return db.execute(
        """
        SELECT * FROM refresh_tokens
        WHERE token IN (?, ?) AND revoked=0
        ORDER BY CASE WHEN token=? THEN 0 ELSE 1 END
        LIMIT 1
        """,
        (hashed, presented_token, hashed),
    ).fetchone()


def _revoke_refresh_tokens(db: sqlite3.Connection, user_id: str) -> None:
    db.execute(
        "UPDATE refresh_tokens SET revoked=1 WHERE user_id=? AND revoked=0",
        (user_id,),
    )

def send_password_reset_email(to_email: str, display_name: str, reset_url: str) -> bool:
    if not SMTP_HOST:
        print("[KA-AUTH] SMTP not configured; password-reset email not sent.")
        return False

    msg = EmailMessage()
    msg["Subject"] = "K-ATLAS password reset"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(
        f"Hello {display_name or 'K-ATLAS user'},\n\n"
        "A password reset was requested for your K-ATLAS account.\n\n"
        f"Reset your password here:\n{reset_url}\n\n"
        f"This link expires in {RESET_TOKEN_EXPIRE_MINUTES} minutes. "
        "If you did not request this reset, you can ignore this message.\n\n"
        "K-ATLAS\n"
    )

    try:
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=20) as smtp:
                if SMTP_USER:
                    smtp.login(SMTP_USER, SMTP_PASSWORD)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
                smtp.ehlo()
                if SMTP_USE_STARTTLS:
                    smtp.starttls(context=ssl.create_default_context())
                    smtp.ehlo()
                if SMTP_USER:
                    smtp.login(SMTP_USER, SMTP_PASSWORD)
                smtp.send_message(msg)
        return True
    except Exception as exc:
        print(f"[KA-AUTH] Password-reset email failed for {_mask_email(to_email)}: {exc}")
        return False


def issue_reset_token(db: sqlite3.Connection, user_id: str) -> tuple[str, str]:
    """
    Invalidate older unused reset tokens for the same user, then issue one fresh
    token and return `(token, expires_at_iso)`.
    """
    token = secrets.token_urlsafe(32)
    exp = (datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)).isoformat()
    db.execute("UPDATE reset_tokens SET used=1 WHERE user_id=? AND used=0", (user_id,))
    db.execute("INSERT INTO reset_tokens VALUES (?,?,?,0)", (_hash_token(token), user_id, exp))
    return token, exp

# ════════════════════════════════════════════════
# DATABASE
# ════════════════════════════════════════════════
def get_db() -> sqlite3.Connection:
    db = sqlite3.connect(str(DB_PATH), timeout=5.0)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=5000")
    return db


def _ensure_column(db: sqlite3.Connection, table: str, column: str, spec: str) -> None:
    cols = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
    if column not in cols:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {spec}")


_GITHUB_USERNAME_RE = re.compile(r"^(?!-)(?!.*--)[a-z0-9-]{1,39}(?<!-)$")


def _normalize_github_username(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        raise HTTPException(400, "GitHub username is required")

    if "github.com/" in value:
        value = value.split("github.com/", 1)[1]
    value = value.strip().strip("/")
    value = value.split("/", 1)[0]
    if value.startswith("@"):
        value = value[1:]
    value = value.strip().lower()

    if not _GITHUB_USERNAME_RE.fullmatch(value):
        raise HTTPException(
            400,
            "Invalid GitHub username. Use 1-39 letters, numbers, or single hyphens; no spaces; no leading or trailing hyphen."
        )
    return value

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id     TEXT PRIMARY KEY,
        email       TEXT UNIQUE NOT NULL,
        first_name  TEXT NOT NULL,
        last_name   TEXT NOT NULL,
        role        TEXT NOT NULL DEFAULT 'student',
        password_hash TEXT NOT NULL,
        status      TEXT NOT NULL DEFAULT 'pending',
        track       TEXT,
        question_id TEXT,
        institution TEXT DEFAULT 'UC San Diego',
        department  TEXT,
        created_at  TEXT NOT NULL,
        approved_at TEXT,
        last_login  TEXT
    );
    CREATE TABLE IF NOT EXISTS reset_tokens (
        token       TEXT PRIMARY KEY,
        user_id     TEXT NOT NULL,
        expires_at  TEXT NOT NULL,
        used        INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        token       TEXT PRIMARY KEY,
        user_id     TEXT NOT NULL,
        expires_at  TEXT NOT NULL,
        revoked     INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS research_questions (
        question_id TEXT PRIMARY KEY,
        label       TEXT NOT NULL,
        domain      TEXT NOT NULL,
        text        TEXT NOT NULL,
        atlas_topic TEXT,
        notes       TEXT
    );
    """)
    # Seed research questions if table is empty
    count = db.execute("SELECT COUNT(*) FROM research_questions").fetchone()[0]
    if count == 0:
        questions = [
            # ── 1. Lighting (3 questions) ──
            ("Q01", "Daylighting & Sustained Attention",  "Lighting",
             "Does access to natural daylight during working hours improve sustained attention? How large is the effect compared to equivalent artificial lighting, and does it depend on circadian timing?",
             "luminous__cog_attention", "High-VOI gap; Boubekri et al. 2014 gives one anchor."),
            ("Q02", "Colour Temperature & Alertness",     "Lighting",
             "Does correlated colour temperature of artificial lighting affect alertness independently of illuminance level? Is the effect robust across different tasks and times of day?",
             "luminous__cog_performance", "Direction unclear in older studies; recent LED research needed."),
            ("Q03", "Circadian Lighting & Sleep Quality",  "Lighting",
             "How does daytime exposure to circadian-effective light (melanopic EDI > 250 lux) in offices and classrooms affect nighttime sleep quality, and what minimum daily dose is required?",
             "luminous__health", "Boundary gap; dose-response poorly characterized outside clinical settings."),

            # ── 2. Acoustics and Soundscape (3 questions) ──
            ("Q04", "Soundscape Features & Hedonic Valence", "Acoustics and Soundscape",
             "What features of an acoustic environment — reverberation time, background noise level, spectral content — most reliably predict hedonic valence ratings from occupants?",
             "acoustic__affect_soundscape", "Multi-feature gap; almost no VR-based evidence."),
            ("Q05", "Background Noise & Working Memory",    "Acoustics and Soundscape",
             "At what sound pressure level does continuous background noise begin to impair working memory performance, and does the impairment threshold differ for speech-spectrum vs. broadband noise?",
             "acoustic__cog_memory", "Boundary gap; existing thresholds are task-specific and not generalized."),
            ("Q06", "Designed Soundscapes & Restoration",   "Acoustics and Soundscape",
             "Can a designed soundscape (birdsong, flowing water, wind) in an indoor environment produce attentional restoration comparable to actual outdoor nature exposure as measured by ANT and PRS?",
             "acoustic__affect_restoration", "Direction gap; soundscape restoration literature is observational."),

            # ── 3. Spatial Form and Configuration (3 questions) ──
            ("Q07", "Ceiling Height & Creativity",        "Spatial Form and Configuration",
             "Does ceiling height influence divergent thinking independently of perceived spaciousness? What is the boundary condition at which the effect disappears?",
             "spatial__cog_performance", "Direction + Boundary gap; Meyers-Levy replication contested."),
            ("Q08", "Enclosure Ratio & Stress Physiology", "Spatial Form and Configuration",
             "What enclosure ratio (wall height to floor area) produces the lowest physiological stress markers (cortisol, EDA) during focused work, and does the optimal ratio shift between individual and collaborative tasks?",
             "spatial__physio", "Boundary gap; prospect-refuge theory predicts optimum but not tested parametrically."),
            ("Q09", "Spatial Openness & Social Interaction", "Spatial Form and Configuration",
             "Does the degree of spatial openness in a shared workspace predict the frequency and quality of spontaneous social interaction, or do acoustic and visual privacy override spatial layout effects?",
             "spatial__social", "Direction gap; open-plan office debate lacks controlled spatial parametric studies."),

            # ── 4. Natural and Biophilic Conditions (3 questions) ──
            ("Q10", "Fractal Dimension & Stress Recovery", "Natural and Biophilic Conditions",
             "Is fractal dimension of a visual scene causally related to psychophysiological stress recovery, or is the correlation mediated by familiarity with natural environments?",
             "natural__affect_negative_stress", "Mechanism gap; Taylor fractal work is correlational only."),
            ("Q11", "Window Views & Cortisol Reduction",   "Natural and Biophilic Conditions",
             "What is the minimum exposure duration to a window view of nature sufficient to produce measurable cortisol reduction? Does view content matter independently of view presence?",
             "natural__affect_restoration", "Boundary gap; Ulrich 1984 seminal but not replicated with modern measures."),
            ("Q12", "Indoor Plants & Cognitive Restoration", "Natural and Biophilic Conditions",
             "Do indoor plants in a workspace improve attentional restoration beyond visual preference, and does the effect depend on plant density, species, or visibility from the workstation?",
             "natural__cog_attention", "Direction gap; Lohr et al. 1996 widely cited but effect sizes unreplicated."),

            # ── 5. Material and Surface Conditions (2 questions) ──
            ("Q13", "Wood Interiors & Wellbeing",          "Material and Surface Conditions",
             "Do visible wood surfaces in an interior environment predict wellbeing outcomes beyond what is explained by lighting and texture diversity alone?",
             "material__affect_wellbeing", "Low evidence base; Rice et al. 2006 is exploratory only."),
            ("Q14", "Surface Texture & Haptic Comfort",    "Material and Surface Conditions",
             "Does the tactile roughness of interior surfaces (desks, walls, flooring) independently affect self-reported comfort and physiological arousal, or is the effect entirely mediated by visual texture perception?",
             "material__affect_comfort", "Mechanism gap; haptic vs. visual texture confounded in most material studies."),

            # ── 6. Thermal and Air Conditions (2 questions) ──
            ("Q15", "Temperature & Cognitive Performance",  "Thermal and Air Conditions",
             "What is the optimal indoor air temperature range for maximizing cognitive performance on complex tasks, and does the optimum shift with acclimatization, age, or clothing insulation?",
             "thermal__cog_performance", "Boundary gap; Seppänen et al. 2006 meta-analysis uses coarse categories."),
            ("Q16", "CO2 Concentration & Decision Quality", "Thermal and Air Conditions",
             "At what CO2 concentration does strategic decision-making quality (measured by SMS or comparable instrument) begin to decline, and is the threshold lower for cognitively demanding vs. routine tasks?",
             "thermal__cog_cognitive_load", "Boundary gap; Allen et al. 2016 COGFX study needs replication across task types."),

            # ── 7. Aesthetic Conditions (2 questions) ──
            ("Q17", "Interior Colour & Cognitive Performance", "Aesthetic Conditions",
             "Does the dominant colour of interior surfaces (warm vs. cool hues, saturation level) affect sustained attention or creative output when luminance and illuminance are controlled?",
             "material__cog_performance", "Direction gap; colour psychology findings rarely control for luminance confounds."),
            ("Q18", "Visual Complexity & Aesthetic Preference", "Aesthetic Conditions",
             "Is there an optimal level of visual complexity in interior design that maximizes both aesthetic preference and psychological comfort, and does the optimum follow an inverted-U (Berlyne) curve across diverse populations?",
             "spatial__affect_preference", "Boundary gap; Berlyne arousal-potential model untested in real architectural settings."),

            # ── 8. Wayfinding and Environmental Legibility (2 questions) ──
            ("Q19", "Spatial Complexity & Wayfinding Stress", "Wayfinding and Environmental Legibility",
             "How does the visual complexity of a building interior affect wayfinding efficiency and associated stress — and does this interaction depend on the user's spatial ability?",
             "spatial__behav_navigation", "Mechanism gap; wayfinding literature is separate from neuroarchitecture."),
            ("Q20", "Signage vs. Spatial Legibility",       "Wayfinding and Environmental Legibility",
             "Does improving the spatial legibility of a building (sight lines, landmarks, layout regularity) reduce wayfinding errors more effectively than adding signage, and do the two interventions interact?",
             "spatial__behav_navigation", "Direction gap; signage and architectural legibility studied separately."),

            # ── 9. Social-Spatial Conditions (2 questions) ──
            ("Q21", "Density & Crowding Stress",              "Social-Spatial Conditions",
             "What spatial density threshold (persons per square metre) triggers subjective crowding and elevated cortisol in shared workspaces, and does visual access to an exit or window moderate the threshold?",
             "social_spatial__affect_negative_stress", "Boundary gap; crowding literature is mostly residential or transportation."),
            ("Q22", "Privacy Gradient & Collaboration Quality", "Social-Spatial Conditions",
             "Does a graduated privacy gradient (open → semi-open → enclosed spaces within one floor) improve the quality of collaborative output compared to uniformly open or uniformly enclosed plans?",
             "social_spatial__social", "Direction gap; activity-based working studies are mostly survey-based."),

            # ── 10. Olfactory Conditions (2 questions) ──
            ("Q23", "Ambient Scent & Cognitive Performance", "Olfactory Conditions",
             "Does ambient scent (e.g., peppermint, rosemary, lemon) in a work environment improve sustained attention or memory recall beyond placebo, and does the effect depend on scent-task congruence?",
             "natural__cog_performance", "Direction gap; aroma studies have small n and rarely control for expectancy."),
            ("Q24", "Natural Scent & Stress Restoration",    "Olfactory Conditions",
             "Does exposure to forest-associated volatile organic compounds (phytoncides, terpenes) in an indoor setting reduce cortisol and sympathetic nervous system activation comparably to actual forest bathing?",
             "natural__affect_restoration", "Mechanism gap; shinrin-yoku literature confounds scent with visual and auditory cues."),

            # ── 11. Temporal and Exposure Conditions (2 questions) ──
            ("Q25", "Exposure Duration & Habituation",       "Temporal and Exposure Conditions",
             "How quickly do occupants habituate to environmental interventions (nature views, soundscapes, lighting changes), and does the restorative benefit decay linearly, asymptotically, or show a rebound effect after removal?",
             "natural__affect_restoration", "Boundary gap; almost no longitudinal studies of environmental intervention persistence."),
            ("Q26", "Acute vs. Chronic Environmental Effects", "Temporal and Exposure Conditions",
             "Do environmental design features (biophilic elements, optimal lighting) that show acute benefits in laboratory studies produce sustained improvements over weeks and months of daily exposure in real buildings?",
             "luminous__health", "Replication gap; most studies are single-session; ecological validity is unknown."),

            # ── 12. Cultural Framing (2 questions) ──
            ("Q27", "Cultural Background & Spatial Preference", "Cultural Framing",
             "Do preferences for enclosure, prospect, and spatial openness vary systematically across cultural backgrounds (collectivist vs. individualist societies), and does cultural background moderate the stress-reduction effects of architectural form?",
             "spatial__affect_preference", "Direction gap; prospect-refuge theory tested almost exclusively in Western samples."),
            ("Q28", "Meaning & Place Attachment in Design",    "Cultural Framing",
             "Does culturally meaningful architectural symbolism (ornament, material choice, spatial organisation) affect occupant wellbeing and sense of belonging independently of physical comfort and spatial quality?",
             "social_spatial__affect_wellbeing", "Mechanism gap; environmental psychology rarely separates symbolic from sensory effects."),

            # ── 13. Participant State, Expertise, and Perceived Control (2 questions) ──
            ("Q29", "Personal Control & Stress Reduction",     "Participant State, Expertise, and Perceived Control",
             "Does giving occupants personal control over lighting, temperature, or acoustic conditions reduce physiological stress markers more than providing objectively optimal fixed conditions, and is the benefit mediated by perceived agency?",
             "control__affect_negative_stress", "Mechanism gap; perceived control confounded with actual environmental change."),
            ("Q30", "Expertise & Environmental Sensitivity",   "Participant State, Expertise, and Perceived Control",
             "Do architects and design professionals show different physiological and neural responses to spatial quality (proportion, complexity, coherence) compared to non-experts, and does expertise sharpen or blunt environmental stress effects?",
             "spatial__neural", "Direction gap; expertise effects studied in aesthetic judgment but not in environmental stress."),
        ]
        db.executemany(
            "INSERT INTO research_questions VALUES (?,?,?,?,?,?)", questions)

    _ensure_column(db, "users", "github_username", "TEXT")
    _ensure_column(db, "users", "github_username_source", "TEXT")
    _ensure_column(db, "users", "github_username_updated_at", "TEXT")

    # Seed instructor account if no instructor exists
    instr = db.execute("SELECT user_id FROM users WHERE role='instructor' LIMIT 1").fetchone()
    if not instr:
        uid = "instructor_kirsh"
        email = "dkirsh@ucsd.edu"
        bootstrap_password = os.getenv("KA_BOOTSTRAP_INSTRUCTOR_PASSWORD", "change-me-local-only")
        ph = pwd_context.hash(bootstrap_password)
        now = datetime.now(timezone.utc).isoformat()
        db.execute("""INSERT OR IGNORE INTO users
            (user_id,email,first_name,last_name,role,password_hash,status,created_at,approved_at)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (uid, email, "David", "Kirsh", "instructor", ph, "approved", now, now))
        print("[KA-AUTH] Seeded instructor account")
        print("[KA-AUTH] Set KA_BOOTSTRAP_INSTRUCTOR_PASSWORD before first run, or change the instructor password immediately via POST /auth/change-password")

    db.commit()
    db.close()

# ════════════════════════════════════════════════
# JWT HELPERS
# ════════════════════════════════════════════════
def create_access_token(user_id: str, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "role": role, "exp": exp, "type": "access"},
                      SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    token = secrets.token_urlsafe(48)
    exp = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db = get_db()
    db.execute("INSERT INTO refresh_tokens VALUES (?,?,?,0)",
               (_hash_token(token), user_id, exp.isoformat()))
    db.commit(); db.close()
    return token

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise JWTError("wrong token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(creds.credentials)
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE user_id=?", (payload["sub"],)).fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    if row["status"] != "approved":
        raise HTTPException(status_code=403, detail="Account not yet approved by instructor")
    return dict(row)

def require_instructor(user=Depends(get_current_user)):
    if user["role"] not in ("instructor", "admin"):
        raise HTTPException(status_code=403, detail="Instructor access required")
    return user

# ════════════════════════════════════════════════
# PYDANTIC MODELS
# ════════════════════════════════════════════════
class RegisterRequest(BaseModel):
    email:       str
    password:    str
    first_name:  str
    last_name:   str
    department:  str = ""
    track:       str = ""
    question_id: str = ""

class LoginRequest(BaseModel):
    email:    str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token:        str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str


class ChangeEmailRequest(BaseModel):
    current_password: str
    new_email:        EmailStr


class ManualResetLinkRequest(BaseModel):
    email: EmailStr

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UpdateGitHubUsernameRequest(BaseModel):
    github_username: str
    source: str = "explicit"

# ════════════════════════════════════════════════
# APP
# ════════════════════════════════════════════════
app = FastAPI(title="Knowledge Atlas Auth API", version="1.0.0",
              description="Lightweight JWT authentication for Knowledge Atlas (local dev)")

app.add_middleware(CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"])

# ── DB INIT ON STARTUP (runs whether invoked via __main__ or uvicorn)
@app.on_event("startup")
def _startup_init_db():
    init_db()
    try:
        import ka_article_endpoints
        ka_article_endpoints._init_article_tables()
    except Exception:
        pass

# ── REGISTER
@app.post("/auth/register", status_code=201)
def register(req: RegisterRequest):
    if len(req.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    email = req.email.strip().lower()
    uid = "u_" + secrets.token_hex(8)
    ph  = pwd_context.hash(req.password)
    now = datetime.now(timezone.utc).isoformat()
    db  = get_db()
    # Auto-approve COGS 160 students so they can start working immediately.
    initial_status = "approved"
    approved_at    = now

    try:
        db.execute("""INSERT INTO users
            (user_id,email,first_name,last_name,role,password_hash,status,
             track,question_id,department,created_at,approved_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid, email, req.first_name.strip(), req.last_name.strip(),
             "student", ph, initial_status,
             req.track, req.question_id, req.department, now, approved_at))
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(409, "An account with that email already exists")
    finally:
        db.close()
    return {"message": "Registration complete! Your account is active — you can sign in now.",
            "user_id": uid, "status": "approved"}

# ── LOGIN
@app.post("/auth/login")
def login(req: LoginRequest):
    email = req.email.strip().lower()
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    db.close()
    if not row or not pwd_context.verify(req.password, row["password_hash"]):
        raise HTTPException(401, "Incorrect email or password")
    if row["status"] == "pending":
        raise HTTPException(403, "Your account is pending approval. Check back after the instructor reviews it.")
    if row["status"] == "rejected":
        raise HTTPException(403, "Your account application was not approved. Contact the course instructor.")
    # Update last_login
    db = get_db()
    db.execute("UPDATE users SET last_login=? WHERE user_id=?",
               (datetime.now(timezone.utc).isoformat(), row["user_id"]))
    db.commit(); db.close()
    access  = create_access_token(row["user_id"], row["role"])
    refresh = create_refresh_token(row["user_id"])
    return {
        "access_token":  access,
        "refresh_token": refresh,
        "token_type":    "bearer",
        "user": {
            "user_id":    row["user_id"],
            "email":      row["email"],
            "first_name": row["first_name"],
            "last_name":  row["last_name"],
            "role":       row["role"],
            "track":      row["track"],
            "question_id": row["question_id"],
        }
    }

# ── FORGOT PASSWORD
@app.post("/auth/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    email = req.email.strip().lower()
    db = get_db()
    try:
        row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            raise HTTPException(404, "That email is not registered in K-ATLAS. Check the address or register a new account.")
        token, exp = issue_reset_token(db, row["user_id"])
        db.commit()
        first_name = row["first_name"]
        last_name = row["last_name"]
    except HTTPException:
        db.rollback()
        raise
    except sqlite3.Error as exc:
        db.rollback()
        print(f"[KA-AUTH] Password-reset token write failed for {email}: {exc}")
        raise HTTPException(503, "Password reset is temporarily unavailable. Please try again in a moment.")
    finally:
        db.close()
    reset_url = f"{PUBLIC_SITE_URL}/ka_reset_password.html?token={token}"
    display_name = f"{first_name} {last_name}".strip()
    email_sent = send_password_reset_email(email, display_name, reset_url)
    print(f"[KA-AUTH] Password reset requested for {_mask_email(email)}; email_sent={email_sent}; expires={exp}")
    message = "Password reset email sent. Check your inbox."
    if not email_sent:
        message = "That email is registered, but reset email is not working on this server right now. Contact the instructor from that address for a manual reset."
    return {
        "message": message,
        "registered": True,
        "email_sent": email_sent
    }

# ── RESET PASSWORD
@app.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest):
    if len(req.new_password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    db = get_db()
    try:
        row = _find_reset_token_row(db, req.token)
        if not row:
            raise HTTPException(400, "Reset token is invalid or has already been used")
        exp = datetime.fromisoformat(row["expires_at"])
        if exp < datetime.now(timezone.utc):
            raise HTTPException(400, "Reset token has expired. Request a new one.")
        ph = pwd_context.hash(req.new_password)
        db.execute("UPDATE users SET password_hash=? WHERE user_id=?", (ph, row["user_id"]))
        db.execute("UPDATE reset_tokens SET used=1 WHERE token=?", (row["token"],))
        _revoke_refresh_tokens(db, row["user_id"])
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except sqlite3.Error:
        db.rollback()
        raise HTTPException(503, "Password reset is temporarily unavailable. Please try again in a moment.")
    finally:
        db.close()
    return {"message": "Password updated successfully. You can now log in."}

# ── CHANGE PASSWORD (authenticated)
@app.post("/auth/change-password")
def change_password(req: ChangePasswordRequest, user=Depends(get_current_user)):
    db = get_db()
    try:
        row = db.execute("SELECT password_hash FROM users WHERE user_id=?",
                         (user["user_id"],)).fetchone()
        if not pwd_context.verify(req.current_password, row["password_hash"]):
            raise HTTPException(400, "Current password is incorrect")
        if len(req.new_password) < 8:
            raise HTTPException(400, "New password must be at least 8 characters")
        db.execute("UPDATE users SET password_hash=? WHERE user_id=?",
                   (pwd_context.hash(req.new_password), user["user_id"]))
        _revoke_refresh_tokens(db, user["user_id"])
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except sqlite3.Error:
        db.rollback()
        raise HTTPException(503, "Password change is temporarily unavailable. Please try again in a moment.")
    finally:
        db.close()
    return {"message": "Password changed successfully"}


@app.post("/auth/change-email")
def change_email(req: ChangeEmailRequest, user=Depends(get_current_user)):
    new_email = str(req.new_email).strip().lower()
    db = get_db()
    try:
        row = db.execute("""
            SELECT user_id, email, first_name, last_name, role, status, track, question_id, last_login, password_hash
            FROM users
            WHERE user_id=?
        """, (user["user_id"],)).fetchone()
        if not row:
            raise HTTPException(401, "User not found")
        if not pwd_context.verify(req.current_password, row["password_hash"]):
            raise HTTPException(400, "Current password is incorrect")
        if new_email == row["email"]:
            return {
                "message": "That is already the email on this account.",
                "user": {
                    "user_id": row["user_id"],
                    "email": row["email"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "role": row["role"],
                    "status": row["status"],
                    "track": row["track"],
                    "question_id": row["question_id"],
                    "last_login": row["last_login"],
                }
            }
        db.execute("UPDATE users SET email=? WHERE user_id=?", (new_email, row["user_id"]))
        _revoke_refresh_tokens(db, row["user_id"])
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(409, "An account with that email already exists")
    except sqlite3.Error:
        db.rollback()
        raise HTTPException(503, "Email change is temporarily unavailable. Please try again in a moment.")
    finally:
        db.close()
    return {
        "message": "Email changed successfully.",
        "user": {
            "user_id": row["user_id"],
            "email": new_email,
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "role": row["role"],
            "status": row["status"],
            "track": row["track"],
            "question_id": row["question_id"],
            "last_login": row["last_login"],
        }
    }

# ── ME
@app.get("/auth/me")
def me(user=Depends(get_current_user)):
    return {k: user[k] for k in
            (
                "user_id",
                "email",
                "first_name",
                "last_name",
                "role",
                "status",
                "track",
                "question_id",
                "last_login",
                "github_username",
                "github_username_source",
                "github_username_updated_at",
            )}


@app.post("/auth/github-username")
def update_github_username(req: UpdateGitHubUsernameRequest, user=Depends(get_current_user)):
    username = _normalize_github_username(req.github_username)
    source = (req.source or "explicit").strip().lower()
    if source not in {"explicit", "email_local_part"}:
        source = "explicit"

    now = datetime.now(timezone.utc).isoformat()
    db = get_db()
    try:
        db.execute(
            """
            UPDATE users
            SET github_username=?, github_username_source=?, github_username_updated_at=?
            WHERE user_id=?
            """,
            (username, source, now, user["user_id"])
        )
        db.commit()
    except sqlite3.Error:
        db.rollback()
        raise HTTPException(503, "GitHub username update is temporarily unavailable. Please try again in a moment.")
    finally:
        db.close()

    return {
        "message": "GitHub username saved.",
        "github_username": username,
        "github_username_source": source,
        "github_username_updated_at": now,
    }

# ── UPDATE TRACK
class UpdateTrackRequest(BaseModel):
    track: str

@app.post("/auth/update-track")
def update_track(req: UpdateTrackRequest, user=Depends(get_current_user)):
    valid_tracks = {"track1", "track2", "track3", "track4"}
    if req.track not in valid_tracks:
        raise HTTPException(400, f"Invalid track. Must be one of: {', '.join(sorted(valid_tracks))}")
    db = get_db()
    db.execute("UPDATE users SET track=? WHERE user_id=?", (req.track, user["user_id"]))
    db.commit(); db.close()
    track_names = {
        "track1": "Track 1: Image Tagger",
        "track2": "Track 2: Article Finder",
        "track3": "Track 3: AI & VR",
        "track4": "Track 4: Interaction Design"
    }
    return {
        "message": f"You have joined {track_names.get(req.track, req.track)}!",
        "track": req.track,
        "track_name": track_names.get(req.track, req.track)
    }

# ── ASSIGNMENTS
@app.get("/api/assignments")
def get_assignment(user=Depends(get_current_user)):
    if not user["question_id"]:
        return {"assigned": False,
                "message": "No question assigned yet. Contact the course instructor."}
    db = get_db()
    q = db.execute("SELECT * FROM research_questions WHERE question_id=?",
                   (user["question_id"],)).fetchone()
    db.close()
    if not q:
        return {"assigned": False, "message": "Question not found in database"}
    return {
        "assigned":    True,
        "question_id": q["question_id"],
        "label":       q["label"],
        "domain":      q["domain"],
        "text":        q["text"],
        "atlas_topic": q["atlas_topic"],
        "notes":       q["notes"],
    }

# ── RESEARCH QUESTIONS LIST
@app.get("/api/questions")
def list_questions(user=Depends(require_instructor)):
    db = get_db()
    rows = db.execute("SELECT * FROM research_questions ORDER BY question_id").fetchall()
    db.close()
    return [dict(r) for r in rows]

# ── TOKEN REFRESH
@app.post("/auth/refresh")
def refresh_access_token(req: RefreshTokenRequest):
    db = get_db()
    row = _find_refresh_token_row(db, req.refresh_token)
    if not row:
        db.close()
        raise HTTPException(401, "Invalid or revoked refresh token")
    if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
        db.execute("UPDATE refresh_tokens SET revoked=1 WHERE token=?", (row["token"],))
        db.commit()
        db.close()
        raise HTTPException(401, "Refresh token expired — please sign in again")
    user = db.execute("SELECT * FROM users WHERE user_id=?", (row["user_id"],)).fetchone()
    if not user:
        db.close()
        raise HTTPException(401, "User not found")
    if user["status"] != "approved":
        db.close()
        raise HTTPException(403, "Account not active")
    db.close()
    access = create_access_token(user["user_id"], user["role"])
    return {
        "access_token": access,
        "token_type": "bearer",
        "user": {
            "user_id":    user["user_id"],
            "email":      user["email"],
            "first_name": user["first_name"],
            "last_name":  user["last_name"],
            "role":       user["role"],
            "track":      user["track"],
            "question_id": user["question_id"],
        }
    }


@app.post("/api/instructor/manual-reset-link")
@app.post("/auth/manual-reset-link")
def manual_reset_link(req: ManualResetLinkRequest, user=Depends(require_instructor)):
    email = str(req.email).strip().lower()
    db = get_db()
    try:
        row = db.execute("""
            SELECT user_id, email, first_name, last_name, role, status
            FROM users
            WHERE email=?
        """, (email,)).fetchone()
        if not row:
            raise HTTPException(404, "That email is not registered in K-ATLAS.")
        token, exp = issue_reset_token(db, row["user_id"])
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except sqlite3.Error as exc:
        db.rollback()
        raise HTTPException(503, f"Could not create a manual reset link right now: {exc}")
    finally:
        db.close()

    reset_url = f"{PUBLIC_SITE_URL}/ka_reset_password.html?token={token}"
    print(
        f"[KA-AUTH] Manual reset link generated by {_mask_email(user['email'])} "
        f"for {_mask_email(email)}; expires={exp}"
    )
    return {
        "message": f"Manual reset link generated for {email}.",
        "user": {
            "user_id": row["user_id"],
            "email": row["email"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "role": row["role"],
            "status": row["status"],
        },
        "reset_url": reset_url,
        "expires_at": exp,
    }

# ── HEALTH CHECK
@app.get("/health")
def health():
    modules = ["auth"]
    if ARTICLE_MODULE_LOADED:
        modules.append("articles")
    return {
        "status": "ok",
        "server": "Knowledge Atlas Auth",
        "version": "1.1.0",
        "modules": modules,
        "article_module_loaded": ARTICLE_MODULE_LOADED,
        "article_classifier_backend": ARTICLE_MODULE_BACKEND,
    }

# ════════════════════════════════════════════════
# ARTICLE SUBMISSION MODULE
# ════════════════════════════════════════════════
# Import and configure the article submission endpoints (see ka_article_endpoints.py)
try:
    import ka_article_endpoints
    ka_article_endpoints.configure(
        get_db=get_db,
        get_current_user=get_current_user,
        get_current_user_optional=None,  # articles module uses its own optional auth
        require_instructor=require_instructor,
    )
    app.include_router(ka_article_endpoints.router)
    app.include_router(ka_article_endpoints.student_router)
    ARTICLE_MODULE_LOADED = True
    ARTICLE_MODULE_BACKEND = getattr(ka_article_endpoints, "CLASSIFIER_BACKEND", "unknown")
    print("[KA-AUTH] Article submission module loaded ✓")
    print("[KA-AUTH] Student endpoints loaded ✓ (/api/student/fetch-abstracts, /title-only, /classify-one)")
except ImportError as e:
    ARTICLE_MODULE_LOADED = False
    ARTICLE_MODULE_BACKEND = "unavailable"
    print(f"[KA-AUTH] Article submission module not available: {e}")
    print("[KA-AUTH] Server running with auth-only endpoints")

# ── CRITIQUE SUGGESTION MODULE (KA-T22)
# POST /api/critique/suggest — accepts the usability-critic payload, calls the
# local subscription CLI, and returns per-heuristic suggestions. If the CLI is
# unavailable, returns rule-based fallback suggestions so the UI remains
# functional in local dev. API-AI calls are forbidden.
try:
    import ka_critique_endpoints
    app.include_router(ka_critique_endpoints.router)
    print("[KA-AUTH] Critique suggest endpoint loaded ✓ (POST /api/critique/suggest)")
except ImportError as e:
    print(f"[KA-AUTH] Critique module not available: {e}")

# ── SUBSTITUTION SKILL + V7-LITE CONTRACT MODULES
try:
    import ka_substitution_skill
    ka_substitution_skill.init_substitution_graph_db()
    app.include_router(ka_substitution_skill.router)
    print("[KA-AUTH] Substitution skill loaded ✓ (/api/substitution_skill/*)")
except ImportError as e:
    print(f"[KA-AUTH] Substitution skill not available: {e}")

try:
    import ka_v7_lite
    app.include_router(ka_v7_lite.router)
    print("[KA-AUTH] V7-Lite endpoint loaded ✓ (POST /api/v7_lite/ingest)")
except ImportError as e:
    print(f"[KA-AUTH] V7-Lite module not available: {e}")

try:
    import ka_search_synthesis
    app.include_router(ka_search_synthesis.router)
    print("[KA-AUTH] Search synthesis loaded ✓ (POST /api/search/synthesize)")
except ImportError as e:
    print(f"[KA-AUTH] Search synthesis not available: {e}")

# ── RESET PAGE REDIRECT (convenience link in reset email)
@app.get("/reset")
def reset_page_redirect(token: str):
    from fastapi.responses import RedirectResponse
    import urllib.parse
    safe_token = urllib.parse.quote(token, safe='')
    return RedirectResponse(f"ka_reset_password.html?token={safe_token}", status_code=302)

# ════════════════════════════════════════════════
# STATIC FILE SERVING
# ════════════════════════════════════════════════
# Serve the KA HTML/JS/CSS/data files from the same origin as the API.
# Uses a catch-all GET route so API routes (/auth/*, /api/*, /health) take priority.
_static = StaticFiles(directory=str(BASE_DIR), html=True)

@app.get("/{full_path:path}")
async def serve_static(full_path: str, request: Request):
    """Fallback: serve static files for any GET not matched by API routes."""
    from starlette.responses import Response as StarletteResponse
    # Let StaticFiles handle the request
    response = await _static.get_response(full_path, request.scope)
    return response

# ════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    init_db()
    # Initialize article tables if module is loaded
    try:
        ka_article_endpoints._init_article_tables()
        print("[KA-AUTH] Article tables initialized ✓")
    except Exception as e:
        print(f"[KA-AUTH] Article table init skipped: {e}")
    print("\n" + "═"*60)
    print("  Knowledge Atlas Auth Server")
    print("  http://localhost:8765")
    print("  API docs: http://localhost:8765/docs")
    print("  Health:   http://localhost:8765/health")
    print("═"*60 + "\n")
    uvicorn.run("ka_auth_server:app", host="127.0.0.1", port=8765, reload=False)
