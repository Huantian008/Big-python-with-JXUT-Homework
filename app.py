"""
Tkinter + SQLite 学生成绩管理系统（多模块版）
功能：新增、查询、更新、删除、统计、CSV 导入导出
运行：python app.py
"""

import tkinter as tk

from database import DB_FILE, get_connection
from repository import GradeRepository
from services import GradeService
from ui import GradeApp


def main() -> None:
    conn = get_connection(DB_FILE)
    service = GradeService(GradeRepository(conn))

    root = tk.Tk()
    GradeApp(root, service)
    root.geometry("900x600")
    root.minsize(820, 520)
    root.mainloop()


if __name__ == "__main__":
    main()
