"""
치와와(눈운동) / 시라소니(목스트레칭) 마스코트 PNG 생성 (Pillow only).
플랫 카와이 스타일. 각 운동 포즈별로 표정/액션 배지를 바꿔 5장씩 생성.
"""
from PIL import Image, ImageDraw
import os, math

OUT = os.environ.get("OUT", "images")
os.makedirs(OUT, exist_ok=True)
W = H = 400

# 팔레트
CREAM = (245, 222, 179)      # 치와와 몸
CREAM_D = (222, 194, 148)
GRAY = (176, 190, 197)       # 시라소니 몸
GRAY_D = (144, 164, 174)
WHITE = (255, 255, 255)
BLACK = (60, 55, 55)
PINK = (255, 179, 186)
BG_EYE = (255, 249, 230)     # 눈운동 배경(노랑끼)
BG_NECK = (232, 250, 244)    # 목스트레칭 배경(민트끼)


def base(bg):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([10, 10, W-10, H-10], radius=48, fill=bg)
    return img, d


def ell(d, cx, cy, rx, ry, **kw):
    d.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], **kw)


def blush(d, cx, cy):
    ell(d, cx, cy, 22, 13, fill=PINK)


def arrow_arc(d, cx, cy, r, color=(255, 140, 90)):
    # 회전 화살표 (눈 굴리기용)
    d.arc([cx-r, cy-r, cx+r, cy+r], start=30, end=300, fill=color, width=9)
    d.polygon([(cx+r-2, cy-r+6), (cx+r+14, cy-r+2), (cx+r+2, cy-r+22)], fill=color)


def draw_chihuahua(pose):
    img, d = base(BG_EYE)
    cx, cy = 200, 210
    # 귀 (뾰족, 큰)
    d.polygon([(cx-118, cy-40), (cx-70, cy-150), (cx-40, cy-70)], fill=CREAM_D)
    d.polygon([(cx+118, cy-40), (cx+70, cy-150), (cx+40, cy-70)], fill=CREAM_D)
    d.polygon([(cx-100, cy-50), (cx-70, cy-120), (cx-52, cy-72)], fill=PINK)
    d.polygon([(cx+100, cy-50), (cx+70, cy-120), (cx+52, cy-72)], fill=PINK)
    # 얼굴
    ell(d, cx, cy, 120, 108, fill=CREAM)
    ell(d, cx, cy+18, 78, 66, fill=WHITE)  # 주둥이 밝은 부분
    # 볼터치
    blush(d, cx-78, cy+22); blush(d, cx+78, cy+22)

    # 눈 (포즈별)
    lx, rx, ey = cx-46, cx+46, cy-8
    if pose == 3:            # 꾹 감기
        for ex in (lx, rx):
            d.arc([ex-24, ey-6, ex+24, ey+30], start=200, end=340, fill=BLACK, width=8)
    elif pose == 0:          # 먼 곳 응시 (눈동자 옆으로)
        for ex in (lx, rx):
            ell(d, ex, ey, 26, 30, fill=WHITE, outline=BLACK, width=3)
            ell(d, ex+12, ey, 12, 15, fill=BLACK)
            ell(d, ex+16, ey-6, 4, 4, fill=WHITE)
        d.line([cx+150, cy-70, cx+185, cy-90], fill=(120,120,120), width=4)  # 먼 곳 표시
    else:                    # 기본 초롱초롱
        for ex in (lx, rx):
            ell(d, ex, ey, 26, 30, fill=WHITE, outline=BLACK, width=3)
            ell(d, ex, ey+2, 15, 18, fill=BLACK)
            ell(d, ex-5, ey-5, 6, 6, fill=WHITE)
    # 코 + 입
    ell(d, cx, cy+34, 13, 9, fill=BLACK)
    d.arc([cx-22, cy+40, cx, cy+64], start=20, end=160, fill=BLACK, width=4)
    d.arc([cx, cy+40, cx+22, cy+64], start=20, end=160, fill=BLACK, width=4)

    # 포즈별 액션
    if pose == 1:            # 눈 굴리기
        arrow_arc(d, cx, cy-2, 96)
    if pose == 2:            # 초점 전환 (앞발로 근/원 지시)
        ell(d, cx-150, cy+70, 16, 22, fill=CREAM_D)  # 앞발
        ell(d, cx-150, cy+40, 7, 7, fill=(255,120,90))
        ell(d, cx+150, cy-40, 5, 5, fill=(255,120,90))
    if pose == 4:            # 눈 지압 (관자놀이 앞발)
        ell(d, cx-96, cy-6, 18, 24, fill=CREAM_D)
        ell(d, cx+96, cy-6, 18, 24, fill=CREAM_D)
    return img


def draw_lynx(pose):
    img, d = base(BG_NECK)
    cx, cy = 200, 205
    # 귀 + 귀털(시라소니 특징)
    for sx in (-1, 1):
        bx = cx + sx*78
        d.polygon([(bx-30, cy-60), (bx+30, cy-60), (bx+sx*6, cy-140)], fill=GRAY_D)
        d.line([(bx+sx*6, cy-140), (bx+sx*6, cy-172)], fill=BLACK, width=7)  # 귀털
    # 얼굴
    ell(d, cx, cy, 118, 104, fill=GRAY)
    # 볼 털 (양쪽 삐침)
    for sx in (-1, 1):
        for k in range(3):
            d.polygon([(cx+sx*110, cy+10+k*22), (cx+sx*150, cy+2+k*24),
                       (cx+sx*112, cy+26+k*22)], fill=WHITE)
    ell(d, cx, cy+16, 74, 60, fill=WHITE)
    blush(d, cx-70, cy+20); blush(d, cx+70, cy+20)

    # 눈
    lx, rx, ey = cx-44, cx+44, cy-6
    for ex in (lx, rx):
        ell(d, ex, ey, 24, 28, fill=WHITE, outline=BLACK, width=3)
        ell(d, ex, ey+2, 13, 16, fill=BLACK)
        ell(d, ex-4, ey-5, 5, 5, fill=WHITE)
    # 코+입
    d.polygon([(cx-12, cy+30), (cx+12, cy+30), (cx, cy+42)], fill=(120,90,90))
    d.arc([cx-20, cy+40, cx, cy+60], start=20, end=160, fill=BLACK, width=4)
    d.arc([cx, cy+40, cx+20, cy+60], start=20, end=160, fill=BLACK, width=4)

    C = (90, 170, 140)  # 액션 색(민트그린)
    if pose == 0:        # 턱 당기기 (뒤로 화살표)
        d.line([cx+120, cy+10, cx+170, cy+10], fill=C, width=9)
        d.polygon([(cx+120, cy), (cx+104, cy+10), (cx+120, cy+20)], fill=C)
    if pose == 1:        # 목 옆으로 (기울임 화살표)
        d.arc([cx-40, cy-150, cx+120, cy-30], start=200, end=330, fill=C, width=9)
        d.polygon([(cx+96, cy-96), (cx+120, cy-84), (cx+112, cy-60)], fill=C)
    if pose == 2:        # 뒤통수 벽 밀기 (벽 + 화살표)
        d.rectangle([cx-176, cy-90, cx-150, cy+120], fill=(200,200,200))
        d.line([cx-70, cy, cx-120, cy], fill=C, width=9)
        d.polygon([(cx-120, cy-10), (cx-138, cy), (cx-120, cy+10)], fill=C)
    if pose == 3:        # 가슴 열기 (양쪽 화살표)
        for sx in (-1, 1):
            d.line([cx+sx*70, cy+96, cx+sx*150, cy+96], fill=C, width=9)
            d.polygon([(cx+sx*150, cy+86), (cx+sx*166, cy+96), (cx+sx*150, cy+106)], fill=C)
    if pose == 4:        # 어깨 으쓱 (위 화살표)
        for sx in (-1, 1):
            d.line([cx+sx*96, cy+70, cx+sx*96, cy+10], fill=C, width=9)
            d.polygon([(cx+sx*96-10, cy+18), (cx+sx*96, cy), (cx+sx*96+10, cy+18)], fill=C)
    return img


for i in range(5):
    draw_chihuahua(i).save(f"{OUT}/eye_{i}.png")
    draw_lynx(i).save(f"{OUT}/neck_{i}.png")
print("생성 완료:", sorted(os.listdir(OUT)))
