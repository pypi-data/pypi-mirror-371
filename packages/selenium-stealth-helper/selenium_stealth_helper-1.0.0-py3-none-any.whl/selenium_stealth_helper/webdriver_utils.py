from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import time
import random
import json
import hashlib
import base64
import socket
import platform
import psutil

def setup_driver(headless=False, proxy=None):
    chrome_options = Options()
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    if headless:
        chrome_options.add_argument("--headless")
    
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")
    
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--disable-css")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Подавление логов
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--disable-web-resources")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-component-update")
    chrome_options.add_argument("--disable-domain-reliability")
    chrome_options.add_argument("--disable-features=AudioServiceOutOfProcess")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-downloads")
    chrome_options.add_argument("--disable-background-upload")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--disable-web-resources")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-component-update")
    chrome_options.add_argument("--disable-domain-reliability")
    chrome_options.add_argument("--disable-features=AudioServiceOutOfProcess")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-downloads")
    chrome_options.add_argument("--disable-background-upload")
    
    # Скрытие логов DevTools
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Отключение логирования
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    
    # Создание сервиса с подавлением логов
    service = Service(log_output=os.devnull)
    
    driver = webdriver.Chrome(options=chrome_options, service=service)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def setup_driver_with_stealth(headless=False):
    return setup_driver(headless=headless)

def get_driver_info(driver):
    try:
        info = {
            'user_agent': driver.execute_script("return navigator.userAgent"),
            'platform': driver.execute_script("return navigator.platform"),
            'language': driver.execute_script("return navigator.language"),
            'cookies_enabled': driver.execute_script("return navigator.cookieEnabled"),
            'java_enabled': driver.execute_script("return navigator.javaEnabled()"),
            'on_line': driver.execute_script("return navigator.onLine"),
            'screen_width': driver.execute_script("return screen.width"),
            'screen_height': driver.execute_script("return screen.height"),
            'color_depth': driver.execute_script("return screen.colorDepth"),
            'pixel_depth': driver.execute_script("return screen.pixelDepth"),
            'timezone_offset': driver.execute_script("return new Date().getTimezoneOffset()"),
            'timezone': driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone")
        }
        return info
    except:
        return {}

def close_driver(driver):
    try:
        driver.quit()
    except:
        pass

def get_system_info():
    try:
        info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').total
        }
        return info
    except:
        return {}

def validate_webdriver_capabilities(driver):
    try:
        capabilities = driver.capabilities
        
        validation = {
            'browser_name': capabilities.get('browserName'),
            'browser_version': capabilities.get('browserVersion'),
            'platform_name': capabilities.get('platformName'),
            'accept_insecure_certs': capabilities.get('acceptInsecureCerts'),
            'page_load_strategy': capabilities.get('pageLoadStrategy'),
            'proxy': capabilities.get('proxy'),
            'set_window_rect': capabilities.get('setWindowRect'),
            'timeouts': capabilities.get('timeouts'),
            'unhandled_prompt_behavior': capabilities.get('unhandledPromptBehavior')
        }
        
        return validation
    except:
        return {}

def check_webdriver_stealth(driver):
    try:
        stealth_checks = {
            'webdriver_property': driver.execute_script("return navigator.webdriver"),
            'chrome_automation': driver.execute_script("return window.chrome && window.chrome.runtime"),
            'selenium_property': driver.execute_script("return window.selenium"),
            'webdriver_undefined': driver.execute_script("return typeof navigator.webdriver === 'undefined'"),
            'chrome_runtime': driver.execute_script("return typeof chrome !== 'undefined' && chrome.runtime")
        }
        
        return stealth_checks
    except:
        return {}

def analyze_page_performance(driver):
    try:
        performance = driver.execute_script("""
            var performance = window.performance;
            if (performance) {
                var timing = performance.timing;
                return {
                    'navigation_start': timing.navigationStart,
                    'dom_loading': timing.domLoading,
                    'dom_interactive': timing.domInteractive,
                    'dom_complete': timing.domComplete,
                    'load_event_start': timing.loadEventStart,
                    'load_event_end': timing.loadEventEnd,
                    'dom_content_loaded': timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart,
                    'load_time': timing.loadEventEnd - timing.navigationStart
                };
            }
            return null;
        """)
        
        return performance
    except:
        return {}

def get_page_metrics(driver):
    try:
        metrics = {
            'title': driver.title,
            'url': driver.current_url,
            'window_size': driver.get_window_size(),
            'page_source_length': len(driver.page_source),
            'cookies_count': len(driver.get_cookies()),
            'local_storage_count': driver.execute_script("return Object.keys(localStorage).length"),
            'session_storage_count': driver.execute_script("return Object.keys(sessionStorage).length")
        }
        
        return metrics
    except:
        return {}

def validate_network_connectivity():
    try:
        test_urls = [
            'https://www.google.com',
            'https://www.cloudflare.com',
            'https://www.github.com'
        ]
        
        results = {}
        for url in test_urls:
            try:
                import requests
                response = requests.get(url, timeout=5)
                results[url] = {
                    'status': 'success',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                results[url] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return results
    except:
        return {}

def check_browser_compatibility(driver):
    try:
        compatibility = {
            'local_storage': driver.execute_script("return typeof(Storage) !== 'undefined'"),
            'session_storage': driver.execute_script("return typeof(sessionStorage) !== 'undefined'"),
            'geolocation': driver.execute_script("return 'geolocation' in navigator"),
            'web_workers': driver.execute_script("return typeof(Worker) !== 'undefined'"),
            'web_sockets': driver.execute_script("return typeof(WebSocket) !== 'undefined'"),
            'canvas': driver.execute_script("return typeof(HTMLCanvasElement) !== 'undefined'"),
            'webgl': driver.execute_script("return typeof(WebGLRenderingContext) !== 'undefined'"),
            'indexed_db': driver.execute_script("return 'indexedDB' in window"),
            'service_workers': driver.execute_script("return 'serviceWorker' in navigator")
        }
        
        return compatibility
    except:
        return {}

def analyze_memory_usage():
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent(),
            'num_threads': process.num_threads(),
            'create_time': process.create_time()
        }
    except:
        return {}

def validate_file_permissions():
    try:
        test_paths = [
            os.path.expanduser('~'),
            os.getcwd(),
            '/tmp' if os.name != 'nt' else os.environ.get('TEMP', 'C:\\Windows\\Temp')
        ]
        
        permissions = {}
        for path in test_paths:
            try:
                permissions[path] = {
                    'readable': os.access(path, os.R_OK),
                    'writable': os.access(path, os.W_OK),
                    'executable': os.access(path, os.X_OK),
                    'exists': os.path.exists(path)
                }
            except:
                permissions[path] = {
                    'readable': False,
                    'writable': False,
                    'executable': False,
                    'exists': False
                }
        
        return permissions
    except:
        return {}
