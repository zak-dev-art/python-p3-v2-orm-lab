from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    all = {}

    def __init__(self, year, summary, employee, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee = employee  # sets employee and employee_id via setter

    # ============================
    #       ORM METHODS
    # ============================

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee.id)
            )
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            self.update()
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee):
        review = cls(year, summary, employee)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        id, year, summary, employee_id = row

        if id in cls.all:
            instance = cls.all[id]
            instance.year = year
            instance.summary = summary
        else:
            from .employee import Employee
            employee = Employee.find_by_id(employee_id)
            instance = cls(year, summary, employee, id=id)
            cls.all[id] = instance

        return instance

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id=?", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        CURSOR.execute(
            "UPDATE reviews SET year=?, summary=?, employee_id=? WHERE id=?",
            (self.year, self.summary, self.employee.id, self.id)
        )
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id=?", (self.id,))
        CONN.commit()
        if self.id in type(self).all:
            del type(self).all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # ============================
    #       PROPERTIES
    # ============================

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise TypeError("Year must be an integer.")
        if value < 2000:
            raise ValueError("Year must be >= 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str):
            raise TypeError("Summary must be a string.")
        if not value.strip():
            raise ValueError("Summary cannot be empty.")
        self._summary = value

    @property
    def employee(self):
        return self._employee

    @employee.setter
    def employee(self, value):
        from .employee import Employee
        if not isinstance(value, Employee):
            raise TypeError("Employee must be an Employee instance.")
        if value.id is None:
            raise ValueError("Employee must be saved before assigning to Review.")

        self._employee = value
        self.employee_id = value.id
