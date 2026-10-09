#!/usr/bin/env python3
"""
process_data.py (우아화장실) - 행정안전부 전국공중화장실표준데이터(data.go.kr 15012892) JSON을 가공한다.
입력: data/raw/toilets.json (scripts/fetch_toilets.py 결과)  출력: _rawdata/tl_{시도}.json, search_index.json
주소가 없는 행(약 21%)은 위치를 알 수 없어 제외한다. 좌표는 데이터에 있는 경우(약 80%)만 쓴다.
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib_localdata import *  # noqa

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).parent.parent
RAW = ROOT / "data" / "raw" / "toilets.json"
CATMETA = {"공중화장실": ("public", "🚻"), "개방화장실": ("open", "🚪"), "간이화장실": ("simple", "🏗️"), "이동화장실": ("mobile", "🚐")}


def yes(v):
    return clean(v).upper() in ("Y", "YES", "있음", "설치")


def main():
    rows = json.loads(RAW.read_text(encoding="utf-8"))
    records = []
    for r in rows:
        name = clean(r.get("TOILET_NM"))
        road, lot = clean(r.get("RDNMADR")), clean(r.get("LNMADR"))
        cat = clean(r.get("TOILET_TYPE"))
        if cat not in CATMETA:
            cat = "공중화장실"
        try:
            lat, lng = float(r.get("LATITUDE") or 0), float(r.get("LONGITUDE") or 0)
            if not (33 <= lat <= 39 and 124 <= lng <= 132):
                lat = lng = None
        except ValueError:
            lat = lng = None
        year = clean(r.get("INSTALLATION_YEAR"))
        year = year if re.fullmatch(r"(19|20)\d\d", year) else ""
        open_time = clean(r.get("OPEN_TIME"))
        extras, hrows = [], []
        m_bowl, m_uri = int(num(r.get("MEN_TOILET_BOWL_NUMBER"))), int(num(r.get("MEN_URINE_NUMBER")))
        l_bowl = int(num(r.get("LADIES_TOILET_BOWL_NUMBER")))
        handi = int(num(r.get("MEN_HANDICAP_TOILET_BOWL_NUMBER")) + num(r.get("LADIES_HANDICAP_TOILET_BOWL_NUMBER")) + num(r.get("MEN_HANDICAP_URINAL_NUMBER")))
        child = int(num(r.get("MEN_CHILDREN_TOILET_BOWL_NUMBER")) + num(r.get("LADIES_CHILDREN_TOILET_BOWL_NUMBER")) + num(r.get("MEN_CHILDREN_URINAL_NUMBER")))
        if open_time:
            hrows.append({"i": "🕘", "t": f"개방시간 {open_time}"})
            extras.append({"l": "개방시간", "v": open_time})
        if m_bowl or m_uri:
            extras.append({"l": "남성용", "v": f"대변기 {m_bowl}·소변기 {m_uri}"})
        if l_bowl:
            extras.append({"l": "여성용", "v": f"대변기 {l_bowl}"})
        if handi:
            extras.append({"l": "장애인용 변기", "v": f"{handi}개"})
        if child:
            extras.append({"l": "어린이용 변기", "v": f"{child}개"})
        if yes(r.get("UNISEX_TOILET_YN")):
            extras.append({"l": "남녀 공용", "v": "있음"})
        if yes(r.get("EMG_BELL_YN")):
            extras.append({"l": "비상벨", "v": "있음"})
        if yes(r.get("ENTERENT_CCTV_YN")):
            extras.append({"l": "출입구 CCTV", "v": "있음"})
        if clean(r.get("DIPERS_EXCHG_POSI")):
            extras.append({"l": "기저귀 교환대", "v": clean(r.get("DIPERS_EXCHG_POSI"))})
        inst = clean(r.get("INSTITUTION_NM"))
        if inst:
            hrows.append({"i": "🏢", "t": f"관리 {inst}"})
        note = open_time[:24]
        records.append(dict(name=name or "화장실", cat=cat, road=road, lot=lot, tel=r.get("PHONE_NUMBER"), permit=year,
                            upd=clean(r.get("REFERENCE_DATE"))[:10], lat=lat, lng=lng, extras=extras, hrows=hrows, note=note))
        records[-1]["openTime"] = open_time
    items = finalize(records, ROOT / "_rawdata", "tl", ROOT, CATMETA)


if __name__ == "__main__":
    main()
