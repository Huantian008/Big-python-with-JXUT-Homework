import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Iterable, List
from pathlib import Path

from models import Grade
from services import GradeService


class GradeApp:
    def __init__(self, root: tk.Tk, service: GradeService) -> None:
        self.service = service
        self.root = root
        self.root.title("学生成绩管理系统")

        self.student_no_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.score_var = tk.StringVar()

        self.stat_total = tk.StringVar(value="0")
        self.stat_avg = tk.StringVar(value="-")
        self.stat_max = tk.StringVar(value="-")
        self.stat_min = tk.StringVar(value="-")
        self.stat_subjects = tk.StringVar(value="无数据")

        self._build_form()
        self._build_table()
        self._build_stats()
        self.refresh()

    def _build_form(self) -> None:
        form = ttk.LabelFrame(self.root, text="录入 / 查询")
        form.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(form, text="学号").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form, textvariable=self.student_no_var, width=20).grid(
            row=0, column=1, padx=5, pady=5
        )

        ttk.Label(form, text="姓名*").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form, textvariable=self.name_var, width=20).grid(
            row=0, column=3, padx=5, pady=5
        )

        ttk.Label(form, text="科目*").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form, textvariable=self.subject_var, width=20).grid(
            row=1, column=1, padx=5, pady=5
        )

        ttk.Label(form, text="分数*").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(form, textvariable=self.score_var, width=20).grid(
            row=1, column=3, padx=5, pady=5
        )

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="新增", command=self.handle_add).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="更新选中", command=self.handle_update).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(btn_frame, text="删除选中", command=self.handle_delete).grid(
            row=0, column=2, padx=5
        )
        ttk.Button(btn_frame, text="查询/过滤", command=self.handle_search).grid(
            row=0, column=3, padx=5
        )
        ttk.Button(btn_frame, text="重置", command=self.handle_reset).grid(row=0, column=4, padx=5)
        ttk.Button(btn_frame, text="导入 CSV", command=self.handle_import).grid(
            row=0, column=5, padx=5
        )
        ttk.Button(btn_frame, text="导出 CSV", command=self.handle_export).grid(
            row=0, column=6, padx=5
        )

    def _build_table(self) -> None:
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "student_no", "name", "subject", "score", "created_at")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse", height=12
        )
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.heading("student_no", text="学号")
        self.tree.column("student_no", width=120)
        self.tree.heading("name", text="姓名")
        self.tree.column("name", width=120)
        self.tree.heading("subject", text="科目")
        self.tree.column("subject", width=120)
        self.tree.heading("score", text="分数")
        self.tree.column("score", width=80, anchor=tk.CENTER)
        self.tree.heading("created_at", text="创建时间")
        self.tree.column("created_at", width=160)

        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _build_stats(self) -> None:
        stats_frame = ttk.LabelFrame(self.root, text="统计")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(stats_frame, text="总记录:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.stat_total).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W
        )

        ttk.Label(stats_frame, text="平均分:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.stat_avg).grid(
            row=0, column=3, padx=5, pady=5, sticky=tk.W
        )

        ttk.Label(stats_frame, text="最高分:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.stat_max).grid(
            row=0, column=5, padx=5, pady=5, sticky=tk.W
        )

        ttk.Label(stats_frame, text="最低分:").grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.stat_min).grid(
            row=0, column=7, padx=5, pady=5, sticky=tk.W
        )

        ttk.Label(stats_frame, text="按科目统计:").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W
        )
        ttk.Label(stats_frame, textvariable=self.stat_subjects).grid(
            row=1, column=1, columnspan=7, padx=5, pady=5, sticky=tk.W
        )

    def refresh(self, rows: Iterable[Grade] | None = None) -> None:
        self._refresh_table(rows)
        self._refresh_stats()

    def _refresh_table(self, rows: Iterable[Grade] | None = None) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        data = list(rows) if rows is not None else self.service.search()
        for grade in data:
            self.tree.insert(
                "", tk.END, values=(grade.id, grade.student_no, grade.name, grade.subject, grade.score, grade.created_at)
            )

    def _refresh_stats(self) -> None:
        stats = self.service.stats()
        self.stat_total.set(str(stats.get("total", 0)))
        self.stat_avg.set(self._format_score(stats.get("avg_score")))
        self.stat_max.set(self._format_score(stats.get("max_score")))
        self.stat_min.set(self._format_score(stats.get("min_score")))
        subjects = stats.get("subjects") or []
        if subjects:
            parts = [
                f"{row['subject']}: {row['count']}人, 平均 {self._format_score(row['avg_score'])}"
                for row in subjects
            ]
            self.stat_subjects.set(" | ".join(parts))
        else:
            self.stat_subjects.set("无数据")

    def handle_add(self) -> None:
        try:
            student_no, name, subject, score = self._get_form_values()
            self.service.create_grade(student_no, name, subject, score)
            self.handle_reset()
            messagebox.showinfo("成功", "新增成绩成功")
        except ValueError as exc:
            messagebox.showerror("错误", str(exc))

    def handle_update(self) -> None:
        selection = self.tree.focus()
        if not selection:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        grade_id = int(self.tree.item(selection, "values")[0])
        try:
            student_no, name, subject, score = self._get_form_values()
            self.service.update_grade(grade_id, student_no, name, subject, score)
            self.handle_reset()
            messagebox.showinfo("成功", "更新成功")
        except ValueError as exc:
            messagebox.showerror("错误", str(exc))

    def handle_delete(self) -> None:
        selection = self.tree.focus()
        if not selection:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        grade_id = int(self.tree.item(selection, "values")[0])
        if not messagebox.askyesno("确认", "确认删除选中的记录吗？"):
            return
        self.service.delete_grade(grade_id)
        self.refresh()

    def handle_search(self) -> None:
        rows = self.service.search(
            student_no=self.student_no_var.get(),
            name=self.name_var.get(),
            subject=self.subject_var.get(),
        )
        self.refresh(rows)

    def handle_reset(self) -> None:
        self.student_no_var.set("")
        self.name_var.set("")
        self.subject_var.set("")
        self.score_var.set("")
        self.refresh()

    def handle_import(self) -> None:
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        try:
            count = self.service.import_csv(Path(file_path))
            self.refresh()
            messagebox.showinfo("导入完成", f"成功导入 {count} 条记录")
        except ValueError as exc:
            messagebox.showerror("导入失败", str(exc))

    def handle_export(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
            initialfile="grades.csv",
        )
        if not file_path:
            return
        count = self.service.export_csv(Path(file_path))
        messagebox.showinfo("导出完成", f"已导出 {count} 条记录")

    def on_row_select(self, event: tk.Event) -> None:  # type: ignore[override]
        selection = self.tree.focus()
        if not selection:
            return
        values = self.tree.item(selection, "values")
        self.student_no_var.set(values[1])
        self.name_var.set(values[2])
        self.subject_var.set(values[3])
        self.score_var.set(values[4])

    def _get_form_values(self) -> tuple[str, str, str, str]:
        return (
            self.student_no_var.get(),
            self.name_var.get(),
            self.subject_var.get(),
            self.score_var.get(),
        )

    @staticmethod
    def _format_score(value: object) -> str:
        return "-" if value is None else f"{float(value):.1f}"
