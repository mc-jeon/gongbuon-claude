"""공부ON × Claude 업무 자동화 실습 교안 빌드
실행: python src/build.py <교안폴더>   → index.html, practice/prompts.md
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lessonkit import (E, Page, app_window, box, build, cards, chat_view, code_block, dialog, downloads, fig, figs, flow,
                       gbtn, grid, hero, kbd, mk, prompt, section, shot_list_section, sidebar, step, table, ui, wrap)

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SITE = os.environ.get("SITE_URL", "https://mc-jeon.github.io/gongbuon-claude/")
PC = "설치·실습은 PC에서 해야 합니다. 휴대폰에서는 복습용으로 보세요. 그림은 탭하면 크게 보입니다."

# ───────────── 프롬프트: 교안과 prompts.md가 같은 원본을 쓴다 ─────────────
PROMPTS: list[tuple[str, str]] = []


def P(title: str, text: str) -> str:
    PROMPTS.append((title, text))
    return prompt(text)


# ───────────── 이 교안 전용 모형 부품 ─────────────
CSS = """
.term{background:#0c0c0c;color:#e6e6e6;font-family:Consolas,'D2Coding',monospace;font-size:11.5px;padding:10px 12px;border-radius:4px;white-space:pre-wrap;line-height:1.6;min-height:170px}
.term .pr{color:#7fd17f}.term .cm{color:#f3d36b}.term .dim{color:#9a9a9a}.term .cl{color:#e8a27c}
.term .mk::after{top:-9px}
.term .mk,.cs-nav .mk{display:inline-block;padding-right:16px}
.prompt{padding-top:38px}
.cs{display:flex;min-height:230px;margin:-10px}
.cs-nav{width:30%;background:#f7f5f0;border-right:1px solid #e5e1d8;padding:10px 8px;font-size:12px}
.cs-nav div{padding:5px 8px;border-radius:6px;margin:2px 0}.cs-nav .on{background:#e9e4d8;font-weight:700}
.cs-nav .sub{padding-left:18px;font-size:11.5px}
.cs-main{flex:1;padding:12px}.cs-main h5{font-size:14px;margin-bottom:8px}
.li{display:flex;justify-content:space-between;align-items:center;border:1px solid #e3e3e3;border-radius:8px;padding:7px 10px;margin:5px 0;font-size:12px}
.li small{color:#777}
.tg{display:inline-block;width:28px;height:16px;border-radius:9px;background:#c96442;position:relative;vertical-align:middle}
.tg::after{content:"";position:absolute;right:2px;top:2px;width:12px;height:12px;border-radius:50%;background:#fff}
.tg.off{background:#bbb}.tg.off::after{right:auto;left:2px}
.addr{display:block;background:#f1f3f4;border-radius:14px;padding:4px 12px;color:#444;margin:0 0 8px;font-size:11.5px}
.fold{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.fold span{border:1px solid #e0e0e0;border-radius:6px;padding:6px 8px;font-size:11.5px;background:#fff}
.lb{font-size:11px;color:#666;margin-top:7px}
.ta{border:1px solid #c9d1dd;border-radius:6px;padding:6px 8px;min-height:54px;white-space:pre-wrap;font-size:11.5px;background:#fff}
.ex{display:flex;min-height:220px;margin:-10px}.ex-nav{width:28%;background:#f3f6fb;padding:8px;font-size:11.5px;border-right:1px solid #e1e6ef}
.ex-nav div{padding:4px 6px}.ex-nav .on{background:#dce7f7;border-radius:4px}.ex-main{flex:1;padding:8px 10px}
.wsr{display:flex;gap:10px;align-items:center;border:1px solid #e3e3e3;border-radius:10px;padding:10px;margin:6px 0}
.wsr .ic2{width:42px;height:42px;border-radius:10px;background:#c96442;color:#fff;font:800 20px/42px Arial;text-align:center}
.mini{font-size:11px;color:#666}
"""


def term(lines, title="Windows PowerShell"):
    """lines: [(종류, 글자)] 종류: pr(입력 줄) / out / dim / cm(강조) / cl(Claude) / raw(HTML 그대로)"""
    out = []
    for kind, text in lines:
        if kind == "raw":
            out.append(text)
        elif kind == "pr":
            out.append(f'<span class="pr">PS C:\\Users\\공부ON&gt;</span> {E(text)}')
        else:
            out.append(f'<span class="{kind}">{E(text)}</span>')
    return app_window(title, f'<div class="term">{"<br>".join(out)}</div>', icon_color="#012456")


def pr_mk(text, n, path="C:\\Users\\공부ON"):
    return ("raw", mk(f'<span class="pr">PS {E(path)}&gt;</span> {E(text)}', n))


def claude_settings(on, main_html, marks=None, overlay=""):
    marks = marks or {}
    items = [("채팅", ""), ("프로젝트", ""), ("사용자 지정", ""), ("커넥터", "sub"), ("스킬", "sub")]
    nav = ""
    for name, cls in items:
        label = mk(E(name), marks[name]) if name in marks else E(name)
        nav += f'<div class="{cls} {"on" if name == on else ""}">{label}</div>'
    return app_window("Claude", f'<div class="cs"><div class="cs-nav">{nav}</div><div class="cs-main">{main_html}</div></div>',
                      icon_color="#c96442", overlay=overlay)


def chrome(title, url, body, overlay="", url_mark=None):
    a = f'<span class="addr">🔒 {E(url)}</span>'
    return app_window(f"{title} — Chrome", (mk(a, url_mark, block=True) if url_mark else a) + body,
                      icon_color="#1a73e8", overlay=overlay)


def explorer(path, nav_on, items, addr_mark=None, title="파일 탐색기"):
    navs = ["바탕 화면", "다운로드", "내 PC", "USB 드라이브 (E:)", "Google Drive (G:)"]
    nav = "".join(f'<div class="{"on" if n == nav_on else ""}">{E(n)}</div>' for n in navs)
    a = f'<span class="addr">📁 {E(path)}</span>'
    a = mk(a, addr_mark, block=True) if addr_mark else a
    fold = "".join(f"<span>{i}</span>" for i in items)
    return app_window(title, f'<div class="ex"><div class="ex-nav">{nav}</div><div class="ex-main">{a}<div class="fold">{fold}</div></div></div>',
                      icon_color="#f2b01e")


# ═════════════════════════════ 홈 ═════════════════════════════
home = hero("공부ON 스터디카페 · AI 활용 멘토링 실습 교안",
            "혼자 운영해도 손이 덜 가게<br><em>Claude로 백업·배포·반복 업무 줄이기</em>",
            "최종 검수와 발행 버튼만 내가 누르고, 나머지는 Claude에게 맡깁니다. 화면 순서대로 따라 하면 됩니다.") + wrap(
    section("오늘 만드는 것", "실제 업무 흐름 그대로 실습합니다")
    + cards([("☁️", "잃어버리지 않는 작업 환경", "USB 파일을 구글 드라이브로 분류·백업하고 Claude와 연결"),
             ("📣", "글 한 편 → 4개 채널", "블로그 원고를 당근·플레이스·인스타용으로 바꾸고, 크롬에서 <b>올리기 직전</b>까지 자동으로"),
             ("🎨", "미리캔버스 + Claude", "MCP로 연결해 카드뉴스 시안을 대화로 만들기"),
             ("🧩", "반복 업무를 스킬로", "매번 어긋나던 지시를 <b>스킬 파일</b> 하나로 고정")], cols=4)
    + section("전체 흐름") + flow([("0 준비", "설치 4가지"), ("1 백업", "드라이브"), ("2 크롬", "배포 자동화"),
                                ("3 MCP", "미리캔버스"), ("4 스킬", "반복 고정"), ("5 활용", "수납·상담")])
    + section("탭 구성")
    + table(["탭", "내용", "결과물"], [
        ["0 준비", "PowerShell · Git · Python · Claude Code · 구글 드라이브 설치", "명령창에서 claude 실행"],
        ["1 드라이브 백업", "USB 파일 자동 분류 → 드라이브 복사 → 개수 대조", "공부ON_백업 폴더"],
        ["2 크롬 제어", "Claude in Chrome으로 채널 글쓰기 화면 입력까지", "검수 후 내가 발행"],
        ["3 MCP 연결", "미리캔버스 커스텀 커넥터 추가 · 카드뉴스 시안", "미리캔버스 디자인 1개"],
        ["4 스킬 파일", "스킬 구조 · 만드는 법 2가지 · 등록 · 고치기", "공부ON 채널 변형 스킬"],
        ["5 업무 자동화", "결제 3종 → 수납 대조표 / 상담 녹음 → 상담 기록", "수납대조표 · 상담기록"],
    ])
    + section("꼭 지킬 원칙 3가지")
    + box("ok", "① 발행·결제·삭제 버튼은 내가 누릅니다.", "Claude는 입력·정리·초안까지. 밖으로 나가는 마지막 클릭은 사람이 합니다.")
    + box("no", "② 학생·학부모 실명, 연락처, 카드 정보는 그대로 넣지 않습니다.", "실습은 모두 가상 자료입니다. 실제 업무에서는 이름을 가리거나 내 PC 안에서만 처리합니다.")
    + box("warn", "③ AI 결과는 검수 후 사용합니다.", "날짜·시간·금액은 원본과 한 번 더 대조하세요. 지금처럼 '의심하며 검수하는 습관'이 가장 좋은 안전장치입니다.")
    + section("실습 파일 내려받기", "모두 가상 데이터입니다")
    + downloads([("practice/usb_sample.zip", "📦 USB 샘플 파일 21개", "g"), ("practice/blog_sample.md", "📝 블로그 원고", ""),
                 ("practice/pay.zip", "💳 결제 내역 3종 + 명단", ""), ("practice/consult_transcript.txt", "🎙 상담 녹취", ""),
                 ("practice/gongbuon-channel-post.zip", "🧩 완성 스킬(업로드용)", "g"), ("practice/skill_template.md", "🧩 빈 스킬 양식", ""),
                 ("practice/prompts.md", "💬 프롬프트 모음", "")])
    + box("info", "그림 안내", "교안의 화면 그림은 실제 화면을 단순화한 <b>모형</b>입니다. 메뉴 이름은 업데이트로 조금 바뀔 수 있어 괄호 안에 다른 이름을 함께 적었습니다."))

# ═════════════════════════════ 0 준비 ═════════════════════════════
p0 = wrap("".join([
    section("0. 작업 환경 준비", "한 번만 하면 됩니다 · 약 30분"),
    box("info", "왜 설치하나요?", "지금 쓰는 Claude 앱(대화창)은 <b>말로 답하는</b> 도구입니다. 오늘 설치하는 Claude Code는 내 PC에서 <b>파일을 옮기고, 크롬을 움직이고, 표를 만드는</b> 도구입니다. "
        "글자로 명령하는 검은 창(CLI)에서 쓰지만, 명령어를 외울 필요는 없습니다. 한국어로 부탁하면 됩니다."),
    step("0-1", "PowerShell 열기", "명령을 입력할 검은 창(PowerShell)을 엽니다.",
         [f"키보드 {kbd('Win')} 키 누르기", f"검색창에 {ui('powershell')} 입력", f"{ui('Windows PowerShell')} 클릭"],
         ok="파란색(또는 검은색) 창에 <code>PS C:\\Users\\…&gt;</code> 가 보이면 성공입니다.",
         stuck="'관리자 권한' 창이 뜨면 그냥 닫고 일반 PowerShell로 다시 여세요. 오늘 실습은 관리자 권한이 필요 없습니다.",
         figure=fig("m0-01", "시작 메뉴에서 PowerShell 찾기", app_window("검색", mk('<span class="minput">🔍 powershell</span>', 2, block=True)
             + '<div class="lb">가장 일치하는 항목</div>' + mk('<div class="li"><span>🟦 <b>Windows PowerShell</b><br><small>앱</small></span><span>열기 ›</span></div>', 3, block=True)
             + '<div class="li"><span>Windows PowerShell ISE</span></div>', icon_color="#0078d4"))),
    step("0-2", "Git·Python 설치", "Claude Code가 쓰는 기본 도구 두 가지를 설치합니다.",
         [f"아래 상자의 {ui('전체 복사')} 클릭", f"PowerShell 창에 마우스 오른쪽 클릭(또는 {kbd('Ctrl', 'V')}) → {kbd('Enter')}",
          f"중간에 '계약 조건에 동의하십니까?'가 나오면 {kbd('Y')} → {kbd('Enter')}", "두 줄 모두 '설치됨'이 나오면 PowerShell 창을 <b>닫았다가 다시</b> 열기"],
         extra=code_block("Git·Python 설치", text="winget install --id Git.Git -e\nwinget install --id Python.Python.3.12 -e\n", cid="c-winget"),
         ok="마지막에 <code>설치됨</code>(또는 Successfully installed)이 두 번 보이면 성공입니다.",
         stuck="'winget을 찾을 수 없습니다'가 나오면 Microsoft Store에서 <b>앱 설치 관리자</b>를 업데이트한 뒤 다시 하세요.",
         figure=fig("m0-02", "명령 붙여넣기 → 설치", term([pr_mk("winget install --id Git.Git -e", 2), ("out", "찾음 Git [Git.Git] 버전 2.x"),
                                                     ("out", "다운로드 중 ██████████ 100%"), ("cm", "설치됨"),
                                                     ("pr", "winget install --id Python.Python.3.12 -e"), ("cm", "설치됨")]))),
    step("0-3", "Claude Code 설치·로그인", "Claude Code를 설치하고 지금 쓰는 Claude 계정으로 로그인합니다.",
         [f"아래 명령 복사 → PowerShell에 붙여넣기 → {kbd('Enter')}", "설치가 끝나면 창을 닫고 다시 열기",
          f"{ui('claude')} 입력 → {kbd('Enter')}", f"글자 색 고르기 화면은 {kbd('Enter')}로 넘기기",
          f"로그인 방법에서 {ui('Claude account with subscription')} 선택 → 브라우저에서 {ui('승인')}(Authorize)"],
         extra=code_block("Claude Code 설치", text="irm https://claude.ai/install.ps1 | iex\n", cid="c-install")
         + box("info", "요금제", "지금 쓰시는 최고 단계 요금제(Max)로 그대로 씁니다. 추가 결제는 없습니다. 웹 대화창보다 명령창이 같은 일을 할 때 토큰을 덜 씁니다."),
         ok="창에 <code>Welcome to Claude Code</code>와 입력칸(<code>&gt;</code>)이 보이면 성공입니다.",
         stuck="'claude 명령을 찾을 수 없습니다'가 나오면 PowerShell을 완전히 닫고 새로 여세요. 그래도 안 되면 PC를 다시 시작합니다.",
         figure=fig("m0-03", "claude 실행 → 계정 로그인", term([("pr", "irm https://claude.ai/install.ps1 | iex"), ("cm", "✔ Claude Code successfully installed"),
                                                         pr_mk("claude", 3), ("cl", "Select login method:"),
                                                         ("raw", mk('<span class="cl">❯ 1. Claude account with subscription</span>', 5)),
                                                         ("dim", "  2. Anthropic Console account")]))),
    step("0-4", "설치 확인", "세 가지가 모두 제대로 설치됐는지 확인합니다.",
         [f"Claude 화면이면 {ui('/exit')} 입력 → {kbd('Enter')}로 나오기", "아래 세 줄 복사 → 붙여넣기 → Enter"],
         extra=code_block("설치 확인", text="git --version\npython --version\nclaude --version\n", cid="c-check"),
         ok="세 줄 모두 <code>git version 2.…</code> / <code>Python 3.12…</code> / <code>2.… (Claude Code)</code>처럼 <b>버전 숫자</b>가 나오면 성공입니다.",
         stuck="python만 안 되면 Microsoft Store가 열릴 수 있습니다. 창을 닫고 PowerShell을 새로 연 뒤 다시 확인하세요.", one=True),
    step("0-5", "구글 드라이브 데스크톱 설치", "내 PC에 'G 드라이브'를 만들어, 드라이브를 USB처럼 쓰게 합니다.",
         [f"크롬에서 <a href='https://www.google.com/drive/download/' target='_blank' rel='noopener'>{ui('google.com/drive/download')}</a> 접속 → 아래로 내려 {ui('데스크톱용 Drive 다운로드')}",
          "내려받은 파일 실행 → 설치", f"<b>Gemini 유료 구독 중인 구글 계정</b>으로 로그인 (2TB 저장 공간이 있는 계정)",
          f"파일 탐색기 왼쪽에 {ui('Google Drive (G:)')} 가 생겼는지 확인"],
         ok="탐색기에 <b>Google Drive (G:)</b> → <b>내 드라이브</b> 폴더가 보이면 성공입니다.",
         stuck="G가 아닌 다른 글자(H: 등)로 생길 수 있습니다. 이후 교안의 G: 를 내 PC 글자로 바꿔 읽으세요.",
         figure=fig("m0-04", "탐색기에 생긴 Google Drive (G:)", explorer("Google Drive (G:) › 내 드라이브", "Google Drive (G:)",
                                                                   ["📁 내 드라이브", "📁 공유 드라이브", "📁 컴퓨터"]))),
    box("ok", "여기까지 배운 것", "검은 창(PowerShell)을 열고, Claude Code를 실행하고, 내 PC에 구글 드라이브를 연결했습니다."),
]), pc_note=PC)

# ═════════════════════════════ 1 드라이브 백업 ═════════════════════════════
USB_ITEMS = ["📄 시간표_A형_학기중.csv", "📄 블로그_기말D30_원고.md", "🖼 카드뉴스_기말대비_시안.png", "📄 상담일지_양식.md",
             "📄 견적비교_메모.csv", "📄 새 텍스트 문서.txt", "🖼 사진_001.png", "📄 당근_소식_11월.txt", "…총 21개"]
p1 = wrap("".join([
    section("1. 드라이브 백업", "USB 한 개에만 있던 파일을 안전하게 · 약 30분"),
    flow([("① 연습 파일", "USB 대신"), ("② Claude", "분류표 제안"), ("③ 내가 확인", "고칠 것 말하기"), ("④ 복사", "G 드라이브로"), ("⑤ 대조", "개수 확인")]),
    box("warn", "원칙: '이동'이 아니라 '복사'", "원본(USB)은 지우지 않습니다. 드라이브에 다 옮겨진 걸 확인한 뒤, USB는 보조 백업으로 남겨 두세요."),
    step("1-1", "연습 파일 준비", "실제 USB 대신 가상 파일 21개로 먼저 연습합니다.",
         [f"홈 탭의 {ui('USB 샘플 파일 21개')} 내려받기", f"내려받은 zip에 마우스 오른쪽 클릭 → {ui('모두 압축 풀기')}",
          f"풀 위치를 {ui('바탕 화면')}으로 지정 → {ui('압축 풀기')}"],
         ok="바탕 화면에 <b>usb_sample</b> 폴더가 생기고, 안에 파일 21개가 섞여 있으면 성공입니다.",
         stuck="실제 USB로 할 때는 탐색기 왼쪽의 <b>USB 드라이브 (E:)</b>처럼 보이는 글자를 확인해 두세요(D:, F:일 수도 있습니다).",
         figure=fig("m1-01", "뒤섞인 파일 21개", explorer("바탕 화면 › usb_sample", "바탕 화면", USB_ITEMS))),
    step("1-2", "폴더에서 Claude Code 열기", "작업할 폴더 안에서 Claude를 실행합니다. 그래야 그 폴더만 다룹니다.",
         ["탐색기에서 바탕 화면 → usb_sample 폴더 열기", "위쪽 주소창 클릭", f"{ui('powershell')} 입력 → {kbd('Enter')}",
          f"열린 창에 {ui('claude')} 입력 → {kbd('Enter')}", f"'이 폴더의 파일을 신뢰합니까?'에서 {ui('Yes, proceed')} 선택"],
         ok="Claude Code 화면 위쪽에 <code>…\\Desktop\\usb_sample</code> 경로가 보이면 성공입니다.",
         figure=figs(fig("m1-02", "주소창에 powershell 입력", explorer("powershell", "바탕 화면", USB_ITEMS[:6], addr_mark=2)),
                     fig("m1-03", "폴더 신뢰 확인", term([pr_mk("claude", 4, "C:\\Users\\공부ON\\Desktop\\usb_sample"),
                                                     ("cl", "Do you trust the files in this folder?"), ("dim", "C:\\Users\\공부ON\\Desktop\\usb_sample"),
                                                     ("raw", mk('<span class="cl">❯ 1. Yes, proceed</span>', 5)), ("dim", "  2. No, exit")])))),
    step("1-3", "분류표 먼저 받기", "바로 옮기지 않고, 어떻게 나눌지 <b>표로 먼저</b> 받아 봅니다.",
         ["아래 프롬프트 복사 → Claude 입력칸에 붙여넣기 → Enter", "Claude가 보여 준 분류표 읽기", "바꾸고 싶은 게 있으면 말로 고치기(예: '견적비교는 홍보 말고 정산서류로')"],
         extra=P("1-3 분류표 먼저 받기", "이 폴더에 있는 파일을 전부 살펴보고, 아래 폴더로 나누는 분류표를 먼저 보여줘.\n"
                 "아직 옮기거나 복사하지 마.\n\n[분류 폴더]\n01_시간표 / 02_상담 / 03_홍보 / 04_정산서류 / 99_확인필요\n\n"
                 "[규칙]\n- 파일 이름만으로 애매하면 내용을 열어 보고 판단해\n- 그래도 모르겠으면 99_확인필요로\n- 표: 파일명 | 분류 | 이유(한 줄)"),
         ok="표에 21개 파일이 모두 있고, 대략 <b>시간표 5 · 상담 4 · 홍보 6 · 정산서류 4 · 확인필요 2</b>로 나뉘면 성공입니다(조금 달라도 괜찮습니다. 내가 고치면 됩니다).",
         figure=fig("m1-04", "Claude가 보여 준 분류표", term([("raw", mk('<span class="pr">&gt;</span> 이 폴더에 있는 파일을 전부 살펴보고…', 1)),
                                                        ("cl", "● 21개 파일을 확인했습니다. 분류 제안입니다:"),
                                                        ("out", "  01_시간표    5개  시간표_A형_학기중.csv …"), ("out", "  02_상담      4개  상담일지_양식.md …"),
                                                        ("out", "  03_홍보      6개  블로그_기말D30_원고.md …"), ("out", "  04_정산서류  4개  견적비교_메모.csv …"),
                                                        ("out", "  99_확인필요  2개  새 텍스트 문서.txt(빈 파일), 사진_001.png"),
                                                        ("cl", "이대로 복사할까요?")], title="Claude Code"))),
    step("1-4", "드라이브로 복사", "확인한 분류대로 G 드라이브에 폴더를 만들고 복사합니다.",
         ["아래 프롬프트 복사 → 붙여넣기 → Enter", f"Claude가 명령 실행 허락을 물으면 내용 읽고 {ui('1. Yes')} 선택",
          "복사가 끝났다는 메시지 기다리기"],
         extra=P("1-4 드라이브로 복사", "좋아, 그 분류대로 진행해줘.\n- 복사할 곳: G:\\내 드라이브\\공부ON_백업\\\n- 분류 폴더를 만들고 그 안에 복사\n"
                 "- 원본은 절대 지우거나 옮기지 마 (복사만)\n- 끝나면 폴더별 파일 개수를 알려줘")
         + box("info", "Claude가 자꾸 '허락'을 묻는 이유", "파일을 만들거나 복사하는 명령은 실행 전에 꼭 물어봅니다. "
               "<b>1. Yes</b>는 이번 한 번, <b>2. Yes, and don't ask again…</b>은 같은 종류를 계속 허락합니다. 처음에는 1번으로 하나씩 보세요. "
               "'삭제(Remove, del)'가 들어간 명령이면 <b>3. No</b>를 누르고 이유를 물어보세요."),
         ok="탐색기 <b>Google Drive (G:) › 내 드라이브 › 공부ON_백업</b>에 폴더 5개가 생기면 성공입니다.",
         stuck="'G: 경로를 찾을 수 없습니다'가 나오면 0-5의 드라이브 글자를 확인하고 프롬프트의 G: 를 바꾸세요.",
         figure=fig("m1-05", "드라이브에 생긴 분류 폴더", explorer("Google Drive (G:) › 내 드라이브 › 공부ON_백업", "Google Drive (G:)",
                                                            ["📁 01_시간표", "📁 02_상담", "📁 03_홍보", "📁 04_정산서류", "📁 99_확인필요"]))),
    step("1-5", "개수 대조", "빠진 파일이 없는지 원본과 숫자로 확인합니다.",
         ["아래 프롬프트 복사 → 붙여넣기 → Enter", "합계가 같은지 확인", "브라우저에서 drive.google.com 을 열어 같은 폴더가 보이는지 확인"],
         extra=P("1-5 개수 대조", "원본 폴더와 G:\\내 드라이브\\공부ON_백업 을 비교해서\n폴더별 파일 개수, 전체 개수, 전체 용량을 표로 보여줘.\n빠진 파일이 있으면 이름을 알려줘."),
         ok="원본 <b>21개</b> = 복사본 <b>21개</b>, '빠진 파일 없음'이 나오면 성공입니다. 웹 드라이브에는 몇 분 뒤에 나타날 수 있습니다(동기화 중).",
         one=True),
    step("1-6", "Claude 대화창에서 드라이브 연결 확인", "Claude 앱에서도 드라이브 파일을 찾아 읽을 수 있게 커넥터를 켭니다.",
         [f"Claude 앱(또는 claude.ai) 왼쪽 메뉴 {ui('사용자 지정')}(Customize) 클릭", f"{ui('커넥터')} 클릭",
          f"{ui('Google Drive')} 옆 {ui('연결')} → 같은 구글 계정 선택 → 허용", "새 대화에서 아래 프롬프트로 시험"],
         extra=P("1-6 드라이브 연결 시험", "내 구글 드라이브에서 '공부ON_백업' 폴더를 찾아서, 안에 있는 폴더와 파일 개수를 알려줘."),
         ok="Claude가 폴더 5개와 파일 개수를 답하면 성공입니다. 같은 계정으로 로그인한 Claude Code에서도 이 연결을 함께 씁니다.",
         stuck="예전 화면에서는 <b>설정 → 커넥터</b>에 있습니다. '연결됨'인데 못 찾으면 새 대화에서 다시 물어보세요.",
         figure=fig("m1-06", "사용자 지정 → 커넥터 → Google Drive", claude_settings("커넥터",
             '<h5>커넥터</h5>' + mk('<div class="li"><span>🟩 <b>Google Drive</b><br><small>문서·시트·PDF 검색과 읽기</small></span><span class="mbtn p">연결</span></div>', 3, block=True)
             + '<div class="li"><span>✉️ Gmail</span><span class="mini">연결됨</span></div><div class="li"><span>📓 Notion</span><span class="mini">연결됨</span></div>',
             marks={"사용자 지정": 1, "커넥터": 2}))),
    step("1-7", "실제 USB에 적용하기", "연습과 똑같이, 경로만 바꿔 실제 파일을 백업합니다.",
         ["USB를 꽂고 탐색기에서 USB 드라이브 글자 확인(예: E:)", "USB 안 작업 폴더에서 1-2처럼 Claude Code 열기",
          "1-3 프롬프트의 분류 폴더를 <b>내 실제 업무 폴더</b>로 바꿔 실행(예: 01_시간표, 02_상담, 03_홍보, 04_정산서류, 05_지원사업)",
          "1-4 · 1-5 그대로 진행"],
         extra=table(["앞으로의 저장 규칙", "이유"], [
             ["새 작업 파일은 처음부터 G:\\내 드라이브\\공부ON\\ 안에 만든다", "PC가 고장 나도 그대로 남습니다"],
             ["프로젝트(사업)마다 폴더 하나", "Claude에게 '이 폴더 보고 해줘'라고 말하기 쉬워집니다"],
             ["USB는 한 달에 한 번 보조 백업", "드라이브와 USB 두 곳에 남깁니다"],
         ]),
         ok="USB 파일이 드라이브 폴더에 분류되어 들어가고, 개수 대조가 맞으면 완료입니다.", one=True),
    box("ok", "여기까지 배운 것", "Claude Code에게 '먼저 표로 보여줘 → 확인 → 실행 → 숫자로 대조' 순서로 일을 맡기는 법. 이 순서는 다른 모든 작업에도 똑같이 씁니다."),
]), pc_note=PC)

# ═════════════════════════════ 2 크롬 제어 ═════════════════════════════
DAANGN_TEXT = "기말고사 D-30, 시간표는 '빼기'부터"
DAANGN_BODY = "계획이 3일을 못 가는 이유, 학교·학원 시간을\n먼저 빼지 않아서예요. 공부ON은 기말 4주 전부터\n학생별 시간표를 새로 짜 드려요.\n상담: 평일 오후 2시~밤 10시(예약)"
p2 = wrap("".join([
    section("2. 크롬 제어로 채널 배포", "글 한 편으로 4개 채널 · 약 50분"),
    flow([("① 블로그 원고", "내가 씀"), ("② 채널별 문구", "Claude"), ("③ 글쓰기 화면 입력", "Claude가 크롬 조작"), ("④ 검수", "내가"), ("⑤ 발행 클릭", "내가")]),
    box("no", "로그인·비밀번호·발행은 맡기지 않습니다", "각 사이트 로그인은 내가 먼저 해 둡니다. Claude에게 비밀번호를 알려주지 마세요. 게시 버튼은 검수 후 내가 누릅니다."),
    step("2-1", "Claude in Chrome 설치", "크롬에 Claude 확장 프로그램을 설치합니다.",
         [f"크롬에서 {ui('Chrome 웹 스토어')} 열기 → {ui('Claude')} 검색", f"제공자가 {ui('Anthropic')}인지 확인",
          f"{ui('Chrome에 추가')} → {ui('확장 프로그램 추가')}", f"주소창 오른쪽 🧩(퍼즐) → Claude 옆 📌 고정"],
         ok="주소창 오른쪽에 Claude 아이콘이 고정되면 성공입니다.",
         stuck="비슷한 이름의 다른 확장이 많습니다. 반드시 제공자 <b>Anthropic</b>을 확인하세요.",
         figure=fig("m2-01", "Chrome 웹 스토어 → Claude", chrome("Chrome 웹 스토어", "chromewebstore.google.com",
             '<span class="minput">🔍 Claude</span><div class="wsr"><span class="ic2">✳</span><div style="flex:1"><b>Claude</b><br>'
             + mk('<span class="mini">제공: Anthropic</span>', 2) + '</div>' + mk('<span class="mbtn p">Chrome에 추가</span>', 3) + '</div>'))),
    step("2-2", "로그인하고 첫 시험", "옆 창(사이드 패널)에서 Claude가 크롬을 움직이는지 확인합니다.",
         ["Claude 아이콘 클릭 → 오른쪽에 패널 열림", "지금 쓰는 Claude 계정으로 로그인", "아래 프롬프트를 패널에 붙여넣기 → 보내기",
          f"'이 사이트에서 작업해도 될까요?'가 뜨면 {ui('허용')}(Allow) 클릭"],
         extra=P("2-2 크롬 첫 시험", "네이버에서 '공부ON 스터디카페'를 검색해서, 플레이스에 나온 영업시간과 리뷰 개수를 알려줘. 아무것도 클릭해서 바꾸지는 마."),
         ok="Claude가 검색창에 직접 입력하고, 결과를 읽어 영업시간을 답하면 성공입니다. 화면이 저절로 움직이는 게 정상입니다.",
         stuck="패널이 안 열리면 크롬을 완전히 닫았다 다시 여세요. 회사·학교 계정 크롬에서는 확장이 막혀 있을 수 있습니다.",
         figure=fig("m2-02", "사이드 패널에서 요청 → 사이트 허용", chrome("네이버", "search.naver.com",
             '<span class="minput">공부ON 스터디카페</span><div class="li"><span>📍 공부ON 스터디카페<br><small>영업시간 · 리뷰</small></span></div>',
             overlay=sidebar("Claude", mk('<div class="msg">네이버에서 \'공부ON 스터디카페\'를 검색해서…</div>', 3, block=True)
                             + '<div class="msg">search.naver.com 에서 작업해도 될까요?</div>' + mk('<button class="main">허용</button>', 4, block=True))))),
    step("2-3", "채널별 문구 만들기", "블로그 원고 하나로 당근·플레이스·인스타 문구를 한 번에 만듭니다.",
         [f"홈 탭에서 {ui('블로그 원고')} 내려받아 열기 → 전체 복사", "Claude 앱 새 대화에 아래 프롬프트 + 원고 붙여넣기",
          "결과를 <b>채널문구.md</b> 파일로 저장(또는 메모장에 붙여 두기)"],
         extra=P("2-3 채널별 문구", "아래 블로그 원고를 3개 채널용으로 바꿔줘.\n- 당근 소식: 제목 20자 이내 + 본문 300자 이내, 이웃에게 말하듯\n"
                 "- 네이버 플레이스 소식: 400자 이내, 대상·기간·상담 방법을 줄바꿈으로\n- 인스타 캡션: 첫 줄 훅 15자 이내 + 5줄 이내 + 해시태그 5~8개\n"
                 "원고에 없는 숫자나 과장 표현(최고, 100%)은 쓰지 마.\n\n[원고]\n(여기에 붙여넣기)")
         + box("info", "매번 이렇게 길게 써야 하나요?", "아니요. <b>4. 스킬 파일</b> 탭에서 이 지시를 스킬로 저장하면 '당근용으로 바꿔줘' 한마디로 끝납니다."),
         ok="세 채널 문구가 정해진 길이로 나오고, 원고의 상담 시간(평일 오후 2시~밤 10시)이 그대로 들어 있으면 성공입니다.", one=True),
    step("2-4", "Claude Code와 크롬 연결", "명령창의 Claude Code가 크롬을 조작할 수 있게 연결합니다.",
         ["작업 폴더(채널문구.md가 있는 폴더)에서 Claude Code 열기", f"입력칸에 {ui('/chrome')} 입력 → {kbd('Enter')}",
          f"{ui('Enabled by default')} 선택(다음부터 자동 연결)"],
         ok="<code>Chrome extension connected</code>처럼 연결됐다는 문구가 보이면 성공입니다.",
         stuck="'Extension not detected'가 나오면 크롬 확장이 켜져 있는지 확인하고 /chrome → <b>Reconnect extension</b>을 고르세요.",
         figure=fig("m2-03", "/chrome → 연결", term([("raw", mk('<span class="pr">&gt;</span> /chrome', 2)), ("cl", "Claude in Chrome"),
                                                ("cm", "Status: Connected"), ("raw", mk('<span class="cl">❯ Enabled by default</span>', 3)),
                                                ("dim", "  Reconnect extension")], title="Claude Code"))),
    step("2-5", "글쓰기 화면에 입력까지만 맡기기", "Claude가 당근 소식 작성 화면을 열고 제목·본문을 채운 뒤 <b>멈추게</b> 합니다.",
         ["크롬에서 당근 비즈니스(비즈프로필)에 <b>내가 직접 로그인</b>해 두기", "Claude Code에 아래 프롬프트 붙여넣기 → Enter",
          "Claude가 크롬을 움직이는 동안 손대지 않고 지켜보기"],
         extra=P("2-5 당근 소식 입력", "크롬에서 당근 비즈니스의 내 비즈프로필 소식 작성 화면을 열어줘. (로그인은 이미 되어 있어)\n"
                 "채널문구.md 의 [당근 소식] 제목과 본문을 그대로 입력해줘.\n사진은 넣지 말고, 게시(등록) 버튼은 절대 누르지 마.\n입력이 끝나면 멈추고 '입력 완료'라고 알려줘."),
         ok="당근 소식 작성 화면에 제목·본문이 채워지고, Claude가 '입력 완료'라고 멈추면 성공입니다.",
         stuck="보안문자(로봇이 아닙니다)가 나오면 내가 풀고 '계속해줘'라고 말하세요. 메뉴 이름이 달라 못 찾으면 그 화면까지 내가 열어 두고 '지금 화면에 입력해줘'라고 하면 됩니다.",
         figure=fig("m2-04", "Claude가 채워 둔 당근 소식", chrome("당근 비즈니스", "business.daangn.com",
             '<b>소식 작성</b><div class="lb">제목</div>' + f'<div class="minput" style="color:#202124">{E(DAANGN_TEXT)}</div>'
             + f'<div class="lb">본문</div><div class="ta">{E(DAANGN_BODY)}</div>'
             + '<div style="margin-top:8px;display:flex;gap:6px;justify-content:space-between"><span class="mbtn">📷 사진</span><span class="mbtn p" style="background:#ff6f0f;border-color:#ff6f0f">게시하기</span></div>'))),
    step("2-6", "검수하고 내가 발행", "마지막 확인과 발행은 사람이 합니다.",
         ["제목·본문을 채널문구.md와 비교", "날짜·시간·가격이 원고와 같은지 확인", f"{ui('📷 사진')}으로 카드뉴스 이미지 직접 첨부", f"{ui('게시하기')}(등록) 클릭"],
         ok="당근 비즈프로필 소식에 글이 올라가면 완료입니다.",
         figure=fig("m2-05", "사진 첨부 → 게시", chrome("당근 비즈니스", "business.daangn.com",
             '<b>소식 작성</b><div class="lb">제목</div>' + mk(f'<div class="minput" style="color:#202124">{E(DAANGN_TEXT)}</div>', 1, block=True)
             + f'<div class="lb">본문</div>' + mk(f'<div class="ta">{E(DAANGN_BODY)}</div>', 2, block=True)
             + '<div style="margin-top:8px;display:flex;gap:6px;justify-content:space-between">' + mk('<span class="mbtn">📷 사진</span>', 3)
             + mk('<span class="mbtn p" style="background:#ff6f0f;border-color:#ff6f0f">게시하기</span>', 4) + '</div>'))),
    step("2-7", "플레이스·인스타에도 적용", "같은 방식으로 다른 채널도 '입력까지만' 맡깁니다.",
         ["네이버 스마트플레이스에 로그인 → 아래 프롬프트로 소식 입력", "인스타그램은 Meta 비즈니스 수트(웹)에서 게시물 만들기 화면까지 맡기기", "각 채널 2-6처럼 검수 → 발행"],
         extra=P("2-7 플레이스 소식 입력", "크롬에서 네이버 스마트플레이스의 내 업체 '소식' 새 글 작성 화면을 열어줘.\n"
                 "채널문구.md 의 [네이버 플레이스 소식] 본문을 입력하고, 등록 버튼은 누르지 말고 멈춰줘.")
         + box("info", "다음 단계: 정해진 요일에 자동으로", "입력까지 맡기는 흐름이 2~3주 안정적으로 돌아가면, 그다음에 '매주 월요일 오전 10시에 이번 주 원고로 입력해 두기' 같은 예약 실행을 붙입니다. "
               "처음부터 예약하면 화면이 바뀌었을 때 엉뚱한 글이 들어갈 수 있습니다."),
         ok="두 채널 이상에서 '입력 → 검수 → 내가 발행'을 한 번씩 해 보면 완료입니다.",
         stuck="메뉴 위치는 사이트 업데이트로 자주 바뀝니다. 못 찾으면 작성 화면까지 내가 열고 '지금 화면에 입력해줘'로 바꾸세요.", one=True),
    box("ok", "여기까지 배운 것", "원고 → 채널 문구 → 입력은 Claude, 검수와 발행은 나. 채널마다 직접 접속해서 붙여넣던 시간이 확인 시간으로 줄어듭니다."),
]), pc_note=PC)

# ═════════════════════════════ 3 MCP ═════════════════════════════
MIRI_URL = "https://mcp.miricanvas.com/mcp"
p3 = wrap("".join([
    section("3. MCP로 미리캔버스 연결", "대화로 카드뉴스 시안 만들기 · 약 40분"),
    step("3-1", "MCP가 뭔가요?", "Claude와 다른 서비스를 잇는 '연결 플러그'라고 이해하면 충분합니다.",
         ["아래 그림으로 구조 이해하기", "캔바·노션처럼 유명한 서비스는 커넥터 목록에 이미 있음", "미리캔버스처럼 새로 나온 서비스는 <b>주소를 직접 넣어</b> 추가(커스텀 커넥터)"],
         extra=flow([("나", "카드뉴스 만들어줘"), ("Claude", "내용·구성 기획"), ("MCP(연결)", "미리캔버스에 전달"), ("미리캔버스", "디자인 생성")])
         + table(["구분", "예", "연결 방법"], [["기본 커넥터", "Google Drive, Gmail, Notion, Canva", "목록에서 '연결' 클릭"],
                                           ["커스텀 커넥터", "미리캔버스", "이름 + MCP 주소 직접 입력"]]),
         ok="'미리캔버스는 주소를 직접 넣어야 한다'만 기억하면 됩니다.", one=True),
    step("3-2", "커스텀 커넥터 추가", "Claude에 미리캔버스 연결 주소를 등록합니다.",
         [f"Claude 왼쪽 메뉴 {ui('사용자 지정')}(Customize) 클릭", f"{ui('커넥터')} 클릭", f"{ui('＋')} → {ui('커스텀 커넥터 추가')} 클릭",
          f"이름 {ui('MiriCanvas')}, 주소에 아래 URL 붙여넣기", f"{ui('추가')} 클릭"],
         extra=code_block("미리캔버스 MCP 주소", text=MIRI_URL + "\n", cid="c-miri"),
         ok="커넥터 목록에 <b>MiriCanvas</b>가 생기면 성공입니다.",
         stuck="무료 플랜은 커스텀 커넥터를 1개까지만 추가할 수 있습니다. 대표님 요금제(Max)는 해당 없습니다.",
         figure=figs(fig("m3-01", "사용자 지정 → 커넥터 → ＋", claude_settings("커넥터",
                         '<div style="display:flex;justify-content:space-between"><h5>커넥터</h5>' + mk('<span class="mbtn">＋</span>', 3) + '</div>'
                         + '<div class="li"><span>🟩 Google Drive</span><span class="mini">연결됨</span></div><div class="li"><span>🎨 Canva</span><span class="mbtn">연결</span></div>',
                         marks={"사용자 지정": 1, "커넥터": 2})),
                     fig("m3-02", "이름·주소 입력 → 추가", claude_settings("커넥터", "<h5>커넥터</h5>", overlay=dialog("커스텀 커넥터 추가",
                         '<div class="lb">이름</div>' + mk('<span class="minput" style="color:#202124">MiriCanvas</span>', 4, block=True)
                         + f'<div class="lb">원격 MCP 서버 URL</div><span class="minput" style="color:#202124">{E(MIRI_URL)}</span>',
                         gbtn("취소") + gbtn("추가", True, 5)))))),
    step("3-3", "미리캔버스 로그인·승인", "Claude가 내 미리캔버스 계정에 디자인을 만들 수 있게 허락합니다.",
         [f"MiriCanvas 옆 {ui('연결')} 클릭", "새 창에서 <b>쓰던 미리캔버스 계정</b>으로 로그인", "디자인을 저장할 워크스페이스 선택", f"{ui('허용')} 클릭"],
         ok="Claude 커넥터 목록에서 MiriCanvas가 <b>연결됨</b>으로 바뀌면 성공입니다.",
         stuck="새 창이 안 뜨면 브라우저 주소창 오른쪽의 '팝업 차단됨' 아이콘에서 허용하세요.",
         figure=fig("m3-03", "워크스페이스 선택 → 허용", app_window("미리캔버스 — 연결 승인",
             '<b>Claude가 미리캔버스에 접근하려고 합니다</b><div class="lb">디자인을 저장할 워크스페이스</div>'
             + mk('<span class="minput" style="color:#202124">공부ON 워크스페이스 ▾</span>', 3, block=True)
             + '<div class="mini" style="margin:8px 0">· 디자인 만들기 · 내 디자인 보기</div>'
             + '<div style="text-align:right"><span class="mbtn">취소</span> ' + mk('<span class="mbtn p">허용</span>', 4) + '</div>', icon_color="#17b5b0"))),
    step("3-4", "대화로 카드뉴스 시안 만들기", "Claude에게 기획과 디자인 생성을 함께 맡깁니다.",
         ["Claude 새 대화 열기", f"입력창의 {ui('＋')}(또는 🔧 도구) → {ui('MiriCanvas')} 켜져 있는지 확인", "아래 프롬프트 붙여넣기 → 보내기",
          "답변의 미리캔버스 링크 열기 → 글자·사진은 미리캔버스에서 직접 다듬기"],
         extra=P("3-4 카드뉴스 시안", "미리캔버스로 인스타그램 카드뉴스(정사각형) 5장 시안을 만들어줘.\n주제: 기말고사 D-30, 공부 시간표는 '빼기'부터\n"
                 "대상: 고등학생 학부모\n구성: 1장 표지 / 2~4장 핵심 내용 / 5장 상담 안내(평일 오후 2시~밤 10시, 예약제)\n"
                 "톤: 차분하고 신뢰감 있게. 과장 표현과 원고에 없는 숫자는 넣지 마."),
         ok="Claude가 미리캔버스 디자인 링크를 주고, 링크를 열면 5장짜리 시안이 내 워크스페이스에 있으면 성공입니다.",
         stuck="'도구를 사용할 수 없습니다'가 나오면 새 대화를 열고 ＋에서 MiriCanvas가 켜져 있는지 다시 확인하세요.",
         figure=fig("m3-04", "MiriCanvas를 켜고 요청", chat_view([("user", "미리캔버스로 인스타그램 카드뉴스 5장 시안을 만들어줘…"),
                                                           ("ai", "🎨 MiriCanvas 사용 중… 5장 시안을 만들었습니다. [미리캔버스에서 열기]")],
                                                          input_text="＋  MiriCanvas ●", marks={0: 3, 1: 4, "input": 2}))),
    step("3-5", "Claude Code에서도 쓰기(선택)", "명령창에서도 같은 연결을 쓸 수 있는지 확인합니다.",
         [f"Claude Code에서 {ui('/mcp')} 입력 → 목록에 MiriCanvas가 있는지 확인", "없으면 PowerShell에서 아래 명령 실행 후 claude 다시 실행",
          f"{ui('/mcp')} → MiriCanvas → {ui('Authenticate')} → 브라우저에서 로그인·허용"],
         extra=code_block("Claude Code에 미리캔버스 추가", text=f"claude mcp add --transport http miricanvas {MIRI_URL}\n", cid="c-miri-cli"),
         ok="/mcp 목록에 miricanvas가 <b>connected</b>로 보이면 성공입니다.",
         figure=fig("m3-05", "/mcp 목록", term([("raw", mk('<span class="pr">&gt;</span> /mcp', 1)), ("cl", "Manage MCP servers"),
                                              ("out", "  claude.ai Google Drive   ✔ connected"), ("out", "  claude.ai MiriCanvas     ✔ connected"),
                                              ("dim", "  (Esc로 닫기)")], title="Claude Code"))),
    step("3-6", "연결이 안 될 때 (캔바 실패 경험 정리)", "예전 캔바 연결이 실패했던 흔한 원인을 순서대로 확인합니다.",
         ["아래 표의 위에서부터 하나씩 확인"],
         extra=table(["증상", "흔한 원인", "해결"], [
             ["추가 버튼이 안 눌림", "주소 앞뒤 공백, http/https 오타", "교안의 주소를 <b>전체 복사</b>로 다시 붙여넣기"],
             ["로그인 창이 안 뜸", "팝업 차단", "주소창 오른쪽 팝업 아이콘 → 항상 허용"],
             ["연결됨인데 대화에서 안 씀", "대화의 도구 목록에서 꺼져 있음", "새 대화 → ＋ → 커넥터 켜기"],
             ["다른 계정 디자인이 안 보임", "다른 미리캔버스 계정으로 승인", "커넥터 연결 해제 → 다시 연결해서 맞는 계정으로"],
             ["Claude Code에서만 안 됨", "인증 안 됨", "/mcp → Authenticate"],
         ], raw=True), ok="표대로 확인하면 대부분 해결됩니다. 그래도 안 되면 화면을 캡처해서 멘토에게 보내 주세요.", one=True),
    box("ok", "여기까지 배운 것", "목록에 없는 서비스도 'MCP 주소'만 있으면 Claude에 연결할 수 있습니다. 앞으로 새 서비스가 'MCP 지원'이라고 하면 같은 방법으로 붙이면 됩니다."),
]), pc_note=PC)

# ═════════════════════════════ 4 스킬 파일 ═════════════════════════════
SKILL_DIR = OUT / "practice" / "skill_example" / "gongbuon-channel-post"
p4 = wrap("".join([
    section("4. 스킬 파일 만들기", "매번 어긋나던 지시를 파일 하나로 고정 · 약 60분"),
    step("4-1", "스킬이란?", "자주 하는 일의 '작업 지시서'를 파일로 저장해 두고 꺼내 쓰는 기능입니다.",
         ["아래 비교표 읽기", "내 업무 중 '매번 같은 지시를 다시 쓰는 일'을 하나 떠올리기"],
         extra=table(["방식", "어떻게", "문제점 / 장점"], [
             ["매번 프롬프트 입력", "대화마다 지시를 새로 붙여넣기", "조금씩 달라져서 결과가 어긋남"],
             ["프로젝트 지침", "프로젝트 안 대화에만 적용", "그 프로젝트 밖에서는 안 됨"],
             ["<b>스킬</b>", "SKILL.md 파일 하나로 저장", "<b>어느 대화에서든</b> 필요할 때 자동으로 불려 와 같은 순서·형식으로 처리"],
         ], raw=True)
         + box("info", "대표님 사례", "블로그 → 당근·플레이스 축약을 할 때마다 지침을 새로 쓰고 결과가 달라 다시 요청했던 일. 이것이 스킬로 만들기 가장 좋은 일입니다."),
         ok="'반복되는 일 + 정해진 순서 + 정해진 결과 형식'이면 스킬 후보라는 것을 이해하면 됩니다.", one=True),
    step("4-2", "스킬 파일의 구조", "완성된 스킬 파일 한 장을 보며 각 부분의 역할을 익힙니다.",
         ["아래 완성 예시를 위에서부터 읽기", "특히 맨 위 <b>description</b>(설명) 줄 확인 — Claude는 이 줄을 보고 언제 이 스킬을 쓸지 판단합니다"],
         extra=table(["부분", "역할", "쓰는 요령"], [
             ["name", "스킬 이름(영문 소문자·하이픈)", "폴더 이름과 똑같이"],
             ["description", "<b>언제</b> 이 스킬을 쓰는지", "내가 실제로 하는 말을 따옴표로 2~3개 넣기"],
             ["작업 순서", "A → B → C 순서", "번호를 붙여 짧게"],
             ["규칙 / 지킬 것", "길이·말투·금지 표현", "표로 쓰면 덜 어긋납니다"],
             ["결과 형식", "결과물의 모양", "실제 결과처럼 틀을 그대로"],
         ], raw=True) + code_block("완성 예시: gongbuon-channel-post/SKILL.md", path=SKILL_DIR / "SKILL.md", cid="c-skill",
                                    download_href="practice/gongbuon-channel-post.zip", tall=True, wrap=True),
         ok="SKILL.md는 <b>맨 위 이름·설명 + 아래 작업 지시서</b>로 되어 있다는 것을 알면 됩니다.", one=True),
    step("4-3", "방법 ① 대화로 만들기 (추천)", "결과가 잘 나온 대화에서 '방금 한 걸 스킬로 만들어줘'라고 부탁합니다.",
         ["2-3에서 채널 문구가 마음에 들게 나온 대화로 돌아가기(여러 번 고쳤다면 그 대화가 가장 좋습니다)", "아래 프롬프트 붙여넣기 → 보내기",
          "Claude가 만든 SKILL.md 내용 확인 → 빠진 규칙이 있으면 말로 추가", f"{ui('다운로드')}(또는 파일 저장)로 스킬 파일(zip) 받기"],
         extra=P("4-3 대화로 스킬 만들기", "지금까지 이 대화에서 블로그 원고를 당근·플레이스·인스타 문구로 바꾼 과정을 스킬 파일로 만들어줘.\n"
                 "- 스킬 이름: gongbuon-channel-post\n- 내가 중간에 고쳐 달라고 한 내용도 모두 규칙에 넣어줘\n"
                 "- description에는 내가 실제로 할 말(예: '당근용으로 바꿔줘')을 넣어줘\n- 업로드할 수 있게 폴더째 zip으로 만들어줘"),
         ok="Claude가 SKILL.md 내용을 보여 주고 zip 파일을 내려받을 수 있게 주면 성공입니다.",
         stuck="zip이 안 나오면 'SKILL.md 내용만 보여줘'라고 한 뒤, 4-4처럼 직접 파일로 저장해도 됩니다.",
         figure=fig("m4-01", "잘 된 대화에서 스킬로 만들기", chat_view([("user", "지금까지 이 대화에서 블로그 원고를 … 스킬 파일로 만들어줘."),
                                                             ("ai", "스킬 파일을 만들었습니다.\n📦 gongbuon-channel-post.zip  [다운로드]\n• 작업 순서 3단계 • 채널 규칙 표 • 금지 표현 4개")],
                                                            marks={0: 2, 1: 4}))),
    step("4-4", "방법 ② 양식으로 직접 쓰기", "빈 양식에 내 업무 순서를 채워 넣어 처음부터 만듭니다.",
         [f"홈 탭에서 {ui('빈 스킬 양식')} 내려받기 → 메모장으로 열기", "[대괄호] 부분을 내 업무에 맞게 바꾸기",
          f"폴더 하나 만들고(이름 = name과 똑같이) 그 안에 {ui('SKILL.md')} 이름으로 저장", f"폴더에 마우스 오른쪽 → {ui('압축(ZIP) 폴더')}로 압축"],
         extra=code_block("빈 스킬 양식", path=OUT / "practice" / "skill_template.md", cid="c-tpl", download_href="practice/skill_template.md", wrap=True)
         + box("warn", "저장할 때 주의", "메모장에서 '다른 이름으로 저장' → 파일 형식 <b>모든 파일</b> → 이름 <b>SKILL.md</b>, 인코딩 <b>UTF-8</b>. 그렇지 않으면 SKILL.md.txt가 되어 인식되지 않습니다. "
               "zip 안에는 SKILL.md가 바로 있으면 안 되고 <b>폴더째</b> 들어 있어야 합니다."),
         ok="<code>gongbuon-consult-summary.zip</code> 안에 <code>gongbuon-consult-summary/SKILL.md</code>가 들어 있으면 성공입니다.", one=True),
    step("4-5", "등록 ① Claude 앱(대화창)", "만든 스킬을 Claude 앱에 올립니다.",
         [f"왼쪽 메뉴 {ui('사용자 지정')}(Customize) 클릭", f"{ui('스킬')} 클릭", f"{ui('＋')} → {ui('스킬 업로드')} 클릭",
          f"zip 파일 선택(연습: 홈 탭 {ui('완성 스킬(업로드용)')})", "목록에 생긴 스킬이 <b>켜짐</b>인지 확인"],
         ok="스킬 목록에 <b>gongbuon-channel-post</b>가 켜진 상태로 보이면 성공입니다.",
         stuck="예전 화면에서는 <b>설정 → 기능 → 스킬</b>에 있습니다. 업로드 오류는 대부분 zip 구조(폴더째 압축 여부)나 name·폴더 이름 불일치입니다.",
         figure=fig("m4-02", "사용자 지정 → 스킬 → 업로드", claude_settings("스킬",
             '<div style="display:flex;justify-content:space-between"><h5>스킬</h5>' + mk('<span class="mbtn">＋ 스킬 업로드</span>', 3) + '</div>'
             + mk('<div class="li"><span>🧩 <b>gongbuon-channel-post</b><br><small>블로그 원고 → 당근·플레이스·인스타</small></span><span class="tg"></span></div>', 5, block=True)
             + '<div class="li"><span>🧩 skill-creator<br><small>기본 제공</small></span><span class="tg"></span></div>',
             marks={"사용자 지정": 1, "스킬": 2}))),
    step("4-6", "등록 ② Claude Code(명령창)", "명령창에서도 같은 스킬을 쓰도록 내 PC의 스킬 폴더에 넣습니다.",
         ["압축을 푼 스킬 폴더가 있는 곳에서 Claude Code 열기", "아래 프롬프트 붙여넣기 → Enter (허락을 물으면 1. Yes)",
          f"{ui('/exit')}로 나왔다가 {ui('claude')}로 다시 실행", f"입력칸에 {ui('/')}만 입력 → 목록에 {ui('/gongbuon-channel-post')}가 보이는지 확인"],
         extra=P("4-6 Claude Code에 스킬 설치", "이 폴더의 gongbuon-channel-post 폴더를 내 개인 스킬로 설치해줘.\n"
                 "위치는 내 사용자 폴더의 .claude\\skills\\ 아래야. 설치 후 경로와 SKILL.md 첫 5줄을 보여줘.")
         + box("info", "직접 넣고 싶다면", "탐색기 주소창에 <code>%USERPROFILE%\\.claude\\skills</code> 입력 → 그 안에 스킬 폴더를 통째로 복사하면 됩니다(폴더가 없으면 만들기)."),
         ok="<code>/</code> 목록에 <b>gongbuon-channel-post</b>가 나오면 성공입니다.",
         figure=fig("m4-03", "/ 입력 → 스킬 목록", term([("raw", mk('<span class="pr">&gt;</span> /', 4)), ("cl", "  /gongbuon-channel-post   블로그 원고를 당근·플레이스·인스타…"),
                                                      ("dim", "  /chrome                  Claude in Chrome 설정"), ("dim", "  /mcp                     MCP 서버 관리")], title="Claude Code"))),
    step("4-7", "불러 쓰기 (자동 · 직접)", "스킬이 실제로 불려 와 같은 형식으로 결과가 나오는지 확인합니다.",
         ["<b>자동</b>: 새 대화에 '이 블로그 글 당근이랑 플레이스용으로 바꿔줘' + 원고 붙여넣기", "답변 위에 스킬 사용 표시가 나오는지 확인",
          f"<b>직접</b>(Claude Code): {ui('/gongbuon-channel-post')} 입력 → 원고 파일 이름 알려주기", "결과 맨 끝 [검수 체크] 표 확인"],
         extra=P("4-7 스킬 자동 호출 시험", "이 블로그 글 당근이랑 플레이스, 인스타용으로 바꿔줘.\n\n(여기에 블로그 원고 붙여넣기)"),
         ok="길게 지시하지 않았는데도 [당근 소식] / [네이버 플레이스 소식] / [인스타그램 캡션] / [검수 체크] 순서로 나오면 성공입니다.",
         stuck="스킬이 안 불려 오면 description에 내가 한 말과 비슷한 표현이 있는지 확인하고, 직접 호출로 먼저 써 보세요.",
         figure=fig("m4-04", "스킬이 자동으로 불려 온 대화", chat_view([("user", "이 블로그 글 당근이랑 플레이스, 인스타용으로 바꿔줘. …"),
                                                             ("ai", "🧩 gongbuon-channel-post 사용 중\n[당근 소식]\n제목: 기말고사 D-30, 시간표는 '빼기'부터\n…\n[검수 체크] 상담 시간 ✔ 과장 표현 없음 ✔")],
                                                            marks={0: 1, 1: 2}))),
    step("4-8", "시험하고 고치기", "다른 원고로 다시 돌려 보고, 어긋난 부분을 규칙으로 추가합니다.",
         ["블로그 원고를 <b>다른 글</b>로 바꿔 4-7을 한 번 더", "마음에 안 드는 부분을 아래 프롬프트처럼 '규칙 추가'로 요청",
          "Claude Code에서는 Claude가 SKILL.md를 바로 고침 / Claude 앱에서는 고친 zip을 다시 업로드(같은 이름이면 교체)", "다시 시험 → 같은 문제가 안 나오면 완료"],
         extra=P("4-8 스킬 규칙 추가", "gongbuon-channel-post 스킬에 규칙을 추가해줘.\n- 당근 본문 마지막 줄은 항상 '상담 예약은 채팅으로 편하게 주세요 :)'\n"
                 "- 인스타 해시태그에 #공부ON 은 항상 맨 앞\n고친 뒤 바뀐 부분만 보여줘."),
         ok="두 번째 원고에서도 형식이 똑같이 나오고, 추가한 규칙이 반영되면 완료입니다.", one=True),
    step("4-9", "내 업무 스킬 후보", "오늘 만든 방식 그대로 다음 스킬을 골라 만듭니다.",
         ["아래 표에서 가장 자주 하는 일 1개 고르기", "4-3(대화로) 또는 4-4(양식으로)로 만들기"],
         extra=table(["스킬 후보", "이럴 때 부름", "들어갈 규칙 예"], [
             ["학사 일정별 홍보 문구", "'중간고사 3주 전 홍보 문구 써줘'", "시기별 메시지, 채널별 길이"],
             ["상담 요약 기록", "'이 상담 녹취 정리해줘'", "5-6의 기록 양식, 이탈 신호 기준"],
             ["학부모 안내 카톡", "'12월 등록 안내 카톡 써줘'", "인사말, 결제 링크 위치, 마감일 표기"],
             ["수납 대조", "'이번 달 수납 대조해줘'", "5-2의 대조 규칙, 확인 필요 기준"],
             ["카드뉴스 기획", "'카드뉴스 기획해줘'", "5장 구성, 톤, 미리캔버스로 만들기"],
         ]), ok="스킬 1개를 더 만들어 목록에 2개 이상이 되면 이 탭은 완료입니다.", one=True),
    box("ok", "여기까지 배운 것", "스킬 = 이름·설명 + 작업 지시서. 잘 된 대화를 스킬로 굳히고, 어긋날 때마다 규칙을 한 줄씩 추가하면 결과가 점점 일정해집니다."),
]), pc_note=PC)

# ═════════════════════════════ 5 업무 자동화 ═════════════════════════════
p5 = wrap("".join([
    section("5. 업무 자동화 활용", "수납 대조 · 상담 기록 · 약 50분"),
    "<h3>A. 결제 내역 3종 → 수납 대조표</h3>",
    flow([("결제선생", "엑셀 내려받기"), ("토스 POS", "엑셀 내려받기"), ("계좌이체", "거래내역 내려받기"), ("Claude Code", "학생별 대조"), ("나", "확인 필요만 확인")]),
    box("info", "API 연동과의 관계", "개발사에 문의 중인 결제 API 연동이 되면 이 작업이 플랫폼 안에서 자동으로 됩니다. 그 전까지는 <b>매달 파일 3개를 내려받아 Claude에게 맡기는 방법</b>으로 대조 시간을 줄입니다."),
    step("5-1", "결제 내역 내려받기", "세 곳의 결제 기록을 파일로 받아 한 폴더에 모읍니다.",
         [f"연습: 홈 탭 {ui('결제 내역 3종 + 명단')} 내려받기 → 압축 풀기", "실제: 결제선생 관리자 화면 → 결제 내역 → 엑셀 다운로드",
          "실제: 토스 POS(토스 플레이스) 매출 내역 → 엑셀 내보내기 / 은행 인터넷뱅킹 → 거래내역 → 엑셀 저장",
          "네 파일(명단 포함)을 <b>G:\\내 드라이브\\공부ON\\04_정산서류\\2026-12_수납</b> 한 폴더에 넣기"],
         ok="폴더에 <b>재원생_명단 · 결제선생_내역 · 토스POS_내역 · 계좌이체_내역</b> 4개 파일이 있으면 성공입니다.",
         stuck="메뉴 이름은 서비스마다 다릅니다. '내역', '매출', '엑셀', '다운로드' 단어를 찾으세요.",
         figure=fig("m5-01", "한 폴더에 모은 4개 파일", explorer("Google Drive (G:) › 내 드라이브 › 공부ON › 04_정산서류 › 2026-12_수납", "Google Drive (G:)",
                                                            ["📄 재원생_명단.csv", "📄 결제선생_내역.csv", "📄 토스POS_내역.csv", "📄 계좌이체_내역.csv"]))),
    step("5-2", "수납 대조표 만들기", "Claude Code가 세 파일을 합쳐 학생별로 냈는지 안 냈는지 표를 만듭니다.",
         ["그 폴더에서 Claude Code 열기(1-2 방법)", "아래 프롬프트 붙여넣기 → Enter", "명령 실행 허락은 내용 확인 후 1. Yes", "만들어진 <b>수납대조표.xlsx</b> 열기"],
         extra=P("5-2 수납 대조표", "이 폴더의 결제 파일 3개(결제선생, 토스POS, 계좌이체)와 재원생_명단을 대조해서\n12월 수납 대조표 엑셀(수납대조표.xlsx)을 만들어줘.\n\n"
                 "[대조 규칙]\n- 결제선생: 학생이름으로 매칭, 상태가 결제완료인 것만 입금으로\n- 토스POS: 메모에 학생 이름이 있으면 매칭\n"
                 "- 계좌이체: 입금자명에 학생 또는 학부모 이름이 들어 있으면 매칭\n- 상태: 완납 / 부분납 / 결제대기 / 미납\n"
                 "- 누구 것인지 모르는 거래는 '확인 필요' 시트에 따로\n\n[열] 학생명, 학부모명, 청구액, 입금액, 남은 금액, 결제 경로, 상태\n"
                 "원본 파일은 수정하지 마. 끝나면 상태별 인원 수를 알려줘.")
         + code_block("정답 확인용 예시 코드(직접 실행할 필요 없음)", path=OUT / "code" / "reconcile.py", cid="c-recon", download_href="code/reconcile.py"),
         ok="연습 파일 기준 <b>완납 8명 · 부분납 1명 · 결제대기 1명 · 미납 2명 · 확인 필요 거래 1건</b>이 나오면 성공입니다.",
         stuck="인원이 다르면 'OOO은 왜 미납이야?'라고 물어보세요. Claude가 어떤 기록을 봤는지 설명하고 규칙을 고칩니다.",
         figure=fig("m5-02", "만들어진 수납대조표", app_window("수납대조표.xlsx — Excel", grid([
             ["학생명", "청구액", "입금액", "결제 경로", "상태"], ["김하늘", "280,000", "280,000", "결제선생", "완납"],
             ["강시우", "340,000", "340,000", "토스POS", "완납"], ["장서연", "280,000", "0", "-", "결제대기"],
             ["임준우", "340,000", "0", "-", "미납"], ["한소율", "280,000", "140,000", "계좌이체", "부분납"]],
             colors={3: "#fff4d6", 4: "#fde2e1", 5: "#fff4d6"}), icon_color="#107c41"))),
    step("5-3", "'확인 필요'만 사람이 확인", "Claude가 판단하지 못한 거래만 내가 봅니다.",
         ["'확인 필요' 시트 열기", "연습 파일: <b>토스POS 11. 27. 20:48, 340,000원, 메모 없음</b>", "같은 금액(340,000원) 미납 학생이 <b>2명</b>(임준우·오태윤)이라 금액만으로는 알 수 없음 → 카드 승인 시간·CCTV·학부모 확인으로 판단",
          "확인되면 '토스 340,000원은 임준우 결제야. 표 고쳐줘'라고 말하기"],
         extra=box("ok", "재발 방지 규칙", "POS 결제 때 <b>메모에 학생 이름</b>을 꼭 입력하고, 계좌이체 안내 문자에 '입금자명은 학생 이름으로'를 넣으면 다음 달에는 확인 필요가 거의 사라집니다."),
         ok="확인 필요 거래가 0건이 되면 이번 달 대조 완료입니다.", one=True),
    step("5-4", "매달 쓰는 스킬로 만들기", "이번 대조 과정을 스킬로 저장해 다음 달엔 한 줄로 끝냅니다.",
         ["대조가 끝난 같은 Claude Code 대화에서 아래 프롬프트 입력", "4-6처럼 스킬 폴더에 설치됐는지 / 목록에서 확인", "다음 달: 파일 4개 넣고 '이번 달 수납 대조해줘'"],
         extra=P("5-4 수납 대조 스킬", "방금 한 수납 대조 과정을 'gongbuon-monthly-payment' 스킬로 만들어서 내 개인 스킬 폴더에 설치해줘.\n"
                 "내가 중간에 고친 규칙과 '확인 필요' 처리 방식도 넣어줘."),
         ok="다음 달에는 프롬프트 없이 '이번 달 수납 대조해줘' 한 줄로 같은 표가 나옵니다.", one=True),
    "<h3>B. 상담 녹음 → 상담 기록 데이터</h3>",
    flow([("상담", "녹음(동의)"), ("클로바노트", "텍스트 변환"), ("Claude", "양식대로 요약"), ("상담기록", "한 줄씩 누적"), ("직원", "같은 기록 공유")]),
    box("no", "녹음 전 꼭", "학부모·학생에게 <b>녹음 사실을 알리고 동의</b>를 받습니다. 미성년 학생 정보가 들어가므로 기록 파일은 드라이브의 비공개 폴더에만 두고, 공유는 필요한 직원에게만 합니다."),
    step("5-5", "녹음을 텍스트로", "상담 음성을 글로 바꿉니다.",
         ["휴대폰 클로바노트 앱에서 녹음(또는 통화 녹음 파일 업로드)", "변환이 끝나면 텍스트 내보내기(.txt) → 드라이브 02_상담 폴더에 저장",
          f"연습: 홈 탭 {ui('상담 녹취')} 내려받기"],
         ok="상담 내용이 텍스트 파일로 저장되면 성공입니다.", one=True),
    step("5-6", "양식대로 요약해 기록 쌓기", "Claude가 정해진 칸에 맞춰 요약하고, 상담기록 파일에 한 줄씩 추가합니다.",
         ["02_상담 폴더에서 Claude Code 열기", "아래 프롬프트 붙여넣기 → Enter", "요약 내용 확인 → 틀린 곳은 말로 고치기", "상담기록.csv(엑셀로 열림)에 한 줄 추가됐는지 확인"],
         extra=P("5-6 상담 요약 기록", "consult_transcript.txt 상담 녹취를 아래 양식으로 요약해서 상담기록.csv 맨 아래에 한 줄 추가해줘. 파일이 없으면 새로 만들어.\n\n"
                 "[열] 상담일 | 학생(가명) | 상담 대상 | 이탈 신호 | 원인 | 합의한 조치 | 시간표 변경 | 다음 확인일 | 등록 의사\n\n"
                 "[규칙]\n- 녹취에 없는 내용은 추측하지 말고 '언급 없음'\n- 날짜는 2026. 11. 20.(금) 형식\n- 학부모 이름·연락처는 쓰지 마"),
         ok="한 줄에 <b>지각 3회(2주) · 수학학원 종료 30분 늦어짐 · 화·목 등원 20:30, 토 오전 2시간 추가 · 매일 첫 20분 영어 단어 · 다음 확인 2026. 11. 27.(금) · 12월 등록 예정</b>이 들어가면 성공입니다.",
         stuck="날짜가 틀리면 '다음 주 금요일은 11. 27.이야'처럼 바로잡고, 이 규칙을 4-9의 '상담 요약 기록' 스킬에 넣으세요.",
         figure=fig("m5-03", "상담기록에 쌓인 한 줄", app_window("상담기록.csv — Excel", grid([
             ["상담일", "학생", "이탈 신호", "합의한 조치", "다음 확인"],
             ["2026. 11. 20.(금)", "가온", "지각 3회/2주", "화·목 20:30 등원, 토 +2h, 단어 20분", "11. 27.(금)"]]), icon_color="#107c41"))),
    step("5-7", "직원과 함께 쓰기", "종이 대신 드라이브 기록을 직원과 공유합니다.",
         ["드라이브에서 02_상담 폴더 마우스 오른쪽 → 공유", "직원 구글 계정만 추가(링크 공개 금지)", "직원에게 '상담 전 이 학생 기록 요약해줘'로 Claude에게 묻는 법 알려주기"],
         ok="직원이 같은 기록을 보고 이어서 상담할 수 있으면 완료입니다.", one=True),
]), pc_note=PC)

# ═════════════════════════════ AI 활용 ═════════════════════════════
pai = wrap("".join([
    section("AI에게 잘 맡기는 법", "줘도 되는 것 · 주면 안 되는 것 · 고치는 말"),
    box("ok", "✅ 줘도 되는 것", "블로그 원고, 홍보 문구, 시간표 규칙, 가상 예시, 파일·폴더 이름, 오류 메시지 전체"),
    box("no", "⛔ 주면 안 되는 것", "비밀번호·인증번호, 카드번호, 학생·학부모 실명과 연락처를 묶은 명단(웹 대화창), 주민번호. 내 PC 안의 파일을 Claude Code로 처리할 때도 결과물을 외부에 올리기 전에 이름을 가리세요."),
    box("info", "💡 요령", "① 먼저 계획·표를 보여 달라고 하기 ② 원본은 건드리지 말라고 하기 ③ 끝나면 숫자로 확인시키기 ④ 잘 되면 스킬로 저장하기"),
    section("상황별 프롬프트"),
    "<h3>새 작업 맡기기</h3>",
    P("AI 새 작업", "[하고 싶은 일]을 하고 싶어.\n바로 실행하지 말고, 어떤 순서로 할지 계획을 먼저 보여줘.\n내가 '진행해'라고 하면 시작하고, 원본 파일은 수정하지 마."),
    "<h3>오류가 났을 때</h3>",
    P("AI 오류 해결", "아래 오류가 났어. 원인을 쉬운 말로 설명하고, 내가 할 일과 네가 할 일을 나눠서 알려줘.\n\n[오류 메시지 전체]\n(여기에 붙여넣기)"),
    "<h3>결과를 고칠 때</h3>",
    P("AI 결과 수정", "방금 결과에서 [고칠 부분]만 바꿔줘. 나머지는 그대로 두고, 바뀐 부분만 보여줘."),
    "<h3>결과가 맞는지 확인할 때</h3>",
    P("AI 검수", "방금 결과를 원본과 비교해서 날짜·시간·금액·이름이 하나라도 다른 곳이 있는지 표로 보여줘."),
    "<h3>반복되는 일을 굳힐 때</h3>",
    P("AI 스킬로 저장", "방금 이 대화에서 한 작업을 다음에도 똑같이 할 수 있게 스킬 파일로 만들어줘. 내가 고쳐 달라고 한 내용도 규칙에 넣어줘."),
]))

# ═════════════════════════════ 부록 ═════════════════════════════
pap = wrap("".join([
    section("부록", "막혔을 때 · 되돌리기 · 개인정보 · 캡처 목록"),
    "<h3>자주 보는 오류</h3>",
    table(["화면에 나온 말", "원인", "해결"], [
        ["'claude' 용어가 cmdlet… 이름으로 인식되지 않습니다", "설치 직후 창을 다시 안 엶", "PowerShell 닫고 새로 열기 → 안 되면 PC 재시작"],
        ["winget을 찾을 수 없습니다", "앱 설치 관리자 구버전", "Microsoft Store → 앱 설치 관리자 업데이트"],
        ["Do you want to proceed?", "명령 실행 허락 요청(정상)", "내용 읽고 1. Yes / 삭제 명령이면 3. No"],
        ["Extension not detected", "크롬 확장 꺼짐·연결 끊김", "chrome://extensions 에서 켜기 → /chrome → Reconnect extension"],
        ["보안문자·로봇 확인", "사이트의 자동화 방지(정상)", "내가 직접 풀고 '계속해줘'"],
        ["커넥터 추가 실패", "주소 오타·팝업 차단", "주소 전체 복사로 다시 붙여넣기, 팝업 허용"],
        ["스킬 업로드 실패", "zip 구조·이름 불일치", "폴더째 압축, 폴더 이름 = name"],
        ["G: 경로를 찾을 수 없습니다", "드라이브 글자가 다름", "탐색기에서 Google Drive 글자 확인 후 프롬프트 수정"],
    ]),
    "<h3>되돌리기</h3>",
    table(["상황", "되돌리는 법"], [
        ["드라이브에 잘못 복사됨", "복사본 폴더만 삭제(원본은 USB에 그대로) → 1-3부터 다시"],
        ["드라이브에서 실수로 지움", "drive.google.com → 휴지통 → 복원(30일 이내)"],
        ["Claude가 파일을 고쳤는데 마음에 안 듦", "Claude Code에서 Esc 두 번 → 이전 시점 선택(되감기), 또는 '방금 바꾼 것 원래대로 되돌려줘'"],
        ["크롬 입력이 엉뚱하게 됨", "게시 전이므로 작성 화면을 닫으면 끝(그래서 발행은 사람이)"],
        ["스킬이 이상하게 동작", "스킬 끄기(Claude 앱: 사용자 지정 → 스킬 → 끄기) 또는 이전 zip 다시 업로드"],
    ]),
    "<h3>토큰 아끼는 법</h3>",
    table(["요령", "이유"], [
        ["긴 작업은 웹 대화창보다 Claude Code에서", "파일을 통째로 붙여넣지 않고 필요한 부분만 읽습니다"],
        ["영상 원본은 대화창에 올리지 않기", "컷 편집·자막은 Claude Code에서 파일로 처리하는 편이 훨씬 적게 씁니다"],
        ["주제가 바뀌면 새 대화(/clear)", "앞 대화 내용을 계속 다시 읽지 않습니다"],
        ["자주 하는 일은 스킬로", "긴 지시문을 매번 보내지 않습니다"],
    ]),
    "<h3>개인정보 체크리스트</h3>",
    table(["확인", "항목"], [
        ["☐", "녹음 전 동의를 받았다"], ["☐", "웹 대화창에 학생 실명+연락처 명단을 붙여넣지 않았다"],
        ["☐", "드라이브 상담·수납 폴더는 '링크가 있는 모든 사용자' 공유가 꺼져 있다"],
        ["☐", "카드뉴스·홍보 글에 학생 실명·학교명이 없다"], ["☐", "크롬 자동화 중 비밀번호를 Claude에게 알려주지 않았다"],
    ]),
    shot_list_section(),
]))

pages = [Page("home", "", "홈", home), Page("p0", "0", "준비", p0), Page("p1", "1", "드라이브 백업", p1), Page("p2", "2", "크롬 제어", p2),
         Page("p3", "3", "MCP 연결", p3), Page("p4", "4", "스킬 파일", p4), Page("p5", "5", "업무 자동화", p5),
         Page("ai", "AI", "AI 활용", pai), Page("ap", "+", "부록", pap)]
build(OUT / "index.html", pages, title="공부ON × Claude 업무 자동화 실습 교안",
      description="드라이브 백업, 크롬 채널 배포, 미리캔버스 MCP, 스킬 파일까지 화면 순서대로 따라 하는 실습 교안",
      brand=("ON", "Claude 업무 자동화 실습", "공부ON 스터디카페 · AI 활용 멘토링"),
      site_url=SITE, og_image="og_image.jpg", extra_css=CSS)

md = ["# 공부ON × Claude 실습 프롬프트 모음", "", "교안 각 단계에서 쓰는 프롬프트입니다. [대괄호]는 내 상황에 맞게 바꾸세요.", ""]
for t, txt in PROMPTS:
    md += [f"## {t}", "", "```", txt, "```", ""]
(OUT / "practice" / "prompts.md").write_text("\n".join(md), encoding="utf-8")
print("wrote", OUT / "index.html", "/", len(PROMPTS), "prompts")
