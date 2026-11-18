# 비원 법률사무소 홈페이지 (beonelaw.com)

- `site/` — 실제로 게시되는 파일. 문구는 HTML에서 직접 고친다.
- `<!--AUTO:...-->` ~ `<!--/AUTO-->` 사이는 칼럼 목록 자동 구간이다. 손으로 고치지 않는다.
- `data/posts.json` — 티스토리 칼럼 목록. `data/areas.json` — 업무분야 순서와 칼럼 분류 규칙(메뉴 순서와 같게 유지).
- `scripts/update_posts.py` — 티스토리 RSS에서 새 글을 가져온다.
- `scripts/refresh_columns.py` — 자동 구간과 sitemap.xml만 다시 쓴다.
- `.github/workflows/deploy.yml` — push할 때와 매일 06:17(KST)에 위 두 스크립트를 돌리고 GitHub Pages로 게시한다.
