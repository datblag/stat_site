from wtforms.fields import StringField, SubmitField, DateField, FloatField, PasswordField, BooleanField, IntegerField
from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from wtforms.validators import Length, NumberRange, InputRequired, DataRequired, ValidationError, Optional
from site_app.models.reference import RefDoctors, RefBureauMse, RefDisabilityGroup
import requests
from bs4 import BeautifulSoup
import logging


class SearchDoctorForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[InputRequired(message=u'Заполните это поле')])
    password = PasswordField('Пароль', validators=[InputRequired(message=u'Заполните это поле')])
    remember_me = BooleanField('Запомнить пароль', id='_remember_me')
    submit = SubmitField('Войти')


class AddPatientForm(FlaskForm):
    num = StringField('Номер карты')
    fam = StringField('Фамилия')
    im = StringField('Имя')
    ot = StringField('Отчество')
    birthday = DateField('Дата рождения', validators=[Optional()])
    submit = SubmitField('Найти в МИС')

    @staticmethod
    def validate_num(self, num):
        if not self.fam.data or self.fam.data is None and not self.im.data or self.im.data is None:
            if not num.data or num.data is None:
                raise ValidationError('Ошибка! Введите номер карты, или фамилию и имя')

    @staticmethod
    def validate_fam(self, fam):
        if not self.num.data or self.num.data is None:
            if not fam.data or fam.data is None:
                raise ValidationError('Ошибка! Введите фамилию и имя, или номер карты')

    @staticmethod
    def validate_im(self, im):
        if not self.num.data or self.num.data is None:
            if not im.data or im.data is None:
                raise ValidationError('Ошибка! Введите фамилию и имя, или номер карты')


class PatientForm(FlaskForm):
    fam = StringField('Фамилия', validators=[InputRequired(message=u'Заполните это поле')])
    im = StringField('Имя', validators=[InputRequired(message=u'Заполните это поле')])
    ot = StringField('Отчество')
    birthday = DateField('Дата рождения', validators=[Optional()])
    num = StringField('N карты', validators=[Optional()])


class PolisForm(FlaskForm):
    enp = StringField('ЕНП', validators=[InputRequired(message=u'Заполните это поле')])

    @staticmethod
    def validate_enp(self, enp):
        URL = "http://aofoms.ru/index.php?c=availPolicy"

        with requests.Session() as s:
            s.headers = {"User-Agent": "Mozilla/5.0"}
            res = s.get(URL)
            soup = BeautifulSoup(res.text, "lxml")
            # payload = {item['name']: item.get('value', '') for item in soup.select("input[name]")}
            # # print(payload)
            # # payload['__EVENTTARGET'] = 'polisYesEnp'
            # payload['polis'] = 'enp'
            # payload['npolEnp'] = enp.data.strip()
            #     # '2847040848000286'
            # payload['spol'] = ''
            # payload['npol'] = ''
            # payload['npolVrem'] = ''
            # payload['npolBlank'] = ''
            # payload['polisYesEnp'] = 'Найти'

            data = {'polis': 'enp', 'npolEnp': enp.data.strip(), 'spol': '', 'npol': '', 'npolVrem': '',
                    'npolBlank': '', 'polisYesEnp': 'Найти'}

            req = s.post(URL, data=data, headers={"User-Agent": "Mozilla/5.0"})
            soup_obj = BeautifulSoup(req.text, "lxml")
            # print(soup_obj.text)
            res = []
            for items in soup_obj.select("div.content_in > h2"):
                res.append(items.get_text())

            if not 'не найден среди действующих' in ' '.join(res):

                data = {'dispance': 'DisEnp', 'disEnp': enp.data.strip(), 'disSpol': '', 'disNpol': '', 'disNpolVrem': '',
                        'disNpolBlank': '', 'DisYesEnp': 'Найти'}

                req = s.post(URL, data=data, headers={"User-Agent": "Mozilla/5.0"})
                soup_obj = BeautifulSoup(req.text, "lxml")
                for items in soup_obj.select("div.content_in > h2"):
                    res.append(items.get_text())

            raise ValidationError(' '.join(res))


class DefectDeleteForm(FlaskForm):
    pass


class MseReferralEditForm(FlaskForm):
    bureau_id = StringField('Филиал бюро МСЭ', id='bureau_id', validators=[InputRequired(message=u'Заполните это поле'),
                                                                         Length(min=1, max=1,
                                                                         message=u'Необходимо ввести 1 символ')])


    bureau_label = StringField('', id='bureau_label')


    is_first_direction = BooleanField('Направлен первично', id='is_first_direction', default=False)

    doctor_code = StringField('Код врача', id='DoctorInput', validators=[InputRequired(message=u'Заполните это поле'),
                                                                         Length(min=4, max=4,
                                                                         message=u'Необходжимо ввести 4 символа')])

    mse_disease = StringField('Код МКБ10', id='disease_code', validators=[InputRequired(message=u'Заполните это поле')])

    is_disability_no_set = BooleanField('Инвалидность не установлена', id='is_disability_no_set', default=False)

    is_set_indefinitely = BooleanField('Установлена бессрочно', id='is_set_indefinitely', default=False)

    disability_group_id = StringField('Группа инвалидности', id='disability_group_id')
    disability_group_label = StringField('', id='disability_group_label')

    expert_date = DateField('Дата экспертизы', id='ExpertDate',
                            validators=[InputRequired(message=u'Введите дату экспертизы')])

    next_date = DateField('Дата следующей явки', id='NextDate', validators=[Optional()])

    mse_comment = StringField('Описание дефекта', id='DefectCommentTextArea', widget=TextArea())

    degree_disability = IntegerField('% утраты трудоспособности', id='degree_disability', default=0)

    @staticmethod
    def validate_bureau_id(self, bureau_id):
        bureau_rec = RefBureauMse.query.get(bureau_id.data.strip())
        if bureau_rec is None:
            raise ValidationError('Ошибка! Код бюро не найден')

    @staticmethod
    def validate_disability_group_id(self, disability_group_id):
        if not disability_group_id.data.isdigit() or self.is_disability_no_set.data:
            disability_group_id.data = '0'

        logging.warning(['is_disability_no_set', self.is_disability_no_set.data])

        dis_rec = RefDisabilityGroup.query.get(disability_group_id.data.strip())
        if dis_rec is None and not self.is_disability_no_set.data:
            raise ValidationError('Ошибка! Код не найден')



    @staticmethod
    def validate_doctor_code(self, doctor_code):
        doctor_rec = RefDoctors.query.filter_by(doctor_stat_code=doctor_code.data.strip()).first()
        if doctor_rec is None:
            raise ValidationError('Ошибка! Код врача не найден')


class MedServiceEditForm(FlaskForm):
    doctor_code = StringField('Код врача', id='DoctorInput', validators=[InputRequired(message=u'Заполните это поле'),
                                                                         Length(min=4, max=4,
                                                                         message=u'Необходжимо ввести 4 символа')])
    service_date = DateField('Дата', id='ServiceDate',
                             validators=[InputRequired(message=u'Введите дату оказания услуги')])
    disease = StringField('Диагноз', id='disease_code', validators=[InputRequired(message=u'Заполните это поле')])

    @staticmethod
    def validate_doctor_code(self, doctor_code):
        doctor_rec = RefDoctors.query.filter_by(doctor_stat_code=doctor_code.data.strip()).first()
        if doctor_rec is None:
            raise ValidationError('Ошибка! Код врача не найден')


class DefectEditForm(FlaskForm):
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
    expert_act_number = StringField('№ экспертизы', id='ExpertActNumber',
                                    validators=[InputRequired(message=u'Введите номер экспертизы')])
    expert_date = DateField('Дата экспертизы СМО', id='ExpertDate',
                            validators=[InputRequired(message=u'Введите дату экспертизы')])
    expert_name = StringField('Эксперт СМО', id='ExpertName',
                              validators=[InputRequired(message=u'Введите ФИО эксперта')])
    disease = StringField('Код МКБ10', id='disease_code', validators=[InputRequired(message=u'Заполните это поле')])
    sum_service = FloatField('Стоимость услуги', id='sum_service', validators=[InputRequired(),
                                                                               NumberRange(min=0.01,
                                                                               max=1000000,
                                                                               message=
                                                                               u'Сумма услуги должна быть больше нуля')])
    sum_no_pay = FloatField('Не подлежит оплате', id='sum_no_pay', validators=[InputRequired()])
    sum_penalty = FloatField('Сумма штрафа', id='sum_penalty')
    # fam = StringField('Фамилия')

    @staticmethod
    def validate_doctor_code(self, doctor_code):
        doctor_rec = RefDoctors.query.filter_by(doctor_stat_code=doctor_code.data.strip()).first()
        if doctor_rec is None:
            raise ValidationError('Ошибка! Код врача не найден')

    @staticmethod
    def validate_period_start(self, period_start):
        if self.period_end.data and period_start.data > self.period_end.data:
            raise ValidationError('Ошибка! Неправильный период')
