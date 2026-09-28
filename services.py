class DomainError(RuntimeError):
    pass


def allocate_student(connection, stu_id: str, dorm_id: str, check_in_date: str) -> None:
    """Allocate one bed atomically while locking the selected dormitory row."""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT 1 FROM student WHERE stu_id = %s", (stu_id,))
        if cursor.fetchone() is None:
            raise DomainError(f"学号 {stu_id} 不存在")
        cursor.execute("SELECT empty_bed FROM dormitory WHERE dorm_id = %s FOR UPDATE", (dorm_id,))
        dorm = cursor.fetchone()
        if dorm is None:
            raise DomainError(f"宿舍 {dorm_id} 不存在")
        if dorm[0] <= 0:
            raise DomainError(f"宿舍 {dorm_id} 已满")
        cursor.execute("SELECT 1 FROM dorm_allocation WHERE stu_id = %s", (stu_id,))
        if cursor.fetchone() is not None:
            raise DomainError(f"学号 {stu_id} 已分配宿舍")
        cursor.execute(
            "INSERT INTO dorm_allocation (stu_id, dorm_id, check_in_date) VALUES (%s, %s, %s)",
            (stu_id, dorm_id, check_in_date),
        )
        affected = cursor.execute(
            "UPDATE dormitory SET empty_bed = empty_bed - 1 WHERE dorm_id = %s AND empty_bed > 0",
            (dorm_id,),
        )
        if affected != 1:
            raise DomainError("床位已被其他事务占用，请刷新后重试")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def cancel_allocation(connection, stu_id: str) -> str:
    """Cancel an allocation and restore exactly one bed in the same transaction."""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT dorm_id FROM dorm_allocation WHERE stu_id = %s FOR UPDATE", (stu_id,))
        row = cursor.fetchone()
        if row is None:
            raise DomainError(f"学号 {stu_id} 未分配宿舍")
        dorm_id = row[0]
        cursor.execute("DELETE FROM dorm_allocation WHERE stu_id = %s", (stu_id,))
        affected = cursor.execute(
            "UPDATE dormitory SET empty_bed = empty_bed + 1 "
            "WHERE dorm_id = %s AND empty_bed < bed_count",
            (dorm_id,),
        )
        if affected != 1:
            raise DomainError("宿舍床位数据异常，已回滚")
        connection.commit()
        return dorm_id
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
