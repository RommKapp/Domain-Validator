# 🚀 Быстрый старт - Email Domain Validator

## Как проверить ваш список доменов

### 1. Запуск системы

Сначала убедитесь, что система запущена:

```bash
# Убиваем возможные предыдущие процессы
docker-compose down

# Запускаем все сервисы
docker-compose up -d
```

Проверьте, что все сервисы работают:
```bash
curl http://localhost/health
# Должен вернуть: {"status":"healthy"}
```

### 2. Способы проверки доменов

#### А) Через готовый Python скрипт (Рекомендуется)

```bash
# Установите зависимости
pip install requests

# Запустите скрипт
python batch_domain_checker.py
```

Скрипт создаст файл `domains_to_check.txt` - отредактируйте его, добавив ваши домены:

```
# Ваши домены (можно email адреса или просто домены)
company1.com
user@company2.com  
info@potential-client.org
# и так далее...
```

#### Б) Через API напрямую

**Один домен:**
```bash
curl -X POST "http://localhost/api/v1/domain/validate" \
     -H "Content-Type: application/json" \
     -d '{"domain": "example.com"}'
```

**Несколько доменов:**
```bash
curl -X POST "http://localhost/api/v1/domain/validate-batch" \
     -H "Content-Type: application/json" \
     -d '{"domains": ["example.com", "test@gmail.com", "info@company.org"]}'
```

#### В) Через веб-интерфейс

Откройте в браузере: http://localhost

### 3. Понимание результатов

Каждый домен получает:

- **domain_type**: Тип домена
  - `corporate` - корпоративный домен ✅
  - `educational` - образовательное учреждение ✅  
  - `government` - государственный ✅
  - `public_provider` - публичный провайдер (Gmail, Yahoo) ⚠️
  - `disposable` - временный email ❌
  - `suspicious` - подозрительный ❌
  - `unreachable` - недоступный ❌

- **recommendation**: Рекомендация
  - `accept` - принять ✅
  - `manual_review` - ручная проверка ⚠️
  - `reject` - отклонить ❌

- **quality_score**: Балл качества (0-10)

### 4. Пример результата

```json
{
  "domain": "microsoft.com",
  "domain_type": "corporate",
  "validation_status": "valid",
  "quality_score": 8.5,
  "recommendation": "accept",
  "metadata": {
    "has_mx_record": true,
    "has_a_record": true,
    "mx_servers": ["microsoft-com.mail.protection.outlook.com"],
    "website_accessible": true,
    "has_ssl_certificate": true
  },
  "checked_at": "2024-01-01T12:00:00Z"
}
```

### 5. Фильтрация результатов

После проверки вы получите файл `domain_validation_results.json`. Можете фильтровать:

**Принять (высокое качество):**
- `recommendation = "accept"`
- `quality_score >= 7`

**Проверить вручную:**
- `recommendation = "manual_review"`
- `domain_type = "public_provider"`

**Отклонить:**
- `recommendation = "reject"`
- `domain_type` в `["disposable", "suspicious", "unreachable"]`

### 6. Полезные команды

```bash
# Проверить статус сервисов
docker-compose ps

# Посмотреть логи
docker-compose logs edv_app

# Остановить все
docker-compose down

# Перезапустить
docker-compose restart

# Очистить кеш Redis
docker-compose exec redis redis-cli FLUSHALL
```

### 7. Настройки производительности

В файле `.env` (создайте из `.env.example`):

```env
# Размер батча для обработки
BATCH_SIZE=100

# Таймаут запросов (секунды)
REQUEST_TIMEOUT=5

# TTL кеша (секунды)
CACHE_TTL=3600
```

### 8. Администрирование

**Добавить домен в белый список:**
```bash
curl -X POST "http://localhost/api/v1/admin/whitelist" \
     -H "Content-Type: application/json" \
     -d '{"domain": "trusted-partner.com", "notes": "Проверенный партнер"}'
```

**Добавить в черный список:**
```bash
curl -X POST "http://localhost/api/v1/admin/blacklist" \
     -H "Content-Type: application/json" \
     -d '{"domain": "spam-domain.com", "notes": "Спам источник"}'
```

**Статистика кеша:**
```bash
curl http://localhost/api/v1/domain/cache/stats
```

## Практический пример использования

1. У вас есть CSV файл с email адресами
2. Извлекаете домены: `cut -d'@' -f2 emails.csv | sort | uniq > domains.txt`
3. Запускаете: `python batch_domain_checker.py` 
4. Получаете результаты в `domain_validation_results.json`
5. Фильтруете по рекомендациям для дальнейших действий

## Поддержка

- API документация: http://localhost/docs
- Админ панель: http://localhost/admin
- Health check: http://localhost/health 