"""병원 찾기 콘솔 프로그램 (메뉴 반복, 입력, 표 출력, 예외 처리).

새 조회 기능을 붙일 때는 queries.py에 함수를 만들고 아래 FEATURES에 한 줄만 추가하면 된다.
"""
import sys

try:
    import pymysql
    from tabulate import tabulate
except ImportError as e:
    sys.exit(f"라이브러리가 없습니다: {e.name}\n  pip install -r requirements.txt")

try:
    import queries
except ImportError:
    sys.exit("config.py가 없습니다. app/config_example.py를 복사해 config.py로 만들고 비밀번호를 넣으세요.")


# ───────── 입력 항목 정의 ─────────
# (매개변수 이름, 화면 라벨, 필수 여부, 자료형, '?' 입력 시 보여줄 목록 종류)
SIDO     = ("sido",    "시도 (예: 서울)",          True,  str, "sido")
SIDO_OPT = ("sido",    "시도 (예: 서울)",          False, str, "sido")
SGG      = ("sgg",     "시군구 (예: 강남구)",      True,  str, None)
SGG_OPT  = ("sgg",     "시군구 (예: 강남구)",      False, str, None)
TYPE_OPT = ("htype",   "종별 (예: 의원)",          False, str, "type")
NAME     = ("name",    "병원명 일부",              True,  str, None)
NAME_OPT = ("name",    "병원명 일부",              False, str, None)
DEPT     = ("dept",    "진료과목 (예: 소아청소년과)", True, str, "dept")
TOP_N    = ("n",       "몇 개까지 볼까요 (N)",      True,  int, None)
MIN_CNT  = ("min_cnt", "최소 진료과목 수",          True,  int, None)

# ───────── 메뉴 = 조회 기능 ─────────
# 메뉴 번호: (제목, 실행 함수, 입력 항목들)
FEATURES = {
    "1": ("병원 검색",                 queries.search_hospital,      [SIDO_OPT, SGG_OPT, TYPE_OPT, NAME_OPT]),
    "2": ("진료과목으로 병원 찾기",     queries.find_by_dept,         [DEPT, SIDO, SGG_OPT]),
    "3": ("지역별 진료과목 현황",       queries.dept_stats_by_region, [SIDO, DEPT]),
    # ── 추가 기능 (보완 주, 가산점 최대 5개) ──
    "4": ("병원 상세 (진료과목 목록)",  queries.hospital_detail,      [NAME]),
    "5": ("전문의가 많은 병원 TOP N",   queries.top_specialists,      [DEPT, SIDO, TOP_N]),
    "6": ("종별 병원 수 통계",          queries.type_stats,           [SIDO]),
    "7": ("진료과목이 많은 병원",       queries.many_depts,           [SGG, MIN_CNT]),
    "8": ("특정 과목 병원이 없는 지역", queries.no_dept_regions,      [SIDO, DEPT]),
}


def print_menu():
    print("\n========== 병원 찾기 ==========")
    for key, (title, _, _) in FEATURES.items():
        print(f" {key}. {title}")
    print(" 0. 종료")
    print("===============================")


def show_choices(kind):
    values = queries.distinct_values(kind)
    print("  선택 가능:", ", ".join(values) if values else "(없음)")


def ask(field):
    """입력 항목 하나를 받는다. 선택 항목은 Enter면 None, '?'면 선택지 목록을 보여준다."""
    _, label, required, kind, choices = field
    hint = "" if required else " [생략: Enter]"
    if choices:
        hint += " [목록: ?]"
    while True:
        raw = input(f"  {label}{hint}: ").strip()
        if raw == "?" and choices:
            show_choices(choices)
            continue
        if not raw:
            if required:
                print("  필수 입력입니다.")
                continue
            return None
        if kind is int:
            if raw.isdigit() and int(raw) > 0:
                return int(raw)
            print("  1 이상의 숫자를 입력하세요.")
            continue
        return raw


def show(cols, rows):
    if not rows:
        print("\n조건에 맞는 결과가 없습니다.")
        return
    print()
    print(tabulate(rows, headers=cols, tablefmt="simple_grid"))
    print(f"총 {len(rows)}건")


def run_feature(key):
    title, func, fields = FEATURES[key]
    print(f"\n[{title}]")
    args = {f[0]: ask(f) for f in fields}
    show(*func(**args))


def main():
    while True:
        print_menu()
        menu = input("메뉴 선택: ").strip()
        if menu == "0":
            print("프로그램을 종료합니다.")
            break
        if menu not in FEATURES:
            print("메뉴 번호를 다시 입력하세요.")
            continue
        try:
            run_feature(menu)
        except pymysql.err.OperationalError as e:
            print("DB에 연결할 수 없습니다. MySQL 실행 여부와 config.py를 확인하세요.", e)
        except pymysql.MySQLError as e:
            print("SQL 실행 중 오류가 발생했습니다:", e)
        except Exception as e:  # 예상 못 한 오류가 나도 메뉴로 돌아간다
            print("오류가 발생했습니다:", e)
        input("\n(Enter를 누르면 메뉴로 돌아갑니다)")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n프로그램을 종료합니다.")
