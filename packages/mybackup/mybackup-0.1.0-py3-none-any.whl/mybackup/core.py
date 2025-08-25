import socket
import requests
import ssl
import time
import urllib3
import subprocess

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COMMON_PORTS = [80, 443, 8080, 8443, 21, 22]

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception as e:
        return f"Error: {e}"

def get_reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception as e:
        return f"Error: {e}"

def get_geoip(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=6)
        return r.json()
    except Exception as e:
        return {"GeoIP error": str(e)}

def get_asn(ip):
    try:
        r = requests.get(f"https://api.hackertarget.com/aslookup/?q={ip}", timeout=6)
        return r.text
    except Exception as e:
        return f"ASN error: {e}"

def get_dns_ns(domain):
    # Use 'nslookup -type=ns domain' in subprocess for portability
    try:
        output = subprocess.check_output(["nslookup", "-type=ns", domain], universal_newlines=True, timeout=5)
        ns_records = []
        for line in output.splitlines():
            if 'nameserver =' in line:
                ns_records.append(line.split('=')[1].strip())
        return ns_records if ns_records else "No NS records found"
    except Exception as e:
        return f"DNS NS lookup failed: {e}"

def get_http_info(domain):
    info = {}
    urls = [f"http://{domain}", f"https://{domain}"]
    for url in urls:
        proto = 'HTTPS' if url.startswith("https") else 'HTTP'
        try:
            start = time.time()
            r = requests.get(url, timeout=8, allow_redirects=True, verify=False)
            duration = round(time.time() - start, 3)
            info[f"{proto} Status Code"] = r.status_code
            info[f"{proto} Headers"] = dict(r.headers)
            info[f"{proto} Response Time (s)"] = duration
            info[f"{proto} Response Size (bytes)"] = len(r.content)
            if "<title>" in r.text and "</title>" in r.text:
                title = r.text.split("<title>")[1].split("</title>")[0].strip()
            else:
                title = "N/A"
            info[f"{proto} Page Title"] = title
        except Exception as e:
            info[f"{proto} Error"] = str(e)
    return info

def get_https_cert(domain):
    cert_info = {}
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(4)
            s.connect((domain, 443))
            cert = s.getpeercert()
            if cert:
                cert_info['Subject'] = dict(x[0] for x in cert.get('subject', []))
                cert_info['Issuer'] = dict(x[0] for x in cert.get('issuer', []))
                cert_info['Valid From'] = cert.get('notBefore', '')
                cert_info['Valid Until'] = cert.get('notAfter', '')
            else:
                cert_info['SSL Certificate'] = "No certificate found"
    except Exception as e:
        cert_info['SSL Error'] = str(e)
    return cert_info

def get_whois(domain):
    try:
        import whois
    except ImportError:
        return "python-whois library not installed. Install with `pip install python-whois`"
    try:
        w = whois.whois(domain)
        return w.text if hasattr(w, "text") else str(w)
    except Exception as e:
        return f"Whois error: {e}"

def check_robots_txt(domain):
    try:
        r = requests.get(f"http://{domain}/robots.txt", timeout=5)
        if r.status_code == 200:
            return "Exists"
        else:
            return f"Status code: {r.status_code}"
    except Exception as e:
        return f"Error checking robots.txt: {e}"

def scan_common_ports(ip):
    open_ports = []
    for port in COMMON_PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
        except Exception:
            pass
        finally:
            sock.close()
    return open_ports if open_ports else "No common ports open"

def site_info(target):
    results = {}
    ip = get_ip(target)
    results['IP Address'] = ip
    results['Reverse DNS'] = get_reverse_dns(ip) if "Error" not in ip else "N/A"
    results['GeoIP'] = get_geoip(ip) if "Error" not in ip else "N/A"
    results['ASN Info'] = get_asn(ip) if "Error" not in ip else "N/A"
    results['DNS NS Records'] = get_dns_ns(target)
    results['Website Info'] = get_http_info(target)
    results['SSL Certificate'] = get_https_cert(target)
    results['Robots.txt'] = check_robots_txt(target)
    results['Open Common Ports'] = scan_common_ports(ip) if "Error" not in ip else "N/A"
    results['Whois'] = get_whois(target)
    return results

def create_backup(domain):
    try:
        r = requests.get("http://" + domain, timeout=10)
        fname = f"{domain.replace('.', '_')}_backup.html"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(r.text)
        return f"Backup created: {fname}"
    except Exception as e:
        return f"Failed to backup: {e}"

def list_backups():
    import glob
    return glob.glob("*_backup.html")

def delete_backup(fname):
    import os
    try:
        os.remove(fname)
        return f"Deleted: {fname}"
    except Exception as e:
        return f"Delete failed: {e}"
