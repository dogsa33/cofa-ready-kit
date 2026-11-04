# 필요한 문서를 바로 찾는 전체 지도

**시험 당일 첫 화면은 [루트 README](../README.md)다.** Cofa 일반 터미널에서 키트를 받은 뒤 `.cofa-kit/README.md`를 연다. README 순서대로 제공 Codex에 시작 요청 → SCENARIO 직접 읽기 → 구현·검증·제출 준비를 진행한다. 스킬 설치와 MCP 연결은 필요한 경우에 선택한다.

이 페이지에서는 현재 상황에 맞는 한 행을 골라 연다. EXAM-PLAYBOOK은 화면과 진행의 추가 설명, MANUAL은 명령과 도구의 추가 상세다. 요청문과 스킬은 **제출 확정 전**에 사용하며, 확정 후 대기·후속 서술형은 AI 없이 직접 진행한다.

## 화면·규칙·도구를 확인할 때

| 문서 | 필요한 시점 | 확인할 내용 |
| --- | --- | --- |
| [EXTENSIONS.md](EXTENSIONS.md) | 외부 MCP·플러그인을 추가할 때 | 문서 서버 프리셋·직접 URL·설정 합치기·키트와 타사 플러그인 설치 |
| [EXAM-PLAYBOOK.md](EXAM-PLAYBOOK.md) | README로 시작한 뒤 화면 위치·진행 방법이 궁금할 때 | 11월 4일 가이드의 Browser 포트·경로·버튼, 저장 충돌, 승인·실행 구분, 영역 복구, 직접 제출 |
| [RULES.md](RULES.md) | 준비물·허용 도구·제출 제한을 확인할 때 | 참가자 PDF의 규칙과 출처별 요약; 당일 공지·실제 안내와 함께 확인 |
| [DAY-PLAN.md](DAY-PLAN.md) | 사전 체험이나 시험 당일 시간 배분을 준비할 때 | 15분 체험, 연습, 접속·과제·제출을 위한 권장 계획 |
| [SKILLS-BEGINNER.md](SKILLS-BEGINNER.md) | 스킬 이름 호출이나 여러 스킬 조합이 궁금할 때 | 셸과 Codex 입력란, 선택형 설치, 직접 파일 읽기, 병렬 에이전트와의 차이 |
| [MANUAL.md](MANUAL.md) | 설치·업데이트·기록 도구의 자세한 예제가 필요할 때 | 개인 PC와 Cofa 경로 구분, CLI 실행, 충돌 처리, 오류 복구의 상세 설명 |
| [SETUP.md](SETUP.md) | 이름 호출용 설치 또는 로컬 MCP 연결을 선택했을 때 | 실제 환경에서 확인할 설치·연결 설정과 파일 직접 읽기 대안 |
| [MCP-PLUGINS.md](MCP-PLUGINS.md) | 초기 CLI·MCP 입력칸에서 연결하거나 추가 도구를 검토할 때 | 로컬+공식 문서 두 서버 설정, 실제 호출 확인·자동 선택 조건, 플러그인 지원·규칙 구분 |
| [TOOLS.md](TOOLS.md) | 특정 CLI 명령이나 검증 기록 확인법이 필요할 때 | 제출 전 용량·필수 파일 확인, 요구사항·실행 기록·CSV 검사·반도체 계산·변경 확인 |

## 실제 과제 유형에 맞는 자료를 찾을 때

| 문서 | 필요한 시점 | 확인할 내용 |
| --- | --- | --- |
| [SEMICONDUCTOR.md](SEMICONDUCTOR.md) | 반도체 검사·계측·결함 자료가 실제로 주어졌을 때 | 데이터에 따라 사용할 분석과 먼저 물을 업무 기준 선택 |
| [SEMICONDUCTOR-WALKTHROUGH.md](SEMICONDUCTOR-WALKTHROUGH.md) | 통과율·I-MR 도구 사용을 익히거나 예제와 대조할 때 | 합성 CSV의 실제 명령·기대값·해석 범위; 실제 과제의 기준은 별도 확인 |
| [DATA-JOIN.md](DATA-JOIN.md) | 두 CSV를 키로 결합해야 할 때 | 키 관계·미매칭·예상 행 수 검사; 실제 조인과 수량 보존 검증의 구분 |

## 제공 Codex에 보낼 요청문이 필요할 때

README의 기본 진행 중 특정 작업을 따로 요청하고 싶을 때 사용한다. 코드블록의 자연어 요청은 **Codex 입력란**에 넣는다.

| 요청문 | 필요한 시점 | 맡길 작업 |
| --- | --- | --- |
| [prompts/README.md](../prompts/README.md) | 요청문을 고르거나 직접 작성할 때 | 상황별 요청 선택과 목표·자료·제약·완료 기준·진행 범위 정리 |
| [SCENARIO.md](../prompts/SCENARIO.md) | README의 시작 요청을 받은 Codex가 진행할 때 | 실제 과제부터 읽고 스킬·연결된 MCP 도구를 선택; 현재 증거를 기준으로 재개 |
| [START.md](../prompts/START.md) | 요구사항 파악만 따로 요청할 때 | 실제 과제의 필수조건·제출물·확인 질문 정리 |
| [BUILD.md](../prompts/BUILD.md) | 확정된 필수조건을 구현하거나 기존 결함을 고칠 때 | 기존 스택·계약을 유지한 작은 구현과 관련 검증 |
| [IMPROVE.md](../prompts/IMPROVE.md) | 더 높은 완성도·반복 검증 또는 결과 수정을 원할 때 | 원하는 품질·중단 시각·보존 범위, 수정 후 검증 반복, `/goal` 확인과 일반 요청 대안 |
| [RESCUE.md](../prompts/RESCUE.md) | 오류가 발생하거나 같은 수정이 반복될 때 | 작은 재현 입력·기대값·실제값으로 원인을 좁혀 최소 수정 |
| [RESUME.md](../prompts/RESUME.md) | 대화가 길어지거나 제출 확정 전에 다시 시작할 때 | 실제 파일·결정·검증 기록에서 이어갈 작업 확인 |
| [VERIFY.md](../prompts/VERIFY.md) | 제출 확정 전 마지막 점검을 맡길 때 | 필수 파일·기능·독립 기대값·문서 일치와 실패·미검증 확인 |
| [PRACTICE.md](../prompts/PRACTICE.md) | 시험 전 또는 제출 확정 전에 본인 이해를 점검할 때 | 실제 선택과 검증을 본인이 먼저 설명하는 한 질문씩의 연습 |
| [SEMICONDUCTOR.md](../prompts/SEMICONDUCTOR.md) | 반도체 검사·측정 분석을 요청할 때 | 행 단위·분모·재검사·적절한 도구 선택과 해석 |
| [MODEL-EVAL.md](../prompts/MODEL-EVAL.md) | 분류·회귀 예측 모델의 학습·평가가 요구될 때 | 예측 시점·누수 없는 분할·기준선·업무 지표·최종 평가 |

## Codex가 필요한 때 읽는 여섯 스킬

스킬은 작업 지침이다. 현재 키트의 해당 파일을 직접 읽어 적용할 수 있으며, 실제 과제에 해당하는 것만 선택한다.

| 스킬 | 필요한 시점 | 맡는 역할 |
| --- | --- | --- |
| [cofa-triage](../skills/cofa-triage/SKILL.md) | 목표·필수조건·업무 기준을 파악할 때 | 요구사항·출처·질문·검증 기준 연결 |
| [cofa-build](../skills/cofa-build/SKILL.md) | 필수 기능 구현 또는 기존 코드 수정 | 작은 동작부터 구현하고 기존 계약·정상 동작을 보존 |
| [cofa-verify](../skills/cofa-verify/SKILL.md) | 구현 완료 주장·제출 준비를 점검할 때 | 실제 실행과 독립 기대값으로 확인하고 현재 파일과 증거를 대조 |
| [cofa-explain](../skills/cofa-explain/SKILL.md) | 제출 확정 전 작업 정리·본인 설명 연습 | 구현·AI 활용·참가자 판단·검증·한계를 실제 근거로 정리하고 이해 점검 |
| [cofa-semiconductor](../skills/cofa-semiconductor/SKILL.md) | 실제 반도체 검사·결함·설비 데이터 분석 | 단위·분모·재검 정책·관리한계와 분석 해석 확인 |
| [cofa-model-eval](../skills/cofa-model-eval/SKILL.md) | 표·시계열 예측 모델의 실제 학습·평가 | 누수·분할·기준선·평가지표 점검; 단순 집계·SPC·API 수정은 제외 |

## 해당 스킬이 더 자세히 확인하는 참조

| 참조 파일 | 필요한 시점 | 확인할 내용 |
| --- | --- | --- |
| [스킬·MCP 점검](../skills/cofa-triage/references/tool-check.md) | 스킬 탐색·설치본 차이·MCP 호출 문제 | 필요한 능력 확인, 선택형 로컬 진단, 파일 보존과 CLI 대안 |
| [기존 프로젝트 수정](../skills/cofa-build/references/existing-project.md) | 기존 API·서비스·스크립트의 오류 수정 | 변경 전 재현, 유지할 계약, 회귀 검사, 최소 변경, 수정 후 재확인 |
| [검증 기록과 파일 변경](../skills/cofa-verify/references/evidence.md) | 키트 실행기의 선택형 `--watch`를 사용할 때 | 추적한 파일의 변경 여부와 실제 검사 성공의 구분·한계 |
| [데이터 계약과 수율](../skills/cofa-semiconductor/references/data-contract.md) | 검사 집계·재검사·CSV 결합 | 행과 개체 키, 분자·분모, 재검 선택, 조인 전후 수량 보존 |
| [SPC 적용과 한계](../skills/cofa-semiconductor/references/spc.md) | 연속 계측값의 I-MR·관리한계를 다룰 때 | 같은 조건의 시계열, 고정 기준기간, 신호와 규격 판정의 차이 |
| [결함 조사와 예측 판단](../skills/cofa-semiconductor/references/investigation.md) | 결함 우선순위·원인 후보·반도체 예측을 검토할 때 | 사건과 개체 수 구분, 관찰과 인과의 구분, 예측 시점·대상 확인 |

## 연습·근거·유지보수 자료가 필요할 때

| 문서 | 필요한 시점 | 확인할 내용 |
| --- | --- | --- |
| [docs/PRACTICE.md](PRACTICE.md) | 시험 전에 전체 흐름을 연습할 때 | 60분 합성 CSV 과제와 완료 기준; 실제 출제 문제·정답은 아님 |
| [REHEARSAL-2026-10-30.md](REHEARSAL-2026-10-30.md) | 로컬 리허설에서 무엇을 확인했는지 볼 때 | 합성 과제 실행·별도 검증 결과와 Cofa·Sol 실측의 한계 |
| [VALIDATION.md](VALIDATION.md) | 도구의 검증 범위와 남은 미확인을 볼 때 | 버전별 검사 기록; 키트 검사와 실제 대회 기능 검증의 구분 |
| [RESEARCH.md](RESEARCH.md) | 공식 시연·공개 저장소·설계 근거가 궁금할 때 | 확인한 출처, 최신순 조사, 참고 아이디어와 실제 반영 범위 |
| [PUBLISH.md](PUBLISH.md) | 시험 전 개인 PC에서 범용 준비 도구를 게시할 때 | 공개 대상 검토와 게시 절차; 시험 중 문제·결과물 게시에 사용하지 않음 |
| [AGENTS.md](../AGENTS.md) | 이 준비 키트 자체를 개발·수정할 때 | 개발자를 위한 유지보수 지침; 실제 과제의 AGENTS를 덮어쓰지 않음 |
| [LICENSE](../LICENSE) | 준비 키트의 재사용·배포 조건이 필요할 때 | 자체 공개 도구의 MIT 이용 조건 |
