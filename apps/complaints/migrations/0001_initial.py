from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_id', models.CharField(db_index=True, editable=False, max_length=20, unique=True)),
                ('description', models.TextField(max_length=3000)),
                ('photo_file_id', models.CharField(max_length=512)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('status', models.CharField(choices=[('PENDING', 'Kutilmoqda'), ('UNDER_REVIEW', "Ko'rib chiqilmoqda"), ('APPROVED', 'Tasdiqlandi'), ('REJECTED', 'Rad etildi'), ('RESOLVED', 'Hal qilindi')], db_index=True, default='PENDING', max_length=20)),
                ('moderation_comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='complaints', to='users.telegramuser')),
            ],
            options={
                'verbose_name': 'Murojaat',
                'verbose_name_plural': 'Murojaatlar',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ComplaintStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.CharField(choices=[('PENDING', 'Kutilmoqda'), ('UNDER_REVIEW', "Ko'rib chiqilmoqda"), ('APPROVED', 'Tasdiqlandi'), ('REJECTED', 'Rad etildi'), ('RESOLVED', 'Hal qilindi')], max_length=20)),
                ('new_status', models.CharField(choices=[('PENDING', 'Kutilmoqda'), ('UNDER_REVIEW', "Ko'rib chiqilmoqda"), ('APPROVED', 'Tasdiqlandi'), ('REJECTED', 'Rad etildi'), ('RESOLVED', 'Hal qilindi')], max_length=20)),
                ('comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='complaints.complaint')),
            ],
            options={
                'verbose_name': 'Holat tarixi',
                'verbose_name_plural': 'Holat tarixi',
                'ordering': ['-created_at'],
            },
        ),
    ]
