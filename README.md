# 🚀 Shadowrocket Vietnamese Rules

> Bộ quy tắc (module) **Shadowrocket** tối ưu cho người Việt: vượt tường lửa khi ở **Trung Quốc (GFW)** hoặc **UAE**, vẫn giữ các app trong nước (Zalo, ZaloPay, ngân hàng…) chạy thẳng — không vòng qua proxy.

<p align="center">
  <a href="https://github.com/kulinh/shadowrocket-vietnamese/stargazers">
    <img src="https://img.shields.io/github/stars/kulinh/shadowrocket-vietnamese?label=Stars&style=social">
  </a>
  <a href="https://github.com/kulinh/shadowrocket-vietnamese/network/members">
    <img src="https://img.shields.io/github/forks/kulinh/shadowrocket-vietnamese?label=Fork&style=social">
  </a>
</p>

---

## 📖 Giới thiệu

Đây là bản fork & tùy biến tiếng Việt của [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules), bổ sung các **module chuyên biệt cho người Việt sống/đi công tác ở nước ngoài**:

- **Ở Trung Quốc:** vượt GFW để vào Google, Meta (Facebook/Instagram/WhatsApp/Threads/Messenger), Telegram, Viber, TikTok, YouTube, X/Twitter, AI (ChatGPT/Claude/Gemini)… mà **không làm chậm** các trang nội địa TQ.
- **Ở UAE:** mở khóa cuộc gọi VoIP (WhatsApp, FaceTime, Skype, Viber, Telegram) và các dịch vụ bị TDRA chặn.
- **Mọi nơi:** module **Zalo & ZaloPay** gom đủ domain + toàn bộ dải IP của VNG (AS38244), cho phép route trọn traffic Zalo/ZaloPay qua proxy (chat, gọi, gửi ảnh/video/file, thanh toán).
- **Chặn quảng cáo / tracker** bằng danh sách REJECT khổng lồ.

Repo dùng dạng **module rule** thay vì file config đầy đủ — gọn gàng, dễ bật/tắt, dễ chỉnh sửa, và không động đến phần chứng chỉ / cài đặt riêng của từng người.

---

## 🧩 Các module trong repo

| Module | Mục đích | Loại |
|--------|----------|------|
| [`sr_proxy_list_CN.module`](sr_proxy_list_CN.module) | **Vượt GFW ở Trung Quốc.** Bao phủ toàn diện Google/Alphabet, Meta, Telegram, Viber, TikTok, X, AI, Dev, Media + IP-CIDR cho dịch vụ hay bị nhiễm DNS | PROXY (blacklist) |
| [`sr_proxy_list_UAE.module`](sr_proxy_list_UAE.module) | **Vượt firewall TDRA ở UAE.** Mở VoIP, nội dung bị chặn & dịch vụ thiết yếu | PROXY (blacklist) |
| [`zalo_zalopay.module`](zalo_zalopay.module) | Route **toàn bộ** traffic Zalo/ZaloPay qua proxy: đầy đủ domain (chat/API/media/thanh toán) **+ toàn bộ dải IP VNG (AS38244)** đã gộp tối thiểu | PROXY |
| [`sr_direct_list.module`](sr_direct_list.module) | ~115.000 domain nội địa TQ → đi thẳng (dùng cho **whitelist mode**) | DIRECT |
| [`sr_reject_list.module`](sr_reject_list.module) | ~175.000 domain quảng cáo / tracker → chặn | REJECT |

> `sr_direct_list` và `sr_reject_list` được **đồng bộ thủ công** từ upstream [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules) (repo này không chạy CI tự build). Ba module `CN`, `UAE`, `zalo_zalopay` là **tùy biến riêng** của repo.

---

## ⚙️ Nguyên tắc hoạt động (đọc kỹ phần này!)

Shadowrocket xử lý theo thứ tự ưu tiên:

1. **Quy tắc trong module > quy tắc trong config.**
2. **Module ở TRÊN ưu tiên hơn module ở DƯỚI** (kéo–thả để sắp xếp).
3. Dòng **`FINAL`** trong config quyết định những gì *không khớp* rule nào sẽ đi đâu.

Có 2 chế độ:

| | **Blacklist mode** (khuyên dùng) | **Whitelist mode** |
|---|---|---|
| Ý tưởng | Chỉ những site trong list mới qua proxy, còn lại đi thẳng | Mặc định qua proxy, chỉ site nội địa đi thẳng |
| Module nạp | `sr_proxy_list_CN` (+ `zalo_zalopay`, `sr_reject_list`) | `sr_direct_list` + `sr_reject_list` |
| Dòng FINAL | `FINAL,DIRECT` | `GEOIP,cn,DIRECT` rồi `FINAL,PROXY` |
| Hợp với | Phần lớn người Việt (giữ tốc độ trang TQ/VN) | Ai muốn "mọi thứ qua proxy trừ TQ" |

> ⚠️ **Lỗi thường gặp:** bật proxy toàn cục thì vào được mọi site, nhưng bật theo Config/rule lại không vào được. Nguyên nhân gần như luôn là **`FINAL` sai** (phải là `FINAL,DIRECT` ở blacklist mode) hoặc **thiếu domain phụ trợ** khiến một request con bị đẩy đi thẳng và bị chặn. Module `sr_proxy_list_CN` đã được mở rộng để khắc phục điều này.

---

## 🛠️ Cài đặt

### Bước 1 — Tạo config tối giản
Trong Shadowrocket: **Cấu hình → Tệp từ xa**, dán link config mẫu (~20 dòng) rồi thêm máy chủ proxy của bạn:

```
https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/docs/03.shadowsocks_tiny.conf
```

Đảm bảo phần `[Rule]` kết thúc bằng `FINAL,DIRECT` (cho blacklist mode).

### Bước 2 — Thêm module
**Cấu hình → Mô-đun → góc trên phải (+)**, thêm các link bên dưới theo nhu cầu, rồi sắp xếp thứ tự (reject ở trên cùng):

**Khi ở Trung Quốc 🇨🇳**
```
https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/sr_reject_list.module
https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/sr_proxy_list_CN.module
https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/zalo_zalopay.module
```

**Khi ở UAE 🇦🇪**
```
https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/sr_reject_list.module
https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/sr_proxy_list_UAE.module
```

### Bước 3 — Xong!
Bật cấu hình, lưu lượng sẽ được phân luồng chính xác. Khi có cập nhật, chỉ cần bấm **làm mới module** trong Shadowrocket là đủ (link raw không đổi).

---

## 🔗 Link tải module

Mỗi module có 2 link: `raw.githubusercontent.com` (nhanh, đôi khi cần proxy để tải) và `jsdelivr` (truy cập thẳng, có thể trễ vài giờ so với bản mới nhất — không ảnh hưởng đáng kể).

| Module | raw.githubusercontent | jsDelivr (mirror) |
|--------|-----------------------|-------------------|
| Proxy CN | [link](https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/sr_proxy_list_CN.module) | [link](https://cdn.jsdelivr.net/gh/kulinh/shadowrocket-vietnamese@master/sr_proxy_list_CN.module) |
| Proxy UAE | [link](https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/sr_proxy_list_UAE.module) | [link](https://cdn.jsdelivr.net/gh/kulinh/shadowrocket-vietnamese@master/sr_proxy_list_UAE.module) |
| Zalo & ZaloPay | [link](https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/zalo_zalopay.module) | [link](https://cdn.jsdelivr.net/gh/kulinh/shadowrocket-vietnamese@master/zalo_zalopay.module) |
| Direct (TQ) | [link](https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/sr_direct_list.module) | [link](https://cdn.jsdelivr.net/gh/kulinh/shadowrocket-vietnamese@master/sr_direct_list.module) |
| Reject (ads) | [link](https://raw.githubusercontent.com/kulinh/shadowrocket-vietnamese/master/sr_reject_list.module) | [link](https://cdn.jsdelivr.net/gh/kulinh/shadowrocket-vietnamese@master/sr_reject_list.module) |

---

## 📁 Cấu trúc repo

```
shadowrocket-vietnamese/
├── sr_proxy_list_CN.module     # PROXY - vượt GFW khi ở Trung Quốc
├── sr_proxy_list_UAE.module    # PROXY - mở OTT VoIP/video khi ở UAE
├── zalo_zalopay.module         # PROXY - full traffic Zalo/ZaloPay + dải IP VNG
├── sr_direct_list.module       # DIRECT - domain nội địa TQ (sync upstream)
├── sr_reject_list.module       # REJECT - quảng cáo/tracker (sync upstream)
├── docs/                       # Tài liệu tham khảo (xem bên dưới)
├── README.md
└── LICENSE
```

### 📚 Tài liệu tham khảo (`docs/`)
- [`01.shadowrocket_configure.md`](docs/01.shadowrocket_configure.md) — giới thiệu chi tiết file cấu hình Shadowrocket.
- [`02.shadowrocket_update_modules.md`](docs/02.shadowrocket_update_modules.md) — cách cập nhật module thủ công/tự động.
- [`03.shadowsocks_tiny.conf`](docs/03.shadowsocks_tiny.conf) — file config mẫu tối giản (~20 dòng) để bắt đầu.

### 🤖 Dùng cho v2rayNG (Android)
File `.module` **không** dùng trực tiếp trên v2rayNG (khác nhân/định dạng). Em đã chuyển sẵn rule proxy sang định dạng routing Xray — dán khối `"routing"` vào `config.json` của v2rayNG (cần đủ outbound tag `proxy`/`direct`/`block`):
- [`docs/v2rayng_routing_CN.json`](docs/v2rayng_routing_CN.json) — kịch bản **Trung Quốc** (kèm `geosite:cn`/`geoip:cn` đi thẳng).
- [`docs/v2rayng_routing_UAE.json`](docs/v2rayng_routing_UAE.json) — kịch bản **UAE** (mở OTT VoIP/video).

> Cả hai đã tích hợp chặn quảng cáo qua `geosite:category-ads-all` và mô phỏng `FINAL,DIRECT` bằng rule catch-all → thay luôn cho các file `.module` tương ứng trên Android.

---

## ❓ Câu hỏi thường gặp

**Bật Shadowrocket xong, app ngân hàng / app nội địa TQ báo lỗi không chạy?**
> Vào **Cài đặt → Proxy**, đổi loại proxy từ `HTTP` sang `none` (tức chế độ **TUN**).

**Hàng nghìn dòng rule có làm chậm máy không?**
> Không. Trong Shadowrocket, 50 dòng hay 50.000 dòng đều cùng độ phức tạp ~O(1).

**Nên chọn blacklist hay whitelist?**
> Đa số người Việt nên dùng **blacklist** (`sr_proxy_list_CN` + `FINAL,DIRECT`): chỉ những gì bị chặn mới qua proxy, các trang TQ/VN giữ nguyên tốc độ. Whitelist hợp với ai muốn "mọi thứ qua proxy trừ Trung Quốc".

**Muốn ghi đè một quy tắc riêng của mình?**
> Tạo một module nhỏ chứa rule của bạn rồi kéo lên **trên cùng** — nó sẽ được khớp trước tiên.

**Chặn quảng cáo có sạch 100% không?**
> Không đảm bảo tuyệt đối, nhất là quảng cáo video (YouTube/Youku) vì chúng đổi chiến lược liên tục, khó chặn chỉ bằng so khớp URL.

---

## 🙏 Nguồn & Giấy phép

- Dựa trên [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules) — danh sách DIRECT/REJECT được tổng hợp từ `dnsmasq-china-list`, `domain-list-community`, `gfwlist`, `cn-blocked-domain`, EasyList, AdGuard, pgl.yoyo.org…
- Các module `CN`, `UAE`, `zalo_zalopay` do repo này tùy biến thêm.
- Giấy phép: xem [LICENSE](LICENSE).

> 💡 Repo này phục vụ nhu cầu cá nhân hợp pháp (truy cập dịch vụ bị giới hạn địa lý khi ra nước ngoài). Hãy tuân thủ pháp luật nơi bạn đang ở.
