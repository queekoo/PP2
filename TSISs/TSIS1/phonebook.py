import json
import csv
from connect import connect


# ============================================================
#  3.2 — Filter by group
# ============================================================
def filter_by_group():
    """Show all contacts belonging to a chosen group."""
    conn = connect()
    cur  = conn.cursor()

    # Show available groups
    cur.execute("SELECT id, name FROM groups ORDER BY name")
    groups = cur.fetchall()
    print("\nAvailable groups:")
    for gid, gname in groups:
        print(f"  {gid}. {gname}")

    group_name = input("Enter group name: ").strip()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name AS grp
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        WHERE g.name ILIKE %s
        ORDER BY c.name
    """, (group_name,))

    rows = cur.fetchall()
    if rows:
        print(f"\n{'Name':<20} {'Email':<30} {'Birthday':<12} {'Group'}")
        print("-" * 70)
        for name, email, bday, grp in rows:
            print(f"{name:<20} {str(email or ''):<30} {str(bday or ''):<12} {grp or ''}")
    else:
        print("No contacts found in that group.")

    conn.close()


# ============================================================
#  3.2 — Search by email (partial match)
# ============================================================
def search_by_email():
    """Search contacts by partial email match."""
    pattern = input("Enter email or part of it (e.g. gmail): ").strip()

    conn = connect()
    cur  = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday
        FROM contacts c
        WHERE c.email ILIKE %s
        ORDER BY c.name
    """, (f"%{pattern}%",))

    rows = cur.fetchall()
    if rows:
        print(f"\n{'Name':<20} {'Email':<35} {'Birthday'}")
        print("-" * 65)
        for name, email, bday in rows:
            print(f"{name:<20} {str(email or ''):<35} {str(bday or '')}")
    else:
        print("No contacts found.")

    conn.close()


# ============================================================
#  3.2 — Sort contacts
# ============================================================
def sort_contacts():
    """Display all contacts sorted by name, birthday, or date added."""
    print("\nSort by:")
    print("  1. Name")
    print("  2. Birthday")
    print("  3. Date added")
    choice = input("Choose: ").strip()

    order = {
        "1": "c.name",
        "2": "c.birthday",
        "3": "c.created_at",
    }.get(choice, "c.name")

    conn = connect()
    cur  = conn.cursor()

    cur.execute(f"""
        SELECT c.name, c.email, c.birthday, g.name AS grp, c.created_at
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY {order} NULLS LAST
    """)

    rows = cur.fetchall()
    print(f"\n{'Name':<20} {'Email':<30} {'Birthday':<12} {'Group':<12} {'Added'}")
    print("-" * 90)
    for name, email, bday, grp, created in rows:
        print(f"{name:<20} {str(email or ''):<30} {str(bday or ''):<12} "
              f"{str(grp or ''):<12} {str(created or '')[:10]}")

    conn.close()


# ============================================================
#  3.2 — Paginated navigation (uses existing get_con_pag from Practice 8)
# ============================================================
def paginate():
    """Navigate through contacts page by page using next/prev/quit."""
    page_size = 5
    offset    = 0

    while True:
        conn = connect()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM get_con_pag(%s, %s)", (page_size, offset))
        rows = cur.fetchall()
        conn.close()

        print(f"\n--- Page {offset // page_size + 1} ---")
        if rows:
            for row in rows:
                print(row)
        else:
            print("No more contacts.")

        cmd = input("next / prev / quit: ").strip().lower()
        if cmd == "next":
            if len(rows) == page_size:   # Only go forward if there was a full page
                offset += page_size
            else:
                print("Already on the last page.")
        elif cmd == "prev":
            offset = max(0, offset - page_size)
        elif cmd == "quit":
            break


# ============================================================
#  3.3 — Export contacts to JSON
# ============================================================
def export_json():
    """Export all contacts (with phones and group) to contacts.json."""
    conn = connect()
    cur  = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name AS grp
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY c.name
    """)
    contacts = cur.fetchall()

    result = []
    for cid, name, email, bday, grp in contacts:
        # Fetch all phone numbers for this contact
        cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (cid,))
        phones = [{"phone": p, "type": t} for p, t in cur.fetchall()]

        result.append({
            "name":     name,
            "email":    email,
            "birthday": str(bday) if bday else None,
            "group":    grp,
            "phones":   phones,
        })

    conn.close()

    filename = input("Enter filename (default: contacts.json): ").strip() or "contacts.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(result)} contacts to '{filename}'.")


# ============================================================
#  3.3 — Import contacts from JSON
# ============================================================
def import_json():
    """Import contacts from a JSON file. On duplicate name: ask skip or overwrite."""
    filename = input("Enter JSON filename (default: contacts.json): ").strip() or "contacts.json"

    try:
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    conn = connect()
    cur  = conn.cursor()

    for contact in data:
        name     = contact.get("name", "").strip()
        email    = contact.get("email")
        birthday = contact.get("birthday")
        grp_name = contact.get("group")
        phones   = contact.get("phones", [])

        if not name:
            continue

        # Resolve group_id
        group_id = None
        if grp_name:
            cur.execute("SELECT id FROM groups WHERE name = %s", (grp_name,))
            row = cur.fetchone()
            if row:
                group_id = row[0]
            else:
                cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (grp_name,))
                group_id = cur.fetchone()[0]

        # Check for duplicate name
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            choice = input(f'Duplicate: "{name}" already exists. (s)kip / (o)verwrite? ').strip().lower()
            if choice == "o":
                cur.execute("""
                    UPDATE contacts
                    SET email = %s, birthday = %s, group_id = %s
                    WHERE id = %s
                """, (email, birthday, group_id, existing[0]))
                # Replace phones
                cur.execute("DELETE FROM phones WHERE contact_id = %s", (existing[0],))
                for ph in phones:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (existing[0], ph.get("phone"), ph.get("type"))
                    )
                print(f'  Updated "{name}".')
            else:
                print(f'  Skipped "{name}".')
            continue

        # Insert new contact
        cur.execute("""
            INSERT INTO contacts (name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (name, email, birthday, group_id))
        contact_id = cur.fetchone()[0]

        # Insert phones
        for ph in phones:
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, ph.get("phone"), ph.get("type"))
            )
        print(f'  Imported "{name}".')

    conn.commit()
    conn.close()
    print("Import complete.")


# ============================================================
#  3.3 — Extended CSV import (adds email, birthday, group, phone type)
# ============================================================
def import_csv():
    """
    Import contacts from a CSV file.
    Expected columns: name, phone, type, email, birthday, group
    (type = home/work/mobile)
    """
    filename = input("Enter CSV filename (default: contacts.csv): ").strip() or "contacts.csv"

    try:
        f = open(filename, encoding="utf-8")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    conn = connect()
    cur  = conn.cursor()

    reader = csv.DictReader(f)
    count  = 0

    for row in reader:
        name     = row.get("name", "").strip()
        phone    = row.get("phone", "").strip()
        ptype    = row.get("type", "mobile").strip()
        email    = row.get("email", "").strip() or None
        birthday = row.get("birthday", "").strip() or None
        grp_name = row.get("group", "").strip() or None

        if not name:
            continue

        # Resolve group_id
        group_id = None
        if grp_name:
            cur.execute("SELECT id FROM groups WHERE name = %s", (grp_name,))
            row_g = cur.fetchone()
            if row_g:
                group_id = row_g[0]
            else:
                cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (grp_name,))
                group_id = cur.fetchone()[0]

        # Upsert contact (reuse existing upsert logic via direct SQL)
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            contact_id = existing[0]
            cur.execute("""
                UPDATE contacts SET email = %s, birthday = %s, group_id = %s
                WHERE id = %s
            """, (email, birthday, group_id, contact_id))
        else:
            cur.execute("""
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (name, email, birthday, group_id))
            contact_id = cur.fetchone()[0]

        # Add phone if provided
        if phone:
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, phone, ptype)
            )
        count += 1

    conn.commit()
    conn.close()
    f.close()
    print(f"Imported {count} rows from '{filename}'.")


# ============================================================
#  3.4 — Add phone via stored procedure
# ============================================================
def add_phone():
    """Add a phone number to an existing contact using the add_phone procedure."""
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    print("Type: home / work / mobile")
    ptype = input("Type: ").strip()

    conn = connect()
    cur  = conn.cursor()
    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
    conn.commit()
    conn.close()
    print("Done.")


# ============================================================
#  3.4 — Move to group via stored procedure
# ============================================================
def move_to_group():
    """Move a contact to a group using the move_to_group procedure."""
    name  = input("Contact name: ").strip()
    group = input("Group name: ").strip()

    conn = connect()
    cur  = conn.cursor()
    cur.execute("CALL move_to_group(%s, %s)", (name, group))
    conn.commit()
    conn.close()
    print("Done.")


# ============================================================
#  3.4 — Extended search (uses new search_contacts function)
# ============================================================
def search_extended():
    """Search contacts by name, email, or any phone number."""
    pattern = input("Enter search pattern: ").strip()

    conn = connect()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cur.fetchall()
    conn.close()

    if rows:
        print(f"\n{'Name':<20} {'Email':<30} {'Phone':<15} {'Type':<8} {'Group'}")
        print("-" * 80)
        for name, email, phone, ptype, grp in rows:
            print(f"{str(name or ''):<20} {str(email or ''):<30} "
                  f"{str(phone or ''):<15} {str(ptype or ''):<8} {str(grp or '')}")
    else:
        print("No results.")


# ============================================================
#  Original Practice 8 functions (kept, not re-implemented)
# ============================================================
def search(pattern):
    conn = connect()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM search_con(%s)", (pattern,))
    for row in cur.fetchall():
        print(row)
    conn.close()


def upsert(name, phone):
    conn = connect()
    cur  = conn.cursor()
    cur.execute("CALL upsert_contacts(%s, %s)", (name, phone))
    conn.commit()
    conn.close()


def insert_many():
    conn   = connect()
    cur    = conn.cursor()
    names  = input("Enter names (comma separated): ").split(',')
    phones = input("Enter phones (comma separated): ").split(',')
    cur.execute("CALL insert_many_con(%s, %s)", (names, phones))
    conn.commit()
    conn.close()


def delete(value):
    conn = connect()
    cur  = conn.cursor()
    cur.execute("CALL delete_con(%s)", (value,))
    conn.commit()
    conn.close()


# ============================================================
#  Main menu
# ============================================================
if __name__ == "__main__":
    while True:
        print("\n========== PhoneBook TSIS1 ==========")
        print("--- Practice 8 (existing) ---")
        print("1. Search (name/phone)")
        print("2. Add / Update contact")
        print("3. Insert many")
        print("4. Paginate (simple)")
        print("5. Delete")
        print("--- TSIS1 (new) ---")
        print("6.  Filter by group")
        print("7.  Search by email")
        print("8.  Sort contacts")
        print("9.  Paginated navigation (next/prev)")
        print("10. Export to JSON")
        print("11. Import from JSON")
        print("12. Import from CSV (extended)")
        print("13. Add phone number to contact")
        print("14. Move contact to group")
        print("15. Extended search (name + email + phones)")
        print("0.  Exit")

        choice = input("\nChoose: ").strip()

        if   choice == "1":  search(input("Pattern: "))
        elif choice == "2":  upsert(input("Name: "), input("Phone: "))
        elif choice == "3":  insert_many()
        elif choice == "4":
            limit  = int(input("Limit: "))
            offset = int(input("Offset: "))
            conn = connect(); cur = conn.cursor()
            cur.execute("SELECT * FROM get_con_pag(%s, %s)", (limit, offset))
            for row in cur.fetchall(): print(row)
            conn.close()
        elif choice == "5":  delete(input("Name or phone: "))
        elif choice == "6":  filter_by_group()
        elif choice == "7":  search_by_email()
        elif choice == "8":  sort_contacts()
        elif choice == "9":  paginate()
        elif choice == "10": export_json()
        elif choice == "11": import_json()
        elif choice == "12": import_csv()
        elif choice == "13": add_phone()
        elif choice == "14": move_to_group()
        elif choice == "15": search_extended()
        elif choice == "0":  break
