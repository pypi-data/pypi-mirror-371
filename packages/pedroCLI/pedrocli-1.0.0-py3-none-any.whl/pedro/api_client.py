# src/pedro/api_client.py
import os
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional

# ----- CONFIGURATION: replace INSTALL_KEY at build time or inject via CI
# IMPORTANT: do NOT commit a real install key to public repos.
INSTALL_KEY = os.environ.get("PEDRO_INSTALL_KEY", "z8X1qWf3nKpL9aVrC7dYtH5sBjM4uE0o")

# PEDRO server (Netlify) URL: set env var locally or default placeholder
PEDRO_SERVER_URL = os.environ.get("PEDRO_SERVER_URL", "https://pedrocli.netlify.app")
REGISTER_ENDPOINT = PEDRO_SERVER_URL + "/.netlify/functions/register"
CHAT_ENDPOINT = PEDRO_SERVER_URL + "/.netlify/functions/chat"

# ----- STORAGE
DATA_DIR = Path.home() / ".pedro"
TOKEN_FILE = DATA_DIR / "token.json"
CONV_DIR = DATA_DIR / "conversations"
RATE_FILE = DATA_DIR / "rate.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONV_DIR.mkdir(parents=True, exist_ok=True)

# ----- Rate limit client-side rules
WINDOW_SECONDS = 60  # Aumentato a 60 secondi
MAX_REQUESTS_IN_WINDOW = 5  # Ridotto a 5 per evitare problemi
ESCALATION_SECONDS = [15, 30, 60, 120]  # Ridotti i tempi di blocco: 15s, 30s, 1m, 2m
TOKEN_TTL_MARGIN = 10  # seconds safety margin

class RateLimitException(Exception):
    def __init__(self, block_until: float, message: str = ""):
        self.block_until = block_until
        super().__init__(message or f"Rate limited until {block_until}")

# ---- JSON helpers
def _read_json(path: Path) -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _write_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---- Token management
def save_token(token_data: dict):
    _write_json(TOKEN_FILE, token_data)

def load_token() -> Optional[dict]:
    return _read_json(TOKEN_FILE)

def token_valid(token_data: dict) -> bool:
    if not token_data:
        return False
    exp_iso = token_data.get("expires_at")
    if not exp_iso:
        return False
    try:
        exp_ts = int(time.mktime(time.strptime(exp_iso.split(".")[0], "%Y-%m-%dT%H:%M:%S")))
    except Exception:
        return False
    return time.time() < exp_ts - TOKEN_TTL_MARGIN

def register_and_get_token(client_id: str = None) -> Optional[dict]:
    payload = {"install_key": INSTALL_KEY}
    if client_id:
        payload["client_id"] = client_id
    try:
        r = requests.post(REGISTER_ENDPOINT, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()
        save_token(data)
        return data
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        return None

def get_token() -> Optional[str]:
    token_data = load_token()
    if token_valid(token_data):
        return token_data["token"]
    new = register_and_get_token()
    if new:
        return new.get("token")
    return None

# ---- Conversation storage helpers
def conversation_path(name: str = "default") -> Path:
    return CONV_DIR / f"{name}.json"

def load_conversation(name: str = "default") -> List[Dict]:
    path = conversation_path(name)
    data = _read_json(path)
    if not data:
        return []
    return data.get("messages", [])

def save_conversation(messages: List[Dict], name: str = "default"):
    path = conversation_path(name)
    _write_json(path, {"messages": messages, "updated_at": time.time()})

def append_message(role: str, content: str, name: str = "default"):
    msgs = load_conversation(name)
    msgs.append({"role": role, "content": content, "ts": int(time.time())})
    # cap history length to last 50 messages
    if len(msgs) > 50:
        msgs = msgs[-50:]
    save_conversation(msgs, name)

# ---- Rate limiter (client-side)
def _load_rate_state() -> dict:
    data = _read_json(RATE_FILE)
    if not data:
        data = {"timestamps": [], "strikes": 0, "block_until": 0}
    data.setdefault("timestamps", [])
    data.setdefault("strikes", 0)
    data.setdefault("block_until", 0)
    return data

def _save_rate_state(state: dict):
    _write_json(RATE_FILE, state)

def check_and_record_request() -> None:
    now = time.time()
    st = _load_rate_state()
    if now < st.get("block_until", 0):
        raise RateLimitException(st["block_until"], "Temporarily blocked by client-side anti-spam")
    
    # Rimuovi timestamp vecchi
    ts = [t for t in st["timestamps"] if t > now - WINDOW_SECONDS]
    ts.append(now)
    st["timestamps"] = ts
    
    # Verifica se abbiamo superato il limite
    if len(ts) > MAX_REQUESTS_IN_WINDOW:
        # Calcola un tempo di blocco più breve se è il primo strike
        st["strikes"] = st.get("strikes", 0) + 1
        strike = min(st["strikes"] - 1, len(ESCALATION_SECONDS) - 1)
        
        # Resetta gli strike se l'ultimo è stato più di 10 minuti fa
        if st.get("last_strike_time", 0) < now - 600:  # 10 minuti
            st["strikes"] = 1
            strike = 0
        
        st["last_strike_time"] = now
        block = ESCALATION_SECONDS[strike]
        st["block_until"] = now + block
        st["timestamps"] = []
        _save_rate_state(st)
        raise RateLimitException(st["block_until"], f"Too many requests — blocked for {int(block)} seconds")
    else:
        # Riduci gli strike se non ci sono problemi per un po'
        if st.get("strikes", 0) > 0 and st.get("last_strike_time", 0) < now - 300:  # 5 minuti
            st["strikes"] = max(0, st.get("strikes", 0) - 1)
        
        st["timestamps"] = ts
        _save_rate_state(st)
        return

# ---- Chat call
def chat_send(message: str, conv_name: str = "default") -> Optional[str]:
    check_and_record_request()
    token = get_token()
    if not token:
        print("[ERROR] Unable to obtain token. Check INSTALL_KEY and server.")
        return None

    history = load_conversation(conv_name)
    history_with_user = history + [{"role": "user", "content": message}]
    payload = {"history": history_with_user, "message": message}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        # Ridotto il timeout da 120 a 30 secondi
        r = requests.post(CHAT_ENDPOINT, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        j = r.json()
        reply = j.get("reply")
        append_message("user", message, conv_name)
        if reply is not None:
            append_message("assistant", reply, conv_name)
        return reply
    except requests.Timeout:
        # Gestione specifica per il timeout
        print("[TIMEOUT] La richiesta ha impiegato troppo tempo. Controlla la tua connessione.")
        return None
    except requests.HTTPError as he:
        try:
            detail = he.response.text
            # Controlla se l'errore è dovuto a un token scaduto
            if he.response.status_code == 401 or "token" in detail.lower() or "unauthorized" in detail.lower():
                print("[TOKEN ERROR] Token scaduto o non valido. Tentativo di rinnovo...")
                # Forza il rinnovo del token
                new_token_data = register_and_get_token()
                if new_token_data:
                    print("[TOKEN] Token rinnovato con successo. Riprova il messaggio.")
                    # Potremmo riprovare automaticamente la richiesta qui
                    return None
        except Exception:
            detail = ""
        print(f"[HTTP ERROR] {he} - {detail}")
        return None
    except Exception as e:
        print(f"[ERROR] Chat call failed: {e}")
        return None
