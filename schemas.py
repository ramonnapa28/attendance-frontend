from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: str
    role: str
<<<<<<< HEAD
    dob: Optional[str] = None
    address: Optional[str] = None
=======
    dob: str
    address: str
>>>>>>> d200206 (Initial commit)
    studentId: Optional[str] = None
    instructorId: Optional[str] = None
    school: Optional[str] = None

    @field_validator('studentId')
    @classmethod
    def validate_student_id(cls, v, info):
        if info.data.get('role') == 'student' and not v:
            raise ValueError('Student ID is required for students')
        return v

    @field_validator('instructorId')
    @classmethod
    def validate_instructor_id(cls, v, info):
        if info.data.get('role') == 'instructor' and not v:
            raise ValueError('Instructor ID is required for instructors')
        return v

class UserCreate(UserBase):
    password: str

class LoginSchema(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
<<<<<<< HEAD
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
=======
    created_at: datetime

    class Config:
        from_attributes = True
>>>>>>> d200206 (Initial commit)

class SchoolBase(BaseModel):
    name: str
    archived: Optional[bool] = False

class SchoolCreate(SchoolBase):
    pass

class School(SchoolBase):
    id: int

    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    student_id: int
    date: Optional[datetime] = None
    status: str

class AttendanceCreate(BaseModel):
    student_id: int
    status: str

class Attendance(AttendanceBase):
    id: int
    class Config:
        from_attributes = True