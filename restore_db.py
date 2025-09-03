#!/usr/bin/env python3
"""
Interactive Database Restoration Script for Eventonaut API

This script creates all database tables based on the SQLAlchemy models
and optionally seeds the database with initial data.

Features:
- Interactive step-by-step execution
- Comprehensive logging to file
- Error recovery and analysis
- User confirmation at each step

Usage:
    python restore_db.py
"""

import sys
import logging
import traceback
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup logging
log_filename = f"db_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def log_and_print(message, level="info"):
    """Log message and print to console"""
    print(message)
    if level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.info(message)

def wait_for_user_input(prompt="Press Enter to continue or 'q' to quit: "):
    """Wait for user input before proceeding"""
    user_input = input(prompt).strip().lower()
    if user_input == 'q':
        log_and_print("User requested to quit. Exiting...")
        sys.exit(0)
    return user_input

def step_1_check_environment():
    """Step 1: Check environment and imports"""
    log_and_print("\n" + "="*60)
    log_and_print("STEP 1: Checking Environment and Imports")
    log_and_print("="*60)
    
    try:
        # Check .env file
        log_and_print("Checking .env file...")
        if not os.path.exists('.env'):
            log_and_print("⚠️  Warning: .env file not found in current directory", "warning")
        else:
            log_and_print("✓ .env file found")
        
        # Check DATABASE_URL_ADDRESS
        database_url = os.getenv("DATABASE_URL_ADDRESS")
        if not database_url:
            log_and_print("❌ DATABASE_URL_ADDRESS not found in environment variables", "error")
            log_and_print("Please check your .env file and ensure DATABASE_URL_ADDRESS is set", "error")
            return False
        else:
            # Hide password in log
            safe_url = database_url.split('@')[1] if '@' in database_url else database_url
            log_and_print(f"✓ DATABASE_URL_ADDRESS found: ...@{safe_url}")
        
        # Try importing modules
        log_and_print("Importing application modules...")
        try:
            from app.database import Base, SQLALCHEMY_DATABASE_URL
            from app import models
            log_and_print("✓ Successfully imported app.database and app.models")
            
            # Store in globals for other functions
            globals()['Base'] = Base
            globals()['SQLALCHEMY_DATABASE_URL'] = SQLALCHEMY_DATABASE_URL
            globals()['models'] = models
            
        except ImportError as e:
            log_and_print(f"❌ Error importing modules: {e}", "error")
            log_and_print("Make sure you're running this script from the project root directory", "error")
            log_and_print("Required files: app/database.py, app/models.py", "error")
            return False
        
        log_and_print("✅ Step 1 completed successfully!")
        return True
        
    except Exception as e:
        log_and_print(f"❌ Unexpected error in Step 1: {e}", "error")
        log_and_print(f"Traceback: {traceback.format_exc()}", "error")
        return False


def step_2_create_engine():
    """Step 2: Create database engine"""
    log_and_print("\n" + "="*60)
    log_and_print("STEP 2: Creating Database Engine")
    log_and_print("="*60)
    
    try:
        database_url = globals().get('SQLALCHEMY_DATABASE_URL')
        if not database_url:
            log_and_print("❌ DATABASE_URL_ADDRESS not available", "error")
            return None
        
        log_and_print("Creating SQLAlchemy engine...")
        log_and_print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'Hidden'}")
        
        # Create engine with detailed logging
        engine = create_engine(database_url, echo=False)  # Set to False to reduce log noise
        log_and_print("✓ Database engine created successfully")
        
        log_and_print("✅ Step 2 completed successfully!")
        return engine
        
    except Exception as e:
        log_and_print(f"❌ Error creating database engine: {e}", "error")
        log_and_print(f"Traceback: {traceback.format_exc()}", "error")
        return None


def step_3_test_connection(engine):
    """Step 3: Test database connection"""
    log_and_print("\n" + "="*60)
    log_and_print("STEP 3: Testing Database Connection")
    log_and_print("="*60)
    
    try:
        log_and_print("Attempting to connect to database...")
        
        with engine.connect() as connection:
            log_and_print("Connection established, testing with simple query...")
            result = connection.execute(text("SELECT 1 as test"))
            test_result = result.fetchone()
            log_and_print(f"Test query result: {test_result}")
            
            # Get database info
            log_and_print("Fetching database information...")
            db_info = connection.execute(text("SELECT version()")).fetchone()
            log_and_print(f"Database version: {db_info[0]}")
            
        log_and_print("✓ Database connection successful")
        log_and_print("✅ Step 3 completed successfully!")
        return True
        
    except Exception as e:
        log_and_print(f"❌ Database connection failed: {e}", "error")
        log_and_print(f"Traceback: {traceback.format_exc()}", "error")
        log_and_print("Common issues:", "error")
        log_and_print("- Check if PostgreSQL is running", "error")
        log_and_print("- Verify DATABASE_URL_ADDRESS in .env file", "error")
        log_and_print("- Check database credentials and permissions", "error")
        return False


def step_4_check_existing_tables(engine):
    """Step 4: Check existing tables"""
    log_and_print("\n" + "="*60)
    log_and_print("STEP 4: Checking Existing Tables")
    log_and_print("="*60)
    
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            log_and_print(f"Found {len(existing_tables)} existing tables:")
            for table in existing_tables:
                log_and_print(f"  • {table}")
        else:
            log_and_print("No existing tables found")
        
        log_and_print("✅ Step 4 completed successfully!")
        return existing_tables
        
    except Exception as e:
        log_and_print(f"❌ Error checking existing tables: {e}", "error")
        log_and_print(f"Traceback: {traceback.format_exc()}", "error")
        return []


def step_5_drop_tables(engine, existing_tables):
    """Step 5: Drop existing tables (optional)"""
    log_and_print("\n" + "="*60)
    log_and_print("STEP 5: Drop Existing Tables (Optional)")
    log_and_print("="*60)
    
    if not existing_tables:
        log_and_print("No existing tables to drop, skipping this step")
        return True
    
    log_and_print(f"Found {len(existing_tables)} existing tables")
    drop_choice = wait_for_user_input("Do you want to drop existing tables? (y/n/q): ")
    
    if drop_choice != 'y':
        log_and_print("Skipping table drop")
        return True
    
    # Double confirmation for destructive operation
    log_and_print("⚠️  WARNING: This will permanently delete all existing data!")
    confirm = wait_for_user_input("Type 'DELETE' to confirm: ")
    
    if confirm != 'delete':
        log_and_print("Drop operation cancelled")
        return True
    
    try:
        log_and_print("Dropping all existing tables...")
        Base = globals().get('Base')
        Base.metadata.drop_all(bind=engine)
        log_and_print("✓ All tables dropped successfully")
        log_and_print("✅ Step 5 completed successfully!")
        return True
        
    except Exception as e:
        log_and_print(f"❌ Error dropping tables: {e}", "error")
        log_and_print(f"Traceback: {traceback.format_exc()}", "error")
        return False


def step_6_create_tables(engine):
    """Step 6: Create all tables"""
    log_and_print("\n" + "="*60)
    log_and_print("STEP 6: Creating Database Tables")
    log_and_print("="*60)
    
    try:
        Base = globals().get('Base')
        log_and_print("Creating all tables from SQLAlchemy models...")
        
        # Get list of tables that will be created
        table_names = list(Base.metadata.tables.keys())
        log_and_print(f"Tables to create: {len(table_names)}")
        for table_name in table_names:
            log_and_print(f"  • {table_name}")
        
        log_and_print("Starting table creation...")
        Base.metadata.create_all(bind=engine)
        log_and_print("✓ All tables created successfully")
        
        # Verify tables were created
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        log_and_print(f"Verification: {len(created_tables)} tables now exist in database")
        
        log_and_print("✅ Step 6 completed successfully!")
        return True
        
    except Exception as e:
        log_and_print(f"❌ Error creating tables: {e}", "error")
        log_and_print(f"Traceback: {traceback.format_exc()}", "error")
        return False


def step_7_seed_data(engine):
    """Step 7: Seed initial data (optional)"""
    log_and_print("\n" + "="*60)
    log_and_print("STEP 7: Seed Initial Data (Optional)")
    log_and_print("="*60)
    
    seed_choice = wait_for_user_input("Do you want to seed initial data? (y/n/q): ")
    
    if seed_choice != 'y':
        log_and_print("Skipping data seeding")
        return True
    
    from sqlalchemy.orm import sessionmaker
    models = globals().get('models')
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        log_and_print("Starting data seeding process...")
        
        # Create initial roles
        log_and_print("Creating initial roles...")
        roles_data = [
            {"name": "ORGANIZATION_ADMIN", "description": "Organization Administrator"},
            {"name": "ORGANIZATION_USER", "description": "Organization User"},
            {"name": "ATTENDEE", "description": "Event Attendee"},
            {"name": "REGISTRATION_STAFF", "description": "Registration Staff"},
        ]
        
        for role_data in roles_data:
            existing_role = session.query(models.Role).filter_by(name=role_data["name"]).first()
            if not existing_role:
                role = models.Role(
                    uuid=f"role-{role_data['name'].lower()}",
                    name=role_data["name"],
                    description=role_data["description"],
                    created_on=datetime.utcnow(),
                    updated_on=datetime.utcnow()
                )
                session.add(role)
                log_and_print(f"  ✓ Created role: {role_data['name']}")
            else:
                log_and_print(f"  • Role already exists: {role_data['name']}")
        
        # Create organizer statuses
        log_and_print("Creating organizer statuses...")
        organizer_statuses = [
            {"status": "ACTIVE"},
            {"status": "INACTIVE"},
            {"status": "PENDING"},
            {"status": "SUSPENDED"}
        ]
        
        for status_data in organizer_statuses:
            existing_status = session.query(models.OrganizerStatus).filter_by(status=status_data["status"]).first()
            if not existing_status:
                status = models.OrganizerStatus(
                    uuid=f"org-status-{status_data['status'].lower()}",
                    status=status_data["status"],
                    created_on=datetime.utcnow(),
                    updated_on=datetime.utcnow()
                )
                session.add(status)
                log_and_print(f"  ✓ Created organizer status: {status_data['status']}")
            else:
                log_and_print(f"  • Organizer status already exists: {status_data['status']}")
        
        # Create client statuses
        log_and_print("Creating client statuses...")
        client_statuses = [
            {"status": "ACTIVE"},
            {"status": "INACTIVE"},
            {"status": "PENDING"}
        ]
        
        for status_data in client_statuses:
            existing_status = session.query(models.ClientStatus).filter_by(status=status_data["status"]).first()
            if not existing_status:
                status = models.ClientStatus(
                    uuid=f"client-status-{status_data['status'].lower()}",
                    status=status_data["status"],
                    created_on=datetime.utcnow(),
                    updated_on=datetime.utcnow()
                )
                session.add(status)
                log_and_print(f"  ✓ Created client status: {status_data['status']}")
            else:
                log_and_print(f"  • Client status already exists: {status_data['status']}")
        
        # Create event statuses
        log_and_print("Creating event statuses...")
        event_statuses = [
            {"status": "DRAFT"},
            {"status": "PUBLISHED"},
            {"status": "LIVE"},
            {"status": "COMPLETED"},
            {"status": "CANCELLED"}
        ]
        
        for status_data in event_statuses:
            existing_status = session.query(models.EventStatus).filter_by(status=status_data["status"]).first()
            if not existing_status:
                status = models.EventStatus(
                    uuid=f"event-status-{status_data['status'].lower()}",
                    status=status_data["status"],
                    created_on=datetime.utcnow(),
                    updated_on=datetime.utcnow()
                )
                session.add(status)
                log_and_print(f"  ✓ Created event status: {status_data['status']}")
            else:
                log_and_print(f"  • Event status already exists: {status_data['status']}")
        
        # Create session statuses
        log_and_print("Creating session statuses...")
        session_statuses = [
            {"status": "SCHEDULED"},
            {"status": "LIVE"},
            {"status": "COMPLETED"},
            {"status": "CANCELLED"}
        ]
        
        for status_data in session_statuses:
            existing_status = session.query(models.Sessionstatus).filter_by(status=status_data["status"]).first()
            if not existing_status:
                status = models.Sessionstatus(
                    uuid=f"session-status-{status_data['status'].lower()}",
                    status=status_data["status"],
                    created_on=datetime.utcnow(),
                    updated_on=datetime.utcnow()
                )
                session.add(status)
                log_and_print(f"  ✓ Created session status: {status_data['status']}")
            else:
                log_and_print(f"  • Session status already exists: {status_data['status']}")
        
        # Create attendee statuses
        log_and_print("Creating attendee statuses...")
        attendee_statuses = [
            {"status": "REGISTERED"},
            {"status": "CHECKED_IN"},
            {"status": "NO_SHOW"},
            {"status": "CANCELLED"}
        ]
        
        for status_data in attendee_statuses:
            existing_status = session.query(models.AttendeeStatus).filter_by(status=status_data["status"]).first()
            if not existing_status:
                status = models.AttendeeStatus(
                    uuid=f"attendee-status-{status_data['status'].lower()}",
                    status=status_data["status"],
                    created_on=datetime.utcnow(),
                    updated_on=datetime.utcnow()
                )
                session.add(status)
                log_and_print(f"  ✓ Created attendee status: {status_data['status']}")
            else:
                log_and_print(f"  • Attendee status already exists: {status_data['status']}")
        
        # Create registration order item types
        log_and_print("Creating registration order item types...")
        order_item_types = [
            {"code": "TICKET", "description": "Event Ticket"},
            {"code": "ADDON", "description": "Add-on Item"},
            {"code": "MERCHANDISE", "description": "Merchandise"},
            {"code": "FOOD", "description": "Food & Beverage"}
        ]
        
        for item_type_data in order_item_types:
            existing_type = session.query(models.RegistrationOrderItemType).filter_by(code=item_type_data["code"]).first()
            if not existing_type:
                item_type = models.RegistrationOrderItemType(
                    code=item_type_data["code"],
                    description=item_type_data["description"]
                )
                session.add(item_type)
                log_and_print(f"  ✓ Created order item type: {item_type_data['code']}")
            else:
                log_and_print(f"  • Order item type already exists: {item_type_data['code']}")
        
        log_and_print("Committing changes to database...")
        session.commit()
        log_and_print("✓ Initial seed data inserted successfully")
        log_and_print("✅ Step 7 completed successfully!")
        return True
        
    except Exception as e:
        session.rollback()
        log_and_print(f"❌ Error seeding data: {e}", "error")
        log_and_print(f"Traceback: {traceback.format_exc()}", "error")
        return False
    finally:
        session.close()


def step_8_final_verification(engine):
    """Step 8: Final verification and summary"""
    log_and_print("\n" + "="*60)
    log_and_print("STEP 8: Final Verification and Summary")
    log_and_print("="*60)
    
    try:
        with engine.connect() as connection:
            # Get table names and counts
            log_and_print("Retrieving final database state...")
            
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            log_and_print(f"📊 Database restoration completed successfully!")
            log_and_print(f"Total tables in database: {len(tables)}")
            log_and_print("\nCreated tables:")
            
            for table in tables:
                try:
                    count_result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.fetchone()[0]
                    log_and_print(f"  • {table} ({count} rows)")
                except Exception as e:
                    log_and_print(f"  • {table} (count error: {e})")
            
            log_and_print("✅ Step 8 completed successfully!")
            return True
                
    except Exception as e:
        log_and_print(f"❌ Error in final verification: {e}", "error")
        log_and_print(f"Traceback: {traceback.format_exc()}", "error")
        return False


def main():
    """Main interactive execution flow"""
    log_and_print("🚀 Interactive Database Restoration Script")
    log_and_print(f"📝 Log file: {log_filename}")
    log_and_print("="*60)
    
    engine = None
    existing_tables = []
    
    try:
        # Step 1: Check environment and imports
        if not step_1_check_environment():
            log_and_print("❌ Step 1 failed. Cannot continue.", "error")
            return
        
        wait_for_user_input()
        
        # Step 2: Create database engine
        engine = step_2_create_engine()
        if not engine:
            log_and_print("❌ Step 2 failed. Cannot continue.", "error")
            return
        
        wait_for_user_input()
        
        # Step 3: Test database connection
        if not step_3_test_connection(engine):
            log_and_print("❌ Step 3 failed. Cannot continue.", "error")
            return
        
        wait_for_user_input()
        
        # Step 4: Check existing tables
        existing_tables = step_4_check_existing_tables(engine)
        
        wait_for_user_input()
        
        # Step 5: Drop existing tables (optional)
        if not step_5_drop_tables(engine, existing_tables):
            log_and_print("❌ Step 5 failed. Cannot continue.", "error")
            return
        
        wait_for_user_input()
        
        # Step 6: Create tables
        if not step_6_create_tables(engine):
            log_and_print("❌ Step 6 failed. Cannot continue.", "error")
            return
        
        wait_for_user_input()
        
        # Step 7: Seed initial data (optional)
        if not step_7_seed_data(engine):
            log_and_print("❌ Step 7 failed, but continuing...", "warning")
        
        wait_for_user_input()
        
        # Step 8: Final verification
        step_8_final_verification(engine)
        
        log_and_print("\n" + "="*60)
        log_and_print("🎉 DATABASE RESTORATION COMPLETED SUCCESSFULLY!")
        log_and_print(f"📝 Full log saved to: {log_filename}")
        log_and_print("="*60)
        
    except KeyboardInterrupt:
        log_and_print("\n⚠️  Process interrupted by user", "warning")
    except Exception as e:
        log_and_print(f"\n❌ Unexpected error in main execution: {e}", "error")
        log_and_print(f"Traceback: {traceback.format_exc()}", "error")
    finally:
        if engine:
            engine.dispose()
            log_and_print("Database engine disposed")


if __name__ == "__main__":
    main()