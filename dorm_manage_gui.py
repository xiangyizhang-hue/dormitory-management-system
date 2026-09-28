import sys
import pymysql
from datetime import date
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QDateEdit, QMessageBox, QTabWidget, QGroupBox
)
from PyQt5.QtCore import Qt, QDate

from db_config import mysql_config
from services import DomainError, allocate_student, cancel_allocation as cancel_allocation_service

# ========== 数据库工具函数 ==========
def get_db_conn():
    """获取数据库连接"""
    try:
        conn = pymysql.connect(**mysql_config())
        return conn
    except pymysql.Error as e:
        QMessageBox.critical(None, "数据库错误", f"连接失败：{e}")
        return None

def close_db(conn, cursor):
    """关闭数据库连接"""
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# ========== 主界面窗口 ==========
class DormManageMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 窗口基本设置
        self.setWindowTitle("学生宿舍管理系统")
        self.resize(1000, 700)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 标签页（分模块）
        tab_widget = QTabWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(tab_widget)

        # 添加三个标签页
        self.student_tab = StudentManageTab()
        self.dorm_tab = DormManageTab()
        self.allocation_tab = DormAllocationTab()

        tab_widget.addTab(self.student_tab, "学生信息管理")
        tab_widget.addTab(self.dorm_tab, "宿舍信息管理")
        tab_widget.addTab(self.allocation_tab, "宿舍分配管理")

# ========== 学生信息管理标签页 ==========
class StudentManageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 整体布局
        layout = QVBoxLayout(self)

        # 1. 操作区域
        operate_group = QGroupBox("学生信息操作")
        operate_layout = QGridLayout(operate_group)

        # 表单控件
        operate_layout.addWidget(QLabel("学号："), 0, 0)
        self.stu_id_edit = QLineEdit()
        operate_layout.addWidget(self.stu_id_edit, 0, 1)

        operate_layout.addWidget(QLabel("姓名："), 0, 2)
        self.stu_name_edit = QLineEdit()
        operate_layout.addWidget(self.stu_name_edit, 0, 3)

        operate_layout.addWidget(QLabel("性别："), 0, 4)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        operate_layout.addWidget(self.gender_combo, 0, 5)

        operate_layout.addWidget(QLabel("院系："), 1, 0)
        self.dept_edit = QLineEdit()
        operate_layout.addWidget(self.dept_edit, 1, 1)

        operate_layout.addWidget(QLabel("年级："), 1, 2)
        self.grade_edit = QLineEdit()
        operate_layout.addWidget(self.grade_edit, 1, 3)

        operate_layout.addWidget(QLabel("专业："), 1, 4)
        self.major_edit = QLineEdit()
        operate_layout.addWidget(self.major_edit, 1, 5)

        operate_layout.addWidget(QLabel("电话："), 2, 0)
        self.phone_edit = QLineEdit()
        operate_layout.addWidget(self.phone_edit, 2, 1)

        # 按钮
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加学生")
        self.query_btn = QPushButton("查询所有学生")
        self.update_btn = QPushButton("修改电话")
        self.delete_btn = QPushButton("删除学生")
        self.clear_btn = QPushButton("清空表单")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.query_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.clear_btn)
        operate_layout.addLayout(btn_layout, 3, 0, 1, 6)

        # 2. 表格展示区域
        self.stu_table = QTableWidget()
        self.stu_table.setColumnCount(7)
        self.stu_table.setHorizontalHeaderLabels(["学号", "姓名", "性别", "院系", "年级", "专业", "电话"])
        # 列宽自适应
        self.stu_table.horizontalHeader().setStretchLastSection(True)

        # 组装布局
        layout.addWidget(operate_group)
        layout.addWidget(self.stu_table)

        # 绑定按钮事件
        self.add_btn.clicked.connect(self.add_student)
        self.query_btn.clicked.connect(self.query_all_students)
        self.update_btn.clicked.connect(self.update_student_phone)
        self.delete_btn.clicked.connect(self.delete_student)
        self.clear_btn.clicked.connect(self.clear_form)

    # 添加学生
    def add_student(self):
        stu_id = self.stu_id_edit.text().strip()
        stu_name = self.stu_name_edit.text().strip()
        gender = self.gender_combo.currentText()
        dept = self.dept_edit.text().strip()
        grade = self.grade_edit.text().strip()
        major = self.major_edit.text().strip()
        phone = self.phone_edit.text().strip() or None

        if not (stu_id and stu_name and dept and grade and major):
            QMessageBox.warning(self, "输入错误", "学号、姓名、院系、年级、专业不能为空！")
            return

        conn = get_db_conn()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO student (stu_id, stu_name, gender, department, grade, major, phone)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (stu_id, stu_name, gender, dept, grade, major, phone))
            conn.commit()
            QMessageBox.information(self, "成功", f"添加学生{stu_name}（{stu_id}）成功！")
            self.clear_form()
            self.query_all_students()  # 刷新表格
        except pymysql.IntegrityError:
            QMessageBox.warning(self, "错误", f"学号{stu_id}已存在！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加失败：{e}")
        finally:
            close_db(conn, cursor)

    # 查询所有学生
    def query_all_students(self):
        conn = get_db_conn()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM student")
            students = cursor.fetchall()
            self.stu_table.setRowCount(len(students))
            for row, stu in enumerate(students):
                for col, value in enumerate(stu):
                    self.stu_table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查询失败：{e}")
        finally:
            close_db(conn, cursor)

    # 修改学生电话
    def update_student_phone(self):
        stu_id = self.stu_id_edit.text().strip()
        new_phone = self.phone_edit.text().strip()
        if not (stu_id and new_phone):
            QMessageBox.warning(self, "输入错误", "学号和新电话不能为空！")
            return

        conn = get_db_conn()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            sql = "UPDATE student SET phone = %s WHERE stu_id = %s"
            affected = cursor.execute(sql, (new_phone, stu_id))
            conn.commit()
            if affected > 0:
                QMessageBox.information(self, "成功", f"学号{stu_id}电话更新成功！")
                self.clear_form()
                self.query_all_students()
            else:
                QMessageBox.warning(self, "错误", f"未找到学号{stu_id}的学生！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新失败：{e}")
        finally:
            close_db(conn, cursor)

    # 删除学生
    def delete_student(self):
        stu_id = self.stu_id_edit.text().strip()
        if not stu_id:
            QMessageBox.warning(self, "输入错误", "请输入要删除的学生学号！")
            return

        reply = QMessageBox.question(self, "确认删除", f"确定要删除学号{stu_id}的学生吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        conn = get_db_conn()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM student WHERE stu_id = %s"
            affected = cursor.execute(sql, (stu_id,))
            conn.commit()
            if affected > 0:
                QMessageBox.information(self, "成功", f"学号{stu_id}学生删除成功！")
                self.clear_form()
                self.query_all_students()
            else:
                QMessageBox.warning(self, "错误", f"未找到学号{stu_id}的学生！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除失败：{e}")
        finally:
            close_db(conn, cursor)

    # 清空表单
    def clear_form(self):
        self.stu_id_edit.clear()
        self.stu_name_edit.clear()
        self.gender_combo.setCurrentIndex(0)
        self.dept_edit.clear()
        self.grade_edit.clear()
        self.major_edit.clear()
        self.phone_edit.clear()

# ========== 宿舍信息管理标签页 ==========
class DormManageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 操作区域
        operate_group = QGroupBox("宿舍信息操作")
        operate_layout = QGridLayout(operate_group)

        # 表单
        operate_layout.addWidget(QLabel("宿舍号："), 0, 0)
        self.dorm_id_edit = QLineEdit()
        operate_layout.addWidget(self.dorm_id_edit, 0, 1)

        operate_layout.addWidget(QLabel("楼栋："), 0, 2)
        self.building_edit = QLineEdit()
        operate_layout.addWidget(self.building_edit, 0, 3)

        operate_layout.addWidget(QLabel("楼层："), 0, 4)
        self.floor_edit = QLineEdit()
        operate_layout.addWidget(self.floor_edit, 0, 5)

        operate_layout.addWidget(QLabel("总床位："), 1, 0)
        self.bed_count_edit = QLineEdit()
        self.bed_count_edit.setText("4")  # 默认4人间
        operate_layout.addWidget(self.bed_count_edit, 1, 1)

        # 按钮
        btn_layout = QHBoxLayout()
        self.add_dorm_btn = QPushButton("添加宿舍")
        self.query_dorm_btn = QPushButton("查询所有宿舍")
        self.clear_dorm_btn = QPushButton("清空表单")

        btn_layout.addWidget(self.add_dorm_btn)
        btn_layout.addWidget(self.query_dorm_btn)
        btn_layout.addWidget(self.clear_dorm_btn)
        operate_layout.addLayout(btn_layout, 2, 0, 1, 6)

        # 表格区域
        self.dorm_table = QTableWidget()
        self.dorm_table.setColumnCount(5)
        self.dorm_table.setHorizontalHeaderLabels(["宿舍号", "楼栋", "楼层", "总床位", "剩余床位"])
        self.dorm_table.horizontalHeader().setStretchLastSection(True)

        # 组装
        layout.addWidget(operate_group)
        layout.addWidget(self.dorm_table)

        # 绑定事件
        self.add_dorm_btn.clicked.connect(self.add_dormitory)
        self.query_dorm_btn.clicked.connect(self.query_all_dormitories)
        self.clear_dorm_btn.clicked.connect(self.clear_form)

    # 添加宿舍
    def add_dormitory(self):
        dorm_id = self.dorm_id_edit.text().strip()
        building = self.building_edit.text().strip()
        floor = self.floor_edit.text().strip()
        bed_count = self.bed_count_edit.text().strip()

        if not (dorm_id and building and floor and bed_count):
            QMessageBox.warning(self, "输入错误", "宿舍号、楼栋、楼层、总床位不能为空！")
            return
        try:
            floor = int(floor)
            bed_count = int(bed_count)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "楼层和总床位必须是数字！")
            return

        conn = get_db_conn()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO dormitory (dorm_id, building, floor, bed_count, empty_bed)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (dorm_id, building, floor, bed_count, bed_count))
            conn.commit()
            QMessageBox.information(self, "成功", f"添加宿舍{dorm_id}成功！")
            self.clear_form()
            self.query_all_dormitories()
        except pymysql.IntegrityError:
            QMessageBox.warning(self, "错误", f"宿舍号{dorm_id}已存在！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加失败：{e}")
        finally:
            close_db(conn, cursor)

    # 查询所有宿舍
    def query_all_dormitories(self):
        conn = get_db_conn()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM dormitory")
            dorms = cursor.fetchall()
            self.dorm_table.setRowCount(len(dorms))
            for row, dorm in enumerate(dorms):
                for col, value in enumerate(dorm):
                    self.dorm_table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查询失败：{e}")
        finally:
            close_db(conn, cursor)

    # 清空表单
    def clear_form(self):
        self.dorm_id_edit.clear()
        self.building_edit.clear()
        self.floor_edit.clear()
        self.bed_count_edit.setText("4")

# ========== 宿舍分配管理标签页 ==========
class DormAllocationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 分配操作区域
        allocate_group = QGroupBox("宿舍分配/退宿")
        allocate_layout = QGridLayout(allocate_group)

        # 分配表单
        allocate_layout.addWidget(QLabel("学生学号："), 0, 0)
        self.allocate_stu_id = QLineEdit()
        allocate_layout.addWidget(self.allocate_stu_id, 0, 1)

        allocate_layout.addWidget(QLabel("宿舍号："), 0, 2)
        self.allocate_dorm_id = QLineEdit()
        allocate_layout.addWidget(self.allocate_dorm_id, 0, 3)

        allocate_layout.addWidget(QLabel("入住日期："), 0, 4)
        self.check_in_date = QDateEdit()
        self.check_in_date.setDate(QDate.currentDate())
        self.check_in_date.setDisplayFormat("yyyy-MM-dd")
        allocate_layout.addWidget(self.check_in_date, 0, 5)

        # 分配/退宿按钮
        btn_layout1 = QHBoxLayout()
        self.allocate_btn = QPushButton("分配宿舍")
        self.cancel_btn = QPushButton("学生退宿")
        btn_layout1.addWidget(self.allocate_btn)
        btn_layout1.addWidget(self.cancel_btn)
        allocate_layout.addLayout(btn_layout1, 1, 0, 1, 6)

        # 查询区域
        query_group = QGroupBox("查询宿舍入住学生")
        query_layout = QHBoxLayout(query_group)

        query_layout.addWidget(QLabel("宿舍号："))
        self.query_dorm_id = QLineEdit()
        query_layout.addWidget(self.query_dorm_id)

        self.query_stu_btn = QPushButton("查询入住学生")
        query_layout.addWidget(self.query_stu_btn)

        # 表格区域
        self.allocation_table = QTableWidget()
        self.allocation_table.setColumnCount(4)
        self.allocation_table.setHorizontalHeaderLabels(["学号", "姓名", "院系", "入住日期"])
        self.allocation_table.horizontalHeader().setStretchLastSection(True)

        # 组装
        layout.addWidget(allocate_group)
        layout.addWidget(query_group)
        layout.addWidget(self.allocation_table)

        # 绑定事件
        self.allocate_btn.clicked.connect(self.allocate_dorm)
        self.cancel_btn.clicked.connect(self.cancel_allocation)
        self.query_stu_btn.clicked.connect(self.query_dorm_students)

    # 分配宿舍
    def allocate_dorm(self):
        stu_id = self.allocate_stu_id.text().strip()
        dorm_id = self.allocate_dorm_id.text().strip()
        check_in_date = self.check_in_date.date().toString("yyyy-MM-dd")

        if not (stu_id and dorm_id):
            QMessageBox.warning(self, "输入错误", "学号和宿舍号不能为空！")
            return

        conn = get_db_conn()
        if not conn:
            return
        try:
            allocate_student(conn, stu_id, dorm_id, check_in_date)
            QMessageBox.information(self, "成功", f"学号{stu_id}分配宿舍{dorm_id}成功！")
            self.allocate_stu_id.clear()
            self.allocate_dorm_id.clear()
        except DomainError as e:
            QMessageBox.warning(self, "错误", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分配失败：{e}")
        finally:
            close_db(conn, None)

    # 学生退宿
    def cancel_allocation(self):
        stu_id = self.allocate_stu_id.text().strip()
        if not stu_id:
            QMessageBox.warning(self, "输入错误", "请输入要退宿的学生学号！")
            return

        reply = QMessageBox.question(self, "确认退宿", f"确定要让学号{stu_id}退宿吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        conn = get_db_conn()
        if not conn:
            return
        try:
            dorm_id = cancel_allocation_service(conn, stu_id)
            QMessageBox.information(self, "成功", f"学号{stu_id}退宿成功！")
            self.allocate_stu_id.clear()
            self.allocate_dorm_id.clear()
        except DomainError as e:
            QMessageBox.warning(self, "错误", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"退宿失败：{e}")
        finally:
            close_db(conn, None)

    # 查询宿舍入住学生
    def query_dorm_students(self):
        dorm_id = self.query_dorm_id.text().strip()
        if not dorm_id:
            QMessageBox.warning(self, "输入错误", "请输入要查询的宿舍号！")
            return

        conn = get_db_conn()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            # 联表查询学生信息
            cursor.execute("""
                SELECT s.stu_id, s.stu_name, s.department, da.check_in_date
                FROM dorm_allocation da
                JOIN student s ON da.stu_id = s.stu_id
                WHERE da.dorm_id = %s
            """, (dorm_id,))
            students = cursor.fetchall()
            self.allocation_table.setRowCount(len(students))
            for row, stu in enumerate(students):
                for col, value in enumerate(stu):
                    self.allocation_table.setItem(row, col, QTableWidgetItem(str(value)))
            if not students:
                QMessageBox.information(self, "提示", f"宿舍{dorm_id}暂无入住学生！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查询失败：{e}")
        finally:
            close_db(conn, cursor)

# ========== 程序入口 ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DormManageMainWindow()
    window.show()
    sys.exit(app.exec_())
