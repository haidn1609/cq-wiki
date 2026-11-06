# Crusaders Quest Wiki (Tiếng Việt)

Xem online: https://haidn1609.github.io/cq-wiki/ (GitHub Pages, tự deploy `site/` mỗi khi push lên `main` qua `.github/workflows/pages.yml`).

Hoặc mở `site/index.html` trực tiếp bằng trình duyệt (chạy offline, không cần server).

Nguồn: https://docs.google.com/spreadsheets/d/1CAAUx5Z0nPdjavGpYhFbAgO_4LdQ9GWBpGBx1Muv4gc

## Build lại dữ liệu
1. `raw/html/*.html` – bản htmlview từng tab (tab dài tải thêm theo `&range=`), `raw/sheet.xlsx` – bản export.
2. `python -I scripts/grid.py` – parse thành `raw/grids.json`, tải icon vào `site/img/`.
3. `python -I -X utf8 scripts/extract.py` – gom chuỗi cần dịch vào `raw/tr/in_*.json`.
4. Bản dịch: `raw/tr/out_*.json` (cùng key) + `raw/tr/manual.json` (từ đơn sửa tay). Quy tắc: `raw/tr/GUIDE.md`.
5. `python -I -X utf8 scripts/build.py` – sinh `site/data.js`.

## Hình ảnh
Nguồn: [BWiki 克鲁赛德战记](https://wiki.biligame.com/cq/) (hero, sigil, skin, một phần skill) và [CQ Fandom](https://crusadersquest.fandom.com/) (skill). BWiki giới hạn tần suất gọi API – `scripts/bw.py` đã giãn cách 3s/lần.
- `raw/hero_zh.json` – ánh xạ tên hero EN → trang BWiki (qua bí danh + bảng dịch tên của BWiki, bổ sung tay).
- `raw/sigil_zh.json`, `raw/skin_zh.json` – ánh xạ tên sigil/skin EN → ZH (khớp theo nghĩa + chỉ số).
- `python -I -X utf8 scripts/images.py` – tải icon + chân dung hero (WebP) vào `site/img/hero/`.
- Ảnh skill/sigil/skin: `site/img/{skill,sigil,skin}/`, chỉ mục ở `raw/img_*.json`; `build.py` gắn vào `data.js`.
- Thiếu ảnh chân dung: 4 hero (chỉ có icon).

## Dữ liệu bổ sung (đợt 2)
- Sheet [CQ Guide to Almost Everything](https://docs.google.com/spreadsheets/d/1iQj-tdjBtey3zPn8fiy53UWj0Pq-R7NljdNmqpg4YrU): `raw2/html` + `raw2/sheet2.xlsx` → `python -I scripts/grid.py raw2`.
- BWiki: trang đánh giá của 375 hero 6★ (`raw2/bw_pages6.json` → `raw2/bw_fields.json`), làm sạch bằng `scripts/bw_clean.py`.
- `python -I -X utf8 scripts/extract2.py` → `raw2/tr/in_*.json`; bản dịch ở `raw2/tr/out_*.json` (quy tắc `raw2/tr/GUIDE.md`).
- `build.py` gộp cả 2 đợt; thêm 9 hero mới chỉ có trên BWiki (Milady, Gordian, Anton, Hina, Lime, Rie, Evgenia, Tian Mo, Drago).
- `raw2/my_ranks.json` – hạng + nhận xét tự xếp cho 11 hero chưa có trong tier list EN, dựa trên điểm BWiki (căn theo điểm BWiki trung bình của từng hạng EN: S≈9.3, A≈7.5, B≈6.2, C≈4.5, F≈3.6 – trung bình 2 điểm cao nhất). Hiển thị kèm dấu `*`.
- `python -I -X utf8 scripts/sigils.py` – chi tiết 46 sigil + set (chỉ số, nơi rơi, mô tả, hiệu ứng set) từ BWiki (`raw2/bw_sigil_pages.json`, `raw2/bw_set_pages.json`), bản dịch ở `raw2/tr/sigil_out_manual.json` → `raw2/sigils.json`.
