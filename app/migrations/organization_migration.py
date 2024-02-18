from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from app.models import User, Organization, Organization_User
import uuid
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
DATABASE_URL = os.getenv("DATABASE_URL_ADDRESS")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    # Create Session
    session = SessionLocal()
    try:
        # Iterate over all users
        for user in session.query(User).all():
            print(user)
            # Check if an organization with the same name already exists
            organization = session.query(Organization).filter_by(name=user.company).first()
            print(organization)
            if organization is None:
                # If not, create a new organization
                organization = Organization(
                    name=user.company,
                    business_type=user.business_type,
                    uuid='org-' + str(uuid.uuid4()),
                    created_on=datetime.now(),
                    updated_on=datetime.now()
                )
                # Add the new organization to the session
                session.add(organization)
                # Flush the session to assign an ID to the new organization
                session.flush()
            # Create a new organization_user record for the new organization
            organization_user = Organization_User(
                organization_id=organization.id,
                user_id=user.id,
                uuid='ous-' + str(uuid.uuid4()),
                created_on=datetime.now(),
                updated_on=datetime.now()
            )
            # Add the new organization_user record to the session
            session.add(organization_user)
        # Commit the changes
        session.commit()
        for user in session.query(User).all():
            # Check if an organization with the same name already exists
            organization = session.query(Organization).filter_by(name=user.company).first()
            if organization is None:
                # If not, create a new organization
                organization = Organization(
                    name=user.company,
                    business_type=user.business_type,
                    uuid='org-' + str(uuid.uuid4()),
                    created_on=datetime.now(),
                    updated_on=datetime.now()
                )
                # Add the new organization to the session
                session.add(organization)
                # Flush the session to assign an ID to the new organization
                session.flush()
            # Create a new organization_user record for the new organization
            organization_user = Organization_User(
                organization_id=organization.id,
                user_id=user.id,
                uuid='ous-' + str(uuid.uuid4()),
                created_on=datetime.now(),
                updated_on=datetime.now()
            )
            # Add the new organization_user record to the session
            session.add(organization_user)
        # Commit the changes
        session.commit()
    except exc.IntegrityError as e:
        session.rollback()
        print(str(e))
    finally:
        session.close()

if __name__ == "__main__":
    main()