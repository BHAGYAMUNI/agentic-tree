import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from venv.models import Base, User, TreeSession
from venv.auth import hash_password

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./dev.db')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Create test users
    test_users = [
        {'email': 'demo@example.com', 'password': 'demo123'},
        {'email': 'test@example.com', 'password': 'test123'},
        {'email': 'user@example.com', 'password': 'user123'},
    ]
    
    for user_data in test_users:
        if not db.query(User).filter(User.email == user_data['email']).first():
            user = User(
                email=user_data['email'],
                hashed_password=hash_password(user_data['password'])
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create sample tree for first user
            if user_data['email'] == 'demo@example.com':
                tree = TreeSession(
                    name='sample tree',
                    user_id=user.id,
                    tree_data={
                        'value': 7,
                        'left': {
                            'value': 5,
                            'left': {'value': 3, 'left': None, 'right': None},
                            'right': None
                        },
                        'right': {'value': 9, 'left': None, 'right': None}
                    }
                )
                db.add(tree)
                db.commit()
    
    db.close()
    print("✅ Seeding complete!")
    print("\n📝 Test Credentials:")
    print("=" * 40)
    for user_data in test_users:
        print(f"Email: {user_data['email']}")
        print(f"Password: {user_data['password']}")
        print("-" * 40)


if __name__ == '__main__':
    seed()
