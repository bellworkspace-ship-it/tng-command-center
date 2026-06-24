#!/usr/bin/env python3
"""Resumable FUB collector — run repeatedly until it prints DONE.
Each invocation works for ~BUDGET seconds, checkpoints to disk, exits."""
import json, time, sys, os, base64
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

BUDGET = 35
T0 = time.time()
WD = os.path.dirname(os.path.abspath(__file__))
STATE_F = os.path.join(WD, "state.json")

API = "https://api.followupboss.com/v1"
KEY = os.environ.get("FUB_API_KEY", "")
if not KEY:
    print("FATAL: set the FUB_API_KEY environment variable before running."); sys.exit(1)
AUTH = "Basic " + base64.b64encode((KEY + ":").encode()).decode()
EXCLUDE = {"luke newcomer", "sadie newcomer", "chris mury", "tommy scott",
           "ashley turner", "ryan raymond", "steven bell", "danielle hixon",
           "christina poehlman", "jessie dittmer"}
NOW = datetime.now(timezone.utc)
YTD_START = datetime(NOW.year, 1, 1, tzinfo=timezone.utc)

def parse(s):
    if not s: return None
    try: return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception: return None

def get(path, params=None, tries=4):
    url = API + path + ("?" + urlencode(params) if params else "")
    for i in range(tries):
        try:
            req = Request(url, headers={"Authorization": AUTH, "X-System": "TNGCommandCenter"})
            with urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode())
        except HTTPError as e:
            if e.code == 429: time.sleep(2.5 * (i + 1)); continue
            if i == tries - 1: return {}
            time.sleep(1 + i)
        except Exception:
            if i == tries - 1: return {}
            time.sleep(1 + i)
    return {}

def load_state():
    if os.path.exists(STATE_F):
        return json.load(open(STATE_F))
    return {"stage": "users", "next": None, "watch_i": 0}

def save_state(st):
    json.dump(st, open(STATE_F, "w"))

def append(fname, items):
    with open(os.path.join(WD, fname), "a") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")

def out_of_time(): return time.time() - T0 > BUDGET

st = load_state()
stage = st["stage"]
print(f"stage={stage}", flush=True)

def collect_paged(path, coll, fname, params, next_stage, stop_before=None):
    global st
    p = dict(params); p.setdefault("limit", 100)
    while not out_of_time():
        if st.get("next"): p["next"] = st["next"]
        d = get(path, p)
        items = d.get(coll, [])
        if items: append(fname, items)
        nxt = d.get("_metadata", {}).get("next")
        done = not items or not nxt
        if stop_before and items:
            last = parse(items[-1].get("created"))
            if last and last < stop_before: done = True
        if done:
            st = {"stage": next_stage, "next": None, "watch_i": st.get("watch_i", 0)}
            save_state(st); print(f"-> {next_stage}", flush=True); return True
        st["next"] = nxt; save_state(st)
        time.sleep(0.1)
    save_state(st); return False

if stage == "users":
    users = []
    p = {"limit": 100}; nxt = None
    while True:
        if nxt: p["next"] = nxt
        d = get("/users", p); users += d.get("users", [])
        nxt = d.get("_metadata", {}).get("next")
        if not nxt or not d.get("users"): break
    json.dump(users, open(os.path.join(WD, "users.json"), "w"))
    st = {"stage": "people", "next": None, "watch_i": 0}; save_state(st)
    print("-> people", flush=True)
    stage = "people"

if stage == "people" and not out_of_time():
    collect_paged("/people", "people", "people.jsonl",
        {"sort": "created",
         "fields": "id,name,firstName,lastName,stage,source,created,updated,assignedUserId,lastActivity,price"},
        "calls")
    st = load_state(); stage = st["stage"]

if stage == "calls" and not out_of_time():
    collect_paged("/calls", "calls", "calls.jsonl", {"sort": "-created"}, "appts", stop_before=YTD_START)
    st = load_state(); stage = st["stage"]

if stage == "appts" and not out_of_time():
    collect_paged("/appointments", "appointments", "appts.jsonl", {}, "tasks")
    st = load_state(); stage = st["stage"]

if stage == "tasks" and not out_of_time():
    collect_paged("/tasks", "tasks", "tasks.jsonl", {}, "deals")
    st = load_state(); stage = st["stage"]

if stage == "deals" and not out_of_time():
    collect_paged("/deals", "deals", "deals.jsonl", {}, "watch")
    st = load_state(); stage = st["stage"]

if stage == "watch" and not out_of_time():
    # build list of 7d leads once
    wf = os.path.join(WD, "watch_targets.json")
    if not os.path.exists(wf):
        targets = []
        D7 = NOW - timedelta(days=7)
        for line in open(os.path.join(WD, "people.jsonl")):
            p = json.loads(line)
            c = parse(p.get("created"))
            src = (p.get("source") or "").lower()
            if c and c >= D7 and "biggerpockets" not in src and "agentlead" not in src:
                targets.append(p)
        json.dump(targets, open(wf, "w"))
    targets = json.load(open(wf))
    i = st.get("watch_i", 0)
    results = []
    while i < len(targets) and not out_of_time():
        p = targets[i]
        pid = p["id"]
        d1 = get("/textMessages", {"personId": pid, "limit": 50})
        txts = d1.get("textmessages") or d1.get("textMessages") or []
        emails = get("/emails", {"personId": pid, "limit": 50}).get("emails") or []
        results.append({"person": p, "texts": [
            {"in": bool(t.get("isIncoming"))} for t in txts],
            "emails": [{"in": bool(e.get("isIncoming")),
                        "sentByPerson": any(rp.get("id") == pid and rp.get("sentByPerson") is True
                                            for rp in (e.get("relatedPeople") or []))} for e in emails]})
        i += 1
        time.sleep(0.08)
    if results: append("watch_raw.jsonl", results)
    st["watch_i"] = i; save_state(st)
    if i >= len(targets):
        st = {"stage": "done", "next": None, "watch_i": i}; save_state(st)
        print("-> done", flush=True)
        stage = "done"
    else:
        print(f"watch {i}/{len(targets)}", flush=True)

if stage == "done":
    print("DONE", flush=True)
else:
    print(f"CONTINUE ({load_state()['stage']})", flush=True)
