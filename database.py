import sqlite3
import os
from typing import List, Optional, Tuple, Any

DB_NAME = "alaganghayop.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create owners table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS owners (
        owner_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        address TEXT
    )
    ''')
    
    # Create pets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pets (
        pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        name TEXT NOT NULL,
        species TEXT,
        breed TEXT,
        birthdate TEXT,
        FOREIGN KEY (owner_id) REFERENCES owners (owner_id) ON DELETE CASCADE
    )
    ''')
    
    # Create vaccinations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vaccinations (
        vaccine_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER,
        vaccine_name TEXT NOT NULL,
        date_given TEXT,
        next_due TEXT,
        FOREIGN KEY (pet_id) REFERENCES pets (pet_id) ON DELETE CASCADE
    )
    ''')
    
    # Create medical_records table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medical_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER,
        diagnosis TEXT,
        treatment TEXT,
        date TEXT,
        FOREIGN KEY (pet_id) REFERENCES pets (pet_id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Owner CRUD
def check_duplicate_owner(name, exclude_id=None):
    conn = get_db_connection()
    # Normalize name: lowercase and remove extra spaces
    normalized_new = " ".join(name.lower().split())
    
    owners = conn.execute("SELECT owner_id, name FROM owners").fetchall()
    conn.close()
    
    for owner in owners:
        if exclude_id and owner['owner_id'] == exclude_id:
            continue
            
        normalized_existing = " ".join(owner['name'].lower().split())
        
        # Check for exact match or if one name is contained within the other (to handle middle initials)
        # Example: "sonjeev cabardo" vs "sonjeev c cabardo"
        words_new = set(normalized_new.split())
        words_existing = set(normalized_existing.split())
        
        # If one set of words is a subset of the other, we consider it a duplicate for this specific requirement
        if words_new.issubset(words_existing) or words_existing.issubset(words_new):
            return True, owner['name']
            
    return False, None

def add_owner(name, contact, address):
    is_dup, existing_name = check_duplicate_owner(name)
    if is_dup:
        raise ValueError(f"Duplicate found: '{name}' is too similar to existing owner '{existing_name}'.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO owners (name, contact, address) VALUES (?, ?, ?)", (name, contact, address))
    conn.commit()
    conn.close()

def get_owners() -> List[sqlite3.Row]:
    conn = get_db_connection()
    owners = conn.execute("SELECT * FROM owners").fetchall()
    conn.close()
    return owners

def update_owner(owner_id, name, contact, address):
    is_dup, existing_name = check_duplicate_owner(name, exclude_id=owner_id)
    if is_dup:
        raise ValueError(f"Duplicate found: '{name}' is too similar to existing owner '{existing_name}'.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE owners SET name=?, contact=?, address=? WHERE owner_id=?", (name, contact, address, owner_id))
    conn.commit()
    conn.close()

def delete_owner(owner_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM owners WHERE owner_id=?", (owner_id,))
    conn.commit()
    conn.close()

# Pet CRUD
def add_pet(owner_id, name, species, breed, birthdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pets (owner_id, name, species, breed, birthdate) VALUES (?, ?, ?, ?, ?)", 
                  (owner_id, name, species, breed, birthdate))
    conn.commit()
    conn.close()

def get_pets(owner_id: Optional[int] = None) -> List[sqlite3.Row]:
    conn = get_db_connection()
    if owner_id:
        pets = conn.execute("SELECT * FROM pets WHERE owner_id=?", (owner_id,)).fetchall()
    else:
        pets = conn.execute("SELECT p.*, o.name as owner_name FROM pets p JOIN owners o ON p.owner_id = o.owner_id").fetchall()
    conn.close()
    return pets

def update_pet(pet_id, name, species, breed, birthdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pets SET name=?, species=?, breed=?, birthdate=? WHERE pet_id=?", 
                  (name, species, breed, birthdate, pet_id))
    conn.commit()
    conn.close()

def delete_pet(pet_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pets WHERE pet_id=?", (pet_id,))
    conn.commit()
    conn.close()

# Vaccination CRUD
def add_vaccination(pet_id, vaccine_name, date_given, next_due):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vaccinations (pet_id, vaccine_name, date_given, next_due) VALUES (?, ?, ?, ?)", 
                  (pet_id, vaccine_name, date_given, next_due))
    conn.commit()
    conn.close()

def get_vaccinations(pet_id: Optional[int] = None) -> List[sqlite3.Row]:
    conn = get_db_connection()
    if pet_id:
        vax = conn.execute("SELECT * FROM vaccinations WHERE pet_id=?", (pet_id,)).fetchall()
    else:
        vax = conn.execute("SELECT v.*, p.name as pet_name FROM vaccinations v JOIN pets p ON v.pet_id = p.pet_id").fetchall()
    conn.close()
    return vax

def update_vaccination(vaccine_id: int, vaccine_name: str, date_given: str, next_due: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE vaccinations SET vaccine_name=?, date_given=?, next_due=? WHERE vaccine_id=?", 
                  (vaccine_name, date_given, next_due, vaccine_id))
    conn.commit()
    conn.close()

def delete_vaccination(vaccine_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vaccinations WHERE vaccine_id=?", (vaccine_id,))
    conn.commit()
    conn.close()

# Medical Records CRUD
def add_medical_record(pet_id, diagnosis, treatment, date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO medical_records (pet_id, diagnosis, treatment, date) VALUES (?, ?, ?, ?)", 
                  (pet_id, diagnosis, treatment, date))
    conn.commit()
    conn.close()

def get_medical_records(pet_id: Optional[int] = None) -> List[sqlite3.Row]:
    conn = get_db_connection()
    if pet_id:
        recs = conn.execute("SELECT * FROM medical_records WHERE pet_id=?", (pet_id,)).fetchall()
    else:
        recs = conn.execute("SELECT m.*, p.name as pet_name FROM medical_records m JOIN pets p ON m.pet_id = p.pet_id").fetchall()
    conn.close()
    return recs

def update_medical_record(record_id: int, diagnosis: str, treatment: str, date: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE medical_records SET diagnosis=?, treatment=?, date=? WHERE record_id=?", 
                  (diagnosis, treatment, date, record_id))
    conn.commit()
    conn.close()

def delete_medical_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medical_records WHERE record_id=?", (record_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":

    init_db()
    print("Database initialized successfully.")
