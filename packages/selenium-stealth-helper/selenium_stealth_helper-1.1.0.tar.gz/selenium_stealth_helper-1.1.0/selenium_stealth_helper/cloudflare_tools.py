import requests
import time
import random
import json
import hashlib
import base64
import socket
import ssl
from urllib.parse import urlparse

def bypass_cloudflare(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'CF-Connecting-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return {"status": "success", "message": "Cloudflare bypass successful"}
        else:
            return {"status": "failed", "message": f"Status code: {response.status_code}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_cloudflare_protection(url):
    try:
        response = requests.get(url, timeout=10)
        headers = response.headers
        
        cloudflare_indicators = [
            'cf-ray',
            'cf-cache-status',
            'cf-request-id',
            'server'
        ]
        
        for indicator in cloudflare_indicators:
            if indicator in headers:
                return True
                
        return False
    except:
        return False

def analyze_ssl_certificate(url):
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        port = parsed_url.port or 443
        
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                return {
                    'subject': dict(x[0] for x in cert['subject']),
                    'issuer': dict(x[0] for x in cert['issuer']),
                    'version': cert['version'],
                    'serial_number': cert['serialNumber'],
                    'not_before': cert['notBefore'],
                    'not_after': cert['notAfter']
                }
    except:
        return {}

def check_http_headers(url):
    try:
        response = requests.head(url, timeout=10)
        return dict(response.headers)
    except:
        return {}

def validate_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return {"valid": True, "ip": ip}
    except:
        return {"valid": False, "ip": None}

def analyze_response_headers(url):
    try:
        response = requests.get(url, timeout=10)
        headers = response.headers
        
        analysis = {
            'content_type': headers.get('content-type'),
            'content_length': headers.get('content-length'),
            'server': headers.get('server'),
            'date': headers.get('date'),
            'last_modified': headers.get('last-modified'),
            'etag': headers.get('etag'),
            'cache_control': headers.get('cache-control'),
            'expires': headers.get('expires')
        }
        
        return analysis
    except:
        return {}

def check_robots_txt(domain):
    try:
        robots_url = f"https://{domain}/robots.txt"
        response = requests.get(robots_url, timeout=10)
        
        if response.status_code == 200:
            return {
                'exists': True,
                'content': response.text,
                'size': len(response.content)
            }
        else:
            return {'exists': False, 'content': None, 'size': 0}
    except:
        return {'exists': False, 'content': None, 'size': 0}

def analyze_sitemap(domain):
    try:
        sitemap_url = f"https://{domain}/sitemap.xml"
        response = requests.get(sitemap_url, timeout=10)
        
        if response.status_code == 200:
            return {
                'exists': True,
                'content': response.text,
                'size': len(response.content)
            }
        else:
            return {'exists': False, 'content': None, 'size': 0}
    except:
        return {'exists': False, 'content': None, 'size': 0}

def check_dns_records(domain):
    try:
        import dns.resolver
        
        records = {}
        
        for record_type in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                records[record_type] = [str(answer) for answer in answers]
            except:
                records[record_type] = []
                
        return records
    except:
        return {}

def validate_http_status(url):
    try:
        response = requests.get(url, timeout=10)
        return {
            'status_code': response.status_code,
            'reason': response.reason,
            'url': response.url
        }
    except Exception as e:
        return {
            'status_code': None,
            'reason': str(e),
            'url': url
        }

def analyze_redirects(url):
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        
        redirects = []
        for r in response.history:
            redirects.append({
                'status_code': r.status_code,
                'url': r.url,
                'headers': dict(r.headers)
            })
            
        return {
            'final_url': response.url,
            'redirects': redirects,
            'total_redirects': len(redirects)
        }
    except:
        return {'final_url': url, 'redirects': [], 'total_redirects': 0}

def check_content_security_policy(url):
    try:
        response = requests.get(url, timeout=10)
        csp_header = response.headers.get('Content-Security-Policy')
        
        if csp_header:
            return {
                'exists': True,
                'policy': csp_header
            }
        else:
            return {'exists': False, 'policy': None}
    except:
        return {'exists': False, 'policy': None}

def analyze_cookies(url):
    try:
        response = requests.get(url, timeout=10)
        cookies = response.cookies
        
        cookie_data = []
        for cookie in cookies:
            cookie_data.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'expires': cookie.expires,
                'secure': cookie.secure,
                'http_only': cookie.has_nonstandard_attr('HttpOnly')
            })
            
        return cookie_data
    except:
        return []

def validate_json_api(url):
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                return {
                    'valid_json': True,
                    'data_type': type(json_data).__name__,
                    'size': len(response.content)
                }
            except:
                return {'valid_json': False, 'data_type': 'text', 'size': len(response.content)}
        else:
            return {'valid_json': False, 'data_type': None, 'size': 0}
    except:
        return {'valid_json': False, 'data_type': None, 'size': 0}
