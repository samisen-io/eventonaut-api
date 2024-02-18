from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from app.models import User, Role, User_Role
import uuid
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL_ADDRESS")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    session = SessionLocal()
    try:
        roles = [
            {"name": "ATTENDEE", "description": "Eventonaut application user"},
            {"name": "ORGANIZATION_ADMIN", "description": "Organization creator and Supreme leader of a particular Organizer"},
            {"name": "ORGANIZATION_USER", "description": "This user can have limited access on Command Center"},
        ]
        for role_data in roles:
            role = session.query(Role).filter_by(name=role_data["name"]).first()
            if role is None:
                role_data["uuid"] = "rol-" + str(uuid.uuid4())
                role_data["created_on"] = datetime.now()
                role_data["updated_on"] = datetime.now()
                role = Role(**role_data)
                session.add(role)
        session.commit()

        for user in session.query(User).all():
            if user.role == 'organizer':
                role_name = 'ORGANIZATION_ADMIN'
            elif user.role == 'attendee':
                role_name = 'ATTENDEE'
            else:
                continue

            role = session.query(Role).filter_by(name=role_name).first()
            if role is None:
                continue

            user_role = session.query(User_Role).filter_by(user_id=user.id, role_id=role.id).first()
            if user_role is not None:
                continue

            user_roles = session.query(User_Role).filter_by(user_id=user.id).all()
            if len(user_roles) >= 2:
                continue

            user_role = User_Role(
                role_id=role.id,
                user_id=user.id,
                uuid='uro-' + str(uuid.uuid4()),
                created_on=datetime.now(),
                updated_on=datetime.now()
            )
            session.add(user_role)
            print(f"Added user_role record for user {user.id} with role {role.name}")
        session.commit()
        print("Changes committed successfully")
    except exc.IntegrityError as e:
        session.rollback()
        print(str(e))
    finally:
        session.close()

if __name__ == "__main__":
    main()
    print("Print statements added")