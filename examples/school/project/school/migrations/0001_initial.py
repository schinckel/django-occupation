# Generated by Django 2.0 on 2017-12-16 05:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        migrations.swappable_dependency(settings.OCCUPATION_TENANT_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrolment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolment_date', models.DateField()),
                ('year', models.IntegerField()),
                ('semester', models.IntegerField(choices=[(0, 'Summer Semester'), (1, 'Semester 1'), (2, 'Semester 2')])),
                ('grade', models.CharField(blank=True, choices=[('HD', 'High Distinction'), ('D', 'Distinction'), ('C', 'Credit'), ('P1', 'Pass, Level 1'), ('P2', 'Pass, Level 2'), ('F1', 'Fail, Level 1'), ('F2', 'Fail, Level 2'), ('NGP', 'Non-Graded Pass'), ('NGF', 'Non-Graded Fail')], max_length=3, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('tenant_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('users', models.ManyToManyField(blank=True, related_name='visible_tenants', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StaffMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('staff_id', models.CharField(max_length=16, unique=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_members', to=settings.OCCUPATION_TENANT_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('student_id', models.CharField(max_length=16, unique=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to=settings.OCCUPATION_TENANT_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='enrolment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrolments', to='school.Student'),
        ),
        migrations.AddField(
            model_name='enrolment',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrolments', to='school.Subject'),
        ),
    ]
