# 구독 연장 리포트 자동 생성기

카카오톡 기반 데일리 운영 리포트 대화 로그와 (선택) 매체/캠페인/소재 단위 성과 데이터를 입력하면,
광고주 전달용 **구독 연장 리포트**의 ① 운영 현황 요약, ② 주요 성과 및 인사이트를 자동 생성합니다.

③ 추후 운영 방향성은 담당 마케터 직접 작성 영역으로, 메뉴 구조만 출력됩니다.

---

## 설계 원칙

### 할루시네이션 차단 (최우선)
- **모든 문장은 근거(Evidence) 필수** — 근거 없는 문장은 출력하지 않음
- **금칙어 자동 필터링** — "경쟁 심화", "시즌성", "알고리즘", "타겟 피로도" 등 로그에 없는 원인 단정 차단
- **표본 부족 자동 판정** — 소진액/전환수 기준으로 SUFFICIENT / REFERENCE_ONLY / INSUFFICIENT 분류
- **비교 데이터 없으면 비교 표현 금지** — "전월 대비", "개선", "악화" 표현 제한

### 안전장치
1. **근거 강제 시스템** — 모든 문장에 `(근거: ...)` 태그 필수
2. **금칙어/단정어 필터** — 로그에 명시된 경우만 허용
3. **감사 로그(Audit Log)** — 문장 → 원문 위치 매핑 테이블 자동 생성

---

## 프로젝트 구조

```
├── src/
│   ├── main.py              # 오케스트레이터 + CLI
│   ├── models.py            # 공통 데이터 모델
│   ├── parser/
│   │   ├── chat_log_parser.py   # 카카오톡/슬랙 채팅 로그 파서
│   │   └── data_file_parser.py  # CSV/Excel 데이터 파서
│   ├── normalizer/
│   │   └── normalizer.py    # 데이터 정규화 (채널/SKU/기간별 통합)
│   ├── evidence/
│   │   └── evidence_tracker.py  # 근거 추적 시스템
│   ├── scoring/
│   │   ├── scoring.py       # 표본 충분성 판단 + 인사이트 등급
│   │   └── forbidden_terms.py   # 금칙어/단정어 필터
│   ├── renderer/
│   │   └── renderer.py      # 리포트 렌더링
│   └── audit/
│       └── audit_log.py     # 감사 로그 생성
├── tests/
│   ├── test_parser.py       # KPI 파싱, 액션 인식, ROAS/UE ROAS 구분
│   ├── test_scoring.py      # 표본 부족 판정
│   ├── test_evidence.py     # 근거 누락 검출
│   ├── test_forbidden_terms.py  # 금칙어 필터
│   └── test_integration.py  # 전체 파이프라인 통합 테스트
├── samples/
│   ├── sample_chat_log.txt       # 샘플 채팅 로그
│   ├── sample_data.csv           # 샘플 매체 데이터
│   ├── sample_report_output.txt  # 생성된 리포트
│   ├── sample_audit_log.txt      # 감사 로그 (텍스트)
│   └── sample_audit_log.json     # 감사 로그 (JSON)
└── pyproject.toml
```

---

## 설치 및 실행

### 요구사항
- Python 3.10+
- pandas, openpyxl

### 설치
```bash
pip install pandas openpyxl pytest
```

### CLI 실행
```bash
python -m src.main <채팅로그파일> \
  --brand "브랜드명" \
  --channels META GFA \
  --sku "스큐1" "스큐2" \
  --period-start 2025.01.06 \
  --period-end 2025.01.31 \
  --currency KRW \
  --data-files data1.csv data2.xlsx \
  --output report.txt \
  --audit-output audit.txt \
  --audit-json audit.json
```

### Python API 사용
```python
from src.main import ReportPipeline

pipeline = ReportPipeline()
report, audit_text, audit_json = pipeline.run_from_text(
    chat_log_text="...",
    brand_name="브랜드A",
    channels=["META", "GFA"],
    sku_list=["스큐A"],
    reporting_period_start="2025.01.01",
    reporting_period_end="2025.01.31",
    data_file_paths=["data.csv"],
)
print(report)
```

### 테스트 실행
```bash
python -m pytest tests/ -v
```

---

## 입력값

| 구분 | 필수 | 설명 |
|------|------|------|
| `daily_chat_log` | 필수 | 카카오톡/슬랙 데일리 운영 리포트 대화 원문 텍스트 |
| `data_files` | 선택 | CSV/Excel 매체 데이터 (캠페인/소재 단위) |
| `brand_name` | 선택 | 브랜드명 (미입력 시 "[추가 입력 필요]") |
| `channels` | 선택 | 매체 목록: GFA, META, KAKAO, GOOGLE |
| `sku_list` | 선택 | SKU 목록 |
| `reporting_period` | 선택 | 운영 기간 (start ~ end) |
| `currency` | 선택 | KRW (기본) 또는 USD |

---

## 출력 구조

```
[구독 연장 리포트 | 운영 현황 & 주요 인사이트]

1. 운영 현황 요약
   1-1. 전체 운영 요약
   1-2. 기간별 성과 흐름
   1-3. 주요 운영 액션 로그
   1-4. 데이터 신뢰도 코멘트

2. 주요 성과 및 인사이트
   2-a. 캠페인·타겟·운영 인사이트 (마케터 영역)
   2-b. 콘텐츠·소구·소재 인사이트 (디자인/크리에이티브 영역)

3. 추후 운영 방향성 ← 담당 마케터 직접 작성
```

---

## 표본 판단 기준

| 판단 | 조건 | 리포트 표기 |
|------|------|------------|
| SUFFICIENT | 소진 ≥ 20만원 + 전환 ≥ 5건 | 판단 지표로 활용 가능 |
| REFERENCE_ONLY | 소진 5~20만원 또는 전환 3~4건 | [참고 지표] |
| INSUFFICIENT | 소진 < 5만원 또는 전환 < 3건 | [표본 부족] |

---

## 금칙어 목록

로그에 명시되지 않으면 사용 불가:
- 경쟁 심화 / 시즌성 / 알고리즘 영향/변화/업데이트
- 타겟 피로도 / 학습 안정화/완료/기간
- 업계 평균 / 시장 평균
- 일반적으로 / 보통 / 통상
- 추정 / ~것으로 보임 / ~판단됨

로그 원문에 해당 표현이 있으면 허용됩니다.
