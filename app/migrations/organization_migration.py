from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from app.models import User, Organization, Organization_User
import uuid
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL_ADDRESS")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    session = SessionLocal()
    try:
        for user in session.query(User).all():
            print(f"Processing User ID: {user.id}")
            if user.company and user.role != 'attendee':
                organization = session.query(Organization).filter_by(name=user.company).first()
                if organization is None:
                    organization = Organization(
                        name=user.company,
                        uuid='org-' + str(uuid.uuid4()),
                        created_on=datetime.now(),
                        updated_on=datetime.now(),
                        business_type=user.business_type if user.business_type else None
                    )
                    session.add(organization)
                    session.flush()

                user_exists = session.query(User.id).filter_by(id=user.id).scalar() is not None
                if user_exists:
                    organization_user = Organization_User(
                        organization_id=organization.id,
                        user_id=user.id,
                        uuid='ous-' + str(uuid.uuid4()),
                        created_on=datetime.now(),
                        updated_on=datetime.now()
                    )
                    session.add(organization_user)
        print(f"Processed {session.query(User).count()} users.")
        session.commit()
    except exc.IntegrityError as e:
        session.rollback()
        print(f"IntegrityError: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    main()