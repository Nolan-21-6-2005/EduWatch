from __future__ import annotations

import sqlite3
from utils.database_path import getdatabase_path


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(getdatabase_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_buildings(*, include_deleted: bool = True) -> list[dict]:
    where = "" if include_deleted else "WHERE COALESCE(is_deleted, 0)=0"
    with _connect() as conn:
        rows = conn.execute(
            f"""
            SELECT id, ten_toa, COALESCE(is_deleted, 0) AS is_deleted
            FROM Buildings
            {where}
            ORDER BY is_deleted ASC, ten_toa COLLATE NOCASE ASC, id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_rooms(building_id: int, *, include_deleted: bool = True) -> list[dict]:
    where_deleted = "" if include_deleted else "AND COALESCE(is_deleted, 0)=0"
    with _connect() as conn:
        rows = conn.execute(
            f"""
            SELECT id, building_id, ten_phong,
                   COALESCE(monitor_mode, 0) AS monitor_mode,
                   COALESCE(is_deleted, 0) AS is_deleted
            FROM Rooms
            WHERE building_id=? {where_deleted}
            ORDER BY is_deleted ASC, ten_phong COLLATE NOCASE ASC, id ASC
            """,
            (int(building_id),),
        ).fetchall()
        return [dict(row) for row in rows]


def get_cameras(room_id: int) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, room_id, vi_tri_goc, video_source,
                   COALESCE(status, 0) AS status
            FROM Cameras
            WHERE room_id=?
            ORDER BY id ASC
            """,
            (int(room_id),),
        ).fetchall()
        return [dict(row) for row in rows]


def get_locations() -> list[dict]:
    """Return the full building -> room -> camera tree directly from SQLite."""
    buildings = get_buildings(include_deleted=True)
    for building in buildings:
        rooms = get_rooms(int(building["id"]), include_deleted=True)
        for room in rooms:
            room["cameras"] = get_cameras(int(room["id"]))
            room["status"] = 0 if int(room.get("is_deleted") or 0) else 1
        building["rooms"] = rooms
        building["room_count"] = len([r for r in rooms if not int(r.get("is_deleted") or 0)])
        building["camera_count"] = sum(
            len([c for c in r.get("cameras", []) if int(c.get("status") or 0) == 1])
            for r in rooms
            if not int(r.get("is_deleted") or 0)
        )
        building["status"] = 0 if int(building.get("is_deleted") or 0) else 1
    return buildings


def add_building(ten_toa: str) -> int:
    name = ten_toa.strip()
    if not name:
        raise ValueError("Tên tòa nhà không được để trống.")
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO Buildings (ten_toa, is_deleted) VALUES (?, 0)",
            (name,),
        )
        conn.commit()
        return int(cursor.lastrowid)


def update_building(building_id: int, ten_toa: str) -> None:
    name = ten_toa.strip()
    if not name:
        raise ValueError("Tên tòa nhà không được để trống.")
    with _connect() as conn:
        conn.execute(
            "UPDATE Buildings SET ten_toa=? WHERE id=?",
            (name, int(building_id)),
        )
        conn.commit()


def set_building_status(building_id: int, status: int) -> None:
    # Stable DB does not have a dedicated Buildings.status column.
    # is_deleted=1 is used as the inactive state while preserving the row.
    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE Buildings SET is_deleted=? WHERE id=?",
            (0 if int(status) else 1, int(building_id)),
        )
        if cursor.rowcount == 0:
            raise ValueError("Không tìm thấy tòa nhà.")
        conn.commit()


def soft_delete_building(building_id: int) -> None:
    set_building_status(building_id, 0)


def add_room(building_id: int, ten_phong: str) -> int:
    name = ten_phong.strip()
    if not name:
        raise ValueError("Tên phòng không được để trống.")
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO Rooms (building_id, ten_phong, is_deleted) VALUES (?, ?, 0)",
            (int(building_id), name),
        )
        conn.commit()
        return int(cursor.lastrowid)


def update_room(room_id: int, building_id: int, ten_phong: str) -> None:
    name = ten_phong.strip()
    if not name:
        raise ValueError("Tên phòng không được để trống.")
    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE Rooms SET building_id=?, ten_phong=? WHERE id=?",
            (int(building_id), name, int(room_id)),
        )
        if cursor.rowcount == 0:
            raise ValueError("Không tìm thấy phòng.")
        conn.commit()


def set_room_status(room_id: int, status: int) -> None:
    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE Rooms SET is_deleted=? WHERE id=?",
            (0 if int(status) else 1, int(room_id)),
        )
        if cursor.rowcount == 0:
            raise ValueError("Không tìm thấy phòng.")
        conn.commit()


def soft_delete_room(room_id: int) -> None:
    set_room_status(room_id, 0)


def get_room_monitor_mode(room_id: int) -> int:
    with _connect() as conn:
        row = conn.execute(
            "SELECT COALESCE(monitor_mode, 0) FROM Rooms WHERE id=?",
            (int(room_id),),
        ).fetchone()
        if row is None:
            raise ValueError("Không tìm thấy phòng.")
        return int(row[0] or 0)


def update_room_monitor_mode(room_id: int, monitor_mode: int) -> None:
    mode = 1 if int(monitor_mode) else 0
    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE Rooms SET monitor_mode=? WHERE id=?",
            (mode, int(room_id)),
        )
        if cursor.rowcount == 0:
            raise ValueError("Không tìm thấy phòng.")
        conn.commit()


def add_camera(room_id: int, vi_tri_goc: str, video_source: str, status: int = 1) -> int:
    position = vi_tri_goc.strip()
    if not position:
        raise ValueError("Vị trí camera không được để trống.")
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO Cameras (room_id, vi_tri_goc, video_source, status)
            VALUES (?, ?, ?, ?)
            """,
            (int(room_id), position, video_source.strip(), int(status)),
        )
        conn.commit()
        return int(cursor.lastrowid)


def update_camera(camera_id: int, room_id: int, vi_tri_goc: str, video_source: str, status: int) -> None:
    position = vi_tri_goc.strip()
    if not position:
        raise ValueError("Vị trí camera không được để trống.")
    with _connect() as conn:
        cursor = conn.execute(
            """
            UPDATE Cameras
            SET room_id=?, vi_tri_goc=?, video_source=?, status=?
            WHERE id=?
            """,
            (int(room_id), position, video_source.strip(), int(status), int(camera_id)),
        )
        if cursor.rowcount == 0:
            raise ValueError("Không tìm thấy camera.")
        conn.commit()


def update_camera_status(camera_id: int, status: int) -> None:
    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE Cameras SET status=? WHERE id=?",
            (int(status), int(camera_id)),
        )
        if cursor.rowcount == 0:
            raise ValueError("Không tìm thấy camera.")
        conn.commit()


def delete_camera(camera_id: int) -> None:
    # There is no is_deleted field in Stable's Cameras table.
    # Keep the row and mark it inactive instead of destroying history references.
    update_camera_status(camera_id, 0)


def camera_is_used(camera_id: int) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM Violation_Logs WHERE camera_id=? LIMIT 1",
            (int(camera_id),),
        ).fetchone()
        return row is not None


def get_first_camera_id(building_name: str, room_name: str):
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT c.id
            FROM Cameras c
            JOIN Rooms r ON r.id=c.room_id
            JOIN Buildings b ON b.id=r.building_id
            WHERE COALESCE(c.status, 0)=1
              AND COALESCE(r.is_deleted, 0)=0
              AND COALESCE(b.is_deleted, 0)=0
              AND b.ten_toa=?
              AND r.ten_phong=?
            ORDER BY c.id
            LIMIT 1
            """,
            (building_name, room_name),
        ).fetchone()
        return int(row[0]) if row else None
