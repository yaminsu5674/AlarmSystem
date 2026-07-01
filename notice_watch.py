"""
코레일 + SRT 공지사항 감시.
새 공지가 뜨면 (특히 명절/공휴일 특별예매) 제목 + 링크를 디스코드로 알림.
- 이미 본 공지는 notices_state.json 에 저장해 중복 알림 방지.
- 첫 실행 때는 현재 공지들을 '기준선'으로만 저장하고 알림은 안 보냄.
GitHub Actions가 하루 몇 번 실행, 실행 후 notices_state.json 을 repo에 커밋해 상태 유지.
"""
import os
import re
import json
import urllib.request

import requests
from bs4 import BeautifulSoup

# 기차 전용 웹훅(나만 보는 채널). 없으면 공용 DISCORD_WEBHOOK 사용.
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_TRAIN") or os.environ["DISCORD_WEBHOOK"]
STATE_FILE = "notices_state.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (notice-watch personal bot)"}

SRT_LIST = "https://etk.srail.kr/cms/article/list.do?pageId=TK0502000000"
SRT_VIEW = "https://etk.srail.kr/cms/article/view.do?pageId=TK0502000000&postNo={}"

KORAIL_LIST = "https://info.korail.com/info/selectBbsNttList.do?key=910&bbsNo=200"
KORAIL_VIEW = "https://info.korail.com/info/selectBbsNttView.do?key=910&bbsNo=200&nttNo={}"


def notify(text):
    data = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    urllib.request.urlopen(req, timeout=15)


def fetch_srt():
    """SRT 공지 목록 → [(id, 제목, 링크)]"""
    html = requests.get(SRT_LIST, headers=HEADERS, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        m = re.search(r"postNo=(\d+)", a["href"])
        if not m:
            continue
        title = a.get_text(strip=True)
        if not title:
            continue
        pid = m.group(1)
        out.append((f"srt:{pid}", title, SRT_VIEW.format(pid)))
    return out


def fetch_korail():
    """코레일 공지 목록 → [(id, 제목, 링크)]. 사이트 구조상 실패 가능 → 예외는 상위에서 처리."""
    html = requests.get(KORAIL_LIST, headers=HEADERS, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    out = []
    # href 또는 onclick 안의 nttNo 를 모두 탐색
    for tag in soup.find_all(["a", "td", "tr"]):
        attrs = " ".join(str(v) for v in tag.attrs.values())
        m = re.search(r"nttNo['\"=,\s]+?(\d+)", attrs)
        if not m:
            continue
        title = tag.get_text(strip=True)
        if not title:
            continue
        nid = m.group(1)
        out.append((f"kor:{nid}", title[:80], KORAIL_VIEW.format(nid)))
    return out


def main():
    # 상태 로드
    seen = set()
    initialized = False
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            st = json.load(f)
            seen = set(st.get("seen", []))
            initialized = st.get("initialized", False)

    current = []
    for name, fn in (("SRT", fetch_srt), ("코레일", fetch_korail)):
        try:
            current += fn()
        except Exception as e:
            print(f"[{name}] 공지 조회 실패: {e}")

    new_items = [x for x in current if x[0] not in seen]

    if not initialized:
        # 첫 실행: 기준선만 저장, 알림 X
        print(f"기준선 저장 ({len(current)}건). 다음 실행부터 새 공지 알림.")
    elif new_items:
        for _id, title, link in new_items:
            src = "🚅 SRT" if _id.startswith("srt") else "🚄 코레일"
            notify(f"📢 **[{src}] 새 공지**\n{title}\n{link}")
        print(f"새 공지 {len(new_items)}건 알림 전송")
    else:
        print("새 공지 없음")

    # 상태 저장 (현재 목록 전체를 seen 에 반영)
    all_ids = sorted(seen | {x[0] for x in current})
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"initialized": True, "seen": all_ids}, f,
                  ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
