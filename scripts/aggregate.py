#!/usr/bin/env python3
"""Aggregate raw jsonl pulls into dashboard_data.json (v2.1 — source buckets)."""
import json, os, sys
from datetime import datetime, timedelta, timezone

WD = os.path.dirname(os.path.abspath(__file__))
NOW = datetime.now(timezone.utc)
YTD_START = datetime(NOW.year, 1, 1, tzinfo=timezone.utc)
D15, D7 = NOW - timedelta(days=15), NOW - timedelta(days=7)

EXCLUDE = {"luke newcomer", "sadie newcomer", "chris mury", "tommy scott",
           "ashley turner", "ryan raymond", "steven bell", "danielle hixon",
           "christina poehlman", "allie gardner"}
STAGE_ORDER = {"lead": 0, "attempted contact": 1, "spoke with customer": 2,
               "appointment set": 3, "met with customer": 4, "showing homes": 5,
               "submitting offers": 6, "under contract": 7, "pending": 7,
               "closed": 8, "past client": 8, "nurture": -1, "trash": -2, "pond": -1}
DWELL = {"Lead": 1, "Attempted Contact": 5, "Spoke with Customer": 7,
         "Appointment Set": 7, "Met with Customer": 14, "Showing Homes": 30,
         "Submitting Offers": 21}

def bucket_of(src):
    s = (src or "").lower()
    if "open house" in s or "openhouse" in s: return "agent"
    if "agent lead" in s or "agentlead" in s: return "agent"
    if "import" in s: return "recruiting"
    return "company"

def parse(s):
    if not s: return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception: return None
def day(dt): return dt.strftime("%Y-%m-%d") if dt else None
def jl(name):
    p = os.path.join(WD, name)
    if not os.path.exists(p): return
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line: yield json.loads(line)

users = json.load(open(os.path.join(WD, "users.json")))
agents = {}
for u in users:
    nm = (u.get("name") or "").strip()
    if (u.get("status") or "").lower() != "active": continue
    if nm.lower() in EXCLUDE: continue
    pic = u.get("picture")
    agents[u["id"]] = {"id": u["id"], "name": nm,
                       "firstName": u.get("firstName") or (nm.split()[0] if nm else "?"),
                       "picture": pic.get("162x162") if isinstance(pic, dict) else None}
user_name_by_id = {u["id"]: (u.get("name") or "").strip() for u in users}

series = {}
def bump(aid, dt, key, n=1):
    if aid not in agents or not dt or dt < YTD_START: return
    dd = day(dt)
    series.setdefault(aid, {}).setdefault(dd, {})
    series[aid][dd][key] = series[aid][dd].get(key, 0) + n

def new_bucketstats():
    return {b: {"total": 0, "active": 0, "touched30": 0, "stuck": 0} for b in ("agent", "company", "recruiting")}

# ---------- PEOPLE first (also builds pid -> bucket map for the calls join) ----------
books = {aid: {"total": 0, "stages": {}, "sources": {}, "touched7": 0, "touched30": 0,
               "touched90": 0, "neverTouched": 0, "active": 0,
               "buckets": new_bucketstats(), "sourceDetail": {}} for aid in agents}
pid_bucket, pid_src = {}, {}
stuck, leads15 = [], []
watch_skip = set()   # recruiting leads to exclude from watchlist

for p in jl("people.jsonl"):
    aid = p.get("assignedUserId")
    pid = p.get("id")
    created = parse(p.get("created"))
    stage = p.get("stage") or "Lead"
    so = STAGE_ORDER.get(stage.lower(), 0)
    last = parse(p.get("lastActivity"))
    src = (p.get("source") or "Unknown").strip() or "Unknown"
    bk = bucket_of(src)
    pid_bucket[pid] = bk
    pid_src[pid] = src
    if bk == "recruiting": watch_skip.add(pid)
    if created:
        bump(aid, created, "nl")
        bump(aid, created, "nla" if bk == "agent" else "nlk" if bk == "company" else "nlr")
    if aid not in agents:
        if created and created >= D15 and so != -2:
            if bk == "recruiting":
                mv, agent_lbl = "recruiting", "Recruiting import"
            else:
                mv = "redistributed"
                agent_lbl = "Pond (unassigned)" if not aid else f"Reassigned → {user_name_by_id.get(aid, 'Other')}"
            leads15.append({"id": pid, "name": p.get("name"), "agentId": None,
                            "agent": agent_lbl, "stage": stage, "source": src,
                            "created": day(created), "movement": mv, "bucket": bk})
        continue
    b = books[aid]
    bb = b["buckets"][bk]
    sd = b["sourceDetail"].setdefault(src, [0, 0, 0, 0])  # total, active, touched30, stuck
    b["total"] += 1; bb["total"] += 1; sd[0] += 1
    b["stages"][stage] = b["stages"].get(stage, 0) + 1
    b["sources"][src] = b["sources"].get(src, 0) + 1
    is_active = so >= 0 and stage.lower() not in ("closed", "past client")
    if is_active:
        b["active"] += 1; bb["active"] += 1; sd[1] += 1
        if last:
            dsa = (NOW - last).days
            if dsa <= 7: b["touched7"] += 1
            if dsa <= 30:
                b["touched30"] += 1; bb["touched30"] += 1; sd[2] += 1
            if dsa <= 90: b["touched90"] += 1
        else:
            b["neverTouched"] += 1
    if created and created >= D15:
        age = (NOW - created).days
        mv = ("recruiting" if bk == "recruiting" else
              "trashed" if so == -2 else "converted" if so >= 7 else
              "progressing" if so >= 1 else "stalled" if age > 1 else "new")
        leads15.append({"id": pid, "name": p.get("name"), "agentId": aid,
                        "agent": agents[aid]["name"], "stage": stage, "source": src,
                        "created": day(created), "movement": mv, "bucket": bk})
    if stage in DWELL and created and bk != "recruiting":
        age = (NOW - created).days
        dsa = (NOW - last).days if last else None
        if age > DWELL[stage] and (dsa is None or dsa > DWELL[stage]):
            stuck.append({"id": pid, "name": p.get("name"), "agentId": aid,
                          "agent": agents[aid]["name"], "stage": stage, "source": src,
                          "created": day(created), "age": age,
                          "dsa": dsa if dsa is not None else age,
                          "price": p.get("price") or 0, "bucket": bk})
            bb["stuck"] += 1; sd[3] += 1
stuck.sort(key=lambda x: -x["dsa"])
stuck = stuck[:800]

# ---------- CALLS (joined to lead source bucket) ----------
calls_by_person = {}
for c in jl("calls.jsonl"):
    dt = parse(c.get("created"))
    if not dt or dt < YTD_START: continue
    pid = c.get("personId")
    if not c.get("isIncoming"):
        uid = c.get("userId")
        bump(uid, dt, "c")
        if (c.get("duration") or 0) > 10: bump(uid, dt, "cc")
        bk = pid_bucket.get(pid)
        if bk == "agent": bump(uid, dt, "ca")
        elif bk == "company": bump(uid, dt, "ck")
    if pid:
        calls_by_person.setdefault(pid, []).append(
            {"in": bool(c.get("isIncoming")), "dur": c.get("duration") or 0})

# ---------- APPOINTMENTS ----------
for a in jl("appts.jsonl"):
    dt = parse(a.get("created"))
    cb = a.get("createdBy")
    uid = a.get("createdById") or (cb.get("id") if isinstance(cb, dict) else None)
    bump(uid, dt, "a")

# ---------- TASKS ----------
upcoming = {aid: 0 for aid in agents}
for t in jl("tasks.jsonl"):
    done = t.get("completed") or t.get("isCompleted")
    uid = t.get("assignedUserId") or t.get("userId")
    if done:
        bump(uid, parse(t.get("updated") or t.get("dueDate")), "t")
    else:
        dd = parse(t.get("dueDate"))
        if uid in agents and dd and NOW <= dd <= NOW + timedelta(days=7):
            upcoming[uid] += 1

# ---------- DEALS ----------
deals = []
for d in jl("deals.jsonl"):
    us = d.get("users") or []
    aid, aname = None, None
    for u in us:
        if u.get("id") in agents:
            aid, aname = u["id"], u.get("name"); break
    if aid is None and us:
        aid, aname = us[0].get("id"), us[0].get("name")
    stage = d.get("stageName") or ""
    closed = stage.lower() == "closed"
    ppl = d.get("people") or []
    client = ppl[0].get("name") if ppl else None
    client_id = ppl[0].get("id") if ppl else None
    a1 = (d.get("customAddressLine1") or "").strip()
    if a1:
        city = (d.get("customCity") or "").strip()
        stz = " ".join(x for x in [(d.get("customState") or "").strip(), (d.get("customPostalCode") or "").strip()] if x)
        address = ", ".join(x for x in [a1, city, stz] if x)
    else:
        address = d.get("name")
    deals.append({"id": d.get("id"), "name": d.get("name"), "address": address, "agentId": aid,
                  "agentName": aname, "price": d.get("price") or 0,
                  "gci": d.get("commissionValue") or 0,
                  "pipeline": d.get("pipelineName"), "stage": stage,
                  "side": "Seller" if "seller" in (d.get("pipelineName") or "").lower() else "Buyer",
                  "client": client, "clientId": client_id,
                  "source": pid_src.get(client_id),
                  "bucket": pid_bucket.get(client_id),
                  "enteredStageAt": d.get("enteredStageAt"),
                  "entered": day(parse(d.get("enteredStageAt"))),
                  "projClose": day(parse(d.get("projectedCloseDate"))),
                  "ucDate": d.get("customUnderContractDate"),
                  "mlsLive": d.get("customMlsLiveDate"),
                  "closeDate": day(parse(d.get("enteredStageAt"))) if closed else None})

# ---------- WATCHLIST ----------
watch = []
for rec in jl("watch_raw.jsonl"):
    items = rec if isinstance(rec, list) else [rec]
    for r in items:
        p = r["person"]
        pid = p["id"]
        if p.get("assignedUserId") not in agents: continue
        if pid in watch_skip: continue  # recruiting imports are not sales leads
        created = parse(p.get("created"))
        stage = p.get("stage") or "Lead"
        so = STAGE_ORDER.get(stage.lower(), 0)
        if so < 0: continue
        pcalls = calls_by_person.get(pid, [])
        out_n = sum(1 for c in pcalls if not c["in"]) + \
                sum(1 for t in r["texts"] if not t["in"]) + \
                sum(1 for e in r["emails"] if not e["in"] and not e.get("sentByPerson"))
        in_n = sum(1 for c in pcalls if c["in"]) + \
               sum(1 for t in r["texts"] if t["in"]) + \
               sum(1 for e in r["emails"] if e.get("sentByPerson"))
        conn = sum(1 for c in pcalls if not c["in"] and c["dur"] > 10)
        age_days = max(1, (NOW - created).days) if created else 1
        status = ("reached" if so >= 2 else
                  "responded" if in_n > 0 else
                  "no_contact" if out_n == 0 else
                  "working" if out_n >= 3 * min(age_days, 4) else "under_worked")
        aid = p.get("assignedUserId")
        watch.append({"id": pid, "name": p.get("name"), "agentId": aid,
                      "agent": agents.get(aid, {}).get("name", "—"),
                      "stage": stage, "source": p.get("source") or "Unknown",
                      "created": day(created), "ageDays": age_days,
                      "outbound": out_n, "inbound": in_n, "connected": conn,
                      "status": status, "bucket": bucket_of(p.get("source"))})

out = {"generatedAt": NOW.isoformat(), "ytdStart": day(YTD_START),
       "agents": [{**agents[aid], "book": books[aid], "upcomingTasks": upcoming.get(aid, 0)} for aid in agents],
       "series": series, "deals": deals, "stuck": stuck,
       "leads15": leads15, "watch": watch}
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WD, "dashboard_data.json")
json.dump(out, open(path, "w"))
print(f"wrote {path} ({os.path.getsize(path)//1024} KB) — watch={len(watch)} stuck={len(stuck)} leads15={len(leads15)} deals={len(deals)}")
