# MSIX packaging plan cho bản Windows (bước NGOÀI Godot)

**Trạng thái: PROVISIONAL / plan-level.** Không tạo manifest thật, không chạy MakeAppx, không ký, không
đụng Windows SDK trong tài liệu này.

Vì sao cần tài liệu riêng: Godot **không có** đích export MSIX/APPX (grep `msix|appx` = 0 hit trên
`platform/windows/export/export_plugin.cpp` và `editor/export/editor_export_platform_pc.cpp` @
`4.7.2-stable`). Godot chỉ cho ra `.exe` (+ `.pck` nếu không embed). MS Store cần **MSIX**, nên phải có
một bước đóng gói riêng — tài liệu này chốt bước đó.

## 0. Nguồn pin

`MicrosoftDocs/msix-docs` @ commit **`e07277dfaac354d9b6e7ad86a8d3a53cfb867657`** (2026-10-12), 4 trang
đã tải và băm (xem `reverse-engineering/raw/godot-build-spec/msix-docs.json`). Trích dẫn dưới đây là
`file:dòng` trong 4 trang đó — `STATIC_CONFIRMED` ở mức *tài liệu chính chủ*, không phải tôi đóng gói thử.

## 1. Chuỗi 6 bước

| Bước | Việc | Ai làm | Kết quả kiểm được |
|---|---|---|---|
| M1 | Godot export Windows preset (`binary_format/architecture=x86_64`, `binary_format/embed_pck=true`) | CI/coder | `.exe` + log, sha256 |
| M2 | Gom thư mục package: `.exe` ở root + asset rời (nếu có) + `Assets/` icon | coder | danh sách file + tổng byte |
| M3 | Viết `AppxManifest.xml` theo §2 | coder | file + validate bằng MakeAppx (bước M5 fail nếu sai) |
| M4 | (chỉ khi đổi icon/asset) `makepri createconfig` + `makepri new` để sinh `resources.pri` | coder | `resources.pri` + log |
| M5 | `MakeAppx.exe pack /d <dir> /p <out>.msix` (hoặc `/bv` nếu bundle) | coder | `.msix`, byte, sha256 |
| M6 | Ký: dev = self-signed; store = submit, Partner Center ký bản phân phối | coder (dev) / **USER** (store) | cert SHA-256 trong báo cáo; store listing id |

`MakeAppx.exe` nằm trong Windows SDK; `makepri` trong Windows Kits (`desktop-to-uwp-manual-conversion.md:205`
và mục MakePri cùng trang).

## 2. Manifest — phần tử và thuộc tính bắt buộc (đọc từ tài liệu, không chế)

Khung tối thiểu cho **desktop app đóng gói** (`desktop-to-uwp-manual-conversion.md:27-58`):

```xml
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:uap10="http://schemas.microsoft.com/appx/manifest/uap/windows10/10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities">
  <Identity Name="" Version="" Publisher="" ProcessorArchitecture="" />
  <Properties>
    <DisplayName></DisplayName><PublisherDisplayName></PublisherDisplayName>
    <Description></Description><Logo></Logo>
  </Properties>
  <Resources><Resource Language="" /></Resources>
  <Dependencies><TargetDeviceFamily Name="Windows.Desktop" MinVersion="" MaxVersionTested="" /></Dependencies>
  <Capabilities><rescap:Capability Name="runFullTrust"/></Capabilities>
  <Applications>
    <Application Id="" Executable="" uap10:RuntimeBehavior="packagedClassicApp" uap10:TrustLevel="mediumIL">
      <uap:VisualElements DisplayName="" Description="" Square150x150Logo="" Square44x44Logo="" BackgroundColor="" />
    </Application>
  </Applications>
</Package>
```

Ràng buộc đã đọc:

| Điểm | Giá trị | Nguồn |
|---|---|---|
| `Identity@Version` | dạng **4 thành phần** `1.0.0.0` | `desktop-to-uwp-manual-conversion.md:74` |
| `Identity@ProcessorArchitecture` | chỉ `x64`, `x86`, `arm`, `arm64`, `neutral` | cùng trang, dòng 70 |
| `Identity@Name` + `@Publisher` | nếu đã reserve tên trên Store → lấy từ Partner Center; nếu sideload → tự đặt nhưng **Publisher phải khớp chứng chỉ ký** | cùng trang, dòng 78–80 |
| `Properties` | **3 phần tử con bắt buộc** (DisplayName, PublisherDisplayName, Logo) | cùng trang, §Properties |
| `TargetDeviceFamily@Name` | luôn `Windows.Desktop` với desktop app đóng gói | cùng trang, §Dependencies |
| `Application` | `uap10:RuntimeBehavior="packagedClassicApp"` + `uap10:TrustLevel="mediumIL"`; máy < Win10 2004 thì dùng `EntryPoint` thay thế | cùng trang, dòng 130–138 + note |
| `Capabilities` | full-trust app phải khai `rescap:Capability Name="runFullTrust"` | cùng trang, dòng 114–118 |
| `makepri` | khi đổi icon/asset: `createconfig /cf priconfig.xml /dq en-US` rồi `new /pr <dir> /cf <dir>\priconfig.xml` | cùng trang, §MakePri |
| Ký | **bắt buộc** để deploy; cert phải chain tới trusted root; bundle chỉ cần ký **bundle**, không ký từng gói con | `signing-package-overview.md:11,13,15` |
| Gói không ký | chỉ Win11, phải có OID trong `Publisher`, cài `Add-AppxPackage -AllowUnsigned`, **không dùng để phân phối** | `unsigned-package.md:7,22,32` |
| Đổi chứng chỉ | Win11 21H2+: cần artifact `Publisher` bridging (`Old`/`New`) để giữ identity | `persistent-identity.md:9-30` |

## 3. Ánh xạ giá trị cụ thể cho WindWings (điền sau khi user chốt)

| Trường | Nguồn giá trị | Trạng thái |
|---|---|---|
| `Identity@Name` | tên reserve trên Partner Center (nếu đi store) | `UNKNOWN` — USER |
| `Identity@Publisher` | `CN=...` khớp cert hoặc Partner Center | `UNKNOWN` — USER |
| `Identity@Version` | `version.json` → 4 thành phần, **thành phần 4 = 0** | `INFERRED` |
| `Identity@ProcessorArchitecture` | `x64` (khớp preset `x86_64`) | `STATIC_CONFIRMED` (mapping) |
| `Properties/DisplayName` | tên game mới | USER |
| `Properties/PublisherDisplayName` | pháp nhân user | USER |
| `Properties/Logo`, `Square150x150Logo`, `Square44x44Logo` | icon 150×150 và 44×44 do session art cấp | chờ Gate-5 |
| `Application@Executable` | tên `.exe` Godot xuất (không đổi sau khi build) | coder |
| `TargetDeviceFamily@MinVersion` | `10.0.17763.0` hay mức khác | `UNKNOWN` — chọn theo thiết bị mục tiêu, ghi lý do |
| `Resources/Resource@Language` | `en-us` + `vi-vn` (2 ngôn ngữ launch) | `INFERRED` |

## 4. Cổng kiểm cho bước MSIX (đưa vào V-checks)

- **M-A**: manifest parse được bằng `MakeAppx pack` — fail là fail cứng.
- **M-B**: `Identity@Version` = `version.json` chuẩn hoá 4 thành phần; **không** trùng version đã submit trước.
- **M-C**: `Identity@Publisher` khớp `CN` của cert dùng để ký (dev) hoặc giá trị Partner Center cấp (store).
- **M-D**: `.msix` có `resources.pri` nếu icon/asset đổi; nếu không có thì phải chứng minh asset không đổi.
- **M-E**: `.msix` mở được bằng `Add-AppxPackage -Register` (dev, không cần admin nếu unsigned path dùng đúng OID) **hoặc** cài được bằng cert tin cậy trên máy sạch.
- **M-F**: kích thước `.msix` ghi vào báo cáo; ngưỡng MS Store hiện hành là `UNKNOWN` (không chép số).

## 5. Cái không làm ở đây

- Không tạo cert, không mua cert, không đăng ký Partner Center — USER.
- Không hứa “store sẽ nhận”: định dạng nhận của MS Store (MSIX vs EXE/PWA) là quyết định sản phẩm, xem
  `GODOT_BUILD_PACKAGING_SPEC.md` §4 và U3.
- Không suy ra hiệu năng/khởi động từ việc đóng gói thành công.
