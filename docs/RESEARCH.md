# 공식 사례·공개 저장소 조사와 실제 반영

[시험 첫 화면](../README.md) · [전체 문서 지도](INDEX.md)

조회일: Cofa·GitHub는 **2026-10-30 KST**, OpenAI 공식 자료와 구현 재점검은 **2026-10-31 KST**. Cofa 공식 사이트의 내부 링크·시연 HTML, 참가자 제공 PDF 3개, GitHub 공개 검색·README·주요 파일을 대조했다. 외부 저장소 코드는 실행하거나 복사하지 않았다. 공개 자료는 수시로 바뀌며 준비 저장소의 주장 자체가 대회 규칙은 아니다.

## Cofa 공식 사이트를 실제 확인한 결과

| 확인한 자료 | 관찰 | 우리 준비에 반영 |
| --- | --- | --- |
| [Cofa 홈페이지](https://www.getcofa.com/ko) | 기술·의도·인지: 결과 실행·검증, 목표·위임·방향 조정, 구조·원리·한계 설명. 코드와 협업 기록·사후 Q&A를 함께 살핌 | 기능 결과와 검증·선택 이유를 연결. 이번 시험의 공개 배점표라고 해석하지 않음 |
| [활용 사례](https://www.getcofa.com/ko/usecase) | KRAFTON 내부 채용과 KRAFTON×CJ올리브영 Cofathon에 활용 | 채용·다른 행사 사례와 이번 시험의 개별 조건을 구분 |
| [개발 작업 화면 시연](https://www.getcofa.com/brochure-v2/workspace-mock.html) | 주문 API의 재시도·중복 주문·결제 불확실성, 기존 API 계약 유지, 코드·테스트·판단 문서 예시 | 기존 프로젝트 수정 분기를 build/triage/verify에 보완 |
| [평가·면접 브리핑 시연](https://www.getcofa.com/brochure-v2/admin-briefing.html) | 주문 API 외 월별 매출 분석 사례도 있음. 결측 처리의 이유와 전후 비교를 설명하는지 살핌 | 개발 과제 하나나 반도체 주제로 미리 고정하지 않음 |

사용자 첨부 화면은 위 개발 작업 시연과 같은 `order-service` 예시다. Node.js·TypeScript·PostgreSQL, `DECISIONS.md`가 보이지만 **이번 시험의 기술 스택·필수 파일명·실제 기출이라는 근거는 없다.** HTML도 확인했으며 파일 내용은 문자열, 테스트 버튼은 고정된 결과 문구, 메신저는 고정 안내를 표시한다. 실제 주문 서비스나 테스트를 실행한 증거가 아니다. [공식 시연](https://www.getcofa.com/brochure-v2/workspace-mock.html)

따라서 연습할 것은 `기존 동작 확인 → 오류 재현 → 유지할 계약 확인 → 작은 수정 → 회귀 검사 → 선택 이유 설명`이다. 예시의 구현을 정답으로 가져오거나 과제마다 주문 API·대시보드를 만들지 않는다. [보완한 기존 코드 지침](../skills/cofa-build/references/existing-project.md)

공식 공개 자료에서 확인한 것은 **시연용 문제와 활용 사례**다. 시험 당일 실제 문제, 과거 대회의 전체 출제 원문, 세부 채점표를 확보했다고 주장하지 않는다. SK하이닉스 발표의 문제 정의·AI 활용·결과 검증 방향은 준비의 근거로 사용한다. [Talent Hub](https://talent.skhynix.com/hub/ko/company/story/237), [대회 홈페이지](https://skhynix-hackathon.com/ai-2026)

## 제품 기능·다른 행사와 시험 당일 규칙을 혼동하지 않기

| 공개 사이트의 내용 | 이번 참가자 PDF 기준 |
| --- | --- |
| [관리자 보안 시연](https://www.getcofa.com/brochure-v2/admin-security.html)의 파일 업로드·Skills 메뉴 옵션 | 개인 PC 파일 업로드 금지. 일반 제품 옵션이 이번 허용을 의미하지 않음 |
| [2026-07-30 Cofathon](https://cofathon.getcofa.com/)의 로컬 하네스 업로드 안내 | 다른 행사 조건. 이번에는 허용된 공개 자료를 제공 환경에서 가져오는 방식 |
| 예시의 제공 모델·실행 시간·메모리·제출명 | 시험 당일 화면의 허용 모델·타이머와 실제 README가 결정 |
| 일반 제품의 AI 도움·면접관 도구 | 과제는 제공 Codex, 후속 서술형은 AI·복사/붙여넣기 없이 참가자가 직접 답변 |

업무 기준은 **실무자 에이전트**, 사용법은 **Cofa Helper**, 반복 장애는 **문제 신고**로 구분한다. 공개 Skill·MCP를 받을 수 있어도 시험 자료 외부 전송·Git Push·Computer Use·외부 모델·개인 API 사용은 허용되지 않는다. PDF의 상세 구분은 [규칙 요약](RULES.md)에 있다.

## GitHub 최신순 검색 범위

GitHub 공개 API의 `sort=updated&order=desc`로 검색했다. 인증 없이 조회했고 rate limit 거절은 없었다. 아래 건수는 조회 당시 순간값이며 모두 이번 대회 관련이라는 뜻은 아니다.

| 검색어 | 당시 결과 수 |
| --- | --- |
| [cofa](https://github.com/search?q=cofa&type=repositories&s=updated&o=desc) | 696 |
| ["Cofa Probe"](https://github.com/search?q=%22Cofa+Probe%22&type=repositories&s=updated&o=desc) | 8 |
| ["sk hynix" hackathon](https://github.com/search?q=%22sk+hynix%22+hackathon&type=repositories&s=updated&o=desc) | 7 |
| [hynix hackathon](https://github.com/search?q=hynix+hackathon&type=repositories&s=updated&o=desc) | 9 |
| [하이닉스 해커톤](https://github.com/search?q=%ED%95%98%EC%9D%B4%EB%8B%89%EC%8A%A4+%ED%95%B4%EC%BB%A4%ED%86%A4&type=repositories&s=updated&o=desc) | 3 |
| [cofa skills](https://github.com/search?q=cofa+skills&type=repositories&s=updated&o=desc) | 8 |
| [cofa 이름·10월 20일 이후 생성](https://github.com/search?q=cofa+in%3Aname+created%3A%3E2026-10-20&type=repositories&s=updated&o=desc) | 36, 그중 최신 30개 목록 확인 |

검색 결과를 전부 정밀 감사한 것은 아니다. 관련성 있는 **기존 3곳·신규 8곳, 총 11곳**의 README와 주요 파일을 비교했다. 아래 시각은 GitHub `updated_at` **UTC**이며 최신 커밋 시각·품질 순위와 다르다. 시험 문제와 참가자의 답을 찾은 것이 아니라 공개 준비 도구를 비교한 것이다.

| 저장소·갱신 시각(UTC) | 실제 확인한 파일과 장점 | 라이선스 확인·적용 판단 |
| --- | --- | --- |
| [zittenyetten/cofa-probe-kit](https://github.com/zittenyetten/cofa-probe-kit), 10-30 14:44:20 | [task-evidence-check](https://github.com/zittenyetten/cofa-probe-kit/blob/main/skills/task-evidence-check/SKILL.md): 답변·AI 제안·결정 구분, 불완전한 답 재확인, 짧은 상태 보고 | 자체 자료 MIT, 강의 원자료 등 별도 권리. 질문 후속 확인 원칙 참고 |
| [B0neh3ad/cofa-toolkit](https://github.com/B0neh3ad/cofa-toolkit), 10-30 14:39:36 | [parallel-delivery](https://github.com/B0neh3ad/cofa-toolkit/blob/main/skills/parallel-delivery/SKILL.md): 수정 파일 담당 분리, 통합 담당, 통합 후 검사 | MIT. 실제 위임 기능이 있을 때만 해당 운영 원칙 참고 |
| [JINwonLEE/cofa-codex-harness](https://github.com/JINwonLEE/cofa-codex-harness), 10-30 14:36:43 | [README](https://github.com/JINwonLEE/cofa-codex-harness/blob/main/README.md), [hx-interview](https://github.com/JINwonLEE/cofa-codex-harness/blob/main/skills/hx-interview/SKILL.md): 7개 스킬, 질문 점검과 답 기록 구분 | MIT. 기존 5개 역할과 중복. 추가 AGENTS 관리 블록은 도입하지 않음 |
| [denny6389/cofa-hackathon-kit](https://github.com/denny6389/cofa-hackathon-kit), 10-30 14:29:15 | [README](https://github.com/denny6389/cofa-hackathon-kit/blob/main/README.md): 직접 스킬 읽기, 실제 요구→구현→독립 기대값 연결 | 전체 라이선스 미표시, 일부 스킬 MIT. 단계마다 승인 반복하는 흐름은 채택하지 않음 |
| [bbambbubba/cofa-probe](https://github.com/bbambbubba/cofa-probe), 10-30 14:12:40 | [harness.py](https://github.com/bbambbubba/cofa-probe/blob/main/harness.py): 구현·입력 fingerprint, 출력 SHA256, 명령·경로·최소 검사 수 대조 | MIT. 오래된 검증 증거의 재사용 방지 원칙 참고. 새 기록 규격 전체는 도입하지 않음 |
| [ApexIllumination/cofa-work-kit-devdominics](https://github.com/ApexIllumination/cofa-work-kit-devdominics), 10-30 14:07:50 | [eval-cases.json](https://github.com/ApexIllumination/cofa-work-kit-devdominics/blob/main/templates/eval-cases.json), [pipeline-map.json](https://github.com/ApexIllumination/cofa-work-kit-devdominics/blob/main/templates/pipeline-map.json): 정상·예외 기대값, 진입점·흐름·의존성 연결 | 루트 LICENSE 조회 404/API 미표시. 기존 기록에 실제 기대값·구현 위치를 연결하는 원칙 참고 |
| [allsleep7610/hynix-hackathon-workflow](https://github.com/allsleep7610/hynix-hackathon-workflow), 10-30 11:32:08 | [README](https://github.com/allsleep7610/hynix-hackathon-workflow/blob/main/README.md): 18개 스킬, 단일 기록, 독립 평가·자체 점검 구분 | [NOTICE](https://github.com/allsleep7610/hynix-hackathon-workflow/blob/main/NOTICE.md)는 재사용 라이선스 미부여 명시. 구현 해설과 본인 이해 확인을 구분하는 원칙만 참고 |
| [arcturus0637-rgb/cofa-prelim-kit](https://github.com/arcturus0637-rgb/cofa-prelim-kit), 10-30 06:31:04 | [checks.py](https://github.com/arcturus0637-rgb/cofa-prelim-kit/blob/main/kitlib/checks.py), [session.py](https://github.com/arcturus0637-rgb/cofa-prelim-kit/blob/main/kitlib/session.py): 실행 전후와 현재 source fingerprint 대조 | 자체 코드 MIT, upstream은 원본 조건. 소스 변경 뒤 재검증 원칙 참고 |
| [phy0916/cofa-probe-starter](https://github.com/phy0916/cofa-probe-starter), 10-30 04:38:45 | [run_tests.py](https://github.com/phy0916/cofa-probe-starter/blob/main/scripts/run_tests.py): pytest 종료코드·버전·출력 기록 | 루트 LICENSE 조회 404/API 미표시. 현재 로컬 실행기와 중복 |
| [ColdTbrew/cofa-skills](https://github.com/ColdTbrew/cofa-skills), 10-27 13:34:00 | [honest-eval](https://github.com/ColdTbrew/cofa-skills/blob/main/skills/honest-eval/SKILL.md): 운영 상황에 맞는 평가, 기준선·누수·임계값 선정 자료 구분 | MIT. 예측·분류 과제일 때만 기존 반도체/검증 지침 적용 |
| [hamjoon2003/sk-hynix-2nd-harness](https://github.com/hamjoon2003/sk-hynix-2nd-harness), 10-27 07:38:40 | [README](https://github.com/hamjoon2003/sk-hynix-2nd-harness/blob/main/README.md), [preflight.py](https://github.com/hamjoon2003/sk-hynix-2nd-harness/blob/main/scripts/preflight.py): 환경·시간대·경계·요구사항별 검사 | MIT. 환경 PASS와 과제 검증 성공을 구분하며 키트 폴더를 과제 루트로 혼동하지 않음 |

공개 열람 가능성과 재배포 허가는 다르다. 위 구현을 복사·설치·실행한 비교가 아니며 성능·안전성·점수 우열을 입증하지 않는다. 이전에 본 `zittenyetten/cofa-probe-workkit` 대신 이번에는 실제 확인된 `cofa-probe-kit`을 비교했다. 예전 `hongkevin/cofathon-prep`는 다른 행사의 준비물로, 시험 당일 도구·출제의 증거로 사용하지 않는다.

## 이번 재점검으로 바꾼 것

| 발견한 부족함 | 반영한 수정 | 확인 범위 |
| --- | --- | --- |
| 설치·문서·스킬 호출을 먼저 배워야 하는 복잡성 | README의 제공 Codex 시작 요청 한 번, 필요한 스킬 파일 직접 읽기, 설치·MCP 선택형 | 경로·문서 간 흐름 검토. 실제 Cofa 파일 접근은 사전 체험 필요 |
| 기존 코드 오류 수정 분기가 얕음 | 변경 전 재현·API 계약·회귀 테스트·최소 수정·정상 동작 보존을 기존 build/triage/verify에 추가 | 공개 데모와 대조한 지침 보완. 시험 당일 문제를 가정하지 않음 |
| 검증 후 파일 변경·통합을 놓칠 수 있음 | 관련 검사 재실행 지침에 v1.3.0의 선택형 `run --watch`·파일 대조 추가 | 지정한 파일의 전후·현재 SHA256 비교. 전체 의존성이나 기능 성공을 증명하지 않음 |
| 기존 로그 형식·마지막 개행에 따라 기록 손상 가능 | v1.2.1에서 쓰기 전 검사·보존, run의 명령 실행 전 검사 | 재현 후 회귀 테스트로 검증 |
| Node의 테스트 0개를 명령 성공으로 볼 수 있음 | Node 기본 TAP의 0개·skip·TODO·실패 구분 | 실제 Node 실행 검사. Jest/Vitest·모든 출력 형식 지원은 아님 |

업무 답변이 불완전하면 **실제로 답한 범위만 확정하고, 미응답은 표시한 채 결과를 바꾸는 경계 사례를 재질문**한다. 기다리는 동안 독립된 확정 작업을 진행한다. 그 내용을 triage에 반영했다. 검사와 수정의 상세 기록은 [검증 결과](VALIDATION.md)에 있다.

## 2026-11-04 외부 MCP·플러그인 재점검

사용자가 Cofa에서 외부 MCP 추가가 가능하다고 확인한 점을 반영해 확장 구성을 추가했다. 공개 `cofa-probe` 준비 저장소와 참가자 후기만으로 개별 서버·플러그인의 실제 Cofa 호환성을 확정하지 않고, 제공자 공식 문서와 개발 PC의 실제 실행을 함께 확인했다. 자료별 확인 범위와 바로 쓸 명령은 [외부 MCP·플러그인](EXTENSIONS.md)에 정리했다.

키트에 OpenAI Docs·Microsoft Learn·DeepWiki·Context7 프리셋, 직접 HTTPS 주소 입력, 기존 MCP JSON 보존 병합을 추가했다. 네 서버의 초기화·도구 목록과 공개 기술 질의 호출을 개발 PC에서 확인했다. 플러그인도 공식 portable manifest와 Codex 호환 manifest·marketplace를 만들고 격리된 CLI 환경에서 실제 설치했다. 이전 Context7 제외 판단은 선택형 제공으로 변경했다. 아래 비교표와 과거 조사 기록은 해당 조회일의 판단이다.

## Skill·MCP를 더 추가해야 하나

v1.3.0에서는 기존 다섯 스킬에 **실제 분류·회귀 과제에만 쓰는 `cofa-model-eval`**을 추가했다. 예측 시점에 알 수 없는 특징, 시간·개체 누수, 잘못된 분할·임계값 선정, 불균형 자료의 정확도 과장을 점검한다. 단순 집계·API 수정에는 읽지 않는다. 기존 반도체 스킬은 검사 단위·분모·재검사·장비 비교를, 새 스킬은 모델 학습·평가를 담당한다.

공식 근거는 scikit-learn의 [데이터 누수](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage), [시간·그룹 분할](https://scikit-learn.org/stable/modules/cross_validation.html), [평가지표](https://scikit-learn.org/stable/modules/model_evaluation.html), [분류 임계값](https://scikit-learn.org/stable/modules/classification_threshold.html) 문서를 확인했다. 특정 라이브러리 설치를 요구하지 않고 기존 스택에서 원칙을 적용한다.

MCP는 기존 서버에 **`evidence_freshness`** 한 도구를 추가했다. 이미 `run --watch`로 선택한 파일의 기록이 현재 내용과 같은지 읽기만 한다. 실패한 명령도 파일은 같을 수 있어 `fresh`와 `execution_ok`를 분리한다. 실제 CLI·stdio 검증과 한계는 [검증 기록](VALIDATION.md)에 있다. 새로운 계정·원격 서버·별도 연결은 추가하지 않았으며 README의 시작 요청 한 번을 유지한다.

## OpenAI 공식 자료로 재점검한 내용

공식 본문을 직접 열어 확인했다. 사용자가 기억하는 특정 “서밋” 발표는 식별하지 못했다. 아래 **DevDay 행사 요약**, 개발자 블로그, Cookbook을 구분하며 모두 같은 행사 발표였다고 소개하지 않는다.

| 자료·발행일 | 확인한 핵심 | 이 키트에서의 적용 |
| --- | --- | --- |
| [DevDay 2026](https://learn.chatgpt.com/docs/whats-new/devday-2026), 2026-09-29 · 행사 요약 | 모델·클라우드 환경·플러그인 관련 제품 발표 | Cofa 제공 환경과 허용 모델을 우선. 별도 클라우드·Astra·외부 연결 도입 근거로 사용하지 않음 |
| [Harness-aware evaluation of plugins](https://developers.openai.com/cookbook/examples/partners/harness_aware_plugin_evals/harness_aware_plugin_evals), 2026-09-23 · Cookbook | 도구 단독 검사, 작은 모델 루프, 실제 제품 환경의 검증을 구분 | CLI·MCP 성공, 스킬 지침 검토, 실제 Cofa 작업 성공을 각각 기록 |
| [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), 2026-09-11 · 블로그 | 짧고 정확한 적용 조건, 필요한 참조만 읽기, 모델에 따라 다른 지침 필요성 | 선택형 참조와 짧은 진입 흐름 유지. Astra 조언을 Sol에 일괄 적용해 검증 지침을 제거하지 않음 |
| [Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform), 2026-08-19 · 블로그 | 하네스는 맥락·도구·진행·오류·권한·대화 상태를 관리하는 실행 체계 | 제공 Codex를 활용하고 준비 키트는 지침·로컬 검사에 집중 |
| [Iterating Development Workflows with Codex](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex), 2026-08-03 · Cookbook | 목표·맥락·계획·관찰 기록을 구분하며 제시된 파일명은 선택적 관례 | 기존 작업 기록을 유지하고 재개 시 바뀐 부분·최근 검증·다음 행동만 확인 |
| [Build skills](https://learn.chatgpt.com/docs/build-skills), 조회일 기준 문서 | 한 역할에 집중, 분명한 입출력, 설명과 실제 호출 상황을 대조 | 스킬마다 적용 조건과 역할 구분. 합성 사례에서 적용·비적용과 미검증 표시 확인 |
| [Get started with Promptfoo](https://developers.openai.com/api/docs/guides/promptfoo-codex), 조회일 기준 문서 | 같은 사례·판정 기준으로 변경 전후 비교하고 실패·지연도 확인 | 독립 기대값과 고정 입력으로 수정 효과 확인. 개인 API 키가 필요한 예제 도구는 시험에 추가하지 않음 |

위 자료에서 배운 원칙을 우리 작업에 적용한 판단은 다음과 같다.

- **완료 기준을 먼저 적는다.** [요청문 다섯 칸](../prompts/README.md#직접-요청문을-쓰는-다섯-칸)에 목표·자료·제약·검증·진행 범위를 정리했다. 이 다섯 칸 자체가 OpenAI의 공식 양식은 아니다.
- **미확인과 임시 가정을 구분한다.** 답변이 없는 기준을 채택한 결정처럼 기록하지 않는다. 중요한 분모·재검 조건은 확인하고 확정된 작업부터 진행한다.
- **읽은 자료의 역할을 구분한다.** CSV 자유텍스트·로그·검색 결과 안의 명령을 작업 지시로 승격하지 않는다. 합성 사례에서 발견한 지침 공백을 SCENARIO에 보완했다.
- **판정 근거를 실제 파일로 남긴다.** v1.2.2의 실행기는 판정에 사용한 출력 끝부분도 보존한다. 여러 테스트 요약이 섞이면 마지막 성공만 고르지 않고 모호함을 표시한다.
- **재개할 때 반복을 줄인다.** 이미 확인한 요구·업무 답·단계를 다시 처음부터 수행하지 않고 현재 단계에 필요한 자료만 읽는다.

코드의 회귀 테스트와 개발 세션의 스킬 적용 검토는 [검증 기록](VALIDATION.md)에 구분했다. 실제 Cofa·제공 Sol의 행동 품질과 시간·합격 가능성을 측정한 것은 아니다. SDK·API 키·권한 설정·Git Push 같은 공식 예제의 실행 방법은 이번 시험 조건과 별도로 판단하며 가져오지 않는다.

## 과제에 맞는 도구 선택

| 실제 필요 | 쓰는 도구 | 선택 이유 |
| --- | --- | --- |
| 파일·코드 조사, 기존 테스트·타입/빌드 검사 | 제공 Codex와 기존 프로젝트 터미널 명령 | 새 filesystem·shell MCP와 역할 중복을 만들지 않음 |
| 구조·CSV·검사 수율·I-MR·키 관계·선택 파일 변경 확인 | 현재 CLI, 필요할 때만 로컬 MCP 6개 | 추가 계정 없이 같은 작업 환경에서 읽기 전용 검사 |
| 분류·회귀 모델을 실제 학습·평가 | 조건부 `cofa-model-eval`과 제공된 프로젝트 스택 | 업무 기준·분할·기준선을 확인한 뒤 실제 지표로 비교 |
| 실제 화면 점검 | 사람이 Cofa Browser 사용 | PDF의 Computer Use 금지와 수동 확인 안내 적용 |
| SQL·XLSX·예측 모델 | 실제 파일·목표·제공 의존성이 확인된 뒤 선택 | 문제가 나오기 전 DB·모델·RAG·대시보드를 고정하지 않음 |
| 공개 기술 문서 참고 | 제공 환경에서 시험 내용을 빼고 일반 질의 | 원격 MCP·외부 AI로 과제 파일을 전송하지 않음 |

스킬은 필요한 시점에 지침을 읽는 방식으로 사용한다. [OpenAI 스킬 문서](https://learn.chatgpt.com/docs/build-skills)와 현재 로컬 탐색 확인을 참고했지만, Cofa 제공 버전의 자동 탐색은 별도 검증 대상이다. 기본 경로는 파일 직접 읽기를 사용해 탐색·등록 문제에 덜 의존하도록 했다.

참가자는 사전 체험에서 초기 Codex CLI와 MCP 설정의 `mcpServers` 최상위 이름을 확인했다. 실제 주제·요구 파일명·채점 가중치·MCP의 전체 필드와 HTTP 지원·플러그인 지원·설정 유지 여부·본선 진출 점수는 아직 확인되지 않았다. 도구 개수나 타 저장소와의 비교로 진출을 보장하지 않는다. 준비가 끝났는지는 **실제 요구를 설명하고, 실행 결과를 확인하고, 한계를 본인이 말할 수 있는지**로 점검한다.

추가 도구 검토에서는 [OpenAI Docs MCP](https://developers.openai.com/learn/docs-mcp)를 일반 공개 질의용 선택 후보로 정리했다. Context7는 [공식 데이터 처리](https://context7.com/docs/security/data-privacy)와 인증 흐름을 고려해 기본 구성에서 제외했다. 공식 CLI의 플러그인 지원과 Cofa의 실제 허용·동작을 구분하며, 연결 예제·후보별 판단은 [MCP·플러그인 안내](MCP-PLUGINS.md)에 모았다. 실제 서버·플러그인을 새로 연결하거나 시험 자료를 전송한 검사는 아니다.

이후 참가자의 도구 자동 선택 요청에 맞춰 `--mcp-json --with-openai-docs`로 로컬·공식 문서 두 서버의 설정 후보를 함께 출력하도록 했다. 기본 생성은 여전히 로컬 서버만 포함한다. 공식 본문의 endpoint·Streamable HTTP·공개 문서 검색/읽기 범위와 [인증 불필요 안내](https://developers.openai.com/api/docs/guides/tools-connectors-mcp#authentication)를 재확인했다. [SCENARIO](../prompts/SCENARIO.md#필요한-스킬과-mcp-도구-고르기)에 실제 자료·선행 조건·연결 상태에 따른 스킬/MCP 선택 기준을 넣었다. 이는 준비된 도구를 필요할 때 고르는 설계이며, 임의의 외부 서버 연결·시험 자료 전송·모든 도구 호출을 허용하는 변경이 아니다.
