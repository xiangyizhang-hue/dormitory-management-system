# 学生宿舍数据库管理系统

基于 Python、PyQt5 和 MySQL 的课程设计项目，包含学生、宿舍、入住分配与报修四张关系表，以及学生、宿舍、入住分配三个桌面管理页面。

## 主要实现

- 主键、外键、唯一约束和状态字段保证基础数据完整性。
- 所有界面查询均使用参数化 SQL，避免字符串拼接注入。
- 分配和退宿在事务中同时修改入住记录与剩余床位。
- 对宿舍行使用 `SELECT ... FOR UPDATE`，并用 `empty_bed > 0` 条件更新防止并发超卖。
- 数据库密码从环境变量读取，不写入源码。

## 运行

1. 安装 MySQL 8、Python 3.10+，执行 `pip install -r requirements.txt`。
2. 按 `.env.example` 设置 `DORM_DB_*` 环境变量。
3. 初始化数据库：`python init_dorm_db.py`。
4. 启动桌面端：`python dorm_manage_gui.py`。

运行不依赖真实数据库的事务单元测试：

```bash
python -m unittest discover -s tests -v
```

## 项目边界

当前 GUI 覆盖学生、宿舍和入住分配管理；`repair` 表已建模，但报修管理页面尚未实现。系统用于单机课程演示，尚未加入登录、权限分级、审计日志和生产级部署配置。
