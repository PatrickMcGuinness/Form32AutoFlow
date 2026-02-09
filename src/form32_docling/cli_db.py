"""Command-line interface for Form32 database management."""

import argparse
import sys

from sqlalchemy.orm import Session

from form32_docling.api.db import InjuryEvaluation, Patient, SessionLocal, init_db


def list_patients(db: Session) -> None:
    """List all patients in the database."""
    patients = db.query(Patient).all()
    if not patients:
        print("No patient records found.")
        return

    print(f"{'ID':<5} | {'Name':<25} | {'Exam Date':<15} | {'Status':<10}")
    print("-" * 65)
    for p in patients:
        print(f"{p.id:<5} | {str(p.patient_name)[:25]:<25} | {str(p.exam_date):<15} | {p.status:<10}")

def delete_patient(db: Session, patient_id: int) -> None:
    """Delete a specific patient record."""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        print(f"Error: Patient with ID {patient_id} not found.")
        return

    db.delete(db_patient)
    db.commit()
    print(f"Successfully deleted patient ID {patient_id} ({db_patient.patient_name}).")

def clean_db(db: Session) -> None:
    """Remove all data from the database."""
    confirm = input("Are you sure you want to delete ALL data from the database? (y/N): ")
    if confirm.lower() != 'y':
        print("Cleanup cancelled.")
        return

    try:
        # Delete children first
        db.query(InjuryEvaluation).delete()
        db.query(Patient).delete()
        db.commit()
        print("Successfully cleaned the database.")
    except Exception as e:
        db.rollback()
        print(f"Error cleaning database: {e}")

def main() -> int:
    """Main entry point for form32-db CLI."""
    parser = argparse.ArgumentParser(
        prog="form32-db",
        description="Manage Form32 GUI database",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    subparsers.add_parser("list", help="List all patient records")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a specific patient record")
    delete_parser.add_argument("id", type=int, help="Patient ID to delete")

    # Clean command
    subparsers.add_parser("clean", help="Remove all records from the database")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    init_db()
    db = SessionLocal()
    try:
        if args.command == "list":
            list_patients(db)
        elif args.command == "delete":
            delete_patient(db, args.id)
        elif args.command == "clean":
            clean_db(db)
        return 0
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
