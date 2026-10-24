"""SQLite 資料庫：記錄每次點名的結果。"""

import pathlib
from datetime import datetime, timezone

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS roll_calls (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id      INTEGER NOT NULL,
    channel_id    INTEGER NOT NULL,
    channel_name  TEXT    NOT NULL,
    role_id       INTEGER NOT NULL,
    role_name     TEXT    NOT NULL,
    called_by     INTEGER NOT NULL,
    called_at     TEXT    NOT NULL,  -- UTC ISO 8601
    expected      INTEGER NOT NULL,  -- 應到人數
    present       INTEGER NOT NULL,  -- 已到人數
    absent        INTEGER NOT NULL   -- 未到人數
);

CREATE TABLE IF NOT EXISTS roll_call_members (
    roll_call_id  INTEGER NOT NULL REFERENCES roll_calls(id) ON DELETE CASCADE,
    user_id       INTEGER NOT NULL,
    display_name  TEXT    NOT NULL,
    is_present    INTEGER NOT NULL,  -- 1 = 已到, 0 = 未到
    PRIMARY KEY (roll_call_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_roll_calls_guild ON roll_calls (guild_id, called_at);
"""


class Database:
    def __init__(self, path: str):
        self.path = pathlib.Path(path)
        self.conn: aiosqlite.Connection | None = None

    async def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA foreign_keys = ON")
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self):
        if self.conn is not None:
            await self.conn.close()
            self.conn = None

    async def add_roll_call(
        self,
        *,
        guild_id: int,
        channel_id: int,
        channel_name: str,
        role_id: int,
        role_name: str,
        called_by: int,
        present: list[tuple[int, str]],
        absent: list[tuple[int, str]],
    ) -> int:
        """新增一筆點名紀錄，present / absent 為 (user_id, display_name) 清單，回傳紀錄編號。"""
        cursor = await self.conn.execute(
            """
            INSERT INTO roll_calls (guild_id, channel_id, channel_name, role_id, role_name,
                                    called_by, called_at, expected, present, absent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                guild_id, channel_id, channel_name, role_id, role_name, called_by,
                datetime.now(timezone.utc).isoformat(),
                len(present) + len(absent), len(present), len(absent),
            ),
        )
        roll_call_id = cursor.lastrowid
        await self.conn.executemany(
            "INSERT INTO roll_call_members VALUES (?, ?, ?, ?)",
            [(roll_call_id, uid, name, 1) for uid, name in present]
            + [(roll_call_id, uid, name, 0) for uid, name in absent],
        )
        await self.conn.commit()
        return roll_call_id

    async def recent_roll_calls(
        self,
        guild_id: int,
        limit: int = 10,
        role_id: int | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ):
        """查詢點名紀錄，since / until 為時間範圍 [since, until)。"""
        query = "SELECT * FROM roll_calls WHERE guild_id = ?"
        params: list = [guild_id]
        if role_id is not None:
            query += " AND role_id = ?"
            params.append(role_id)
        # called_at 都以相同格式的 UTC ISO 字串儲存，可直接用字串比較
        if since is not None:
            query += " AND called_at >= ?"
            params.append(since.astimezone(timezone.utc).isoformat())
        if until is not None:
            query += " AND called_at < ?"
            params.append(until.astimezone(timezone.utc).isoformat())
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        async with self.conn.execute(query, params) as cursor:
            return await cursor.fetchall()

    async def absent_names(self, roll_call_ids: list[int]) -> dict[int, list[str]]:
        """回傳 {紀錄編號: [未到成員名稱, ...]}。"""
        result: dict[int, list[str]] = {rid: [] for rid in roll_call_ids}
        if not roll_call_ids:
            return result
        placeholders = ", ".join("?" * len(roll_call_ids))
        async with self.conn.execute(
            f"""
            SELECT roll_call_id, display_name FROM roll_call_members
            WHERE is_present = 0 AND roll_call_id IN ({placeholders})
            ORDER BY display_name
            """,
            roll_call_ids,
        ) as cursor:
            async for row in cursor:
                result[row["roll_call_id"]].append(row["display_name"])
        return result

    async def get_roll_call(self, guild_id: int, roll_call_id: int):
        """回傳 (紀錄, 成員清單)，找不到時回傳 (None, [])。"""
        async with self.conn.execute(
            "SELECT * FROM roll_calls WHERE guild_id = ? AND id = ?", (guild_id, roll_call_id)
        ) as cursor:
            record = await cursor.fetchone()
        if record is None:
            return None, []
        async with self.conn.execute(
            "SELECT * FROM roll_call_members WHERE roll_call_id = ? ORDER BY display_name",
            (roll_call_id,),
        ) as cursor:
            members = await cursor.fetchall()
        return record, members
