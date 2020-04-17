from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from crum import get_current_request


# Create your models here.


def datafile_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dataframes_csv/owner_{}/%Y/%m/%d/{}'.format(instance.user.id, filename)


class User(AbstractUser):
    middle_name = models.CharField(max_length=20, verbose_name='Отчество')
    photo = models.ImageField(upload_to='avatars', blank=True, verbose_name='Фото')

    AbstractUser.first_name.field.verbose_name = 'Имя'
    AbstractUser.last_name.field.verbose_name = 'Фамилия'
    AbstractUser.email.field.verbose_name = 'E-mail'

    # AbstractUser.username.field.verbose_name = 'Логин'
    # AbstractUser.is_staff.field.verbose_name = 'Служебный статус'
    # AbstractUser.date_joined.field.verbose_name = 'Дата подключения'
    # AbstractUser.groups.field.verbose_name = 'Группы'
    # AbstractUser.user_permissions.field.verbose_name = 'Пользовательские разрешения'

    # Эти не работают!
    # AbstractUser.is_active.field.verbose_name = 'Активен'
    # AbstractUser.is_superuser.field.verbose_name = 'Суперпользователь'
    # AbstractUser.last_login.field.verbose_name = 'Последнее подключение'
    # AbstractUser.password.field.verbose_name = 'Пароль'

    def __str__(self):
        return self.username if self._check_personal_data_is_empty() else self.full_name_with_initials

    class Meta:
        verbose_name_plural = "Пользователи"

    @property
    def full_name(self):
        return str(self)

    @property
    def full_name_with_initials(self):
        return "{}.{}. {}".format(self.first_name[0], self.middle_name[0], self.last_name)

    def _check_personal_data_is_empty(self):
        if self.first_name == '' or self.last_name == '' or self.middle_name == '':
            return True
        return False


class ResearchGroup(models.Model):
    group_name = models.CharField(max_length=400, verbose_name='Наименование группы исследований')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания', editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_research_groups',
                                   verbose_name='Создатель группы исследований')
    description = models.TextField(blank=True, verbose_name='Описание группы исследований')

    class Meta:
        verbose_name_plural = "Группы исследований"
        unique_together = [('group_name', 'created_at'), ('group_name', 'created_by')]

    def __str__(self):
        return self.group_name

    def save(self, *args, **kwargs):
        self.created_by = get_current_request().user
        super().save(self, *args, **kwargs)


class Research(models.Model):
    research_name = models.CharField(max_length=400, verbose_name='Наименование исследования')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания', editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_researches',
                                   verbose_name='Создатель исследования')
    group = models.ForeignKey(ResearchGroup, on_delete=models.SET_NULL, blank=True, null=True,
                              related_name='researches', verbose_name='Группа исследований')
    description = models.TextField(blank=True, verbose_name='Описание исследования')

    class Meta:
        verbose_name_plural = "Исследования"
        unique_together = [('research_name', 'created_at'), ('research_name', 'created_by')]

    def __str__(self):
        return "{}. Автор: {}, от {}".format(self.research_name, self.created_by.full_name,
                                             self.created_at.astimezone())

    def save(self, *args, **kwargs):
        self.created_by = get_current_request().user
        super().save(self, *args, **kwargs)


BASE_TYPES = (
    ("object", "object"),
    ("int64", "int64"),
    ("float64", "float64"),
)


class FieldGroup(models.Model):
    name = models.CharField(max_length=20, verbose_name='Наименование', unique=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания', editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_field_groups',
                                   verbose_name='Создатель группы')
    description = models.TextField(blank=True, verbose_name='Описание типа')
    group = models.ForeignKey("self", blank=True, on_delete=models.SET_NULL, null=True, related_name='group_groups',
                              verbose_name='Группа')

    @property
    def nesting(self):
        counter = 0
        parent = self.group
        while parent is not None:
            counter += 1
            parent = parent.group

        return counter

    class Meta:
        verbose_name_plural = "Группы типов"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.created_by = get_current_request().user
        super().save(self, *args, **kwargs)


class CustomType(models.Model):
    base = models.CharField(choices=BASE_TYPES, max_length=20, verbose_name='Базовый тип')
    name = models.CharField(max_length=20, verbose_name='Наименование', unique=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания', editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_types',
                                   verbose_name='Создатель типа')
    description = models.TextField(blank=True, verbose_name='Описание типа')
    group = models.ForeignKey(FieldGroup, blank=True, on_delete=models.SET_NULL, null=True, related_name='group_types',
                              verbose_name='Группа')

    is_active = models.BooleanField(verbose_name='Активность', default=True,
                                    help_text='Неактивные типы недоступны для выбора исследователями. Используется '
                                              'вместо удаления типа.')
    is_default_for_base = models.BooleanField(verbose_name='Базовый для определения', default=False)

    @property
    def nesting(self):
        counter = 0
        parent = self.group
        while parent is not None:
            counter += 1
            parent = parent.group

        return counter

    class Meta:
        verbose_name_plural = "Пользовательские типы"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.created_by = get_current_request().user
        super().save(self, *args, **kwargs)


class CustomConstraint(models.Model):
    custom_type = models.OneToOneField(CustomType, on_delete=models.CASCADE, related_name='constraints',
                                       verbose_name='Пользовательский тип')
    is_unique = models.BooleanField(verbose_name='Уникальность', default=False,
                                    help_text='Если активно, то значения типа должны быть уникальны в рамках набора '
                                              'данных исследования. Исследователь будет предупрежден об ошибке '
                                              'данных, при обнаружении дубликации.')
    validators = models.ManyToManyField(to="CustomValidator", through="ValidatorToConstraint",
                                        related_name='created_constraints', verbose_name='Валидаторы')

    class Meta:
        verbose_name_plural = "Пользовательские ограничения типов"

    def __str__(self):
        return "Ограничения: {}".format(self.custom_type)


CUSTOM_VALIDATION_WARN = "WARN"
CUSTOM_VALIDATION_ERROR = "ERROR"
ON_VALIDATION_ERROR = [
    (CUSTOM_VALIDATION_WARN, "Предупреждение"),
    (CUSTOM_VALIDATION_ERROR, "Ошибка"),
]


class CustomValidator(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование', unique=True)
    regexp = models.TextField(verbose_name='Регулярное выражение')
    error_mess = models.CharField(max_length=400, verbose_name='Сообщение об ошибке')
    error_type = models.CharField(max_length=10, verbose_name='Тип исключения', choices=ON_VALIDATION_ERROR)
    description = models.TextField(blank=True, verbose_name='Описание валидатора')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания', editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_validators',
                                   verbose_name='Создатель валидатора')

    class Meta:
        verbose_name_plural = "Пользовательские валидаторы"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.created_by = get_current_request().user
        super().save(self, *args, **kwargs)


class Dataset(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование', unique=True)
    researches = models.ManyToManyField(to=Research, through="DatasetToResearch", related_name='datasets',
                                        verbose_name='Связанные исследования')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания')
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_datasets',
                                   verbose_name='Создатель набора данных')

    @property
    def creator(self):
        return self.created_by

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='owned_datasets',
                              verbose_name='Владелец набора данных', default=creator)

    # @property
    # def is_empty(self):
    #     return not self.datafiles.all()

    # @property
    # def active_datafile(self):
    #     files = DataFile.objects.filter(dataset=self, is_active=True)
    #     if len(files) == 1:
    #         return files[0]
    #     elif not files:
    #         return None
    #     else:
    #         raise ValidationError(message='Активных файлов больше одного')

    class Meta:
        verbose_name_plural = "Наборы данных"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.created_by = get_current_request().user
        super().save(self, *args, **kwargs)


# class DataFile(models.Model):
#     dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='datafiles',
#                                 verbose_name='Набор даных')
#     file = models.FileField(upload_to=datafile_path, verbose_name='Файл данных',
#                             help_text='Внутри системы данные хранятся и обрабатываются в формате .csv')
#     uploaded_at = models.DateTimeField(auto_now=True, verbose_name='Дата загрузки')
#     uploaded_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='uploaded_datafiles',
#                                     verbose_name='Загружено пользователем')
#     tag = models.CharField(max_length=200, verbose_name='Пользовательский тег к версии данных', blank=True)
#
#     is_active = models.BooleanField(verbose_name='Активность', default=True,
#                                     help_text='Определяет, какая версия данных используется системой. Не может '
#                                               'быть более одного активного файла в рамках набора данных')
#
#     class Meta:
#         verbose_name_plural = "Файлы данных"
#
#     def clean(self):
#         if not self.is_active:
#             pass
#
#         datafiles = DataFile.objects.filter(dataset=self.dataset, is_active=True)
#         if datafiles:
#             raise ValidationError(message='Уже определен активный файл данных')
#
#     def save(self, *args, **kwargs):
#         self.uploaded_by = get_current_request().user
#         super().save(self, *args, **kwargs)


class Header(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='dataset_headers',
                                verbose_name='Набор данных')
    custom_type = models.ForeignKey(CustomType, on_delete=models.DO_NOTHING, related_name='type_headers',
                                    verbose_name='Тип данных')

    class Meta:
        verbose_name_plural = "Заголовки"
        unique_together = ('name', 'dataset')
        indexes = [
            models.Index(fields=['dataset', ]),
            models.Index(fields=['dataset', 'custom_type']),
        ]

    def __str__(self):
        return "{}: {}".format(self.dataset, self.name)


# class DataRow(models.Model):
#     number = models.BigIntegerField(editable=False, default=1)
#     dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='dataset_rows',
#                                 verbose_name='Набор данных')
#
#     class Meta:
#         verbose_name_plural = "Строки данных"
#         unique_together = ('number', 'dataset')
#         indexes = [
#             models.Index(fields=['dataset', ]),
#             models.Index(fields=['number', ]),
#             models.Index(fields=['dataset', 'number', ]),
#         ]
#
#     def __str__(self):
#         return "{}: запись под номером {}".format(self.dataset, self.number)
#
#
# class CellEntry(models.Model):
#     header = models.ForeignKey(Header, on_delete=models.CASCADE, related_name='entries',
#                                verbose_name='Заголовок')
#     data_row = models.ForeignKey(DataRow, on_delete=models.CASCADE, related_name='cells',
#                                  verbose_name='Строка')
#     value = models.TextField()
#
#     class Meta:
#         verbose_name_plural = "Ячейки данных"
#         unique_together = ('header', 'data_row')
#         indexes = [
#             models.Index(fields=['header', ]),
#             models.Index(fields=['data_row', ]),
#             models.Index(fields=['header', 'data_row', ]),
#         ]
#
#     def clean(self):
#         if not self.header.dataset == self.data_row.dataset:
#             raise ValidationError(message='Заголовок и строка должны относиться к одному набору данных')
#
#     @property
#     def dataset(self):
#         return self.header.dataset
#
#     def __str__(self):
#         return "{} - {}:{}. Значение: {}".format(self.dataset, self.header.name, self.data_row.number, self.value)


#######################
# MANY-TO-MANY TABLES #
#######################


class ValidatorToConstraint(models.Model):
    constraint = models.ForeignKey(CustomConstraint, on_delete=models.CASCADE,
                                   related_name='validator_relation_entries')
    validator = models.ForeignKey(CustomValidator, on_delete=models.CASCADE, related_name='constraint_relation_entries')


class DatasetToResearch(models.Model):
    research = models.ForeignKey(Research, on_delete=models.CASCADE, related_name='dataset_relation_entries')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='research_relation_entries')
