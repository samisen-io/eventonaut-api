from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Organization, Organization_User
import uuid

DATABASE_URL = "postgresql://user:password@localhost:5432/mydatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    # Create Session
    session = SessionLocal()
    try:
        # Iterate over all users
        for user in session.query(User).all():
            # Create a new organization for each user
            organization = Organization(
                name=user.company,
                business_type=user.business_type,
                uuid='org-' + str(uuid.uuid4())
            )
            # Add the new organization to the session
            session.add(organization)
            # Flush the session to assign an ID to the new organization
            session.flush()
            # Create a new organization_user record for the new organization
            organization_user = Organization_User(
                organization_id=organization.id,
                user_id=user.id,
                uuid='ous-' + str(uuid.uuid4())
            )
            # Add the new organization_user record to the session
            session.add(organization_user)
        # Commit the changes
        session.commit()
    except Exception as e:
        session.rollback()
        print(str(e))
    finally:
        session.close()

if __name__ == "__main__":
    main()