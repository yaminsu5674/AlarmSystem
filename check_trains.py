"""
코레일 KTX / SRT 좌석 조회 → 자리 나면 디스코드 웹훅으로 알림.
GitHub Actions 크론(5분마다)에서 실행.
- 조회할 노선/날짜는 routes.json 에서 편집 (민감정보 아님)
- 로그인 정보/웹훅은 환경변수(=GitHub Secrets)로 주입
"""
import os
import sys
import json
import urllib.request

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
KORAIL_ID = os.environ.get("KORAIL_ID")
KORAIL_PW = os.environ.get("KORAIL_PW")
SRT_ID    = os.environ.get("SRT_ID")
SRT_PW    = os.environ.get("SRT_PW")

with open("routes.json", encoding="utf-8") as f:
    ROUTES = json.load(f)


def notify(text):
    data = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=data,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=15)


def search_korail(client, r):
    trains = client.search_train(
        r["dep"], r["arr"], r["date"], r["time"], include_no_seats=True
    )
    hits = []
    for t in trains:
        if t.has_seat():
            hits.append(f"🚄 [코레일] {r['dep']}→{r['arr']} {r['date']} · "
                        f"{t.train_type_name} {t.train_no} "
                        f"{t.dep_time[:2]}:{t.dep_time[2:4]} 출발")
    return hits


def search_srt(client, r):
    trains = client.search_train(
        r["dep"], r["arr"], r["date"], r["time"], available_only=False
    )
    hits = []
    for t in trains:
        if t.seat_available():
            hits.append(f"🚅 [SRT] {r['dep']}→{r['arr']} {r['date']} · "
                        f"{t.train_name} {t.train_number} "
                        f"{t.dep_time[:2]}:{t.dep_time[2:4]} 출발")
    return hits


def main():
    # 운영사별 로그인은 한 번만 (여러 노선 재사용)
    korail_client = srt_client = None
    need_korail = any(r["operator"] == "korail" for r in ROUTES)
    need_srt    = any(r["operator"] == "srt"    for r in ROUTES)

    if need_korail and KORAIL_ID and KORAIL_PW:
        from korail2 import Korail
        korail_client = Korail(KORAIL_ID, KORAIL_PW)
    if need_srt and SRT_ID and SRT_PW:
        from SRT import SRT
        srt_client = SRT(SRT_ID, SRT_PW)

    all_hits = []
    for r in ROUTES:
        try:
            if r["operator"] == "korail" and korail_client:
                all_hits += search_korail(korail_client, r)
            elif r["operator"] == "srt" and srt_client:
                all_hits += search_srt(srt_client, r)
        except Exception as e:
            print(f"[{r['operator']}] {r['dep']}→{r['arr']} 조회 실패: {e}",
                  file=sys.stderr)

    if all_hits:
        notify("🎫 **예매 가능 열차 발견!**\n" + "\n".join(all_hits))
        print(f"알림 전송: {len(all_hits)}건")
    else:
        print("좌석 없음 (알림 안 보냄)")


if __name__ == "__main__":
    main()
