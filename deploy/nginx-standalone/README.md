# Standalone Nginx (ARXIV — production'da ISHLATILMAYDI)

Bu katalogdagi fayllar **faol emas**. Ular loyiha ichida o'z nginx
reverse proxy'si ishlagan davrdan qolgan.

Hozirgi arxitekturada reverse proxy va SSL termination'ni **tashqi
Nginx Proxy Manager (NPM)** bajaradi:

```
Internet ──80/443──> Nginx Proxy Manager ──> web:8000 ──> db / redis
```

Fayllar o'chirilmadi — agar biror sababga ko'ra NPM'dan voz kechib,
loyihaning o'z nginx'iga qaytish kerak bo'lsa, ular tayyor turibdi.

| Fayl | Tavsif |
|---|---|
| `nginx.conf` | `conf.d/default.conf` uchun server bloklari + HTTPS shabloni |
| `nginx-app.inc` | HTTP/HTTPS umumiy qismi: static/media, security header, maxfiy fayl bloki |

## Qaytarish (agar kerak bo'lsa)

`docker-compose.yml` ga quyidagi servisni qo'shing va `web` ni
`npm_network` dan uzing:

```yaml
  nginx:
    image: nginx:1.27-alpine
    container_name: sesport_nginx
    restart: unless-stopped
    ports:
      - "2020:80"
      - "443:443"
    volumes:
      - ./deploy/nginx-standalone/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./deploy/nginx-standalone/nginx-app.inc:/etc/nginx/conf.d/sesport-app.inc:ro
      - ./index.html:/app/public/index.html:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    networks:
      - backend
    depends_on:
      web:
        condition: service_healthy
```

Bu konfiguratsiya real `nginx -t` bilan tekshirilgan va ishlagan.
