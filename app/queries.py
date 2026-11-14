"""조회 기능별 SQL과 실행 함수.

- 모든 함수는 (컬럼명 리스트, 결과 행 리스트)를 돌려준다. 출력은 main.py가 맡는다.
- 조건값은 문자열로 이어 붙이지 않고 반드시 %s + params로 넘긴다 (SQL 인젝션·따옴표 에러 방지).
- 값이 None이면 "입력하지 않은 조건"으로 보고 WHERE에서 뺀다.
"""
import pymysql

from config import DB


def run(sql, params=()):
    """SQL 한 개를 실행하고 (컬럼명, 행 목록)을 돌려준다."""
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [c[0] for c in cur.description]
            return cols, cur.fetchall()
    finally:
        conn.close()


def _add(where, params, clause, value):
    """value가 있을 때만 조건을 추가한다 (선택 조건용)."""
    if value is not None:
        where.append(clause)
        params.append(value)


# ───────────────────────── 기본 기능 ─────────────────────────

def search_hospital(sido=None, sgg=None, htype=None, name=None):
    """F1 병원 검색: 시도·시군구·종별·병원명 일부 중 입력한 것만 동시에 적용 (2개 테이블 조인)."""
    where, params = [], []
    _add(where, params, "r.sido = %s", sido)
    _add(where, params, "r.sgg = %s", sgg)
    _add(where, params, "h.type = %s", htype)
    _add(where, params, "h.name LIKE %s", f"%{name}%" if name else None)

    sql = ("SELECT h.name AS 병원명, h.type AS 종별, r.sido AS 시도, r.sgg AS 시군구, "
           "       h.address AS 주소, h.tel AS 전화 "
           "FROM hospital h "
           "JOIN region r ON h.region_id = r.region_id ")
    if where:
        sql += "WHERE " + " AND ".join(where) + " "
    sql += "ORDER BY h.name LIMIT 50"
    return run(sql, params)


def find_by_dept(dept, sido, sgg=None):
    """F2 진료과목으로 병원 찾기: 진료과목 + 시도 (+ 시군구) (4개 테이블 조인)."""
    where, params = ["d.dept_name = %s", "r.sido = %s"], [dept, sido]
    _add(where, params, "r.sgg = %s", sgg)

    sql = ("SELECT h.name AS 병원명, h.type AS 종별, r.sgg AS 시군구, "
           "       hd.specialist_cnt AS 전문의수, h.tel AS 전화 "
           "FROM hospital h "
           "JOIN hospital_dept hd ON h.ykiho = hd.ykiho "
           "JOIN department    d  ON hd.dept_code = d.dept_code "
           "JOIN region        r  ON h.region_id = r.region_id "
           "WHERE " + " AND ".join(where) + " "
           "ORDER BY hd.specialist_cnt DESC, h.name LIMIT 100")
    return run(sql, params)


def dept_stats_by_region(sido, dept):
    """F3 지역별 진료과목 현황: 시군구별 병원 수·전문의 합계 (4개 테이블 조인 + 집계)."""
    sql = ("SELECT r.sgg AS 시군구, "
           "       COUNT(DISTINCT h.ykiho) AS 병원수, "
           "       SUM(hd.specialist_cnt)  AS 전문의합계 "
           "FROM hospital h "
           "JOIN hospital_dept hd ON h.ykiho = hd.ykiho "
           "JOIN department    d  ON hd.dept_code = d.dept_code "
           "JOIN region        r  ON h.region_id = r.region_id "
           "WHERE r.sido = %s AND d.dept_name = %s "
           "GROUP BY r.sgg "
           "ORDER BY 병원수 DESC")
    return run(sql, (sido, dept))


# ───────────────────────── 추가 기능 (보완 주) ─────────────────────────

def hospital_detail(name):
    """E1 병원 상세: 병원명 일부로 찾고 진료과목 목록을 한 칸에 모아 보여준다."""
    sql = ("SELECT h.name AS 병원명, h.type AS 종별, h.address AS 주소, "
           "       GROUP_CONCAT(d.dept_name ORDER BY d.dept_name SEPARATOR ', ') AS 진료과목 "
           "FROM hospital h "
           "LEFT JOIN hospital_dept hd ON h.ykiho = hd.ykiho "
           "LEFT JOIN department    d  ON hd.dept_code = d.dept_code "
           "WHERE h.name LIKE %s "
           "GROUP BY h.ykiho, h.name, h.type, h.address "
           "ORDER BY h.name LIMIT 30")
    return run(sql, (f"%{name}%",))


def top_specialists(dept, sido, n):
    """E2 전문의가 많은 병원 TOP N."""
    sql = ("SELECT h.name AS 병원명, r.sgg AS 시군구, hd.specialist_cnt AS 전문의수 "
           "FROM hospital h "
           "JOIN hospital_dept hd ON h.ykiho = hd.ykiho "
           "JOIN department    d  ON hd.dept_code = d.dept_code "
           "JOIN region        r  ON h.region_id = r.region_id "
           "WHERE d.dept_name = %s AND r.sido = %s "
           "ORDER BY hd.specialist_cnt DESC "
           "LIMIT %s")
    return run(sql, (dept, sido, int(n)))


def type_stats(sido):
    """E3 종별 병원 수 통계."""
    sql = ("SELECT h.type AS 종별, COUNT(*) AS 병원수 "
           "FROM hospital h "
           "JOIN region r ON h.region_id = r.region_id "
           "WHERE r.sido = %s "
           "GROUP BY h.type "
           "ORDER BY 병원수 DESC")
    return run(sql, (sido,))


def many_depts(sgg, min_cnt):
    """E4 진료과목이 많은 병원: HAVING으로 최소 과목 수 조건."""
    sql = ("SELECT h.name AS 병원명, h.type AS 종별, COUNT(*) AS 과목수 "
           "FROM hospital h "
           "JOIN hospital_dept hd ON h.ykiho = hd.ykiho "
           "JOIN region        r  ON h.region_id = r.region_id "
           "WHERE r.sgg = %s "
           "GROUP BY h.ykiho, h.name, h.type "
           "HAVING COUNT(*) >= %s "
           "ORDER BY 과목수 DESC")
    return run(sql, (sgg, int(min_cnt)))


def no_dept_regions(sido, dept):
    """E5 특정 과목 병원이 없는 지역: NOT EXISTS 부속질의."""
    sql = ("SELECT r.sido AS 시도, r.sgg AS 시군구 "
           "FROM region r "
           "WHERE r.sido = %s "
           "  AND NOT EXISTS ( "
           "    SELECT 1 FROM hospital h "
           "    JOIN hospital_dept hd ON h.ykiho = hd.ykiho "
           "    JOIN department    d  ON hd.dept_code = d.dept_code "
           "    WHERE h.region_id = r.region_id AND d.dept_name = %s) "
           "ORDER BY r.sgg")
    return run(sql, (sido, dept))


# ───────────────────────── 입력 도우미 ─────────────────────────

def distinct_values(kind, sido=None):
    """사용자가 입력할 수 있는 값 목록 (시도/시군구/종별/진료과목). 메뉴에서 '?' 입력 시 사용.
    시군구는 앞에서 시도를 입력했으면 그 시도의 시군구만 보여준다."""
    if kind == "sgg" and sido:
        sql, params = "SELECT sgg FROM region WHERE sido = %s ORDER BY sgg", (sido,)
    else:
        sql, params = {
            "sido": "SELECT DISTINCT sido FROM region ORDER BY sido",
            "sgg":  "SELECT sgg FROM region ORDER BY sido, sgg",
            "type": "SELECT DISTINCT type FROM hospital ORDER BY type",
            "dept": "SELECT dept_name FROM department ORDER BY dept_code",
        }[kind], ()
    _, rows = run(sql, params)
    return [r[0] for r in rows]
