#!/usr/bin/env python3
"""전국공중화장실표준데이터(data.go.kr 15012892)를 www.data.go.kr/download/standard.json 로 내려받아 data/raw/toilets.json 으로 저장.
주의: colNmList 에 INSTT_CODE/INSTT_NM 을 넣으면 빈 응답이 오므로 제외한다."""
import json, sys, time
from pathlib import Path
import requests

sys.stdout.reconfigure(encoding="utf-8")
PK, TBL = "15012892", "tn_pubr_public_toilet_api"
URL = "https://www.data.go.kr/download/standard.json"
H = {"User-Agent": "Mozilla/5.0"}
OUT = Path(__file__).parent.parent / "data" / "raw" / "toilets.json"

r = requests.get(f"https://www.data.go.kr/download/columList.json?pk={PK}&ext=JSON", headers=dict(H, Referer=f"https://www.data.go.kr/data/{PK}/standard.do"), timeout=30)
cols = [c["columCode"] for c in r.json()["columList"] if c["columCode"] not in ("INSTT_CODE", "INSTT_NM")]
rows, page = [], 1
while True:
    params = [("publicDataPk", PK)] + [("colNmList", c) for c in cols] + [("perPage", 10000), ("page", page), ("svcTableNm", TBL), ("totalCount", "999999")]
    items = requests.get(URL, params=params, headers=H, timeout=120).json()
    rows.extend(items)
    print(f"{page}페이지 누적 {len(rows):,}", flush=True)
    if len(items) < 10000:
        break
    page += 1
    time.sleep(0.5)
if len(rows) < 20000:
    raise SystemExit("수집 건수가 너무 적어 저장을 중단합니다.")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
print(f"저장 {len(rows):,}건")
