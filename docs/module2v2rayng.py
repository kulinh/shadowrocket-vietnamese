#!/usr/bin/env python3
"""Sinh docs/v2rayng_rulesets_CN.json và sr_proxy_list_CN.list từ sr_proxy_list_CN.module.

Giữ hai file luôn đồng bộ: mọi DOMAIN-SUFFIX / DOMAIN / DOMAIN-KEYWORD / IP-CIDR
trong module được chuyển sang cú pháp routing của Xray (domain:/full:/keyword:
và CIDR), bọc trong bộ ruleset cố định của v2rayNG 2.2.x (chặn quảng cáo,
bypass LAN, proxy, direct CN, FINAL direct).

    python3 docs/module2v2rayng.py            # ghi đè JSON + sr_proxy_list_CN.list
    python3 docs/module2v2rayng.py --check    # chỉ báo lệch, exit 1 nếu file cũ

sr_proxy_list_CN.list là bản RULE-SET (mỗi dòng TYPE,value, không policy) cho
Shadowrocket/Surge/Loon; config RWL8899.conf của cf-vpn dùng nó làm fallback
khi Worker không tải được module để nhúng thẳng vào [Rule].

Thứ tự trong JSON = thứ tự xuất hiện trong module (không sort), để diff dễ đọc.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(HERE, "..", "sr_proxy_list_CN.module")
OUT = os.path.join(HERE, "v2rayng_rulesets_CN.json")
OUT_LIST = os.path.join(HERE, "..", "sr_proxy_list_CN.list")

RULE_TYPES = ("DOMAIN-SUFFIX", "DOMAIN", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6",
              "USER-AGENT", "URL-REGEX", "GEOIP", "IP-ASN")


def build_list(path):
    """Các dòng rule của module, bỏ policy, giữ cờ no-resolve (định dạng RULE-SET)."""
    out, seen = [], set()
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("["):
            continue
        parts = [p.strip() for p in line.split(",")]
        if parts[0] not in RULE_TYPES or len(parts) < 2:
            continue
        flags = [f for f in parts[3:] if f.lower() == "no-resolve"]
        entry = ",".join([parts[0], parts[1]] + flags)
        if entry not in seen:
            seen.add(entry)
            out.append(entry)
    header = ("# sr_proxy_list_CN.list — sinh tự động từ sr_proxy_list_CN.module (không sửa tay).\n"
              "# Dùng làm RULE-SET: RULE-SET,https://raw.githubusercontent.com/kulinh/"
              "shadowrocket-vietnamese/master/sr_proxy_list_CN.list,PROXY\n")
    return header + "\n".join(out) + "\n"


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
    lst = build_list(MODULE)
    outputs = [(OUT, text, f"{len(domains)} domain, {len(ips)} IP"),
               (OUT_LIST, lst, f"{lst.count(chr(10)) - 2} rule")]
    if "--check" in sys.argv:
        rc = 0
        for path, want, desc in outputs:
            current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
            if current == want:
                print(f"OK: {os.path.relpath(path)} khớp module ({desc})")
            else:
                print(f"LỆCH: {os.path.relpath(path)} — chạy lại không có --check để cập nhật")
                rc = 1
        return rc
    for path, want, desc in outputs:
        with open(path, "w", encoding="utf-8") as f:
            f.write(want)
        print(f"đã ghi {os.path.relpath(path)}: {desc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
