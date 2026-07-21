# INDEX

<!-- Derived by bin/build_index.py — do not hand-edit in parallel mode. Format: SCHEMA.md section 7. -->

## Types
- [equipment](types/equipment.md) — A machine the cafe owns or operates
- [menu-item](types/menu-item.md) — An item currently or previously sold on the cafe menu
- [supplier](types/supplier.md) — External company that supplies goods or services to the cafe

## Objects
- [acme-beans](objects/acme-beans.md) (supplier) — 아크메 원두상사 — 에스프레소용 블렌드 원두를 주 1회(월요일) 납품한다.
- [cafe-latte](objects/cafe-latte.md) (menu-item) — 카페라떼 — 판매 가격은 4,500원이다 (2026-06 메뉴 기준).
- [daehan-beans](objects/daehan-beans.md) (supplier) [archived] — 대한빈스 — 2025년 계약으로 디카페인 원두를 납품했던 공급업체다.
- [espresso](objects/espresso.md) (menu-item) — 에스프레소 — 판매 가격은 3,000원이다 (2026-06 메뉴 기준).
- [grinder-mazzer](objects/grinder-mazzer.md) (equipment) — 마쩨르 그라인더 — 에스프레소 원두 분쇄에 사용하는 주력 그라인더다.
- [mazzer-korea](objects/mazzer-korea.md) (supplier) — 마쩨르코리아 서비스 — 그라인더 정기 점검을 분기 1회 수행한다.
- [seoul-dairy](objects/seoul-dairy.md) (supplier) — 서울우유대리점 — 우유를 주 3회(월·수·금) 납품하기로 했다 (2026-06-20 회의 결정).

## Link Types
- [maintains](links/maintains.md) — supplier → equipment
- [supplies](links/supplies.md) — supplier → menu-item

## Actions
- [log-equipment-issue](actions/log-equipment-issue.md) [T1] — 설비 이슈 기록
- [lookup-supplier](actions/lookup-supplier.md) [T0] — 공급처 조회
- [update-menu-price](actions/update-menu-price.md) [T2] — 메뉴 가격 변경

## Roles
- [procurement](roles/procurement.md) [max T1] — Supplier relations, incoming-goods intake, and equipment upkeep tracking
