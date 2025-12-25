import csv
from pathlib import Path
from typing import Iterable, List

from models import Grade, GradeFilters
from repository import GradeRepository


class GradeService:
    def __init__(self, repository: GradeRepository) -> None:
        self.repository = repository

    def create_grade(self, student_no: str, name: str, subject: str, score_raw: str | float) -> int:
        score = self._validate_score(score_raw)
        self._require_text(name, "姓名")
        self._require_text(subject, "科目")
        grade = Grade(student_no=student_no, name=name, subject=subject, score=score)
        return self.repository.add(grade)

    def update_grade(
        self, grade_id: int, student_no: str, name: str, subject: str, score_raw: str | float
    ) -> None:
        score = self._validate_score(score_raw)
        self._require_text(name, "姓名")
        self._require_text(subject, "科目")
        grade = Grade(
            id=grade_id, student_no=student_no, name=name, subject=subject, score=score
        )
        self.repository.update(grade)

    def delete_grade(self, grade_id: int) -> None:
        self.repository.delete(grade_id)

    def search(self, student_no: str = "", name: str = "", subject: str = "") -> List[Grade]:
        filters = GradeFilters(student_no=student_no, name=name, subject=subject)
        return self.repository.search(filters)

    def export_csv(self, path: Path) -> int:
        records = self.repository.all()
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(
                fp, fieldnames=["id", "student_no", "name", "subject", "score", "created_at"]
            )
            writer.writeheader()
            for grade in records:
                writer.writerow(
                    {
                        "id": grade.id,
                        "student_no": grade.student_no,
                        "name": grade.name,
                        "subject": grade.subject,
                        "score": grade.score,
                        "created_at": grade.created_at,
                    }
                )
        return len(records)

    def import_csv(self, path: Path) -> int:
        if not path.exists():
            raise ValueError("文件不存在")
        imported = 0
        with path.open("r", newline="", encoding="utf-8-sig") as fp:
            reader = csv.DictReader(fp)
            required = {"name", "subject", "score"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise ValueError("CSV 必须包含字段: name, subject, score (可选: student_no)")
            for idx, row in enumerate(reader, start=2):  # header counted as row 1
                try:
                    self.create_grade(
                        student_no=row.get("student_no", "") or "",
                        name=row.get("name", "") or "",
                        subject=row.get("subject", "") or "",
                        score_raw=row.get("score", ""),
                    )
                    imported += 1
                except ValueError as exc:
                    raise ValueError(f"第 {idx} 行数据无效: {exc}") from exc
        return imported

    def stats(self) -> dict:
        return self.repository.stats()

    @staticmethod
    def _require_text(value: str, field_name: str) -> None:
        if not str(value).strip():
            raise ValueError(f"{field_name} 为必填项")

    @staticmethod
    def _validate_score(score_raw: str | float) -> float:
        try:
            score = float(score_raw)
        except (ValueError, TypeError) as exc:
            raise ValueError("分数必须是数字") from exc
        if score < 0 or score > 100:
            raise ValueError("分数必须在 0-100 之间")
        return score
