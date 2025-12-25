from typing import Iterable, List
import sqlite3

from models import Grade, GradeFilters


class GradeRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, grade: Grade) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO grades (student_no, name, subject, score)
            VALUES (?, ?, ?, ?)
            """,
            (grade.student_no.strip(), grade.name.strip(), grade.subject.strip(), grade.score),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def update(self, grade: Grade) -> None:
        if grade.id is None:
            raise ValueError("更新需要指定 id")
        with self.conn:
            self.conn.execute(
                """
                UPDATE grades
                SET student_no = ?, name = ?, subject = ?, score = ?
                WHERE id = ?
                """,
                (
                    grade.student_no.strip(),
                    grade.name.strip(),
                    grade.subject.strip(),
                    grade.score,
                    grade.id,
                ),
            )

    def delete(self, grade_id: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM grades WHERE id = ?", (grade_id,))

    def search(self, filters: GradeFilters | None = None) -> List[Grade]:
        filters = filters or GradeFilters()
        query = [
            "SELECT id, student_no, name, subject, score, created_at",
            "FROM grades WHERE 1=1",
        ]
        params: list[str] = []

        if filters.student_no:
            query.append("AND student_no LIKE ?")
            params.append(f"%{filters.student_no.strip()}%")
        if filters.name:
            query.append("AND name LIKE ?")
            params.append(f"%{filters.name.strip()}%")
        if filters.subject:
            query.append("AND subject LIKE ?")
            params.append(f"%{filters.subject.strip()}%")

        query.append("ORDER BY created_at DESC")
        cur = self.conn.execute(" ".join(query), params)
        return [self._row_to_grade(row) for row in cur.fetchall()]

    def all(self) -> List[Grade]:
        return self.search()

    def stats(self) -> dict:
        summary = self.conn.execute(
            "SELECT COUNT(*) AS total, AVG(score) AS avg_score, MAX(score) AS max_score, MIN(score) AS min_score FROM grades"
        ).fetchone()
        subject_rows = self.conn.execute(
            """
            SELECT subject, COUNT(*) AS count, AVG(score) AS avg_score,
                   MAX(score) AS max_score, MIN(score) AS min_score
            FROM grades
            GROUP BY subject
            ORDER BY subject
            """
        ).fetchall()
        return {
            "total": summary["total"],
            "avg_score": summary["avg_score"],
            "max_score": summary["max_score"],
            "min_score": summary["min_score"],
            "subjects": [dict(row) for row in subject_rows],
        }

    @staticmethod
    def _row_to_grade(row: sqlite3.Row) -> Grade:
        return Grade(
            id=row["id"],
            student_no=row["student_no"] or "",
            name=row["name"],
            subject=row["subject"],
            score=row["score"],
            created_at=row["created_at"],
        )
