from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('phone', models.CharField(blank=True, max_length=50, null=True)),
                ('rating', models.DecimalField(decimal_places=1, default=0.0, max_digits=3)),
                ('safety_status', models.CharField(choices=[('GREEN', 'Xavfsiz'), ('YELLOW', "Ehtiyotkor bo'l"), ('RED', 'Xavfli')], default='GREEN', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': "Do'kon",
                'verbose_name_plural': "Do'konlar",
                'ordering': ['name'],
            },
        ),
    ]
