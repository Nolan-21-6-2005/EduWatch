import sqlite3

from utils.database_path import getdatabase_path


def get_violation_type_statistics(
    *,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict]:
    where = ["1=1"]
    params: list[object] = []

    if start_date:
        where.append("date(v.thoi_gian) >= date(?)")
        params.append(start_date)

    if end_date:
        where.append("date(v.thoi_gian) <= date(?)")
        params.append(end_date)

    query = f"""
        SELECT
            v.session AS session,
            v.loai_vi_pham AS violation_type,
            COUNT(*) AS total
        FROM Violation_Logs v
        WHERE {' AND '.join(where)}
        GROUP BY
            v.session,
            v.loai_vi_pham
        ORDER BY
            v.session,
            total DESC,
            violation_type ASC
    """

    with sqlite3.connect(getdatabase_path()) as conn:
        rows = conn.execute(query, params).fetchall()

    return [
        {
            "session": row[0],
            "violation_type": row[1],
            "total": row[2],
        }
        for row in rows
    ]
    

