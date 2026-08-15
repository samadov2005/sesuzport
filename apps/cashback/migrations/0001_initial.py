from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('users', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='CashbackAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_earned', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_spent', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cashback_account', to='users.telegramuser')),
            ],
            options={
                'verbose_name': 'Keshbek hisobi',
                'verbose_name_plural': 'Keshbek hisoblari',
            },
        ),
        migrations.CreateModel(
            name='CashbackTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('transaction_type', models.CharField(choices=[('EARN', 'Olish'), ('SPEND', 'Sarflash'), ('ADJUSTMENT', 'Tuzatish')], max_length=15)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='cashback.cashbackaccount')),
            ],
            options={
                'verbose_name': 'Keshbek tranzaksiyasi',
                'verbose_name_plural': 'Keshbek tranzaksiyalari',
                'ordering': ['-created_at'],
            },
        ),
    ]
