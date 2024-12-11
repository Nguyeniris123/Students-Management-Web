from datetime import date
from app.models import Class, Student, User, UserRole, Semester, Subject, Score
from flask_admin import Admin, BaseView, expose
from app import app, db
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect

# Khởi tạo Flask-Admin
admin = Admin(app, name='Quản trị hệ thống', template_mode='bootstrap4')


class AdminView(ModelView):
    def is_accessible(self):
        # Chỉ admin mới có quyền truy cập
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class GiaoVienView(ModelView):
    def is_accessible(self):
        # Chỉ giáo viên mới có quyền truy cập
        return current_user.is_authenticated and current_user.user_role == UserRole.GIAOVIEN


class NhanVienView(ModelView):
    def is_accessible(self):
        # Chỉ nhân viên mới có quyền truy cập
        return current_user.is_authenticated and current_user.user_role == UserRole.NHANVIEN


class NhanVienAdminView(ModelView):
    def is_accessible(self):
        # Cho phép truy cập nếu user là nhân viên hoặc admin
        return current_user.is_authenticated and (
                current_user.user_role == UserRole.ADMIN or current_user.user_role == UserRole.NHANVIEN)


class GiaoVienAdminView(ModelView):
    def is_accessible(self):
        # Cho phép truy cập nếu user là nhân viên hoặc admin
        return current_user.is_authenticated and (
                current_user.user_role == UserRole.ADMIN or current_user.user_role == UserRole.GIAOVIEN)


class StudentView(NhanVienAdminView):
    column_list = ['id', 'name', 'username','sex', 'birth', 'address', 'phone', 'email', 'class.name', 'user_role']
    column_labels = {
        'class.name': 'Class'
    }
    form_columns = ['name', 'sex', 'birth', 'address', 'phone', 'email']
    column_searchable_list = ['id','name', 'phone', 'email']
    column_editable_list = ['name', 'sex', 'birth', 'address', 'phone', 'email']
    def on_model_change(self, form, model, is_created):
        # Kiểm tra ngày sinh
        if model.birth:
            current_year = date.today().year
            birth_year = model.birth.year
            age = current_year - birth_year

            if age < 15 or age > 20:
                raise ValueError("Học sinh phải có độ tuổi từ 15 đến 20!")

        # Tiếp tục với các thay đổi khác
        super(StudentView, self).on_model_change(form, model, is_created)

    def on_model_change(self, form, model, is_created):
        # Tạo username nếu không có
        if not model.username:  # Nếu username chưa được gán
            name_parts = model.name.split()  # Tách tên thành các từ
            last_name = name_parts[-1] if name_parts else ''  # Lấy từ cuối cùng của tên
            model.username = last_name.lower() + str(model.id)

        existing_user = Student.query.filter_by(username=model.username).first()
        if existing_user:
            model.username = last_name.lower() + str(model.id)

        return super().on_model_change(form, model, is_created)


class SemesterView(AdminView):
    column_list = ['year', 'semester_number']
    column_labels = {
        'year': 'Năm học',
        'semester_number': 'Học kỳ'
    }
    column_filters = ['year', 'semester_number']


class ClassView(NhanVienAdminView):
    column_list = ['id', 'name', 'grade']


class SubjectView(AdminView):
    column_list = ['year', 'semester_number']


class ScoreView(GiaoVienAdminView):
    column_list = ['student.name', 'subject.name', 'semester.year', 'semester.semester_number', 'grade_type',
                   'grade_value',
                   'attempt']
    column_labels = {
        'student.name': 'Học sinh',
        'subject.name': 'Môn học',
        'semester.year': 'Năm học',
        'semester.semester_number': 'Học kỳ',
        'score_type': 'Loại điểm',
        'score_value': 'Giá trị điểm',
        'attempt': 'Lần kiểm tra'
    }
    column_filters = ['score_type', 'semester.year', 'semester.semester_number']


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


# Thêm các bảng vào Flask-Admin
admin.add_view(StudentView(Student, db.session))  # Nhân viên có thể truy cập
admin.add_view(ClassView(Class, db.session))  # Chỉ giáo viên có thể truy cập
admin.add_view(SemesterView(Semester, db.session))
admin.add_view(SubjectView(Subject, db.session))
admin.add_view(ScoreView(Score, db.session))  # Chỉ giáo viên có thể truy cập
admin.add_view(LogoutView(name='Đăng xuất'))  # Đăng xuất trên trang flask-admin
