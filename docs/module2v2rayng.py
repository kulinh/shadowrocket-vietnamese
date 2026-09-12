#!/usr/bin/env python3
"""Sinh docs/v2rayng_rulesets_CN.json từ sr_proxy_list_CN.module.

Giữ hai file luôn đồng bộ: mọi DOMAIN-SUFFIX / DOMAIN / DOMAIN-KEYWORD / IP-CIDR
trong module được chuyển sang cú pháp routing của Xray (domain:/full:/keyword:
và CIDR), bọc trong bộ ruleset cố định của v2rayNG 2.2.x (chặn quảng cáo,
bypass LAN, proxy, direct CN, FINAL direct).

    python3 docs/module2v2rayng.py            # ghi đè docs/v2rayng_rulesets_CN.json
    python3 docs/module2v2rayng.py --check    # chỉ báo lệch, exit 1 nếu JSON cũ

Thứ tự trong JSON = thứ tự xuất hiện trong module (không sort), để diff dễ đọc.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(HERE, "..", "sr_proxy_list_CN.module")
OUT = os.path.join(HERE, "v2rayng_rulesets_CN.json")


def parse(path):
    domains, ips = [], []
    seen_d, seen_ip = set(), set()
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("["):
            continue
        parts = [p.strip() for p in line.split(",")]
        kind, value = parts[0], parts[1] if len(parts) > 1 else ""
        if kind == "DOMAIN-SUFFIX":
            entry = "domain:" + value
        elif kind == "DOMAIN":
            entry = "full:" + value
        elif kind == "DOMAIN-KEYWORD":
            entry = "keyword:" + value
        elif kind in ("IP-CIDR", "IP-CIDR6"):
            if value not in seen_ip:
                seen_ip.add(value)
                ips.append(value)
            continue
        else:
            continue  # USER-AGENT, URL-REGEX… không có tương đương trong routing v2rayNG
        if entry not in seen_d:
            seen_d.add(entry)
            domains.append(entry)
    return domains, ips


def build(domains, ips):
    return [
        {"remarks": "Chan quang cao", "outboundTag": "block", "domain": ["geosite:category-ads-all"]},
        {"remarks": "Bypass LAN (IP)", "outboundTag": "direct", "ip": ["geoip:private"]},
        {"remarks": "Bypass LAN (domain)", "outboundTag": "direct", "domain": ["geosite:private"]},
        {"remarks": "Proxy - domain list", "outboundTag": "proxy", "domain": domains},
        {"remarks": "Proxy - IP ranges", "outboundTag": "proxy", "ip": ips},
        {"remarks": "Direct - China domain", "outboundTag": "direct", "domain": ["geosite:cn"]},
        {"remarks": "Direct - China IP", "outboundTag": "direct", "ip": ["geoip:cn"]},
        {"remarks": "FINAL - phan con lai di thang", "outboundTag": "direct", "port": "0-65535"},
    ]


def main():
    domains, ips = parse(MODULE)
    text = json.dumps(build(domains, ips), indent=2, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current == text:
            print(f"OK: {OUT} khớp module ({len(domains)} domain, {len(ips)} IP)")
            return 0
        print(f"LỆCH: chạy lại không có --check để cập nhật {OUT}")
        return 1
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"đã ghi {OUT}: {len(domains)} domain, {len(ips)} IP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
