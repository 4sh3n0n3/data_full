from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.


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


class Research(models.Model):
    research_name = models.CharField(max_length=400, verbose_name='Наименование исследования')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания', editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_researches',
                                   verbose_name='Создатель исследования')
    description = models.TextField(blank=True, verbose_name='Описание исследования')

    class Meta:
        verbose_name_plural = "Исследования"
        unique_together = [('research_name', 'created_at'), ('research_name', 'created_by')]

    def __str__(self):
        return "{}. Автор: {}, от {}".format(self.research_name, self.created_by.full_name_with_initials,
                                             self.created_at.astimezone())


class BaseType(models.Model):
    key_name = models.CharField(max_length=20, verbose_name='Физическое наименование типа', unique=True)

    class Meta:
        verbose_name_plural = "Базовые типы"

    def __str__(self):
        return self.key_name


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


class CustomType(models.Model):
    base_type = models.ForeignKey(BaseType, on_delete=models.CASCADE, related_name='custom_types',
                                  verbose_name='Базовый тип')
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


class Dataset(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование', unique=True)
    researches = models.ManyToManyField(to=Research, through="DatasetToResearch", related_name='datasets',
                                        verbose_name='Связанные исследования')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания', editable=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_datasets',
                                   verbose_name='Создатель набора данных')

    def creator(self):
        return self.created_by

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='owned_datasets',
                              verbose_name='Владелец набора данных', default=creator)

    class Meta:
        verbose_name_plural = "Наборы данных"

    def __str__(self):
        return self.name


class Header(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='dataset_headers',
                                verbose_name='Набор данных')
    custom_type = models.ForeignKey(CustomType, on_delete=models.DO_NOTHING, related_name='type_headers',
                                    verbose_name='Тип данных')

    class Meta:
        verbose_name_plural = "Заголовки"
        unique_together = ('name', 'dataset')

    def __str__(self):
        return "{}: {}".format(self.dataset, self.name)


class DataRow(models.Model):
    number = models.BigIntegerField(editable=False, default=1)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='dataset_rows',
                                verbose_name='Набор данных')

    class Meta:
        verbose_name_plural = "Строки данных"

    def save(self, *args, **kwargs):
        prev = DataRow.objects.filter(dataset=self.dataset).order_by('number').last()
        self.number = prev.number + 1
        super(self.__class__, self).save(self, *args, **kwargs)

    def __str__(self):
        return "{}: запись под номером {}".format(self.dataset, self.number)


class CellEntry(models.Model):
    header = models.ForeignKey(Header, on_delete=models.CASCADE, related_name='entries',
                               verbose_name='Заголовок')
    data_row = models.ForeignKey(DataRow, on_delete=models.CASCADE, related_name='cells',
                                 verbose_name='Строка')
    value = models.TextField()

    class Meta:
        verbose_name_plural = "Ячейки данных"

    def clean(self):
        if not self.header.dataset == self.data_row.dataset:
            raise ValidationError(message='Заголовок и строка должны относиться к одному набору данных')

    @property
    def dataset(self):
        return self.header.dataset

    def __str__(self):
        return "{} - {}:{}. Значение: {}".format(self.dataset, self.header.name, self.data_row.number, self.value)


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
