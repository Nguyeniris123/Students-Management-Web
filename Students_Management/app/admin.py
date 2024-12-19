from datetime import date
from app.models import (Class, Student, User, UserRole, Semester, Subject,
                        Score, ScoreType, ClassGrade, Year, RegulationMaxStudent, RegulationAge, Schedule)
from flask_admin import Admin, BaseView, expose
from app import app, db
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect
from sqlalchemy.exc import IntegrityError
from flask import flash

# Khởi tạo Flask-Admin
admin = Admin(app, name='Quản trị hệ thống', template_mode='bootstrap4')


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AuthenticatedAdminView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


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
    column_list = ['id', 'name', 'username', 'sex', 'birth', 'regulation_age', 'address', 'phone', 'email', 'class_', 'user_role', 'scores']
    form_columns = ['name', 'username', 'sex', 'birth', 'address', 'phone', 'email']
    column_searchable_list = ['id', 'name']
    column_editable_list = ['name', 'sex', 'birth', 'address', 'phone', 'email']

    # def on_model_change(self, form, model, is_created):
    #     # Kiểm tra ngày sinh
    #     if model.birth:
    #         current_year = date.today().year
    #         birth_year = model.birth.year
    #         age = current_year - birth_year
    #
    #         if age < 15 or age > 20:
    #             raise ValueError("Học sinh phải có độ tuổi từ 15 đến 20!")
    #
    #     # Tiếp tục với các thay đổi khác
    #     super(StudentView, self).on_model_change(form, model, is_created)



class ClassView(NhanVienAdminView):
    column_list = ['id', 'name', 'students', 'regulation_max_student', 'class_grade']
    form_columns = ['name', 'students', 'class_grade']
    column_labels = {
        'students': 'Students - Gender - Birth'
    }
    column_searchable_list = ['id', 'name']


class ClassGradeView(NhanVienAdminView):
    column_list = ['id', 'name', 'subjects', 'classes']
    column_searchable_list = ['id', 'name']


class SemesterView(AdminView):
    column_list = ['id', 'name', 'year', 'subjects']
    form_columns = ['name', 'year']
    column_filters = ['id', 'name']


class YearView(AdminView):
    column_list = ['id', 'name', 'semesters']
    form_columns = ['name', 'semesters']
    column_filters = ['id', 'name']



class SubjectView(AdminView):
    column_list = ['id', 'name', 'class_grade', 'semester', 'description']
    form_columns = ['name', 'class_grade', 'semester', 'description']
    column_searchable_list = ['id', 'name']



class ScoreView(GiaoVienAdminView):
    column_list = ['id', 'student', 'so_diem', 'attempt', 'subject', 'score_type']
    column_filters = ['id']
    can_export = True


class ScoreTypeView(GiaoVienAdminView):
    column_list = ['id', 'name', 'he_so']
    form_columns = ['name', 'he_so']
    column_filters = ['id', 'name']


class RegulationMaxStudentView(AdminView):
    column_list = ['id', 'name', 'max_students', 'classes']
    form_columns = ['name', 'max_students', 'classes']


class RegulationAgeView(AdminView):
    column_list = ['id', 'name', 'min_age', 'max_age']
    form_columns = ['name', 'min_age', 'max_age']


class ScheduleView(AdminView):
    column_list = []
    form_columns = []


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(AuthenticatedAdminView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')


# Thêm các bảng vào Flask-Admin
admin.add_view(StudentView(Student, db.session))
admin.add_view(ClassView(Class, db.session))
admin.add_view(ClassGradeView(ClassGrade, db.session))
admin.add_view(YearView(Year, db.session))
admin.add_view(SemesterView(Semester, db.session))
admin.add_view(SubjectView(Subject, db.session))
admin.add_view(ScoreView(Score, db.session))
admin.add_view(ScoreTypeView(ScoreType, db.session))
admin.add_view(RegulationMaxStudentView(RegulationMaxStudent, db.session))
admin.add_view(RegulationAgeView(RegulationAge, db.session))
admin.add_view(ScheduleView(Schedule, db.session))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
