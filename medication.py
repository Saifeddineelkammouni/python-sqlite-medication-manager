import sqlite3
import random
import unittest



def get_connection():
    return sqlite3.connect("medications.db")



conn = get_connection()
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY,
    person_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    condition TEXT NOT NULL,
    medicine_name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    frequency TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL
)
""")
conn.commit()
conn.close()



def row_2_dict(row):
    """Convert one row tuple to a dictionary."""
    if row is None:
        return None
    return {
        "id": row[0],
        "person_name": row[1],
        "age": row[2],
        "condition": row[3],
        "medicine_name": row[4],
        "dosage": row[5],
        "frequency": row[6],
        "start_date": row[7],
        "end_date": row[8],
    }




def add_medication(id, person_name, age, condition,
                   medicine_name, dosage, frequency,
                   start_date, end_date):
    """
    Insert a new medication record.
    If the id already exists, raise an exception.
    """
    conn = get_connection()
    cur = conn.cursor()


    cur.execute("SELECT id FROM medications WHERE id = ?", (id,))
    existing = cur.fetchone()
    if existing is not None:
        conn.close()
        raise ValueError(f"Medication with id {id} already exists")


    cur.execute("""
        INSERT INTO medications
        (id, person_name, age, condition, medicine_name, dosage,
         frequency, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id, person_name, age, condition,
          medicine_name, dosage, frequency,
          start_date, end_date))

    conn.commit()
    conn.close()


def get_medication_by_id(id):
    """
    Return ONE medication record as a dictionary.
    If not found, return None.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM medications WHERE id = ?", (id,))
    row = cur.fetchone()

    conn.close()
    return row_2_dict(row)


def get_medications_by_person(person_name):
    """
    Fuzzy search by person name (contains the text).
    Return a list of dictionaries.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM medications WHERE person_name LIKE ?",
        (f"%{person_name}%",)
    )
    rows = cur.fetchall()

    conn.close()
    return [row_2_dict(r) for r in rows]


def get_medications_by_condition(condition):
    """Fuzzy search by condition (e.g. 'Diabetes')."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM medications WHERE condition LIKE ?",
        (f"%{condition}%",)
    )
    rows = cur.fetchall()

    conn.close()
    return [row_2_dict(r) for r in rows]


def get_medications_by_medicine(medicine_name):
    """Fuzzy search by medicine name (e.g. 'Metformin')."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM medications WHERE medicine_name LIKE ?",
        (f"%{medicine_name}%",)
    )
    rows = cur.fetchall()

    conn.close()
    return [row_2_dict(r) for r in rows]


def delete_medication(id):
    """
    Delete a medication by id.
    If id does not exist, raise an exception.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM medications WHERE id = ?", (id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        raise ValueError(f"No medication with id {id} to delete")

    cur.execute("DELETE FROM medications WHERE id = ?", (id,))
    conn.commit()
    conn.close()


def update_medications(id, person_name, age, condition,
                       medicine_name, dosage, frequency,
                       start_date, end_date):
    """
    Update a medication record by id.
    If id does not exist, raise an exception.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM medications WHERE id = ?", (id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        raise ValueError(f"No medication with id {id} to update")

    cur.execute("""
        UPDATE medications
        SET person_name = ?, age = ?, condition = ?, medicine_name = ?,
            dosage = ?, frequency = ?, start_date = ?, end_date = ?
        WHERE id = ?
    """, (person_name, age, condition, medicine_name,
          dosage, frequency, start_date, end_date, id))

    conn.commit()
    conn.close()



def create_random_data():
    random_names = ['Ali', 'Ilias', 'Saad', 'Emma', 'Omar',
                    'Liu', 'Mina', 'Sayf', 'Fatima', 'Noah']
    random_conditions = ['Diabetes', 'Hypertension', 'Asthma',
                         'Depression', 'Allergy', 'Arthritis']
    random_medicines = ['Metformin', 'Lisinopril', 'Salbutamol',
                        'Sertraline', 'Cetirizine', 'Ibuprofen']
    random_frequencies = ['1 time/day', '2 times/day',
                          '3 times/day', 'once a week']

    for i in range(1, 11):
        id = i
        person_name = random.choice(random_names)
        age = random.randint(20, 85)
        condition = random.choice(random_conditions)
        medicine_name = random.choice(random_medicines)
        dosage = f"{random.randint(1, 3)} tablet(s)"
        frequency = random.choice(random_frequencies)
        start_date = "2025-01-01"
        end_date = "2025-02-01"

        try:
            add_medication(id, person_name, age, condition,
                           medicine_name, dosage, frequency,
                           start_date, end_date)
        except ValueError:
            pass

class TestMedications(unittest.TestCase):

    def setUp(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM medications")
        conn.commit()
        conn.close()

        add_medication(1, "Test Name", 30, "Test Condition",
                       "TestMed", "1 tablet", "1 time/day",
                       "2025-01-01", "2025-02-01")

    def test_add_medication(self):
        med = get_medication_by_id(1)
        self.assertIsNotNone(med)
        self.assertEqual(med["person_name"], "Test Name")

    def test_add_duplicate_id(self):
        with self.assertRaises(ValueError):
            add_medication(1, "Another Name", 50, "Another Condition",
                           "AnotherMed", "2 tablets", "2 times/day",
                           "2025-01-01", "2025-02-01")

    def test_delete_medication(self):
        delete_medication(1)
        med = get_medication_by_id(1)
        self.assertIsNone(med)

    def test_update_medications(self):
        update_medications(1, "Updated Name", 40, "Updated Condition",
                           "UpdatedMed", "3 tablets", "3 times/day",
                           "2025-03-01", "2025-04-01")
        med = get_medication_by_id(1)
        self.assertEqual(med["person_name"], "Updated Name")

    def test_get_medications_by_person(self):
        results = get_medications_by_person("Test")
        self.assertGreaterEqual(len(results), 1)

    def test_get_medications_by_condition(self):
        results = get_medications_by_condition("Test")
        self.assertGreaterEqual(len(results), 1)

    def test_get_medications_by_medicine(self):
        results = get_medications_by_medicine("TestMed")
        self.assertGreaterEqual(len(results), 1)



if __name__ == "__main__":
    create_random_data()

    print("Medication with id 1:")
    print(get_medication_by_id(1))

    print("\nMedications for person containing 'Ali':")
    print(get_medications_by_person("Ali"))

    print("\nMedications for condition 'Diabetes':")
    print(get_medications_by_condition("Diabetes"))

    print("\nMedications with medicine 'Metformin':")
    print(get_medications_by_medicine("Metformin"))

    unittest.main()