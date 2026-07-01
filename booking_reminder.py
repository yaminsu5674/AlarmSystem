"""
예매 오픈일 리마인더.
매일 저녁 19시(KST)에 실행 → "내일 오전 7시에 어느 날짜 표가 열리는지" 미리 알림.
- 코레일(KTX): 탑승일 1개월(한 달) 전 07:00 오픈  → 내일 열리는 탑승일 = 내일 + 1개월
- SRT:        탑승일 1개월(한 달) 전 07:00 오픈  → 내일 열리는 탑승일 = 내일 + 1개월
  (SRT 공식 안내 기준. 블로그엔 '30일 전'이라고도 하나 공식 문구는 '1개월 전 07:00')
네 이동 패턴(금요일 서울→마산, 일요일 마산→서울)에 해당하면 별표로 강조.
"""
import os
import json
import datetime
import urllib.request
from dateutil.relativedelta import relativedelta

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

WD = ["월", "화", "수", "목", "금", "토", "일"]  # Monday=0


def notify(text):
    data = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=data,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=15)


def fmt(d):
    return f"{d.month}/{d.day}({WD[d.weekday()]})"


def highlight(d):
    """탑승일이 금(내려감)/일(올라옴)이면 강조 문구."""
    if d.weekday() == 4:  # 금
        return "  ⭐ **금요일 — 서울→마산 내려가는 날!**"
    if d.weekday() == 6:  # 일
        return "  ⭐ **일요일 — 마산→서울 올라오는 날!**"
    return ""


def main():
    # KST 기준 '내일'
    today_kst = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).date()
    tomorrow = today_kst + datetime.timedelta(days=1)

    # 코레일·SRT 모두 공식 기준 '탑승 1개월 전 07:00'
    dep = tomorrow + relativedelta(months=1)

    msg = (
        f"🎫 **내일({fmt(tomorrow)}) 오전 7시 예매 오픈 안내**\n\n"
        f"🚄🚅 코레일 & SRT: **{fmt(dep)}** 승차분{highlight(dep)}\n\n"
        f"※ 월말 경계에선 앱 달력 기준 ±1일 차이날 수 있으니 확인!\n"
        f"_아침 7시 땡 하면 코레일톡/SR앱 대기하세요._"
    )
    notify(msg)
    print("예매 오픈 리마인더 전송")


if __name__ == "__main__":
    main()
