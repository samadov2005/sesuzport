import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppLocaleNotifier extends ChangeNotifier {
  static final AppLocaleNotifier instance = AppLocaleNotifier._();
  AppLocaleNotifier._();

  String _lang = 'uz';
  String get lang => _lang;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString('app_lang');
    if (saved != null) {
      _lang = saved;
      notifyListeners();
    }
  }

  Future<void> setLanguage(String newLang) async {
    if (_lang == newLang) return;
    _lang = newLang;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('app_lang', newLang);
  }
}

class AppStrings {
  static String get(String key) {
    final lang = AppLocaleNotifier.instance.lang;
    return _translations[lang]?[key] ?? _translations['uz']?[key] ?? key;
  }

  static const Map<String, Map<String, String>> _translations = {
    'uz': {
      'app_name': 'SESPORT',
      'app_subtitle': 'Sanitariya xavfsizligi va iste\'molchilar himoyasi',
      'login': 'Kirish',
      'register': 'Ro\'yxatdan o\'tish',
      'full_name': 'Ism va Familiya',
      'full_name_hint': 'Avazbek Samadov',
      'phone_number': 'Telefon raqamingiz',
      'phone_hint': '+998 (90) 123-45-67',
      'language': 'Tilni tanlang',
      'login_btn': 'Tizimga kirish',
      'register_btn': 'Ro\'yxatdan o\'tish',
      'have_account': 'Akkauntingiz bormi? Kirish',
      'no_account': 'Akkauntingiz yo\'qmi? Ro\'yxatdan o\'tish',
      'terms_note': 'Kirish orqali xavfsizlik va maxfiylik shartlariga rozilik bildirasiz.',
      'home': 'Asosiy',
      'stores': 'Do\'konlar',
      'complaint': 'Murojaat',
      'menu': 'Menyu',
      'quick_complaint': 'TEZKOR SHIKOYAT',
      'quick_complaint_desc': '📸 Jonli kamera orqali qoidabuzarlikni yuborish',
      'my_complaints': 'Mening murojaatlarim',
      'resolved': 'Hal qilingan',
      'safe_stores': 'Xavfsiz do\'konlar (Yashil reyting)',
      'all': 'Barchasi',
      'cashback_points': 'Keshbek va ballarim',
      'consumer_rights': 'Iste\'molchi huquqlari',
      'support_1080': 'Yordam va Aloqa (1080)',
      'admin_panel': '🛡 SESPORT Admin Paneli',
      'logout': 'Chiqish (Akkauntdan)',
      'dark_mode': 'Tungi rejim (Dark)',
      'light_mode': 'Yorug\' rejim (Light)',
      'submit_complaint': 'Murojaatni tasdiqlash',
      'send_complaint_btn': 'Murojaatni yuborish',
      'problem_category': 'Muammo toifasi:',
      'additional_note': 'Qo\'shimcha izoh (ixtiyoriy):',
      'location_gps': 'Hodisa joylashuvi (GPS)',
      'refresh_location': 'Joylashuvni yangilash',
      'distance_near': 'm yaqinlikda',
      'distance_km_near': 'km yaqinlikda',
    },
    'ru': {
      'app_name': 'SESPORT',
      'app_subtitle': 'Санитарная безопасность и защита прав потребителей',
      'login': 'Вход',
      'register': 'Регистрация',
      'full_name': 'Имя и Фамилия',
      'full_name_hint': 'Авазбек Самадов',
      'phone_number': 'Номер телефона',
      'phone_hint': '+998 (90) 123-45-67',
      'language': 'Выберите язык',
      'login_btn': 'Войти в систему',
      'register_btn': 'Зарегистрироваться',
      'have_account': 'Уже есть аккаунт? Войти',
      'no_account': 'Нет аккаунта? Регистрация',
      'terms_note': 'Входя, вы соглашаетесь с условиями конфиденциальности.',
      'home': 'Главная',
      'stores': 'Магазины',
      'complaint': 'Жалоба',
      'menu': 'Меню',
      'quick_complaint': 'БЫСТРАЯ ЖАЛОБА',
      'quick_complaint_desc': '📸 Отправить нарушение через живую камеру',
      'my_complaints': 'Мои обращения',
      'resolved': 'Решено',
      'safe_stores': 'Безопасные магазины (Зеленый рейтинг)',
      'all': 'Все',
      'cashback_points': 'Кэшбэк и баллы',
      'consumer_rights': 'Права потребителей',
      'support_1080': 'Поддержка и связь (1080)',
      'admin_panel': '🛡 Панель Администратора',
      'logout': 'Выйти из аккаунта',
      'dark_mode': 'Темный режим (Dark)',
      'light_mode': 'Светлый режим (Light)',
      'submit_complaint': 'Подтверждение обращения',
      'send_complaint_btn': 'Отправить жалобу',
      'problem_category': 'Категория проблемы:',
      'additional_note': 'Дополнительный комментарий (необязательно):',
      'location_gps': 'Местоположение события (GPS)',
      'refresh_location': 'Обновить локацию',
      'distance_near': 'м рядом',
      'distance_km_near': 'км рядом',
    },
    'en': {
      'app_name': 'SESPORT',
      'app_subtitle': 'Sanitary Safety & Consumer Rights Protection',
      'login': 'Login',
      'register': 'Sign Up',
      'full_name': 'Full Name',
      'full_name_hint': 'Avazbek Samadov',
      'phone_number': 'Phone Number',
      'phone_hint': '+998 (90) 123-45-67',
      'language': 'Select Language',
      'login_btn': 'Sign In',
      'register_btn': 'Create Account',
      'have_account': 'Already have an account? Sign In',
      'no_account': 'Don\'t have an account? Sign Up',
      'terms_note': 'By continuing you agree to safety and privacy terms.',
      'home': 'Home',
      'stores': 'Stores',
      'complaint': 'Complaints',
      'menu': 'Menu',
      'quick_complaint': 'QUICK COMPLAINT',
      'quick_complaint_desc': '📸 Submit violation via live camera',
      'my_complaints': 'My Complaints',
      'resolved': 'Resolved',
      'safe_stores': 'Safe Stores (Green Rating)',
      'all': 'All',
      'cashback_points': 'Cashback & Points',
      'consumer_rights': 'Consumer Rights',
      'support_1080': 'Help & Hotline (1080)',
      'admin_panel': '🛡 SESPORT Admin Panel',
      'logout': 'Log Out',
      'dark_mode': 'Dark Mode',
      'light_mode': 'Light Mode',
      'submit_complaint': 'Confirm Complaint',
      'send_complaint_btn': 'Submit Complaint',
      'problem_category': 'Issue Category:',
      'additional_note': 'Additional note (optional):',
      'location_gps': 'Incident Location (GPS)',
      'refresh_location': 'Refresh Location',
      'distance_near': 'm away',
      'distance_km_near': 'km away',
    }
  };
}
