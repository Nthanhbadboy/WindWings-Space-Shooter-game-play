# Enemy / boss HP (từ `Enemy_Datas` MonoBehaviour)

- số instance: **800**
- HP lớn nhất: **10,000,000** (`CB(TEST)`)

## Top 40 theo HP

| # | GameObject | StartHealthPoint |
|---:|---|---:|
| 1 | `CB(TEST)` | 10,000,000 |
| 2 | `Boss-37019/Enemy_Ingame/GunParent` | 5,000,000 |
| 3 | `Boss-37018/Enemy_Ingame/GunParent` | 5,000,000 |
| 4 | `Board_FightBoss/Parent/Tab (5)/Boss/Parent_Bosses/Boss 8/Boss 8/HP3` | 4,500,000 |
| 5 | `Boss 8/HP3` | 4,500,000 |
| 6 | `Boss-37010/Enemy_Ingame/GunParent` | 4,500,000 |
| 7 | `Boss/Boss-39012/HP (3)` | 4,500,000 |
| 8 | `Boss-37015/Enemy_Ingame/GunParent` | 4,350,000 |
| 9 | `Boss-37013/Enemy_Ingame/GunParent` | 4,300,000 |
| 10 | `Boss-37017/Enemy_Ingame/GunParent` | 4,300,000 |
| 11 | `Boss-37011` | 4,000,000 |
| 12 | `Boss-37005` | 3,900,000 |
| 13 | `Boss-37016/Enemy_Ingame/GunParent` | 3,870,000 |
| 14 | `Boss/Boss-39012/HP (2)` | 3,600,000 |
| 15 | `Board_SelectBoss/Parent/ScrollView/ObjectMove/Parent_View/Parent/Tab (19)/Boss/Boss-39015/HP (3)` | 3,500,000 |
| 16 | `Parent/Tab (8)/Boss/Boss-39011/HP (3)` | 3,500,000 |
| 17 | `Boss-39020/HP (3)` | 3,200,000 |
| 18 | `Boss-39017/HP (3)` | 3,200,000 |
| 19 | `Boss-39018/HP (3)` | 3,200,000 |
| 20 | `Boss-39021/HP (3)` | 3,200,000 |
| 21 | `Boss-39017/HP (3)` | 3,200,000 |
| 22 | `Boss-39018/HP (3)` | 3,200,000 |
| 23 | `Boss-39019/HP (3)` | 3,200,000 |
| 24 | `Boss-37014/HP (2)` | 3,100,000 |
| 25 | `Parent/Tab (8)/Boss/Boss-39011/HP (2)` | 3,100,000 |
| 26 | `Boss/Boss-37014/HP (2)` | 3,100,000 |
| 27 | `Parent/Tab (10)/Boss/Boss-39013/HP (3)` | 3,000,000 |
| 28 | `Boss/Boss-39014/HP (3)` | 3,000,000 |
| 29 | `Enemy_Ingame/Boss 7/Head/HP3` | 3,000,000 |
| 30 | `Boss-39013/HP (3)` | 3,000,000 |
| 31 | `Boss-39014/HP (3)` | 3,000,000 |
| 32 | `Boss/Boss-39015/HP (2)` | 3,000,000 |
| 33 | `Boss-39015/HP (2)` | 3,000,000 |
| 34 | `Boss/Boss-39012/HP (1)` | 3,000,000 |
| 35 | `Boss-39011/HP (2)` | 2,900,000 |
| 36 | `Board_SelectBoss/Parent/ScrollView/ObjectMove/Parent_View/Parent/Tab (15)/Boss/Boss-39017/HP (2)` | 2,800,000 |
| 37 | `Board_SelectBoss/Parent/ScrollView/ObjectMove/Parent_View/Parent/Tab (16)/Boss/Boss-39018/HP (2)` | 2,800,000 |
| 38 | `Boss-39021/HP (2)` | 2,800,000 |
| 39 | `Boss-39017/HP (2)` | 2,800,000 |
| 40 | `Boss-39018/HP (2)` | 2,800,000 |

## Top 30 prefab gốc theo HP cao nhất

| root prefab | HP max | số component HP |
|---|---:|---:|
| `CB(TEST)` | 10,000,000 | 1 |
| `Boss-37019` | 5,000,000 | 2 |
| `Boss-37018` | 5,000,000 | 1 |
| `Board_FightBoss` | 4,500,000 | 16 |
| `Boss 8` | 4,500,000 | 1 |
| `Boss-37010` | 4,500,000 | 1 |
| `Boss` | 4,500,000 | 25 |
| `Boss-37015` | 4,350,000 | 1 |
| `Boss-37013` | 4,300,000 | 2 |
| `Boss-37017` | 4,300,000 | 1 |
| `Boss-37011` | 4,000,000 | 1 |
| `Boss-37005` | 3,900,000 | 2 |
| `Boss-37016` | 3,870,000 | 3 |
| `Board_SelectBoss` | 3,500,000 | 5 |
| `Parent` | 3,500,000 | 32 |
| `Boss-39020` | 3,200,000 | 3 |
| `Boss-39017` | 3,200,000 | 17 |
| `Boss-39018` | 3,200,000 | 4 |
| `Boss-39021` | 3,200,000 | 4 |
| `Boss-39019` | 3,200,000 | 3 |
| `Boss-37014` | 3,100,000 | 3 |
| `Enemy_Ingame` | 3,000,000 | 14 |
| `Boss-39013` | 3,000,000 | 4 |
| `Boss-39014` | 3,000,000 | 4 |
| `Boss-39015` | 3,000,000 | 3 |
| `Boss-39011` | 2,900,000 | 7 |
| `Boss-39012` | 2,800,000 | 4 |
| `Boss-39009` | 2,500,000 | 4 |
| `Tab (5)` | 2,000,000 | 14 |
| `LegL 1` | 2,000,000 | 2 |

- Bảng đầy đủ: [`15-enemy-hp.csv`](15-enemy-hp.csv)
- Đây là HP serialize trong prefab/scene của `data.unity3d`; giá trị runtime còn bị
  nhân bởi `Enemy_Data_Balance` / `Stage_Get_Datas` theo chapter/stage.
