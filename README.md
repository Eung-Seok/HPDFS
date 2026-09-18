# HPDFS — Heopung Predictive Drive Failure System

> HDD/SSD SMART 데이터를 분석해 저장장치 고장을 사전에 예측하고, 진단 이력을 운영할 수 있도록 만든 시스템

## 대시보드 미리보기

**메인 대시보드 — 전체 디스크 현황과 위험도 분포**

![HPDFS dashboard](v2/docs/images/dashboard.png)

**디스크 상세 — 진단 이력과 조치 상태**

![HPDFS disk detail](v2/docs/images/disk_detail.png)

## 프로젝트 소개

HPDFS는 Backblaze HDD 고장 데이터를 학습한 RandomForest 모델로 SMART 지표를 분석해 고장 확률과 위험 등급을 제공합니다. v1의 Windows 포터블 EXE에서 시작해, v2에서는 수집 에이전트·API·DB·대시보드를 분리한 컨테이너 기반 서비스로 확장했습니다.

## ML 모델

### 데이터와 학습

- **데이터:** 정상 45,500건 + 고장 5,000건 = 총 50,500건
- **알고리즘:** RandomForestClassifier
- **주요 설정:** n_estimators=200, max_depth=20
- **의사결정 임계값:** 0.36
- **선정 기준:** 고장 탐지에서 재현율을 중시하는 F2-score
- **입력:** 재할당 섹터, 대기 섹터, 정정 불가 섹터, 온도 등 SMART 지표 8개
- **출력:** 고장 확률과 정상·주의·위험 등급

### 테스트 성능

| Metric | Result |
|---|---:|
| Accuracy | 97.22% |
| Failure Precision | 86.35% |
| Failure Recall | 85.40% |
| Failure F1 | 85.87% |
| Failure F2 | 85.59% |
| ROC-AUC | 96.80% |
| PR-AUC | 90.93% |

|  | Predicted Normal | Predicted Failure |
|---|---:|---:|
| Actual Normal | TN 8,965 | FP 135 |
| Actual Failure | FN 146 | TP 854 |

## v1 → v2 아키텍처 진화

### v1 — 온프레미스 포터블 EXE

~~~mermaid
flowchart LR
    A[사용자 PC] --> B[smartctl SMART 수집]
    B --> C[RandomForest 예측]
    C --> D[CSV 저장]
    D --> E[Streamlit 대시보드]
~~~

- 단일 PC에서 수집·예측·시각화
- 로컬 CSV에 진단 결과 저장
- Windows 실행 파일과 BAT 런처로 배포

### v2 — 컨테이너 기반 서비스

~~~mermaid
flowchart TD
    A[로컬 에이전트] -->|5분 간격 HTTP POST| B[Nginx]
    B -->|/api/*| C[FastAPI]
    B -->|/*| D[Streamlit]
    C --> E[RandomForest]
    C --> F[(PostgreSQL)]
    D --> C
    G[GitHub Actions] --> H[Docker Hub]
    H --> I[Docker Compose / Kubernetes]
~~~

- 로컬 에이전트가 서버로 SMART 데이터 전송
- FastAPI에서 예측과 진단 이력 저장
- Streamlit에서 전체 현황과 디스크별 이력 조회
- Nginx를 통한 단일 진입점 구성
- Docker Compose와 Kubernetes 배포
- GitHub Actions 기반 이미지 빌드·배포 자동화

## 기술 스택

| 영역 | 기술 |
|---|---|
| Data / ML | Python, pandas, scikit-learn, joblib |
| Backend | FastAPI, Pydantic |
| Dashboard | Streamlit |
| Database | PostgreSQL |
| Collection | smartctl, Python agent |
| Infra | Nginx, Docker Compose, Kubernetes |
| CI/CD | GitHub Actions, Docker Hub |
| Test | pytest |

## 폴더 구조

~~~text
HPDFS/
├── v1/                  # Windows 포터블 EXE 버전
└── v2/
    ├── agent/           # 로컬 SMART 수집 에이전트
    ├── backend/         # FastAPI와 ML 예측
    │   ├── models/      # 학습 모델·임계값
    │   └── tests/       # predictor·API 테스트
    ├── frontend/        # Streamlit 대시보드
    ├── nginx/           # 리버스 프록시
    ├── k8s/             # Kubernetes 매니페스트
    ├── docs/            # 설계 문서와 화면 이미지
    └── docker-compose.yml
~~~

## 실행 방법

### Docker Compose

~~~bash
git clone https://github.com/Eung-Seok/HPDFS.git
cd HPDFS/v2
docker compose up -d
~~~

브라우저에서 `http://localhost`로 접속합니다.

### Kubernetes

~~~bash
cd HPDFS/v2
kubectl apply -f k8s/
kubectl get pods -n pdfs
kubectl port-forward svc/nginx-service 8080:80 -n pdfs
~~~

로컬 접속 주소는 `http://localhost:8080`입니다.

### Windows 수집 에이전트

~~~bat
cd v2\agent
start_agent.bat
stop_agent.bat
~~~

## 테스트

~~~bash
cd v2/backend
pytest tests/ -v
~~~

현재 predictor 경계값과 API 응답·예외 처리를 검증하는 테스트 22개가 포함되어 있습니다.

## 프로젝트 포인트

- 단순 모델 실험에서 끝내지 않고 실제 SMART 수집·예측·저장·시각화 흐름을 완성했습니다.
- 포터블 EXE에서 API·DB·컨테이너·Kubernetes 구조로 단계적으로 확장했습니다.
- 고장 클래스 재현율과 운영 오탐을 함께 고려해 F2 기반 임계값을 적용했습니다.
