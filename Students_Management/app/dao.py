from datetime import datetime
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app.models import User, Score, ScoreType, Student, Gender
from app import app, db
import hashlib

def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))

    # if role:
    #     u = u.filter(User.user_role.__eq__(role))

    return u.first()

def get_user_by_id(id):
    return User.query.get(id)

def get_students_by_kw(keyword=None):
    if keyword:
        return Student.query.filter(Student.name.ilike(f"%{keyword}%")).all()
    return Student.query.order_by(Student.name).all()

def add_student(data):
    try:
        # Lấy thông tin từ form
        name = data.get('name')
        gender = data.get('gender')
        birth = data.get('birth')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')

        # Kiểm tra dữ liệu đầu vào
        if not all([name, gender, birth, email, phone, address]):
            return {'success': False, 'message': 'Dữ liệu không đầy đủ.'}

        # Chuyển đổi ngày sinh từ chuỗi sang kiểu Date
        birth_date = datetime.strptime(birth, '%Y-%m-%d').date() if birth else None

        # Tạo đối tượng học sinh mới
        new_student = Student(
            username=phone,  # Đặt username là số điện thoại
            name=name,
            sex=Gender(int(gender)),  # Chuyển giá trị gender thành Enum
            birth=birth_date,
            email=email,
            phone=phone,
            address=address
        )

        # Thêm học sinh vào cơ sở dữ liệu
        db.session.add(new_student)
        db.session.commit()

        return {'success': True, 'message': 'Thêm học sinh thành công!'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': 'Lỗi: Tuổi học sinh sai quy định,...'}


def delete_student(student_id):
    try:
        # Tìm học sinh theo ID
        student = Student.query.get(student_id)
        if not student:
            return {'success': False, 'message': 'Học sinh không tồn tại.'}

        # Xóa học sinh
        db.session.delete(student)
        db.session.commit()

        return {'success': True, 'message': 'Xóa học sinh thành công!'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': 'Lỗi'}

# Lay ra nhung hoc sinh hoc mon hoc
def get_all_students_average_score(subject_id):
    return db.session.query(Score.student_id,Score.subject_id,(func.sum(Score.so_diem * ScoreType.he_so)/func.sum(ScoreType.he_so)).label('DiemTrungBinh'))\
        .filter(Score.subject_id.__eq__(subject_id)).join(ScoreType,ScoreType.id.__eq__(Score.score_type_id)).group_by(Score.student_id).all()


def get_students_by_class(class_id, keyword=None):
    query = Student.query.filter_by(class_id=class_id)
    if keyword:
        query = query.filter(Student.name.like(f"%{keyword}%"))
    return query.order_by(Student.name).all()


def get_scores_by_subject(subject_id):
    return Score.query.filter_by(subject_id=subject_id).all()


def add_score(student_id, subject_id, score_type_name, score_value):
    try:
        # Lấy loại điểm từ bảng ScoreType
        score_type = ScoreType.query.filter_by(name=score_type_name).first()
        if not score_type:
            return {"success": False, "message": "Không tìm thấy loại điểm."}

        # Tạo điểm mới
        new_score = Score(
            student_id=student_id,
            subject_id=subject_id,
            score_type_id=score_type.id,
            so_diem=score_value
        )

        db.session.add(new_score)
        db.session.commit()
        return {"success": True, "message": "Thêm điểm thành công!"}
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"success": False, "message": 'Lỗi: Điểm phải từ 0 - 10, Số cột điểm không được vượt quá quy định'}


def edit_score(score_id, new_value):
    try:
        # Tìm điểm cần sửa
        score = Score.query.get(score_id)
        if not score:
            return {"success": False, "message": "Không tìm thấy điểm."}

        # Cập nhật giá trị mới
        score.so_diem = new_value
        db.session.commit()
        return {"success": True, "message": "Sửa điểm thành công!"}
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"success": False, "message": 'Lỗi: Điểm phải từ 0 - 10, Số cột điểm không được vượt quá quy định'}


def delete_score(score_id):
    try:
        # Tìm điểm cần xóa
        score = Score.query.get(score_id)
        if not score:
            return {"success": False, "message": "Không tìm thấy điểm."}

        # Xóa điểm
        db.session.delete(score)
        db.session.commit()
        return {"success": True, "message": "Xóa điểm thành công!"}
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"success": False, "message": 'Lỗi'}