from fastapi import FastAPI, Depends, HTTPException, status, Body, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from sqlalchemy import func

import models, schemas, database
from database import engine, get_db
from utils import hash_password, verify_password

import inspect

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS (must be before including routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
     'http://192.168.1.5:5173'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router with prefix '/api'
router = APIRouter(prefix="/api")

@app.on_event("startup")
def print_routes():
    print("\nRegistered routes:")
    for route in app.routes:
        if hasattr(route, 'methods'):
            print(f"{list(route.methods)} {route.path}")
    print()

@router.get("/")
def read_root():
    return {"message": "Hello World"}

@router.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(f"Received registration data: {user}")
    try:
        # Check if email already exists
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            print(f"Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check for unique studentId if provided
        if user.studentId:
            existing_student = db.query(models.User).filter(models.User.studentId == user.studentId).first()
            if existing_student:
                print(f"Student ID already exists: {user.studentId}")
                raise HTTPException(status_code=400, detail="Student ID already exists")
        
        # Check for unique instructorId if provided
        if user.instructorId:
            existing_instructor = db.query(models.User).filter(models.User.instructorId == user.instructorId).first()
            if existing_instructor:
                print(f"Instructor ID already exists: {user.instructorId}")
                raise HTTPException(status_code=400, detail="Instructor ID already exists")
        
        # Hash the password
        hashed_pw = hash_password(user.password)
        
        # Set is_active to False for students and instructors (pending approval), True for others
        is_active = False if user.role in ['student', 'instructor'] else True
        
        # Create new user
        new_user = models.User(
            name=user.name,
            email=user.email,
            password_hash=hashed_pw,
            role=user.role,
            dob=user.dob,
            address=user.address,
            studentId=user.studentId,
            instructorId=user.instructorId,
            is_active=is_active
        )
        
        print(f"Creating new user: {new_user.name} with email: {new_user.email}")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"User created successfully with ID: {new_user.id}")
        return new_user
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except IntegrityError as e:
        print(f"Database integrity error: {str(e)}")
        db.rollback()
        if "email" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        elif "studentid" in str(e).lower():
            raise HTTPException(status_code=400, detail="Student ID already exists")
        elif "instructorid" in str(e).lower():
            raise HTTPException(status_code=400, detail="Instructor ID already exists")
        else:
            raise HTTPException(status_code=400, detail="Registration failed - duplicate data")
    except ValidationError as e:
        print(f"Validation error: {e.errors()}")
        raise HTTPException(status_code=400, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        print(f"Registration error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/auth/login")
def login(form: schemas.LoginSchema, db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.email == form.email).first()
        if not user:
            # Email not found
            raise HTTPException(status_code=401, detail="Email not found")
        if not verify_password(form.password, user.password_hash):
            # Password incorrect
            raise HTTPException(status_code=401, detail="Incorrect password")
        # Prevent inactive students and instructors from logging in
        if user.role in ['student', 'instructor'] and not user.is_active:
            raise HTTPException(status_code=403, detail="Account pending approval. Please wait for approval before logging in.")
        return {"user": user}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/auth/profile", response_model=schemas.User)
def get_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/auth/set-school")
def set_school(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    school = data.get("school")
    if not email or not school:
        raise HTTPException(status_code=400, detail="Email and school are required")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.school = school
    db.commit()
    return {"message": "School updated"}

# Endpoint for instructors to get all pending students
@router.get("/students/pending", response_model=List[schemas.User])
def get_pending_students(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == 'student', models.User.is_active == False).all()

# Endpoint for instructors to approve a student
@router.post("/students/approve/{student_id}")
def approve_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.User).filter(models.User.id == student_id, models.User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail='Student not found')
    student.is_active = True
    db.commit()
    return {'message': 'Student approved'}

# Endpoint for admins to get all pending instructors
@router.get("/instructors/pending", response_model=List[schemas.User])
def get_pending_instructors(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == 'instructor', models.User.is_active == False).all()

# Endpoint for admins to approve an instructor
@router.post("/instructors/approve/{instructor_id}")
def approve_instructor(instructor_id: int, db: Session = Depends(get_db)):
    instructor = db.query(models.User).filter(models.User.id == instructor_id, models.User.role == 'instructor').first()
    if not instructor:
        raise HTTPException(status_code=404, detail='Instructor not found')
    instructor.is_active = True
    db.commit()
    return {'message': 'Instructor approved'}

@router.get("/students/by-id/{student_id}", response_model=schemas.User)
def get_student_by_id(student_id: str, db: Session = Depends(get_db)):
    student = db.query(models.User).filter(models.User.studentId == student_id, models.User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/users", response_model=List[schemas.User])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# --- Admin CRUD Endpoints ---
@router.get("/admins", response_model=List[schemas.User])
def get_admins(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == 'admin').all()

@router.post("/admins", response_model=schemas.User)
def create_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_admin = models.User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role="admin",
        dob=user.dob,
        address=user.address,
        is_active=True
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@router.put("/admins/{admin_id}", response_model=schemas.User)
def update_admin(admin_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    admin = db.query(models.User).filter(models.User.id == admin_id, models.User.role == 'admin').first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    admin.name = user.name
    admin.email = user.email
    if user.password:
        admin.password_hash = hash_password(user.password)
    admin.dob = user.dob
    admin.address = user.address
    db.commit()
    db.refresh(admin)
    return admin

@router.delete("/admins/{admin_id}")
def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(models.User).filter(models.User.id == admin_id, models.User.role == 'admin').first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    db.delete(admin)
    db.commit()
    return {"detail": "Admin deleted"}

@router.get("/instructors", response_model=List[schemas.User])
def get_instructors(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == 'instructor').all()

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: dict = Body(...), db: Session = Depends(get_db)):
    print(f"Updating user {user_id} with data: {user_update}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Only update fields that are present in the request
    for key, value in user_update.items():
        print(f"Setting {key} to {value}")
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    print(f"Updated user: {user}")
    return user

# --- School CRUD Endpoints ---
from models import School as SchoolModel
from schemas import School as SchoolSchema, SchoolCreate, SchoolBase

@router.get("/schools", response_model=List[SchoolSchema])
def get_schools(db: Session = Depends(get_db)):
    return db.query(SchoolModel).all()

@router.post("/schools", response_model=SchoolSchema)
def create_school(school: SchoolCreate, db: Session = Depends(get_db)):
    db_school = db.query(SchoolModel).filter(SchoolModel.name == school.name).first()
    if db_school:
        raise HTTPException(status_code=400, detail="School already exists")
    new_school = SchoolModel(name=school.name)
    db.add(new_school)
    db.commit()
    db.refresh(new_school)
    return new_school

@router.put("/schools/{school_id}", response_model=SchoolSchema)
def update_school(school_id: int, school: SchoolBase, db: Session = Depends(get_db)):
    db_school = db.query(SchoolModel).filter(SchoolModel.id == school_id).first()
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")
    db_school.name = school.name
    db_school.archived = school.archived if school.archived is not None else db_school.archived
    db.commit()
    db.refresh(db_school)
    return db_school

@router.post("/schools/{school_id}/archive", response_model=SchoolSchema)
def archive_school(school_id: int, db: Session = Depends(get_db)):
    db_school = db.query(SchoolModel).filter(SchoolModel.id == school_id).first()
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")
    db_school.archived = True
    db.commit()
    db.refresh(db_school)
    return db_school

@router.post("/schools/{school_id}/unarchive", response_model=SchoolSchema)
def unarchive_school(school_id: int, db: Session = Depends(get_db)):
    db_school = db.query(SchoolModel).filter(SchoolModel.id == school_id).first()
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")
    db_school.archived = False
    db.commit()
    db.refresh(db_school)
    return db_school

@router.get("/students/by-instructor/{instructor_id}", response_model=List[schemas.User])
def get_students_by_instructor(instructor_id: int, db: Session = Depends(get_db)):
    instructor = db.query(models.User).filter(models.User.id == instructor_id, models.User.role == 'instructor').first()
    if not instructor or not instructor.school:
        return []
    return db.query(models.User).filter(
        models.User.role == 'student',
        models.User.school == instructor.school
    ).all()

from models import Attendance as AttendanceModel
from schemas import Attendance as AttendanceSchema, AttendanceCreate

@router.post("/attendance/mark", response_model=AttendanceSchema)
def mark_attendance(att: AttendanceCreate, db: Session = Depends(get_db)):
    print(f"[LOG] /attendance/mark called with: {att}")
    att_date = datetime.utcnow()
    new_att = AttendanceModel(
        student_id=att.student_id,
        date_time=att_date,  # <-- use date_time, not date
        status=att.status
    )
    db.add(new_att)
    db.commit()
    db.refresh(new_att)
    print(f"[LOG] Attendance record created: {new_att}")
    return {
        "id": new_att.id,
        "student_id": new_att.student_id,
        "date": new_att.date_time,  # <-- return as 'date' for frontend
        "status": new_att.status
    }

@router.get("/attendance/summary/{student_id}")
def attendance_summary(student_id: int, db: Session = Depends(get_db)):
    present = db.query(AttendanceModel).filter(AttendanceModel.student_id == student_id, AttendanceModel.status == 'present').count()
    absent = db.query(AttendanceModel.student_id == student_id, AttendanceModel.status == 'absent').count()
    total = db.query(AttendanceModel).filter(AttendanceModel.student_id == student_id).count()
    return {"present": present, "absent": absent, "total": total}

@router.get("/attendance/by-student/{student_id}")
def get_attendance_by_student(student_id: str, db: Session = Depends(get_db)):
    print(f"[LOG] /attendance/by-student/{student_id} called")
    student = db.query(models.User).filter(models.User.studentId == student_id, models.User.role == 'student').first()
    if not student:
        print(f"[ERROR] Student not found for studentId: {student_id}")
        raise HTTPException(status_code=404, detail="Student not found")
    records = db.query(AttendanceModel).filter(AttendanceModel.student_id == student.id).order_by(AttendanceModel.date_time.desc()).all()
    result = [
        {
            "date": record.date_time,  # <-- use date_time, return as 'date'
            "status": record.status
        }
        for record in records
    ]
    print(f"[LOG] Returning {len(result)} attendance records for studentId: {student_id}")
    return result

@router.put("/attendance/by-student/{studentId}")
def update_attendance_by_student(studentId: str, data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Update today's attendance for a student by studentId. Accepts 'status' (required) and 'date' (optional) in the body.
    """
    student = db.query(models.User).filter(models.User.studentId == studentId, models.User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    # Find today's attendance record
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    end = start + timedelta(days=1)
    att = db.query(AttendanceModel).filter(
        AttendanceModel.student_id == student.id,
        AttendanceModel.date_time >= start,
        AttendanceModel.date_time < end
    ).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance record for today not found")
    status = data.get("status")
    date = data.get("date")
    if status:
        att.status = status
    if date:
        att.date_time = date
    db.commit()
    db.refresh(att)
    return {"message": "Attendance updated", "attendance": {"id": att.id, "student_id": att.student_id, "date": att.date_time, "status": att.status}}

@router.get("/attendance")
def get_all_attendance(db: Session = Depends(get_db)):
    print("[LOG] /attendance called")
    records = db.query(AttendanceModel).all()
    result = []
    for record in records:
        student = db.query(models.User).filter(models.User.id == record.student_id).first()
        if student:
            result.append({
                "studentId": student.studentId,
                "name": student.name,
                "status": record.status,
                "date": record.date_time
            })
    print(f"[LOG] Returning {len(result)} attendance records")
    return result

# Include the router in the app (after CORS and after all endpoints are defined)
app.include_router(router)

# --- Add this function to create a default super admin ---
def create_default_super_admin(db):
    from models import User  # adjust if your User model import is different
    super_admin_email = "superadmin@email.com"
    super_admin_password = "superadmin123"  # Change after first login!
    user = db.query(User).filter(User.email == super_admin_email).first()
    if not user:
        super_admin = User(
            name="Super Admin",
            email=super_admin_email,
            password_hash=hash_password(super_admin_password),
            role="superadmin",
            dob="1970-01-01",
            address="Head Office",
            is_active=True
        )
        db.add(super_admin)
        db.commit()
        print("Default super admin created!")
    else:
        print("Super admin already exists.")

if __name__ == "__main__":
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    # Create default super admin
    db = next(get_db())
    create_default_super_admin(db)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# To run the application, use the following command:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Note: The `--reload` flag is for development only. For production, use a proper ASGI server like Daphne or Uvicorn without `--reload`.

# If you need to generate or update the requirements.txt file, run the following command:
# pip freeze > requirements.txt