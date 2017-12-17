# Generated by Django 2.0 on 2017-12-17 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.CharField(blank=True, choices=[('HD', 'High Distinction'), ('D', 'Distinction'), ('C', 'Credit'), ('P1', 'Pass, Level 1'), ('P2', 'Pass, Level 2'), ('F1', 'Fail, Level 1'), ('F2', 'Fail, Level 2'), ('NGP', 'Non-Graded Pass'), ('NGF', 'Non-Graded Fail')], max_length=3, null=True)),
                ('enrolment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='school.Enrolment')),
            ],
        ),
    ]
