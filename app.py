import json
import os
import time
from datetime import date

import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

st.set_page_config(page_title="Suivi du temps de travail", layout="wide")

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

CHRONO_LABELS = [
    "Temps travaillé",
    "Temps sur la route",
    "Temps chez le patient",
    "Temps pause",
]


# ---------- Persistence ----------
def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def empty_day() -> dict:
    return {
        "chrono": {label: {"elapsed": 0.0, "running": False, "start": None} for label in CHRONO_LABELS},
        "custom": [
            {"label": "", "value": ""},
            {"label": "", "value": ""},
        ],
    }


if "data" not in st.session_state:
    st.session_state.data = load_data()


def get_day(day_key: str) -> dict:
    if day_key not in st.session_state.data:
        st.session_state.data[day_key] = empty_day()
    day = st.session_state.data[day_key]
    # Rétrocompatibilité si un ancien format existait
    if "chrono" not in day:
        day["chrono"] = {label: {"elapsed": 0.0, "running": False, "start": None} for label in CHRONO_LABELS}
    if "custom" not in day:
        day["custom"] = [{"label": "", "value": ""}, {"label": "", "value": ""}]
    return day


def format_time(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def get_elapsed(chrono: dict) -> float:
    e = chrono["elapsed"]
    if chrono["running"]:
        e += time.time() - chrono["start"]
    return e


# ---------- UI ----------
st.title("🗓️ Suivi du temps de travail")

if not HAS_AUTOREFRESH:
    st.info(
        "Pour que les chronos avancent tout seuls à l'écran, installe : "
        "`pip install streamlit-autorefresh`. Sinon le temps se met à jour à chaque clic.",
        icon="ℹ️",
    )
else:
    st_autorefresh(interval=1000, key="auto_refresh")

selected_date = st.date_input("Choisir un jour", value=date.today())
day_key = selected_date.isoformat()
day = get_day(day_key)

st.markdown(f"### {selected_date.strftime('%A %d %B %Y')}")
st.markdown("---")

st.subheader("Chronomètres")
cols = st.columns(len(CHRONO_LABELS))
for i, label in enumerate(CHRONO_LABELS):
    with cols[i]:
        c = day["chrono"][label]
        elapsed = get_elapsed(c)

        st.markdown(f"**{label}**")
        st.markdown(f"### {format_time(elapsed)}")

        b1, b2 = st.columns(2)
        with b1:
            if not c["running"]:
                if st.button("▶ Start", key=f"start_{day_key}_{label}"):
                    c["running"] = True
                    c["start"] = time.time()
                    save_data(st.session_state.data)
                    st.rerun()
            else:
                if st.button("⏸ Pause", key=f"pause_{day_key}_{label}"):
                    c["elapsed"] += time.time() - c["start"]
                    c["running"] = False
                    c["start"] = None
                    save_data(st.session_state.data)
                    st.rerun()
        with b2:
            if st.button("↺ Reset", key=f"reset_{day_key}_{label}"):
                c["elapsed"] = 0.0
                c["running"] = False
                c["start"] = None
                save_data(st.session_state.data)
                st.rerun()

st.markdown("---")
st.subheader("Notes libres")
custom_cols = st.columns(2)
for i in range(2):
    with custom_cols[i]:
        new_label = st.text_input(
            "Nom du champ",
            value=day["custom"][i]["label"],
            key=f"customlabel_{day_key}_{i}",
            placeholder=f"Ex : Champ {i + 1}",
        )
        new_value = st.text_area(
            new_label if new_label else f"Champ {i + 1}",
            value=day["custom"][i]["value"],
            key=f"customvalue_{day_key}_{i}",
            height=100,
        )
        if new_label != day["custom"][i]["label"] or new_value != day["custom"][i]["value"]:
            day["custom"][i]["label"] = new_label
            day["custom"][i]["value"] = new_value
            save_data(st.session_state.data)
            
