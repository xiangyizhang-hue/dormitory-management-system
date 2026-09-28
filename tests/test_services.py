import unittest

from services import DomainError, allocate_student, cancel_allocation


class FakeCursor:
    def __init__(self, fetches, updates=None):
        self.fetches = iter(fetches)
        self.updates = iter(updates or [])
        self.executed = []

    def execute(self, sql, params=()):
        self.executed.append((" ".join(sql.split()), params))
        if sql.lstrip().upper().startswith("UPDATE"):
            return next(self.updates, 1)
        return 1

    def fetchone(self):
        return next(self.fetches)

    def close(self):
        pass


class FakeConnection:
    def __init__(self, fetches, updates=None):
        self.fake_cursor = FakeCursor(fetches, updates)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class ServiceTests(unittest.TestCase):
    def test_allocate_commits_once(self):
        conn = FakeConnection([(1,), (2,), None], [1])
        allocate_student(conn, "20230001", "A-101", "2026-09-01")
        self.assertEqual(conn.commits, 1)
        self.assertEqual(conn.rollbacks, 0)
        self.assertTrue(any("FOR UPDATE" in sql for sql, _ in conn.fake_cursor.executed))

    def test_allocate_rolls_back_when_full(self):
        conn = FakeConnection([(1,), (0,)])
        with self.assertRaises(DomainError):
            allocate_student(conn, "20230001", "A-101", "2026-09-01")
        self.assertEqual(conn.rollbacks, 1)

    def test_cancel_restores_bed(self):
        conn = FakeConnection([("A-101",)], [1])
        self.assertEqual(cancel_allocation(conn, "20230001"), "A-101")
        self.assertEqual(conn.commits, 1)


if __name__ == "__main__":
    unittest.main()
