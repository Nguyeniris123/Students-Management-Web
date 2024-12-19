from email.policy import default
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, validates
from app import db, app
from enum import Enum as RoleEnum, unique
from flask_login import UserMixin
from datetime import date, datetime
import hashlib

ma_hs_khoi10 = str(datetime.now().year)[-2:] + "10000"
ma_hs_khoi11 = str(datetime.now().year)[-2:] + "11000"
ma_hs_khoi12 = str(datetime.now().year)[-2:] + "12000"


class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2
    GIAOVIEN = 3
    NHANVIEN = 4


class Gender(RoleEnum):
    MALE = 1
    FEMALE = 2


class HocKy(RoleEnum):
    HK1 = 1
    HK2 = 2


class KhoiLop(RoleEnum):
    Khoi10 = 1
    Khoi11 = 2
    Khoi12 = 3

class LoaiDiem(RoleEnum):
    diem15p = 1
    diem1tiet = 2
    diemck = 3

class HeSo(RoleEnum):
    heso1 = 1
    heso2= 2
    heso3 = 3


class BuoiDay(RoleEnum):
    sang = 1
    chieu = 2

class TietHoc(RoleEnum):
    tiet1 = 1
    tiet2 = 2
    tiet3 = 3
    tiet4 = 4
    tiet5 = 5

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False, default=str(hashlib.md5('1'.encode('utf-8')).hexdigest()))
    user_role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    sex = db.Column(db.Enum(Gender), default=Gender.MALE)  # Giới tính (Enum)
    birth = db.Column(db.Date, nullable=True, default=date(2004, 7, 4))
    address = db.Column(db.String(100), nullable=False, default='123 HCM')  # Địa chỉ
    phone = db.Column(db.String(10), nullable=False, default='0123456789')
    email = db.Column(db.String(100), nullable=False, default='user@example.com')
    avatar = db.Column(db.String(100),
                       default='https://res.cloudinary.com/dnwyvuqej/image/upload/v1733499646/default_avatar_uv0h7z.jpg')


class Admin(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)  # Tham chiếu đến User


class Student(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)  # Tham chiếu đến User
    # num_instances = 0
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False, default=1)
    regulation_age_id = db.Column(db.Integer, db.ForeignKey('regulation_age.id'), nullable=False, default=1)
    scores = db.relationship('Score', backref='student', lazy=True)

    def __str__(self):
        return f"{self.name} - {self.sex} - {self.birth}"


# def create_student(name, password): #dua vao khoi_lop
#     Student.num_instances += 1 # co the bi trung
#     username = str(int(ma_hs_khoi10) + Student.num_instances)
#     password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
#     return Student(name=name,username=username,password=password)

# Lớp Teacher
class Teacher(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)  # Khóa chính tham chiếu từ User
    department = db.Column(db.String(100), nullable=True)  # Khoa/Bộ môn của giáo viên
    schedules = relationship('Schedule', backref='teacher', lazy=True)
    def __str__(self):
        return f"{self.name}"


# Lớp Staff
class Staff(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)  # Khóa chính tham chiếu từ User
    position = db.Column(db.String(100), nullable=True, default='Nhân viên hành chính')  # Vị trí làm việc


# Bảng lớp học
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    students = relationship('Student', backref='class_', lazy=True)
    schedules = relationship('Schedule', backref='class_', lazy=True)
    class_grade_id = db.Column(db.Integer, db.ForeignKey('class_grade.id'), nullable=False)
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id'), nullable=False)
    regulation_max_student_id = db.Column(db.Integer, db.ForeignKey('regulation_max_student.id'), nullable=False, default=1)

    # class_grade = db.relationship('ClassGrade', backref=db.backref('classes', lazy=True))  # Quan hệ ngược

    def __str__(self):
        return self.name


# Bang khoi lop
class ClassGrade(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Enum(KhoiLop), unique=True, default=KhoiLop.Khoi10)
    classes = relationship('Class', backref='class_grade', lazy=True)
    subjects = relationship('Subject', backref='class_grade', lazy=True)

    def __str__(self):
        return f"{self.name}"


# Bảng năm
class Year(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(9), unique=True, nullable=False, default='2023-2024')  # Ví dụ: "2023-2024"
    semesters = relationship('Semester', backref='year', lazy=True)

    def __str__(self):
        return self.name


# Bảng học kỳ
class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Enum(HocKy), default=HocKy.HK1)  # Học kỳ 1 hoặc 2, hoặc cả 2
    year_id = Column(db.Integer, db.ForeignKey('year.id'), nullable=False)
    subjects = relationship('Subject', backref='semester')
    schedules = relationship('Schedule', backref='semester', lazy=True)
    __table_args__ = (
        db.UniqueConstraint('year_id', 'name', name='unique_year_semester'),
    )

    def __str__(self):
        return f"{self.name} - {self.year}"


# Bảng môn học
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    class_grade_id = Column(db.Integer, db.ForeignKey('class_grade.id'), nullable=False)
    semester_id = Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    # class_grade = relationship('ClassGrade', backref='subjects')
    scores = db.relationship('Score', backref='subject', lazy=True)
    __table_args__ = (
        db.UniqueConstraint('semester_id', 'name', name='unique_subject_semester'),
    )

    def __str__(self):
        return f"{self.name} - {self.semester}"


# Bảng loại điểm
class ScoreType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Enum(LoaiDiem), default=LoaiDiem.diem15p, nullable=False)
    he_so = db.Column(db.Enum(HeSo), default=HeSo.heso1, nullable=False)
    scores = db.relationship('Score', backref='score_type', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('name', 'he_so', name='unique_name_he_so'),
    )

    def __str__(self):
        return f"{self.name} - {self.he_so}"


# Bảng điểm
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    so_diem = db.Column(db.Float, nullable=False)
    attempt = db.Column(db.Integer, default=1, nullable=False)
    student_id = db.Column(db.Integer, ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, ForeignKey('subject.id'), nullable=False)
    score_type_id = Column(db.Integer, db.ForeignKey('score_type.id'), nullable=False)
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'score_type_id', 'attempt',
                            name='unique_score_per_attempt'),
    )

    def __str__(self):
        return f"{self.so_diem} - {self.score_type.name} - {self.subject}"


# Bảng quy định
class Regulation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)


# Bảng quy định Số tuổi tối đa
class RegulationAge(Regulation):
    id = db.Column(db.Integer, db.ForeignKey('regulation.id'), primary_key=True)
    min_age = db.Column(db.Integer, nullable=False, default = 15)
    max_age = db.Column(db.Integer, nullable=False, default= 20)
    students = db.relationship('Student', backref='regulation_age', lazy=True)

    def __str__(self):
        return f"{self.name} - {self.min_age} - {self.max_age}"

class RegulationMaxStudent(Regulation):
    id = db.Column(db.Integer, db.ForeignKey('regulation.id'), primary_key=True)
    max_students = db.Column(db.Integer, nullable=False, default=40)
    classes = db.relationship('Class', backref='regulation_max_student', lazy=True)

    def __str__(self):
        return f"{self.name} - {self.max_students}"


class ClassRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    classes = relationship('Class', backref='class_room', lazy=True)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_work = db.Column(db.Date, nullable=True, default=date(2024, 12, 4))
    teaching_session = db.Column(db.Enum(BuoiDay), default=BuoiDay.sang)
    class_period = db.Column(db.Enum(TietHoc), default=TietHoc.tiet1)
    class_id = Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    semester_id = Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)

    # def __str__(self):
    #     return f"{self.name} - {self.min_age} - {self.max_age}"

    __table_args__ = (
        db.UniqueConstraint('date_work','teaching_session','class_period',
                            'class_id', 'semester_id', name='unique_schedule'),
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        admin1 = Admin(name='admin',
                       username='admin',
                       password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()),
                       user_role=UserRole.ADMIN)
        db.session.add(admin1)

        teacher1 = Teacher(
            name="Nguyen Thi B",
            username="teacher1",
            password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()),
            user_role=UserRole.GIAOVIEN,
            sex=Gender.FEMALE,
            birth=date(1998, 6, 20),
            address="12 Nguyen Trai, HCMC",
            phone="0908123456",
            email="lan@example.com",
            avatar="https://res.cloudinary.com/dnwyvuqej/image/upload/v1733499646/default_avatar_uv0h7z.jpg",
        )
        db.session.add(teacher1)

        teacher2 = Teacher(
            name="Nhật Minh",
            username="teacher2",
            password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()),
            user_role=UserRole.GIAOVIEN,
            sex=Gender.FEMALE,
            birth=date(1998, 6, 20),
            address="12 Nguyen Trai, HCMC",
            phone="0908123456",
            email="lan@example.com",
            avatar="https://res.cloudinary.com/dnwyvuqej/image/upload/v1733499646/default_avatar_uv0h7z.jpg",
        )
        db.session.add(teacher2)

        nhanvien1 = Staff(name='Nguyễn Văn A',
                          username='staff1',
                          password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()),
                          user_role=UserRole.NHANVIEN)
        db.session.add(nhanvien1)

        nhanvien2 = Staff(name='Bùi Quyền',
                          username='staff2',
                          password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()),
                          user_role=UserRole.NHANVIEN)
        db.session.add(nhanvien2)

        classgrade1 = ClassGrade(name=KhoiLop.Khoi10)
        classgrade2 = ClassGrade(name=KhoiLop.Khoi11)
        classgrade3 = ClassGrade(name=KhoiLop.Khoi12)
        db.session.add(classgrade1)
        db.session.add(classgrade2)
        db.session.add(classgrade3)

        quydinh1 = RegulationAge (name='Độ tuổi')
        quydinh2 = RegulationMaxStudent(name='Sĩ số')

        phonghoc1 = ClassRoom(name='D101')

        class1 = Class(name='10A1', class_grade=classgrade1, regulation_max_student=quydinh2, class_room=phonghoc1)
        db.session.add(class1)

        # Tạo một đối tượng Student
        student1 = Student(
            name="Nguyen Thi Lan",
            username="student1",
            password=str(hashlib.md5('1'.encode('utf-8')).hexdigest()),
            user_role=UserRole.USER,
            sex=Gender.FEMALE,
            birth=date(2005, 6, 20),
            address="12 Nguyen Trai, HCMC",
            phone="0908123456",
            email="lan@example.com",
            avatar="https://res.cloudinary.com/dnwyvuqej/image/upload/v1733499646/default_avatar_uv0h7z.jpg",
            class_ = class1,  # Tham chiếu đến lớp
            regulation_age = quydinh1,
        )
        db.session.add(student1)

        nam1 = Year()
        db.session.add(nam1)

        hocky1 = Semester(year=nam1)  # mặc định là học kì 1
        db.session.add(hocky1)
        hocky2 = Semester(name=HocKy.HK2, year=nam1)
        db.session.add(hocky2)

        lichday1 = Schedule(teacher=teacher1, semester=hocky1, class_=class1)
        db.session.add(lichday1)

        diem_15p1 = ScoreType(name=LoaiDiem.diem15p, he_so=HeSo.heso1)
        diem_1tiet1 = ScoreType(name=LoaiDiem.diem1tiet, he_so=HeSo.heso2)
        diem_ck1= ScoreType(name=LoaiDiem.diemck, he_so=HeSo.heso3)
        db.session.add(diem_15p1)
        db.session.add(diem_1tiet1)
        db.session.add(diem_ck1)

        toan10 = Subject(name="Toan10", semester=hocky1, class_grade=classgrade1)
        van10 = Subject(name='Van10', semester=hocky1, class_grade=classgrade1)
        anh10 = Subject(name='Anh10', semester=hocky1, class_grade=classgrade1)
        db.session.add(toan10)
        db.session.add(van10)
        db.session.add(anh10)

        diem_toan_15p_hs1_hk1 = Score(so_diem=7, student=student1, subject=toan10, score_type=diem_15p1)
        diem_toan_1tiet_hs1_hk1 = Score(so_diem=10, student=student1, subject=toan10, score_type=diem_1tiet1)
        diem_toan_ck_hs1_hk1 = Score(so_diem=5, student=student1, subject=toan10, score_type=diem_ck1)


        db.session.add(diem_toan_15p_hs1_hk1)
        db.session.add(diem_toan_1tiet_hs1_hk1)
        db.session.add(diem_toan_ck_hs1_hk1)

        db.session.commit()
