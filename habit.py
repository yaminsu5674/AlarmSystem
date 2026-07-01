"""
습관 알림: 눈운동 + 목(거북목) 스트레칭 가이드를 디스코드로 전송.
평일 9~18시(12시 제외) 매 정시에 GitHub Actions가 실행.
시간대에 따라 가이드를 바꿔서 매번 다른 운동을 안내한다.
"""
import os
import json
import datetime
import urllib.request

# 습관 알림 전용 웹훅(여친도 보는 채널). 없으면 공용 DISCORD_WEBHOOK 사용.
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_HABIT") or os.environ["DISCORD_WEBHOOK"]

# 눈운동 목록
EYE = [
    "👀 **20-20-20 법칙** — 6m 이상 먼 곳을 20초간 바라보기 ×3회. 초점 근육 이완.",
    "👀 **눈 굴리기** — 눈알을 시계방향으로 천천히 5바퀴, 반대로 5바퀴.",
    "👀 **초점 전환** — 엄지를 눈앞 30cm에 두고 봤다가, 먼 벽을 봤다가 ×10회.",
    "👀 **꾹 감기** — 3초간 눈을 꽉 감았다 크게 뜨기 ×10회. 눈물막 회복.",
    "👀 **눈 지압** — 눈썹뼈·관자놀이를 엄지로 5초씩 지그시 눌러 5회.",
]

# 목/거북목 스트레칭 목록
NECK = [
    "🦴 **턱 당기기(친턱)** — 턱을 목쪽으로 수평 당겨 5초 유지 ×10회. 거북목 핵심운동.",
    "🦴 **목 옆으로 기울이기** — 오른손으로 머리를 오른쪽으로 당겨 15초, 반대도. 승모근 이완.",
    "🦴 **뒤통수 벽 밀기** — 벽에 뒤통수 붙이고 5초간 뒤로 밀기 ×10회. 심부목근육 강화.",
    "🦴 **가슴 열기** — 등 뒤로 깍지 끼고 팔을 펴 가슴을 15초 펴기. 굽은 어깨 교정.",
    "🦴 **어깨 으쓱** — 어깨를 귀까지 올렸다가 툭 떨어뜨리기 ×10회. 긴장 해소.",
]


def notify(text):
    data = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=data,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=15)


def main():
    # KST 기준 시각으로 운동 선택 (UTC+9)
    kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    idx = kst.hour  # 시간마다 다른 운동
    msg = (
        f"🧘 **{kst.hour}시 스트레칭 타임!** (거북목·눈 건강)\n\n"
        f"{EYE[idx % len(EYE)]}\n"
        f"{NECK[idx % len(NECK)]}\n\n"
        f"_잠깐 일어나서 1분만 움직여요 💪_"
    )
    notify(msg)
    print(f"습관 알림 전송 ({kst.hour}시)")


if __name__ == "__main__":
    main()
