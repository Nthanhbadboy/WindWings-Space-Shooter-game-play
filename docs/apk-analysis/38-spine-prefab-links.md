# 38 — Enemy/boss Spine PPtr joins (PROVISIONAL)

SkeletonAnimation → local SkeletonDataAsset → local TextAsset, không đoán theo tên/bone.

```json
{
  "components": 3,
  "prefabs": 3,
  "statuses": {
    "resolved": 3
  }
}
```

| Prefab | Component | SDA | JSON TextAsset | Initial animation | Scale | Mix |
|---|---:|---:|---:|---|---:|---:|
| Boss-39003 | 602881 | 580613 | 895 |  | 0.009999999776482582 | 0.20000000298023224 |
| Boss-39001 | 602882 | 580611 | 918 |  | 0.009999999776482582 | 0.20000000298023224 |
| Boss-39002 | 664302 | 580611 | 918 |  | 0.009999999776482582 | 0.20000000298023224 |

Nguồn raw giữ danh sách animation, thời lượng, explicit mix và PPtr.
Không coi không tìm thấy SkeletonAnimation là không dùng Spine (có thể renderer/subclass khác).
component_loop chỉ là giá trị serialize ban đầu; script có thể đổi state/loop lúc chạy.
TextAsset path_id là định danh trong tập raw hiện tại; không đồng nhất với tên file skeleton__N.
