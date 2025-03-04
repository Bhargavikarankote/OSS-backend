from fastapi import FastAPI, Depends, HTTPException, Form
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt

# ✅ FastAPI App Initialization
app = FastAPI()

# ✅ Correct MySQL Connection String
DATABASE_URL = "mysql+pymysql://root:root@localhost/data"  # Update credentials if needed
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ✅ Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(15), nullable=False)
    preferred_language = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)

class Mentor(Base):
    __tablename__ = "mentors"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    location = Column(String(100), nullable=False)
    expertise = Column(String(255), nullable=False)
    experience = Column(Integer, nullable=False)

class ServiceProvider(Base):
    __tablename__ = "service_providers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    service_type = Column(String(255), nullable=False)
    experience = Column(Integer, nullable=False)
    pricing_model = Column(String(100), nullable=False)
    availability = Column(String(50), nullable=False)

# ✅ Create Database Tables
Base.metadata.create_all(bind=engine)

# ✅ Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Password Hashing Function
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# ==============================  USER APIs  ==============================
@app.post("/register/")
def register_user(
    name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    preferred_language: str = Form(...),
    role: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(password)
    db_user = User(
        name=name,
        email=email,
        phone=phone,
        preferred_language=preferred_language,
        role=role,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "phone": db_user.phone,
        "preferred_language": db_user.preferred_language,
        "role": db_user.role
    }



@app.post("/users/")
def fetch_users(skip: int = Form(0), limit: int = Form(10), db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

# ==============================  MENTOR APIs  ==============================
@app.post("/mentors/")
def register_mentor(
    name: str = Form(...),
    age: int = Form(...),
    location: str = Form(...),
    expertise: str = Form(...),
    experience: int = Form(...),
    db: Session = Depends(get_db)
):
    db_mentor = Mentor(
        name=name,
        age=age,
        location=location,
        expertise=expertise,
        experience=experience
    )
    db.add(db_mentor)
    db.commit()
    db.refresh(db_mentor)

    return {
        "id": db_mentor.id,
        "name": db_mentor.name,
        "age": db_mentor.age,
        "location": db_mentor.location,
        "expertise": db_mentor.expertise,
        "experience": db_mentor.experience
    }

@app.get("/mentors/")
def fetch_mentors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Mentor).offset(skip).limit(limit).all()



@app.post("/mentors/search/")
def search_mentors_by_expertise(expertise: str = Form(...), db: Session = Depends(get_db)):
    mentors = db.query(Mentor).filter(Mentor.expertise.ilike(f"%{expertise}%")).all()
    if not mentors:
        raise HTTPException(status_code=404, detail="No mentors found with the given expertise")
    return mentors

# ==============================  SERVICE PROVIDER APIs  ==============================
@app.post("/service-providers/")
def register_service_provider(
    name: str = Form(...),
    service_type: str = Form(...),
    experience: int = Form(...),
    pricing_model: str = Form(...),
    availability: str = Form(...),
    db: Session = Depends(get_db)
):
    db_provider = ServiceProvider(
        name=name,
        service_type=service_type,
        experience=experience,
        pricing_model=pricing_model,
        availability=availability
    )
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)

    return {
        "id": db_provider.id,
        "name": db_provider.name,
        "service_type": db_provider.service_type,
        "experience": db_provider.experience,
        "pricing_model": db_provider.pricing_model,
        "availability": db_provider.availability
    }

@app.get("/service-providers/")
def fetch_service_providers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(ServiceProvider).offset(skip).limit(limit).all()

@app.get("/service-providers/{provider_id}")
def fetch_service_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    return provider
 
@app.post("/service-providers/search/")
def search_mentors_by_expertise(service_type: str = Form(...), db: Session = Depends(get_db)):
    provider = db.query(ServiceProvider).filter(ServiceProvider.service_type.ilike(f"%{service_type}%")).all()
    if not provider:
        raise HTTPException(status_code=404, detail="No mentors found with the given expertise")
    return provider