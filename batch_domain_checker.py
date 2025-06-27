#!/usr/bin/env python3
"""
Batch Domain Checker Script
Пример использования Email Domain Validator для проверки списка доменов
"""

import requests
import json
import time
from typing import List, Dict, Any

class DomainChecker:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def validate_single_domain(self, domain: str) -> Dict[str, Any]:
        """Проверка одного домена"""
        url = f"{self.base_url}/api/v1/domain/validate"
        payload = {"domain": domain}
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "domain": domain}
    
    def validate_batch_domains(self, domains: List[str]) -> Dict[str, Any]:
        """Проверка списка доменов одним запросом"""
        url = f"{self.base_url}/api/v1/domain/validate-batch"
        payload = {"domains": domains}
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def process_domains_from_file(self, file_path: str, batch_size: int = 50) -> List[Dict[str, Any]]:
        """Обработка доменов из файла"""
        domains = []
        
        # Читаем домены из файла
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                domain = line.strip()
                if domain and not domain.startswith('#'):  # Пропускаем пустые строки и комментарии
                    # Если это email, извлекаем домен
                    if '@' in domain:
                        domain = domain.split('@')[1]
                    domains.append(domain.lower())
        
        # Убираем дубликаты
        domains = list(set(domains))
        
        print(f"📋 Найдено {len(domains)} уникальных доменов")
        
        all_results = []
        
        # Обрабатываем батчами
        for i in range(0, len(domains), batch_size):
            batch = domains[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(domains) + batch_size - 1) // batch_size
            
            print(f"🔍 Обрабатываем батч {batch_num}/{total_batches} ({len(batch)} доменов)...")
            
            result = self.validate_batch_domains(batch)
            
            if 'error' in result:
                print(f"❌ Ошибка в батче {batch_num}: {result['error']}")
                # Пробуем обработать по одному
                for domain in batch:
                    single_result = self.validate_single_domain(domain)
                    all_results.append(single_result)
            else:
                all_results.extend(result.get('results', []))
                print(f"✅ Обработано {result.get('total_processed', 0)} доменов за {result.get('processing_time_seconds', 0):.2f}с")
            
            # Небольшая пауза между батчами
            time.sleep(0.5)
        
        return all_results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str = "domain_validation_results.json"):
        """Сохранение результатов в файл"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Результаты сохранены в {output_file}")
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Вывод сводки результатов"""
        if not results:
            print("❌ Нет результатов для анализа")
            return
        
        print("\n" + "="*60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ")
        print("="*60)
        
        # Статистика по типам доменов
        type_stats = {}
        recommendation_stats = {}
        quality_scores = []
        
        for result in results:
            if 'error' in result:
                continue
                
            domain_type = result.get('domain_type', 'unknown')
            recommendation = result.get('recommendation', 'unknown')
            quality_score = result.get('quality_score', 0)
            
            type_stats[domain_type] = type_stats.get(domain_type, 0) + 1
            recommendation_stats[recommendation] = recommendation_stats.get(recommendation, 0) + 1
            quality_scores.append(quality_score)
        
        print(f"Всего обработано: {len([r for r in results if 'error' not in r])}")
        print(f"Ошибок: {len([r for r in results if 'error' in r])}")
        
        if quality_scores:
            print(f"Средний балл качества: {sum(quality_scores)/len(quality_scores):.2f}")
        
        print("\n📈 По типам доменов:")
        for domain_type, count in sorted(type_stats.items()):
            print(f"  {domain_type}: {count}")
        
        print("\n🎯 По рекомендациям:")
        for rec, count in sorted(recommendation_stats.items()):
            print(f"  {rec}: {count}")
        
        # Топ проблемных доменов
        problematic = [r for r in results if 'error' not in r and r.get('recommendation') in ['reject', 'manual_review']]
        if problematic:
            print(f"\n⚠️  Проблемные домены ({len(problematic)}):")
            for result in problematic[:10]:  # Показываем первые 10
                domain = result.get('domain', 'unknown')
                rec = result.get('recommendation', 'unknown')
                domain_type = result.get('domain_type', 'unknown')
                score = result.get('quality_score', 0)
                print(f"  {domain} - {domain_type} ({rec}) - {score:.1f}/10")


def main():
    """Основная функция для демонстрации использования"""
    
    # Создаем пример файла с доменами, если его нет
    example_domains = [
        "# Пример списка доменов для проверки",
        "# Можно указывать как домены, так и полные email адреса",
        "example.com",
        "user@gmail.com",
        "info@microsoft.com",
        "test@harvard.edu",
        "support@whitehouse.gov",
        "spam@10minutemail.com",
        "fake@mailinator.com",
        "nonexistent-domain-12345.com"
    ]
    
    with open("domains_to_check.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(example_domains))
    
    print("📋 Создан пример файла domains_to_check.txt")
    print("Отредактируйте его, добавив свои домены для проверки")
    print("\nДля запуска проверки:")
    print("python batch_domain_checker.py")
    
    # Инициализация проверялки
    checker = DomainChecker()
    
    # Проверяем, что сервис доступен
    try:
        response = requests.get(f"{checker.base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Сервис доступен")
        else:
            print("❌ Сервис недоступен. Убедитесь, что он запущен")
            return
    except requests.exceptions.RequestException:
        print("❌ Не удается подключиться к сервису")
        print("Убедитесь, что сервис запущен на http://localhost:8080")
        return
    
    # Обрабатываем домены из файла
    try:
        results = checker.process_domains_from_file("domains_to_check.txt")
        
        # Сохраняем результаты
        checker.save_results(results)
        
        # Выводим сводку
        checker.print_summary(results)
        
    except FileNotFoundError:
        print("❌ Файл domains_to_check.txt не найден")
        print("Создайте файл с доменами (по одному в строке)")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main() 