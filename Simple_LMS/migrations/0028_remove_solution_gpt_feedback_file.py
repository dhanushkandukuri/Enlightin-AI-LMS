# Generated by Django 4.0.8 on 2024-03-31 00:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Simple_LMS', '0027_solution_gpt_feedback_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solution',
            name='gpt_feedback_file',
        ),
    ]
