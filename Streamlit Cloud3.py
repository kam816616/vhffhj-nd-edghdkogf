import streamlit as st
import requests
import time
import random
import pytz
from faker import Faker
from collections import OrderedDict
import socket
from urllib.parse import urlparse
import threading
import queue
import json
import ssl
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
import numpy as np

# Configuration
WEBSITE_URL = st.secrets.get("WEBSITE_URL", "https://iphey.com")
PAGE_LOAD_TIME = (1, 3)
IP_API_URL = "http://ip-api.com/json/"
NUM_VISITS = st.secrets.get("NUM_VISITS", 20)
MIN_DELAY = st.secrets.get("MIN_DELAY", 5)
MAX_DELAY = st.secrets.get("MAX_DELAY", 15)
ENABLE_BROWSER = True

# Enhanced search tasks with real queries
SEARCH_TASKS = [
    ("Check browser fingerprints", "Check browser fingerprints", "https://iphey.com/"),
    ("What is my IP address", "What Is My IP Address - See Your Public Address", "https://iphey.com/"),
    ("browser fingerprint test", "Am I Unique? Learn how identifiable you are", "https://iphey.com/"),
    ("check my digital fingerprint", "Test Your Browser Fingerprint", "https://iphey.com/"),
    ("how to protect my privacy online", "Online Privacy Protection Guide", "https://iphey.com/")
]

# Advanced Device Database
DEVICES = {
    "Android": {
        "models": [
            {"name": "Samsung Galaxy S23 Ultra", "code": "SM-S918B"},
            {"name": "Google Pixel 8 Pro", "code": "GP8P"},
            {"name": "OnePlus 11", "code": "CPH2447"},
            {"name": "Xiaomi 13 Pro", "code": "2210132G"},
            {"name": "Samsung Galaxy S22", "code": "SM-S901B"},
            {"name": "Google Pixel 7", "code": "GP7"},
            {"name": "OnePlus 10 Pro", "code": "NE2213"},
            {"name": "Xiaomi Redmi Note 12", "code": "23021RAA2Y"}
        ],
        "model_resolutions": {
            "SM-S918B": "1440x3088",
            "GP8P": "1344x2992",
            "CPH2447": "1440x3216",
            "2210132G": "1440x3200",
            "SM-S901B": "1080x2340",
            "GP7": "1080x2400",
            "NE2213": "1440x3216",
            "23021RAA2Y": "1080x2400"
        },
        "platform": "Linux armv8l",
        "user_agent_templates": [
            "Mozilla/5.0 (Linux; Android {version}; {model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android {version}; {model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Mobile Safari/537.36 EdgA/{edge_version}",
            "Mozilla/5.0 (Linux; Android {version}; {model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Mobile Safari/537.36 OPR/{opera_version}"
        ],
        "versions": ["11", "12", "13", "14", "15"],
        "chrome_versions": ["118.0.5993", "119.0.6045", "120.0.6099"],
        "edge_versions": ["118.0.2088", "119.0.2151", "120.0.2210"],
        "opera_versions": ["83.0.4254", "84.0.4316", "85.0.4341"]
    },
    "iOS": {
        "models": [
            {"name": "iPhone 15 Pro Max", "code": "iPhone16,2"},
            {"name": "iPhone 15", "code": "iPhone15,4"},
            {"name": "iPhone 14 Pro", "code": "iPhone15,2"},
            {"name": "iPhone 13 mini", "code": "iPhone14,4"},
            {"name": "iPhone SE (3rd gen)", "code": "iPhone14,6"},
            {"name": "iPad Pro (6th gen)", "code": "iPad14,3"},
            {"name": "iPad Air (5th gen)", "code": "iPad13,16"},
            {"name": "iPad mini (6th gen)", "code": "iPad14,1"}
        ],
        "model_resolutions": {
            "iPhone16,2": "1290x2796",
            "iPhone15,4": "1179x2556",
            "iPhone15,2": "1179x2556",
            "iPhone14,4": "1080x2340",
            "iPhone14,6": "750x1334",
            "iPad14,3": "2048x2732",
            "iPad13,16": "1640x2360",
            "iPad14,1": "1488x2266"
        },
        "platform": "iPhone",
        "user_agent_templates": [
            "Mozilla/5.0 (iPhone; CPU iPhone OS {version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_version} Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS {version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_version} Mobile/15E148 Safari/604.1"
        ],
        "versions": ["16_6", "17_1", "17_2"],
        "safari_versions": ["16.6", "17.1", "17.2"]
    },
    "Windows": {
        "models": [
            {"name": "Desktop PC", "code": "Windows NT 10.0"},
            {"name": "Surface Pro 9", "code": "Touch; Tablet; Windows NT 10.0"},
            {"name": "Gaming PC", "code": "Windows NT 10.0; Win64; x64"},
            {"name": "Business Laptop", "code": "Windows NT 10.0; WOW64"}
        ],
        "resolutions": ["1920x1080", "2560x1440", "3840x2160", "1366x768", "3440x1440", "2560x1600"],
        "platform": "Win32",
        "user_agent_templates": [
            "Mozilla/5.0 (Windows NT {version}; {architecture}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36",
            "Mozilla/5.0 (Windows NT {version}; {architecture}; rv:{firefox_version}) Gecko/20100101 Firefox/{firefox_version}",
            "Mozilla/5.0 (Windows NT {version}; {architecture}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36 Edg/{edge_version}"
        ],
        "versions": ["10.0", "11.0"],
        "architectures": ["Win64; x64", "WOW64"],
        "chrome_versions": ["119.0.6045", "120.0.6099", "121.0.6167"],
        "firefox_versions": ["119.0", "120.0", "121.0"],
        "edge_versions": ["119.0.2151", "120.0.2210", "121.0.2277"]
    },
    "macOS": {
        "models": [
            {"name": "MacBook Pro 16\" M3", "code": "Macintosh"},
            {"name": "iMac 24\" M1", "code": "Macintosh"},
            {"name": "MacBook Air 15\" M2", "code": "Macintosh"},
            {"name": "Mac mini M2", "code": "Macintosh"}
        ],
        "resolutions": ["3456x2234", "4480x2520", "3024x1964", "2560x1600", "5120x2880"],
        "platform": "MacIntel",
        "user_agent_templates": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {version}; rv:{firefox_version}) Gecko/20100101 Firefox/{firefox_version}",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {version}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_version} Safari/605.1.15"
        ],
        "versions": ["13_5", "14_1", "14_2"],
        "chrome_versions": ["119.0.6045", "120.0.6099", "121.0.6167"],
        "firefox_versions": ["119.0", "120.0", "121.0"],
        "safari_versions": ["16.6", "17.1", "17.2"]
    }
}

# Global variables
session = None
message_queue = queue.Queue()
simulation_running = False
simulation_lock = threading.Lock()
ua = UserAgent()
fake = Faker()

def get_timezone_for_ip(ip_info):
    """Get timezone based on IP location"""
    if ip_info and 'timezone' in ip_info:
        return ip_info['timezone']
    return random.choice([
        'America/New_York',
        'Europe/London',
        'Asia/Tokyo',
        'Australia/Sydney',
        'Europe/Paris'
    ])

def get_random_device():
    """Select a random device with all necessary properties"""
    platform = random.choice(list(DEVICES.keys()))
    device_data = DEVICES[platform]
    
    if platform in ["Android", "iOS"]:
        model = random.choice(device_data["models"])
        resolution = device_data["model_resolutions"][model["code"]]
    else:
        model = random.choice(device_data["models"])
        resolution = random.choice(device_data["resolutions"])
    
    return {
        "platform": platform,
        "model": model,
        "resolution": resolution,
        "width": resolution.split('x')[0]
    }

def generate_platform_user_agent(device):
    """Generate realistic user agent for the selected device"""
    platform = device["platform"]
    device_data = DEVICES[platform]
    model = device["model"]["code"]
    
    if platform == "Android":
        template = random.choice(device_data["user_agent_templates"])
        version = random.choice(device_data["versions"])
        chrome_version = random.choice(device_data["chrome_versions"])
        
        if "EdgA" in template:
            edge_version = random.choice(device_data["edge_versions"])
            return template.format(
                version=version,
                model=model,
                chrome_version=chrome_version,
                edge_version=edge_version
            )
        elif "OPR" in template:
            opera_version = random.choice(device_data["opera_versions"])
            return template.format(
                version=version,
                model=model,
                chrome_version=chrome_version,
                opera_version=opera_version
            )
        else:
            return template.format(
                version=version,
                model=model,
                chrome_version=chrome_version
            )
    
    elif platform == "iOS":
        template = random.choice(device_data["user_agent_templates"])
        version = random.choice(device_data["versions"])
        safari_version = random.choice(device_data["safari_versions"])
        return template.format(
            version=version.replace('_', '.'),
            safari_version=safari_version
        )
    
    elif platform == "Windows":
        template = random.choice(device_data["user_agent_templates"])
        version = random.choice(device_data["versions"])
        architecture = random.choice(device_data["architectures"])
        
        if "Firefox" in template:
            firefox_version = random.choice(device_data["firefox_versions"])
            return template.format(
                version=version,
                architecture=architecture,
                firefox_version=firefox_version
            )
        elif "Edg" in template:
            edge_version = random.choice(device_data["edge_versions"])
            chrome_version = random.choice(device_data["chrome_versions"])
            return template.format(
                version=version,
                architecture=architecture,
                chrome_version=chrome_version,
                edge_version=edge_version
            )
        else:
            chrome_version = random.choice(device_data["chrome_versions"])
            return template.format(
                version=version,
                architecture=architecture,
                chrome_version=chrome_version
            )
    
    elif platform == "macOS":
        template = random.choice(device_data["user_agent_templates"])
        version = random.choice(device_data["versions"])
        
        if "Firefox" in template:
            firefox_version = random.choice(device_data["firefox_versions"])
            return template.format(
                version=version.replace('_', '.'),
                firefox_version=firefox_version
            )
        elif "Safari" in template and "Chrome" not in template:
            safari_version = random.choice(device_data["safari_versions"])
            return template.format(
                version=version.replace('_', '.'),
                safari_version=safari_version
            )
        else:
            chrome_version = random.choice(device_data["chrome_versions"])
            return template.format(
                version=version.replace('_', '.'),
                chrome_version=chrome_version
            )

def get_session():
    """Create a session with advanced fingerprinting"""
    session = requests.Session()
    
    # Advanced TLS fingerprinting
    ssl_context = ssl.create_default_context()
    ssl_context.set_ciphers(':'.join([
        'ECDHE-ECDSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-ECDSA-CHACHA20-POLY1305',
        'ECDHE-RSA-CHACHA20-POLY1305',
        'ECDHE-ECDSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES128-GCM-SHA256'
    ]))
    ssl_context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    
    adapter = requests.adapters.HTTPAdapter(
        max_retries=3,
        ssl_context=ssl_context
    )
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    
    # Randomize TCP stack
    socket_options = [
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
        (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
        (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, random.randint(30, 120)),
        (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, random.randint(10, 30))
    ]
    adapter.poolmanager.connection_pool_kw['socket_options'] = socket_options
    
    return session

def get_ip_info(ip_address=None):
    """Get detailed IP information with enhanced privacy"""
    try:
        headers = {
            'User-Agent': ua.random,
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        }
        
        if ip_address:
            response = session.get(
                f"{IP_API_URL}{ip_address}",
                params={'fields': 'status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query'},
                headers=headers,
                timeout=10
            )
        else:
            response = session.get(
                IP_API_URL,
                params={'fields': 'status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query'},
                headers=headers,
                timeout=10
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data
        return None
    except Exception as e:
        message_queue.put(f"IP info lookup failed: {str(e)}")
        return None

def renew_ip():
    """Force a new IP by creating a new session"""
    global session
    try:
        old_ip_info = get_ip_info()
        old_ip = old_ip_info.get('query') if old_ip_info else None
        
        # Create new session
        session = get_session()
        
        # Verify IP changed
        max_attempts = 3
        for attempt in range(max_attempts):
            new_ip_info = get_ip_info()
            if new_ip_info:
                new_ip = new_ip_info.get('query')
                if new_ip != old_ip:
                    message_queue.put(f"IP changed from {old_ip} to {new_ip}")
                    message_queue.put(f"New location: {new_ip_info.get('city', 'Unknown')}, {new_ip_info.get('country', 'Unknown')}")
                    return new_ip_info
            time.sleep(2)
        
        raise Exception("IP did not change after multiple attempts")
    except Exception as e:
        message_queue.put(f"IP renewal failed: {str(e)}")
        return None

def generate_advanced_fingerprint(device, ip_info):
    """Generate ultra-realistic browser fingerprint with behavioral patterns"""
    # WebGL fingerprint with realistic values
    webgl_data = {
        "vendor": "Google Inc." if device["platform"] == "Android" else "Intel Inc.",
        "renderer": "ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver-5.0.0)",
        "extensions": [
            "EXT_blend_minmax", "EXT_color_buffer_half_float", "EXT_disjoint_timer_query",
            "EXT_float_blend", "EXT_frag_depth", "EXT_shader_texture_lod",
            "EXT_texture_compression_rgtc", "EXT_texture_filter_anisotropic"
        ],
        "parameters": {
            "MAX_TEXTURE_SIZE": 16384,
            "MAX_VIEWPORT_DIMS": [16384, 16384],
            "GPU_VENDOR": "Google Inc.",
            "UNMASKED_VENDOR_WEBGL": "Google Inc.",
            "UNMASKED_RENDERER_WEBGL": "Google SwiftShader"
        },
        "noise": random.random() * 0.05  # Small random noise
    }
    
    # Canvas fingerprint with realistic patterns
    canvas_data = {
        "text": "CanvasFingerprint " + fake.word(),
        "font": "14px Arial",
        "color": "#" + fake.hex_color(),
        "background": "#" + fake.hex_color(),
        "operations": random.randint(5, 15),
        "winding": random.choice(["evenodd", "nonzero"]),
        "compositeOperation": random.choice(["source-over", "multiply", "screen"]),
        "shadow": {
            "blur": random.randint(0, 10),
            "color": "#" + fake.hex_color(),
            "offsetX": random.randint(0, 5),
            "offsetY": random.randint(0, 5)
        }
    }
    
    # AudioContext fingerprint with realistic values
    audio_data = {
        "sampleRate": 44100,
        "channelCount": 2,
        "frequencyData": [random.randint(-100, -30) for _ in range(32)],
        "timeDomainData": [random.random() * 2 - 1 for _ in range(32)],
        "noise": random.random() * 0.02
    }
    
    # Behavioral patterns
    behavior = {
        "mouseMovements": {
            "count": random.randint(5, 20),
            "pattern": random.choice(["linear", "random", "circular"]),
            "speedVariation": random.uniform(0.8, 1.2)
        },
        "scrollPattern": {
            "type": random.choice(["linear", "quick", "slow"]),
            "pauses": random.randint(1, 3),
            "scrollBackProbability": 0.3
        },
        "clickDelay": random.gammavariate(1.5, 0.3),
        "typingSpeed": random.gammavariate(2, 0.2),
        "attentionSpan": random.gammavariate(3, 1)
    }
    
    return {
        "webgl": webgl_data,
        "canvas": canvas_data,
        "audio": audio_data,
        "hardware": {
            "concurrency": random.choice([2, 4, 6, 8]),
            "memory": random.choice([4, 8, 16]),
            "deviceMemory": random.choice([4, 8, 16])
        },
        "network": {
            "connection": random.choice(["cellular", "wifi", "ethernet"]),
            "effectiveType": random.choice(["4g", "5g"]),
            "rtt": random.randint(50, 300),
            "downlink": random.uniform(1.0, 10.0),
            "saveData": random.choice([True, False])
        },
        "timezone": get_timezone_for_ip(ip_info) if ip_info else "America/New_York",
        "language": random.choice(["en-US", "en-GB", "fr-FR", "de-DE"]),
        "privacy": {
            "doNotTrack": random.choice([True, False]),
            "webdriver": False,
            "chromeExtensions": random.choice([True, False]),
            "adBlock": random.choice([True, False])
        },
        "platform": device["platform"],
        "ip_info": ip_info,
        "behavior": behavior
    }

def get_random_headers(device, fingerprint):
    """Generate natural headers with advanced fingerprinting"""
    headers = OrderedDict([
        ('Host', urlparse(WEBSITE_URL).netloc),
        ('Connection', 'keep-alive'),
        ('Upgrade-Insecure-Requests', '1'),
        ('User-Agent', generate_platform_user_agent(device)),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
        ('Sec-Fetch-Site', 'none'),
        ('Sec-Fetch-Mode', 'navigate'),
        ('Sec-Fetch-User', '?1'),
        ('Sec-Fetch-Dest', 'document'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Accept-Language', fingerprint["language"]),
        ('Cache-Control', 'max-age=0'),
        ('TE', 'trailers'),
        ('DNT', '1' if fingerprint["privacy"]["doNotTrack"] else '0'),
        ('Viewport-Width', device["width"]),
        ('Width', device["width"]),
        ('X-Timezone', fingerprint["timezone"]),
        ('X-Device-Model', device["model"]["name"]),
        ('X-Platform', device["platform"])
    ])
    
    # Random header variations
    if random.random() > 0.7:
        headers.pop('Upgrade-Insecure-Requests', None)
    if random.random() > 0.5:
        headers.pop('Sec-Fetch-User', None)
    
    # Mobile-specific headers
    if device["platform"] in ["Android", "iOS"]:
        headers.update({
            'X-Requested-With': 'com.android.chrome' if device["platform"] == "Android" else 'MobileSafari',
            'X-Mobile': 'true',
            'X-Device-Code': device["model"]["code"]
        })
    
    # Random referrer
    if random.random() > 0.5:
        headers['Referer'] = random.choice([
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://www.facebook.com/',
            'https://twitter.com/',
            'https://m.youtube.com/',
            'https://www.pinterest.com/',
            'https://www.instagram.com/',
            'https://telegram.org/'
        ])
    
    return headers

def simulate_google_search(search_query, device, fingerprint):
    """Simulate realistic Google search with advanced anti-detection"""
    try:
        headers = get_random_headers(device, fingerprint)
        headers['Referer'] = 'https://www.google.com/'
        
        # Step 1: Initial search request with human-like delays
        search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
        
        # Simulate typing delay
        typing_delay = max(0.1, np.random.normal(0.3, 0.1)) * len(search_query)
        time.sleep(typing_delay)
        
        response = session.get(search_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            message_queue.put(f"Search failed with status {response.status_code}")
            return None
        
        # Step 2: Parse search results naturally
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.select('div.g'):
            title = result.select_one('h3')
            link = result.select_one('a[href^="/url?"]')
            
            if title and link:
                url_match = re.search(r'q=(.*?)&', link['href'])
                if url_match:
                    url = requests.utils.unquote(url_match.group(1))
                    results.append({
                        'title': title.text,
                        'url': url,
                        'position': len(results) + 1
                    })
        
        if not results:
            message_queue.put("No search results found")
            return None
        
        # Step 3: Simulate natural result selection
        # Humans often click top results but sometimes scroll
        if random.random() < 0.7:  # 70% chance to click top 3
            selected = random.choices(results[:3], weights=[0.5, 0.3, 0.2], k=1)[0]
        else:  # 30% chance to scroll and click lower
            selected = random.choice(results[3:min(10, len(results))])
        
        # Simulate mouse movement and hesitation
        scroll_time = max(0.5, np.random.normal(1.5, 0.5) * (selected['position'] / 5))
        time.sleep(scroll_time)
        
        # Random hesitation before click
        time.sleep(max(0.1, np.random.normal(0.3, 0.1)))
        
        return selected['url']
        
    except Exception as e:
        message_queue.put(f"Search simulation failed: {str(e)}")
        return None

def simulate_real_visit(url, device, fingerprint):
    """Simulate ultra-realistic website visit with advanced anti-detection"""
    try:
        headers = get_random_headers(device, fingerprint)
        
        # Step 1: Initial page load with realistic timing
        start_time = time.time()
        response = session.get(url, headers=headers, timeout=20)
        load_time = time.time() - start_time
        
        if response.status_code != 200:
            message_queue.put(f"Page load failed with status {response.status_code}")
            return False
        
        # Simulate natural page load perception
        perceived_load_time = load_time * random.uniform(0.8, 1.2)
        time.sleep(max(0, perceived_load_time - load_time))
        
        # Step 2: Simulate reading behavior with realistic patterns
        content_length = len(response.text)
        read_speed = random.gammavariate(300, 0.01)  # Words per minute
        word_count = content_length / 5  # Approximate word count
        read_time = (word_count / read_speed) * 60  # Convert to seconds
        
        # Add random pauses and skimming
        actual_read_time = 0
        while actual_read_time < read_time:
            read_chunk = min(random.gammavariate(30, 0.5), read_time - actual_read_time)
            time.sleep(read_chunk)
            actual_read_time += read_chunk
            
            # Random chance to skim or pause
            if random.random() < 0.2:  # 20% chance to pause
                pause_time = random.gammavariate(5, 0.5)
                time.sleep(pause_time)
                actual_read_time += pause_time
        
        # Step 3: Simulate interactions (clicks, scrolls)
        if random.random() > 0.3:  # 70% chance of interaction
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True) 
                     if a['href'].startswith('http') and WEBSITE_URL in a['href']]
            
            if links:
                clicks = random.randint(1, min(3, len(links)))
                for _ in range(clicks):
                    link = random.choice(links)
                    
                    # Simulate mouse movement to link
                    time.sleep(random.gammavariate(0.5, 0.2))
                    
                    # Click with random delay
                    time.sleep(random.gammavariate(0.3, 0.1))
                    
                    message_queue.put(f"Clicking on: {link}")
                    session.get(link, headers=headers, timeout=15)
        
        return True
    except Exception as e:
        message_queue.put(f"Visit simulation failed: {str(e)}")
        return False

def run_simulation():
    global session, simulation_running
    
    with simulation_lock:
        simulation_running = True
        message_queue.put("🚀 Starting advanced anti-detect traffic simulation...")
        message_queue.put(f"🌐 Target website: {WEBSITE_URL}")
        message_queue.put(f"🔢 Number of visits: {NUM_VISITS}")
        message_queue.put(f"⏱️ Delay range: {MIN_DELAY}-{MAX_DELAY} seconds")
        
        try:
            session = get_session()
            successful_visits = 0
            
            for i in range(NUM_VISITS):
                if not simulation_running:
                    break
                
                # Renew IP for each visit
                ip_info = renew_ip()
                if not ip_info:
                    continue
                
                device = get_random_device()
                fingerprint = generate_advanced_fingerprint(device, ip_info)
                
                # Store current device for UI
                st.session_state.current_device = device
                st.session_state.current_fingerprint = fingerprint
                
                # Alternate between direct visits and search traffic
                if random.choice([True, False]):
                    # Direct/referral traffic
                    message_queue.put(f"\n🔄 Visit {i+1}: Direct/referral traffic")
                    if simulate_real_visit(WEBSITE_URL, device, fingerprint):
                        successful_visits += 1
                else:
                    # Search traffic
                    search_query, _, _ = random.choice(SEARCH_TASKS)
                    message_queue.put(f"\n🔍 Visit {i+1}: Search traffic for '{search_query}'")
                    
                    # Simulate Google search and click
                    target_url = simulate_google_search(search_query, device, fingerprint)
                    if target_url and simulate_real_visit(target_url, device, fingerprint):
                        successful_visits += 1
                
                if i < NUM_VISITS - 1 and simulation_running:
                    # Random delay with human-like variation
                    delay = max(MIN_DELAY, min(MAX_DELAY, random.gammavariate(2, 0.5) * (MAX_DELAY - MIN_DELAY) / 2 + MIN_DELAY))
                    message_queue.put(f"⏳ Waiting {delay:.1f} seconds before next visit...")
                    time.sleep(delay)
            
            message_queue.put(f"\n✅ Simulation complete. {successful_visits}/{NUM_VISITS} successful visits.")
            
        except Exception as e:
            message_queue.put(f"❌ Simulation error: {str(e)}")
        finally:
            simulation_running = False
            st.session_state.simulation_complete = True
            st.rerun()

def stop_simulation():
    global simulation_running
    with simulation_lock:
        simulation_running = False
        message_queue.put("\n🛑 Simulation stopped by user")

def display_browser_view():
    """Display advanced browser simulation"""
    if ENABLE_BROWSER:
        with st.expander("🌐 Advanced Browser Simulation", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("""
                <div style="border:1px solid #ddd; border-radius:5px; padding:10px; height:500px; background-color:#f9f9f9;">
                    <div style="border-bottom:1px solid #ddd; padding-bottom:5px; margin-bottom:10px;">
                        <div style="display:inline-block; width:15px; height:15px; background-color:#ff5f56; border-radius:50%; margin-right:5px;"></div>
                        <div style="display:inline-block; width:15px; height:15px; background-color:#ffbd2e; border-radius:50%; margin-right:5px;"></div>
                        <div style="display:inline-block; width:15px; height:15px; background-color:#27c93f; border-radius:50%; margin-right:10px;"></div>
                        <span style="color:#666;">Anti-Detect Browser Simulation</span>
                    </div>
                    <div style="padding:10px; height:90%; overflow:auto; background-color:white;">
                        {content}
                    </div>
                </div>
                """.format(content=st.session_state.get('browser_content', 'Waiting for simulation to start...')), 
                unsafe_allow_html=True)
            
            with col2:
                if st.session_state.get('current_device'):
                    device = st.session_state.current_device
                    st.metric("📱 Device", f"{device['model']['name']} ({device['platform']})")
                    st.metric("🖥️ Resolution", device['resolution'])
                
                if st.session_state.get('current_fingerprint'):
                    fp = st.session_state.current_fingerprint
                    st.metric("🌍 Location", f"{fp['ip_info'].get('city', 'Unknown')}, {fp['ip_info'].get('country', 'Unknown')}" if fp.get('ip_info') else "Unknown")
                    st.metric("🛡️ Protection", "DNT: " + ("On" if fp['privacy']['doNotTrack'] else "Off"))
    else:
        st.info("Browser simulation is disabled in this mode")

def main():
    st.set_page_config(page_title="Advanced Anti-Detect Simulator", layout="wide")
    st.title("🕵️‍♂️ Advanced Anti-Detect Traffic Simulator")
    
    # Initialize session state
    if 'simulation_running' not in st.session_state:
        st.session_state.simulation_running = False
        st.session_state.simulation_complete = False
        st.session_state.log_content = ""
        st.session_state.browser_content = "Waiting for simulation to start..."
        st.session_state.current_device = None
        st.session_state.current_fingerprint = None
        st.session_state.lock = threading.Lock()
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.session_state.num_visits = st.number_input("Number of Visits", min_value=1, max_value=100, value=NUM_VISITS)
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.min_delay = st.number_input("Min Delay (s)", min_value=1, max_value=60, value=MIN_DELAY)
        with col2:
            st.session_state.max_delay = st.number_input("Max Delay (s)", min_value=1, max_value=60, value=MAX_DELAY)
        
        st.header("🎮 Simulation Control")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶ Start Simulation", 
                        disabled=st.session_state.simulation_running,
                        help="Start the anti-detect traffic simulation",
                        type="primary"):
                with st.session_state.lock:
                    st.session_state.simulation_complete = False
                    st.session_state.simulation_running = True
                    threading.Thread(target=run_simulation).start()
        with col2:
            st.button("⏹ Stop Simulation", 
                     on_click=stop_simulation,
                     disabled=not st.session_state.simulation_running)
        
        st.header("🔒 Privacy Settings")
        st.checkbox("Rotate Fingerprints", 
                   value=True, 
                   key='rotate_fingerprints',
                   help="Generate new fingerprint for each visit")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Browser Simulation", "Fingerprint Details", "Simulation Logs"])
    
    with tab1:
        display_browser_view()
        
        if st.session_state.simulation_running:
            st.info("🔃 Simulation in progress...")
            progress_bar = st.progress(0)
        else:
            progress_bar = st.progress(0)
        
        if st.session_state.simulation_complete:
            st.success("✅ Simulation completed successfully!")
    
    with tab2:
        st.header("🆔 Current Fingerprint Details")
        if st.session_state.get('current_fingerprint'):
            fp = st.session_state.current_fingerprint
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Basic Info")
                st.json({
                    "Platform": fp["platform"],
                    "Device Model": st.session_state.current_device["model"]["name"],
                    "Resolution": st.session_state.current_device["resolution"],
                    "Language": fp["language"],
                    "Timezone": fp["timezone"]
                })
                
                st.subheader("🌐 Network")
                st.json({
                    "IP": fp["ip_info"]["query"] if fp.get("ip_info") else "Unknown",
                    "Location": f"{fp['ip_info'].get('city', 'Unknown')}, {fp['ip_info'].get('country', 'Unknown')}" if fp.get("ip_info") else "Unknown",
                    "ISP": fp["ip_info"].get("isp", "Unknown") if fp.get("ip_info") else "Unknown",
                    "Connection Type": fp["network"]["connection"],
                    "Effective Type": fp["network"]["effectiveType"],
                    "RTT": f"{fp['network']['rtt']}ms"
                })
            
            with col2:
                st.subheader("💻 Hardware")
                st.json({
                    "CPU Cores": fp["hardware"]["concurrency"],
                    "Device Memory": f"{fp['hardware']['deviceMemory']}GB",
                    "System Memory": f"{fp['hardware']['memory']}GB",
                    "WebGL Vendor": fp["webgl"]["vendor"],
                    "WebGL Renderer": fp["webgl"]["renderer"]
                })
                
                st.subheader("🔒 Privacy")
                st.json({
                    "Do Not Track": fp["privacy"]["doNotTrack"],
                    "WebDriver": fp["privacy"]["webdriver"],
                    "Chrome Extensions": fp["privacy"]["chromeExtensions"],
                    "Ad Blocker": fp["privacy"]["adBlock"]
                })
        else:
            st.info("No fingerprint data available. Start the simulation to generate fingerprints.")
    
    with tab3:
        st.header("📝 Simulation Logs")
        log_placeholder = st.empty()
        log_placeholder.code(st.session_state.log_content[-10000:])
    
    # Update UI
    while True:
        if not simulation_running and st.session_state.simulation_complete:
            st.session_state.simulation_running = False
            st.rerun()
            break
        
        # Update log
        new_messages = []
        while not message_queue.empty():
            new_messages.append(message_queue.get())
        
        if new_messages:
            st.session_state.log_content += "\n".join(new_messages) + "\n"
            log_placeholder.code(st.session_state.log_content[-10000:])
        
        # Update progress
        if st.session_state.simulation_running and st.session_state.get('num_visits', NUM_VISITS) > 0:
            progress = min(1.0, len(st.session_state.log_content.split("\n")) / (st.session_state.num_visits * 10))
            progress_bar.progress(progress)
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()