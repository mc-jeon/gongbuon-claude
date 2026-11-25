"""12월 수납 대조표 만들기 (정답 확인용 예시 코드)
Claude Code에게 맡기면 이와 비슷한 코드를 만들어 실행합니다. 직접 실행할 필요는 없습니다.
실행: python reconcile.py <pay 폴더>  →  같은 폴더에 수납대조표.csv
"""
import csv
import sys
from pathlib import Path

d = Path(sys.argv[1] if len(sys.argv) > 1 else ".")


def rows(name):
    with open(d / name, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def won(s):
    return int(str(s).replace(",", "").strip() or 0)


roster = rows("재원생_명단.csv")
paid = {r["학생명"]: [] for r in roster}          # 학생명 → [(경로, 금액)]
waiting, unknown = set(), []


def find(text):
    """메모·입금자명에서 학생(또는 학부모) 이름을 찾는다."""
    for r in roster:
        if r["학생명"] in text or r["학부모명"] in text:
            return r["학생명"]
    return None


for r in rows("결제선생_내역.csv"):
    if r["상태"] != "결제완료":
        waiting.add(r["학생이름"])
        continue
    paid[r["학생이름"]].append(("결제선생", won(r["결제금액"])))
for r in rows("토스POS_내역.csv"):
    who = find(r["메모"])
    (paid[who].append(("토스POS", won(r["승인금액"]))) if who
     else unknown.append(f"토스POS {r['거래일시']} {won(r['승인금액']):,}원 (메모 없음)"))
for r in rows("계좌이체_내역.csv"):
    who = find(r["입금자명"])
    (paid[who].append(("계좌이체", won(r["입금액"]))) if who
     else unknown.append(f"계좌이체 {r['거래일자']} {r['입금자명']} {won(r['입금액']):,}원"))

out, count = [], {}
for r in roster:
    name, due = r["학생명"], won(r["12월 금액"])
    got = sum(a for _, a in paid[name])
    route = "+".join(p for p, _ in paid[name]) or "-"
    state = ("완납" if got >= due else "부분납" if got else "결제대기" if name in waiting else "미납")
    count[state] = count.get(state, 0) + 1
    out.append([name, r["학부모명"], f"{due:,}", f"{got:,}", f"{due - got:,}", route, state])

with open(d / "수납대조표.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["학생명", "학부모명", "청구액", "입금액", "남은 금액", "결제 경로", "상태"])
    w.writerows(out)
    w.writerow([])
    for u in unknown:
        w.writerow(["확인 필요", u])

print(" / ".join(f"{k} {v}명" for k, v in count.items()), f"/ 확인 필요 거래 {len(unknown)}건")
