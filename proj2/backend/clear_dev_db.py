"""Clear all rows from development database tables.

Usage:
  python scripts/clear_dev_db.py        # prompts for confirmation
  python scripts/clear_dev_db.py --yes  # run without prompt

This script uses the existing `get_database` function and `tables` list from
`database.py` in this repo to connect and truncate each table inside the
`movie_munchers_dev` database. Foreign key checks are temporarily disabled so
truncation can run in dependency order.

Be careful: this irreversibly removes rows from the development database.
"""
import argparse
import sys
import traceback
from database import get_database, tables, drop_all_tables, create_tables


def main(force: bool = False, recreate: bool = False):
    if not force:
        ans = input("This will DELETE all rows in 'movie_munchers_dev'. Continue? [y/N]: ")
        if ans.lower() not in ("y", "yes"):
            print("Aborted.")
            return

    db = get_database("movie_munchers_dev")
    cursor = db.cursor()
    # Verify which database we're connected to
    try:
        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()[0]
        print(f"Connected to database: {current_db}")
    except Exception:
        current_db = None
    try:
        print("Fetching table list from server...")
        # Prefer to enumerate actual tables in the connected DB to avoid stale/static lists
        try:
            cursor.execute("SHOW TABLES")
            fetched = cursor.fetchall()
            db_tables = [row[0] for row in fetched]
        except Exception:
            # fall back to static list from database.py
            db_tables = list(tables)

        if not db_tables:
            print("No tables found in database. Nothing to do.")
            return

        # If user wants to drop and recreate schema (stronger reset), support that
        if recreate and force:
            print("--recreate flag detected: dropping and recreating schema...")
            try:
                # drop_all_tables and create_tables expect a connection object
                drop_all_tables(db)
                create_tables(db)
                print("Schema dropped and recreated. All tables should be empty.")
            except Exception:
                print("Error during recreate:")
                traceback.print_exc()
            return

        # Print counts before truncation
        print("Row counts before clearing:")
        for t in db_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
                cnt = cursor.fetchone()[0]
            except Exception:
                cnt = 'n/a'
            print(f"  {t}: {cnt}")

        print("Disabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        for t in db_tables:
            try:
                print(f"Clearing table: {t} ...")
                # Use TRUNCATE to reset auto-increment; fallback to DELETE if truncate fails
                try:
                    cursor.execute(f"TRUNCATE TABLE `{t}`")
                except Exception as e_trunc:
                    print(f"  TRUNCATE failed for {t}: {e_trunc}; trying DELETE...")
                    try:
                        cursor.execute(f"DELETE FROM `{t}`")
                    except Exception as e_del:
                        print(f"  DELETE failed for {t}: {e_del}")
                        print("  Full traceback:")
                        traceback.print_exc()
                        continue

                # attempt to reset auto-increment
                try:
                    cursor.execute(f"ALTER TABLE `{t}` AUTO_INCREMENT = 1")
                except Exception as e_ai:
                    print(f"  ALTER AUTO_INCREMENT failed for {t}: {e_ai}")

            except Exception as e:
                print(f"  Warning: failed to clear {t}: {e}")
                print("  Full traceback:")
                traceback.print_exc()

        print("Re-enabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        db.commit()

        # Print counts after truncation
        print("Row counts after clearing:")
        for t in db_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
                cnt = cursor.fetchone()[0]
            except Exception:
                cnt = 'n/a'
            print(f"  {t}: {cnt}")

        print("Done: development database cleared.")
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clear all rows from movie_munchers_dev tables')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--recreate', action='store_true', help='Drop all tables and recreate schema instead of truncating')
    args = parser.parse_args()
    main(force=args.yes, recreate=args.recreate)
