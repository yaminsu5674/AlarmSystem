"""
습관 알림: 눈운동 + 목(거북목) 스트레칭 가이드를 디스코드로 전송.
평일 9~18시(12시 제외) 매 정시에 GitHub Actions가 실행.
시간대에 따라 가이드를 바꿔서 매번 다른 운동을 안내한다.
그림(치와와=눈운동 / 시라소니=목스트레칭)을 넣으려면 아래 EYE_IMG/NECK_IMG에
디스코드에 올린 이미지 URL을 채워라. 비워두면 그림 없이 텍스트로만 간다.
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

# ── 캐릭터 그림 URL (imgur 또는 '공개' GitHub repo raw 주소 권장) ──
# ※ 디스코드에 올린 이미지 링크는 24시간 뒤 만료되니 쓰지 말 것!
# EYE와 같은 순서로 넣으면 운동마다 다른 그림. 1장만 넣으면 매번 그 그림 사용.
# jsDelivr CDN: 디스코드 임베드가 잘 읽고, 옛 404 캐시도 새 도메인이라 무시됨
_RAW = "https://cdn.jsdelivr.net/gh/yaminsu5674/AlarmSystem@main/images"
EYE_IMG = [f"{_RAW}/eye_{i}.png" for i in range(5)]    # 치와와 눈운동 5포즈
NECK_IMG = [f"{_RAW}/neck_{i}.png" for i in range(5)]  # 시라소니 목스트레칭 5포즈


def pick_img(lst, idx):
    return lst[idx % len(lst)] if lst else None


def send(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    urllib.request.urlopen(req, timeout=15)


def main():
    # KST 기준 시각으로 운동 선택 (UTC+9)
    kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    idx = kst.hour  # 시간마다 다른 운동

    eye_embed = {
        "title": "👀 눈운동",
        "description": EYE[idx % len(EYE)],
        "color": 0xFFD166,
    }
    eye_img = pick_img(EYE_IMG, idx)
    if eye_img:
        eye_embed["image"] = {"url": eye_img}

    neck_embed = {
        "title": "🦴 목 스트레칭",
        "description": NECK[idx % len(NECK)],
        "color": 0x06D6A0,
    }
    neck_img = pick_img(NECK_IMG, idx)
    if neck_img:
        neck_embed["image"] = {"url": neck_img}

    payload = {
        "content": f"🧘 **{kst.hour}시 스트레칭 타임!** 잠깐 일어나서 1분만 움직여요 💪",
        "embeds": [eye_embed, neck_embed],
    }
    send(payload)
    print(f"습관 알림 전송 ({kst.hour}시)")


if __name__ == "__main__":
    main()
