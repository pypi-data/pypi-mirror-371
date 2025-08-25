import pandas as pd
import io, json, requests
from dataclasses import dataclass

CDN_BASE = "https://<your-cloudfront-domain>/<prefix>"


@dataclass(frozen=True)
class EventRef:
    season: int
    event_id: str
    race: str
    key: str  # "season=7/Cardiff_2025__LR3MS4JIB56.parquet"


def _manifest():
    url = f"{CDN_BASE}/catalog/manifest-v1.json"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


def list_seasons() -> list[int]:
    return _manifest()["seasons"]


def list_events(season: int | None = None) -> list[EventRef]:
    m = _manifest()["events"]
    if season is not None:
        m = [e for e in m if e["season"] == season]
    return [EventRef(**{k: e[k] for k in ("season", "event_id", "race", "key")}) for e in m]


def get_race(*, season: int | None = None, location: str | None = None, event_id: str | None = None) -> pd.DataFrame:
    events = list_events(season)
    if event_id:
        ev = next(e for e in events if e.event_id == event_id)
    elif location:
        # naive match; you can add fuzzy/normalized matching later
        cand = [e for e in events if location.lower() in e.race.lower()]
        if not cand:
            raise ValueError(f"No event matching {location!r}")
        ev = cand[0]
    else:
        raise ValueError("Provide event_id or location (optionally season).")
    url = f"{CDN_BASE}/{ev.key}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return pd.read_parquet(io.BytesIO(resp.content))
