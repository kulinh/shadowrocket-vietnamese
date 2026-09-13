#!/usr/bin/env python3
"""Sinh docs/v2rayng_rulesets_<VÙNG>.json và sr_proxy_list_<VÙNG>.list từ
sr_proxy_list_<VÙNG>.module (VÙNG = CN, UAE, RU).

Giữ các file luôn đồng bộ: mọi DOMAIN-SUFFIX / DOMAIN / DOMAIN-KEYWORD / IP-CIDR
trong module được chuyển sang cú pháp routing của Xray (domain:/full:/keyword:
và CIDR), bọc trong bộ ruleset cố định của v2rayNG 2.2.x (chặn quảng cáo,
bypass LAN, proxy, [CN: direct China], FINAL direct).

    python3 docs/module2v2rayng.py            # ghi đè JSON + .list cho mọi vùng
    python3 docs/module2v2rayng.py CN         # chỉ một vùng
    python3 docs/module2v2rayng.py --check    # chỉ báo lệch, exit 1 nếu file cũ

sr_proxy_list_<VÙNG>.list là bản RULE-SET (mỗi dòng TYPE,value, không policy)
cho Shadowrocket/Surge/Loon; config RWL8899.conf của cf-vpn dùng nó làm
fallback khi Worker không tải được module để nhúng thẳng vào [Rule].

Thứ tự trong JSON = thứ tự xuất hiện trong module (không sort), để diff dễ đọc.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
REGIONS = ("CN", "UAE", "RU")

RULE_TYPES = ("DOMAIN-SUFFIX", "DOMAIN", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6",
              "USER-AGENT", "URL-REGEX", "GEOIP", "IP-ASN")


def paths(region):
    return (os.path.join(ROOT, f"sr_proxy_list_{region}.module"),
            os.path.join(HERE, f"v2rayng_rulesets_{region}.json"),
            os.path.join(ROOT, f"sr_proxy_list_{region}.list"))


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


def build(region, domains, ips):
    rules = [
        {"remarks": "Chan quang cao", "outboundTag": "block", "domain": ["geosite:category-ads-all"]},
        {"remarks": "Bypass LAN (IP)", "outboundTag": "direct", "ip": ["geoip:private"]},
        {"remarks": "Bypass LAN (domain)", "outboundTag": "direct", "domain": ["geosite:private"]},
        {"remarks": "Proxy - domain list", "outboundTag": "proxy", "domain": domains},
        {"remarks": "Proxy - IP ranges", "outboundTag": "proxy", "ip": ips},
    ]
    if region == "CN":  # trang TQ đi thẳng để khỏi vòng qua proxy
        rules += [
            {"remarks": "Direct - China domain", "outboundTag": "direct", "domain": ["geosite:cn"]},
            {"remarks": "Direct - China IP", "outboundTag": "direct", "ip": ["geoip:cn"]},
        ]
    rules.append({"remarks": "FINAL - phan con lai di thang", "outboundTag": "direct", "port": "0-65535"})
    return rules


def build_list(region, path):
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
    header = (f"# sr_proxy_list_{region}.list — sinh tự động từ sr_proxy_list_{region}.module (không sửa tay).\n"
              f"# Dùng làm RULE-SET: RULE-SET,https://raw.githubusercontent.com/kulinh/"
              f"shadowrocket-vietnamese/master/sr_proxy_list_{region}.list,PROXY\n")
    return header + "\n".join(out) + "\n"


def main():
    check = "--check" in sys.argv
    regions = [a for a in sys.argv[1:] if a in REGIONS] or list(REGIONS)
    rc = 0
    for region in regions:
        module, out_json, out_list = paths(region)
        domains, ips = parse(module)
        text = json.dumps(build(region, domains, ips), indent=2, ensure_ascii=False) + "\n"
        lst = build_list(region, module)
        outputs = [(out_json, text, f"{len(domains)} domain, {len(ips)} IP"),
                   (out_list, lst, f"{lst.count(chr(10)) - 2} rule")]
        for path, want, desc in outputs:
            rel = os.path.relpath(path)
            if check:
                current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
                if current == want:
                    print(f"OK: {rel} khớp module ({desc})")
                else:
                    print(f"LỆCH: {rel} — chạy lại không có --check để cập nhật")
                    rc = 1
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(want)
                print(f"đã ghi {rel}: {desc}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
