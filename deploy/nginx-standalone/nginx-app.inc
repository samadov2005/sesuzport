# ============================================================
# SESPORT — HTTP va HTTPS server bloklari uchun umumiy qism
#
# /etc/nginx/conf.d/sesport-app.inc sifatida mount qilinadi.
# `.inc` kengaytmasi ataylab tanlangan: nginx'ning asosiy configi
# conf.d/*.conf ni avtomatik include qiladi, `.inc` esa faqat
# nginx.conf dan qo'lda `include` qilinganda ishlaydi.
#
# DIQQAT — nginx `add_header` merosi:
# location ichida hech bo'lmasa bitta add_header bo'lsa, YUQORIDAGI
# barcha add_header'lar O'SHA blokda bekor bo'ladi. Shu sabab static/
# media bloklarida xavfsizlik sarlavhalari qayta takrorlangan.
# ============================================================

# ── Yuklamalar (shikoyat rasm/audio fayllari) ──
client_max_body_size 20M;
client_body_timeout  120s;

# ── Upstream timeoutlari ──
proxy_connect_timeout 30s;
proxy_send_timeout    120s;
proxy_read_timeout    120s;

# ── Siqish ──
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 5;
gzip_min_length 1024;
gzip_types
    text/plain
    text/css
    text/javascript
    application/javascript
    application/json
    application/xml
    application/rss+xml
    image/svg+xml;

# ── Xavfsizlik sarlavhalari (server darajasi) ──
# HSTS bu yerda YO'Q: u faqat HTTPS blokida qo'shiladi (nginx.conf).
add_header X-Content-Type-Options     "nosniff"                         always;
add_header X-Frame-Options            "DENY"                            always;
add_header Referrer-Policy            "strict-origin-when-cross-origin" always;
add_header Permissions-Policy         "geolocation=(self), microphone=(), camera=()" always;
add_header Cross-Origin-Opener-Policy "same-origin"                     always;

# ============================================================
# 1) Maxfiy fayllarni bloklash — regex location'lar eng birinchi
#    yozilgan tartibda tekshiriladi, shuning uchun bular yuqorida.
# ============================================================

# Nuqta bilan boshlanadigan hamma narsa: .env, .git/, .htaccess ...
# (acme-challenge nginx.conf da `^~` bilan oldinroq ushlanadi)
location ~ /\. {
    deny all;
    access_log off;
    log_not_found off;
    return 404;
}

# Kod, konfiguratsiya va baza fayllari hech qachon HTTP orqali berilmasin
location ~* \.(py|pyc|pyo|sqlite3|db|sql|log|ini|cfg|conf|bak|swp|yml|yaml|toml|env)$ {
    deny all;
    access_log off;
    log_not_found off;
    return 404;
}

# Yuklangan fayl brauzerda skript sifatida bajarilmasin (stored XSS himoyasi).
# `root /app` ishlatilgan: /media/x.svg -> /app/media/x.svg
# (`alias` bo'lganida bu regex blok yo'lni meros qilib ololmasdi).
location ~* ^/media/.+\.(php|pl|cgi|sh|jsp|asp|aspx|html?|xhtml|xml|svg|js|mjs)$ {
    root /app;
    add_header Content-Type               "text/plain"    always;
    add_header Content-Disposition        "attachment"    always;
    add_header X-Content-Type-Options     "nosniff"       always;
    add_header X-Frame-Options            "DENY"          always;
    add_header Content-Security-Policy    "default-src 'none'" always;
    access_log off;
    expires 7d;
    try_files $uri =404;
}

# ============================================================
# 2) Static / media
# ============================================================

# collectstatic natijasi — STATIC_ROOT=/app/staticfiles (read-only volume)
location /static/ {
    alias /app/staticfiles/;
    access_log off;
    expires 30d;
    add_header Cache-Control              "public, no-transform"            always;
    add_header X-Content-Type-Options     "nosniff"                         always;
    add_header X-Frame-Options            "DENY"                            always;
    add_header Referrer-Policy            "strict-origin-when-cross-origin" always;
    try_files $uri =404;
}

# Foydalanuvchi yuklagan fayllar (shikoyat rasm/audio)
location /media/ {
    root /app;
    access_log off;
    expires 7d;
    add_header Cache-Control              "public"                          always;
    add_header X-Content-Type-Options     "nosniff"                         always;
    add_header X-Frame-Options            "DENY"                            always;
    add_header Referrer-Policy            "strict-origin-when-cross-origin" always;
    try_files $uri =404;
}

# ── Statik demo sahifa (index.html) ──
location = /demo {
    alias /app/public/index.html;
    default_type text/html;
    expires 1h;
}

# ============================================================
# 3) Django (gunicorn)
# ============================================================

# Healthcheck — access logga yozilmasin (30 soniyada bir marta keladi)
location = /healthz/ {
    access_log off;
    proxy_pass http://django;
    proxy_http_version 1.1;
    proxy_set_header Host              $http_host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection        "";
}

location / {
    proxy_pass http://django;
    proxy_http_version 1.1;

    # $http_host — porti bilan birga ($host portni tashlab yuboradi).
    # 2020-portli kirishda Django redirectlari to'g'ri manzil berishi uchun shart.
    proxy_set_header Host              $http_host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host  $http_host;
    proxy_set_header X-Forwarded-Port  $server_port;
    proxy_set_header Connection        "";

    proxy_redirect off;
    proxy_buffering on;
    proxy_buffers 8 16k;
    proxy_buffer_size 16k;
}
