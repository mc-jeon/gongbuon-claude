"""실습 자료 생성기 — 모두 가상 데이터.
실행: python src/make_practice.py <교안폴더>
만드는 것: practice/usb_sample/(뒤섞인 파일 21개) + usb_sample.zip,
          practice/pay/ 결제 내역 3종 + 재원생 명단, practice/consult_transcript.txt
"""
import csv
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
P = ROOT / "practice"

# ── 1. USB 샘플: 분류 실습용 (정답 분류는 USB_ANSWER) ──
USB_ANSWER = {
    "01_시간표": ["시간표_A형_학기중.csv", "시간표_B형_방학.csv", "시간표_C형_시험기간.csv",
                "시간표유형_16가지_정리.md", "여름방학_재설계_메모.txt"],
    "02_상담": ["상담일지_양식.md", "이탈방지_상담기준.md", "신규상담_체크리스트.txt", "학부모상담_질문모음.txt"],
    "03_홍보": ["블로그_기말D30_원고.md", "당근_소식_11월.txt", "플레이스_소식_11월.txt", "인스타_릴스_대본.txt",
              "카드뉴스_기말대비_시안.png", "카드뉴스_방학등록_시안.png"],
    "04_정산서류": ["사업비_집행계획_메모.txt", "견적비교_메모.csv", "매출요약_3-8월.csv", "현물인건비_체크리스트.md"],
    "99_확인필요": ["새 텍스트 문서.txt", "사진_001.png"],
}
BODY = {
    "시간표_A형_학기중.csv": "요일,시작,끝,내용\n월,18:00,22:00,자습(수학)\n",
    "시간표_B형_방학.csv": "요일,시작,끝,내용\n월,09:00,12:00,자습(국어)\n",
    "시간표_C형_시험기간.csv": "요일,시작,끝,내용\n토,10:00,18:00,시험 범위 복습\n",
    "시간표유형_16가지_정리.md": "# 시간표 유형 16가지(가상 메모)\n- A형: 학원 2곳 + 평일 저녁 자습\n",
    "여름방학_재설계_메모.txt": "방학 시간표 재설계 순서 메모(가상)\n",
    "상담일지_양식.md": "# 상담일지 양식\n날짜 / 학생 / 상담 내용 / 조치\n",
    "이탈방지_상담기준.md": "# 이탈 신호 기준(가상)\n- 2주 연속 지각 2회 이상\n",
    "신규상담_체크리스트.txt": "신규 상담 시 확인할 것: 학교, 학원, 목표\n",
    "학부모상담_질문모음.txt": "학부모님께 자주 받는 질문 모음(가상)\n",
    "블로그_기말D30_원고.md": "# 기말고사 D-30 원고(가상)\n",
    "당근_소식_11월.txt": "당근 소식 초안(가상)\n",
    "플레이스_소식_11월.txt": "플레이스 소식 초안(가상)\n",
    "인스타_릴스_대본.txt": "릴스 대본 초안(가상)\n",
    "사업비_집행계획_메모.txt": "사업비 집행 일정 메모(가상)\n",
    "견적비교_메모.csv": "업체,금액\nA사,8000000\nB사,9500000\n",
    "매출요약_3-8월.csv": "월,매출\n3월,0\n",
    "현물인건비_체크리스트.md": "# 현물 인건비 서류 체크리스트(가상)\n",
    "새 텍스트 문서.txt": "",
}


def png(path: Path, label: str, color):
    im = Image.new("RGB", (320, 320), color)
    ImageDraw.Draw(im).rectangle([20, 20, 300, 300], outline=(255, 255, 255), width=6)
    im.save(path)


usb = P / "usb_sample"
if usb.exists():
    shutil.rmtree(usb)
usb.mkdir(parents=True)
colors = [(11, 31, 75), (201, 100, 66), (120, 120, 120)]
for i, name in enumerate(n for files in USB_ANSWER.values() for n in files):
    f = usb / name
    if name.endswith(".png"):
        png(f, name, colors[i % 3])
    else:
        f.write_text(BODY.get(name, ""), encoding="utf-8")
with zipfile.ZipFile(P / "usb_sample.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(usb.iterdir()):
        z.write(f, f"usb_sample/{f.name}")

# ── 2. 결제 내역 3종 + 재원생 명단 (가상 인물) ──
pay = P / "pay"
pay.mkdir(exist_ok=True)
ROSTER = [  # 학생, 학부모, 이용권, 금액
    ("김하늘", "김정미", "학기 기본", 280000), ("이서준", "이수경", "학기 종일", 340000),
    ("박도윤", "박지영", "학기 기본", 280000), ("최민준", "최은희", "학기 종일", 340000),
    ("정유나", "정혜진", "학기 기본", 280000), ("강시우", "강미숙", "학기 종일", 340000),
    ("조하린", "조은정", "학기 기본", 280000), ("윤지호", "윤선영", "학기 종일", 340000),
    ("장서연", "장미영", "학기 기본", 280000), ("임준우", "임현주", "학기 종일", 340000),
    ("한소율", "한지은", "학기 기본", 280000), ("오태윤", "오정아", "학기 종일", 340000),
]


def write(name, header, rows):
    with open(pay / name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


write("재원생_명단.csv", ["학생명", "학부모명", "이용권", "12월 금액"], ROSTER)
write("결제선생_내역.csv", ["결제일시", "청구서명", "학생이름", "결제금액", "결제수단", "상태"], [
    ["2026-11-24 21:05", "12월 이용료", "김하늘", "280,000", "카드", "결제완료"],
    ["2026-11-25 08:40", "12월 이용료", "이서준", "340,000", "카드", "결제완료"],
    ["2026-11-25 13:12", "12월 이용료", "정유나", "280,000", "간편결제", "결제완료"],
    ["2026-11-26 19:30", "12월 이용료", "윤지호", "340,000", "카드", "결제완료"],
    ["-", "12월 이용료", "장서연", "280,000", "-", "결제대기"],
])
write("토스POS_내역.csv", ["거래일시", "승인번호", "카드사", "승인금액", "메모"], [
    ["2026.11.25 17:21", "30018842", "신한", "340000", "강시우"],
    ["2026.11.26 15:02", "30019107", "국민", "280000", "조하린 12월"],
    ["2026.11.27 20:48", "30019655", "삼성", "340000", ""],
])
write("계좌이체_내역.csv", ["거래일자", "입금자명", "입금액", "적요"], [
    ["11/25", "박지영", "280000", "타행이체"],
    ["11/26", "최민준맘", "340000", "모바일"],
    ["11/27", "한지은", "140000", "모바일"],
])

# ── 3. 상담 녹취(가상) ──
(P / "consult_transcript.txt").write_text("""[실습용 가상 상담 녹취 — 실제 인물 아님]
일시: 2026. 11. 20.(금) 21:10 / 대상: 학생 '가온'(고1) 어머니 / 방식: 전화

원장: 어머님, 가온이가 최근 2주 동안 지각이 세 번 있었어서 연락드렸어요.
어머니: 아, 학원 끝나는 시간이 바뀌어서 그런 것 같아요. 수학학원이 이번 달부터 30분 늦게 끝나요.
원장: 그러면 화·목은 등원 시간을 8시 30분으로 옮기는 게 좋겠어요. 대신 토요일 오전에 2시간을 추가하면 주간 공부 시간은 그대로 유지돼요.
어머니: 좋아요. 그리고 요즘 아이가 영어 단어를 너무 미루는 것 같아요.
원장: 매일 첫 20분을 단어 시간으로 고정해 둘게요. 다음 주 금요일에 단어 시험 결과랑 출결 같이 보고 다시 말씀드릴게요.
어머니: 네, 감사합니다. 12월 등록은 이번 주말에 할게요.
""", encoding="utf-8")
print("practice ready:", sum(len(v) for v in USB_ANSWER.values()), "usb files")

# ── 4. 내려받기용 묶음 ──
with zipfile.ZipFile(P / "pay.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(pay.glob("*.csv")):
        if f.name != "수납대조표.csv":
            z.write(f, f"pay/{f.name}")
skill = P / "skill_example" / "gongbuon-channel-post"
with zipfile.ZipFile(P / "gongbuon-channel-post.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(skill / "SKILL.md", "gongbuon-channel-post/SKILL.md")   # 폴더째 압축(Claude 업로드 규칙)
print("zips ready")
