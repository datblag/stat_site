from wtforms.fields import StringField, SubmitField, DateField, FloatField
from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from wtforms.validators import Length, NumberRange, InputRequired, DataRequired, ValidationError
from site_app.models import RefDoctors

class DefectEditForm(FlaskForm):
    history = StringField('№ мед. карты', id='_history', validators=[InputRequired(message=u'Заполните это поле'),
                                                                     Length(min=6, max=6,
                                                                            message=u'Необходжимо ввести 6 символов')])
    doctor_code = StringField('Код врача', id='DoctorInput', validators=[InputRequired(message=u'Заполните это поле'),
                                                                         Length(min=4, max=4,
                                                                         message=u'Необходжимо ввести 4 символа')])
    defect_codes = StringField('Коды дефектов', id='DefectCodesInput',
                               validators=[InputRequired(message=u'Заполните это поле')])
    defect_comment = StringField('Описание дефекта', id='DefectCommentTextArea', widget=TextArea(),
                                 validators=[InputRequired(message=u'Заполните это поле')])
    period_start = DateField('Проверяемый период', id='PeriodStart',
                             validators=[InputRequired(message=u'Введите начало периода')])
    period_end = DateField(id='PeriodEnd',
                           validators=[InputRequired(message=u'Введите конец периода')])
    disease = StringField('Код МКБ10', id='disease_code', validators=[InputRequired(message=u'Заполните это поле')])
    sum_service = FloatField('Стоимость услуги', id='sum_service', validators=[InputRequired(),
                                                                               NumberRange(min=0.01,
                                                                               max=1000000,
                                                                               message=
                                                                               u'Сумма услуги должна быть больше нуля')])
    sum_no_pay = FloatField('Не подлежит оплате', id='sum_no_pay', validators=[InputRequired()])
    sum_penalty = FloatField('Сумма штрафа', id='sum_penalty')

    @staticmethod
    def validate_doctor_code(self, doctor_code):
        doctor_rec = RefDoctors.query.filter_by(doctor_stat_code=doctor_code.data.strip()).first()
        if doctor_rec is None:
            raise ValidationError('Ошибка! Код врача не найден')

    @staticmethod
    def validate_period_start(self, period_start):
        if self.period_end.data and period_start.data > self.period_end.data:
            raise ValidationError('Ошибка! Неправильный период')
