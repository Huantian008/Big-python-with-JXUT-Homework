# 学生成绩管理系统（Python + Tkinter + SQLite）

中小型桌面应用，提供成绩的录入、查询、更新、删除、统计，以及 CSV 导入导出。项目按模块分层以保持低耦合、高内聚。

## 功能列表
- 增删改查：录入成绩，列表查看，选中行可更新或删除。
- 查询/过滤：按学号、姓名、科目模糊过滤。
- 统计：总记录数、平均分、最高分、最低分，按科目聚合统计。
- CSV 导入导出：批量导入（逐行校验），导出全量数据。

## 运行
```bash
python3 app.py
```
- 首次运行自动创建 `app.db`（SQLite）。
- 建议使用 Python 3.10+。

## 模块说明
- `app.py`：入口。创建数据库连接（`database.py`），装配仓储 → 服务 → UI，配置窗口大小并启动 Tk 主循环。
- `database.py`：管理数据库文件路径 `app.db`，提供 `get_connection` 获取带 `Row` 工厂的连接，初始化表结构 `grades`（字段：id/学号/姓名/科目/分数/创建时间，分数 0-100 约束）。
- `models.py`：数据模型。`Grade` 表示一条成绩记录（可选 id/created_at），`GradeFilters` 封装查询条件。
- `repository.py`：数据访问层（DAO）。封装对 `grades` 表的 CRUD 与查询，返回 `Grade` 对象；`stats()` 提供总数/均值/最高/最低及按科目聚合。
- `services.py`：业务逻辑层。校验必填项与分数范围；封装新增、更新、删除、查询；实现 CSV 导入（必含 name/subject/score，可选 student_no，逐行校验）和导出；提供统计数据给 UI。
- `ui.py`：Tkinter 界面层。录入/查询表单，按钮区（新增/更新/删除/过滤/重置/导入/导出），Treeview 列表（选中行自动回填表单），统计面板显示总数/均值/最高/最低与按科目汇总，所有操作调用 `GradeService` 保持与业务解耦。

## CSV 说明
- 导入文件需包含表头：`name,subject,score`（可选 `student_no`）。
- 分数必须为数字，且在 0–100 范围；导入时按行校验，若某行无效会提示行号。
- 导出会生成 `grades.csv`（含 id、学号、姓名、科目、分数、创建时间）。

## 目录结构
```
app.py           # 程序入口
database.py      # DB 连接与初始化
models.py        # 数据类
repository.py    # 数据访问层
services.py      # 业务层（校验、统计、CSV）
ui.py            # Tkinter 界面层
app.db           # 运行后生成的 SQLite 文件
```

## 开发/扩展建议
- 新增筛选条件：按分数区间、日期排序等。
- 权限/用户：增加登录或简易角色控制。
- 分发：使用 pyinstaller 打包为可执行文件。
