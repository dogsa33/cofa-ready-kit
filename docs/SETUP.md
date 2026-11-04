# 설치와 연결

[시험 첫 화면](../README.md) · [전체 문서 지도](INDEX.md)

**선택형 고급 설정 문서다.** 이번 시험의 기본 흐름은 [README의 시작 요청](../README.md#2-제공-codex에-시작-요청-보내기)으로 필요한 지침 파일을 직접 읽는 방식이며 설치·MCP 등록이 필요하지 않다. 스킬 이름 호출 또는 로컬 검사 도구가 실제로 필요할 때 아래 항목을 사용한다.

사전 체험의 **초기 CLI·`mcpServers` 입력칸**, 추가 문서 MCP·플러그인 후보를 따라 확인하려면 [MCP·플러그인 안내](MCP-PLUGINS.md)를 사용한다. 설치와 연결을 자동으로 완료했다는 뜻은 아니다.

## 1. 시험 전 개인 PC에서 확인

저장소 폴더에서 PowerShell로 실행합니다.

```powershell
python scripts/cofa.py doctor
python -m unittest discover -s tests -v
python scripts/cofa.py profile examples/defects.csv
```

Python 3.10 이상이 필요합니다. 프로젝트를 열고 `skills/`의 필요한 `SKILL.md`를 읽도록 요청하는 방식은 Python 없이도 가능합니다. 시험 전 로컬 환경 성공이 Cofa 환경의 도구 허용이나 연결 성공을 증명하지는 않습니다.

## 2. 시험 당일 Cofa 작업 공간에 가져오기

먼저 과제 README, 기존 파일, 현재 경로를 확인합니다. 아래는 직접 설치를 선택했고 제공 터미널이 Bash 계열이며 `.cofa-kit`이 아직 없을 때의 예시입니다. 이미 있으면 [기존 폴더 처리](MANUAL.md#4-3-cofa-kit이-이미-있는-경우)를 먼저 따릅니다.

```bash
pwd
ls -la
git clone --depth 1 https://github.com/ripplelover/cofa-ready-kit.git .cofa-kit
python3 .cofa-kit/scripts/install.py --workspace . --dry-run
python3 .cofa-kit/scripts/install.py --workspace .
python3 .cofa-kit/scripts/cofa.py doctor
```

`--dry-run`은 복사 예정만 표시합니다. 동일한 스킬이면 두 번째 설치는 건너뛰고, 다른 내용이 이미 있으면 중단합니다. 기존 스킬을 덮어쓰거나 삭제하지 않습니다. 설치된 위치는 `.agents/skills/cofa-*/SKILL.md`입니다.

`python3`이 없다면 `python --version`을 확인합니다. 둘 다 없다면 환경을 무리하게 재설정하지 말고 제공 Codex에 `.cofa-kit/skills/…/SKILL.md`를 직접 읽게 하세요. 핵심은 스킬의 작업 방식이며 CLI 설치는 필수가 아닙니다.

Clone이 차단되면 다른 도메인·프록시·터널로 우회하지 않습니다. Cofa Helper로 사용법을 확인하고 반복 오류는 문제 신고로 접수합니다. 키트가 없어도 README, 제공 Codex, 기본 셸로 과제를 진행할 수 있습니다.

## 3. 제공 Codex에서 스킬 쓰기

```text
codex
/status
/model
```

`codex`는 터미널 명령이고, 나머지는 Codex 입력란 명령입니다. `/model`에서 **실제 제공 목록의 허용 모델**을 고릅니다. PDF 표기상 권장은 Sol 6.1, Terra 5.6, Luna 6, Sol 6.0입니다. 공개 OpenAI 모델명과 대회 표기를 임의로 바꾸거나 인터넷의 모델 ID를 강제로 입력하지 마세요.

기본 운영 제안은 Sol 6.1이 제공된다면 주 작업에 사용하고, 짧은 분류·요약처럼 범위가 작은 일은 환경에서 허용하는 가벼운 모델을 고려하는 것입니다. 대회 환경별 성능·지연을 측정한 결과는 아닙니다. 첫 요청의 실제 지연과 오류를 보고 판단하세요. 고난도 검토에만 더 많은 추론 시간을 쓰고, 모델을 자주 갈아타며 문맥을 잃지 마세요.

Codex CLI에서는 `$cofa-triage`처럼 명시적으로 호출할 수 있습니다. 이미 열린 세션에 스킬 목록이 즉시 반영되는지는 제공 버전에 따라 확인합니다. 목록에 없으면 **파일 경로로 읽게 하는 방식이 가장 간단한 대안**입니다. 인증 재설정·개인 로그인·개인 API 키를 추가할 필요가 없습니다.

공식 참고: [스킬 형식과 호출](https://learn.chatgpt.com/docs/build-skills). 대회 환경의 적용 방법은 제공 환경의 안내를 우선합니다.

## 4. 선택형 로컬 MCP

외부 서버 프리셋·직접 주소·기존 JSON 합치기와 플러그인 설치는 [외부 MCP·플러그인 사용법](EXTENSIONS.md)을 따른다. `doctor --check-plugins`는 Codex CLI의 설치 명령 지원만 읽고 설정을 바꾸지 않는다. 실제 설치 성공은 목록·새 대화에서 따로 확인한다.

Skill은 작업 지침이고, MCP는 AI가 호출할 수 있는 도구 연결입니다. 이 키트의 `cofa_local`은 같은 작업 환경에서 Python 프로세스로 실행됩니다. 이 로컬 서버에는 HTTP 서버, 포트 공개, 외부 계정, API 키가 없습니다. 별도로 선택하는 외부 문서 MCP는 원격 서버입니다. 버전 1.5.0의 로컬 제공 도구는 여섯 가지입니다.

**도구를 매번 직접 고를 필요는 없습니다.** MCP가 연결돼 현재 도구 목록에 나타나면 Codex가 설명과 입력 조건을 보고 필요한 도구를 선택하도록 요청할 수 있습니다. README의 시작 요청에 이 지시를 포함했습니다. 키트를 `git clone`하는 것과 MCP 연결은 별개이며, 미연결이면 CLI·기존 도구로 진행합니다. 일반적인 스킬 선택과 MCP 도구 선택 방식은 OpenAI의 [스킬 활성화](https://developers.openai.com/plugins/concepts/skills)와 [도구 호출](https://developers.openai.com/plugins/concepts/mcp-server) 문서를 확인했습니다. 실제 Cofa에서의 탐색·연결·선택 성공을 실측했다는 뜻은 아닙니다.

| 도구 | 읽는 것 | 결과 |
|---|---|---|
| `workspace_check` | 지정 작업 폴더의 요구사항 파일 | 미완료 선언·누락 파일·근거 경로 확인 |
| `profile_csv` | 지정 작업 폴더 안의 CSV | 제한된 행의 결측·중복·숫자 요약 |
| `semiconductor_yield` | 같은 검사 모집단의 집계 CSV | 그룹별 합격 수 / 검사 수, 중복 키·잘못된 수량 검사 |
| `spc_monitor` | 한 공정 조건의 시간순 계측 CSV | 고정된 과거 기준의 I-MR 관리 한계와 이후 신호 |
| `csv_join_audit` | 결합하려는 두 CSV와 각각의 키 | 키 유일성·미매칭·예상 결합 행 수. 실제 조인·합계 보존은 별도 검사 |
| `evidence_freshness` | `run --watch` 실행 기록과 추적한 파일 | 기록 당시와 현재 파일 내용 비교. 파일 동일성과 기능 성공은 별개 |

반도체 도구의 열 이름·분모·기준 구간은 실제 과제를 읽고 지정해야 합니다. 정확한 예제와 해석은 [반도체 실행 실습](SEMICONDUCTOR-WALKTHROUGH.md)을 보세요. MCP의 최대 행 수는 10,000이며 전체 결과가 너무 크면 CLI를 사용합니다.

검증 기록 비교는 [CLI 사용법](TOOLS.md#검증한-파일이-바뀌었는지-확인하기)을 따릅니다. 먼저 `run --watch`로 기존 파일을 선택해 기록한 경우만 비교할 수 있고, 추적 없는 옛 기록은 정상으로 처리하지 않습니다. 최대 파일 32개·총 32MiB이며 서버가 파일을 수정하거나 테스트 명령을 실행하지는 않습니다. `evidence_freshness`의 인수는 `result_path` 하나입니다.

여러 CSV를 결합할 때는 [조인 검사 실습](DATA-JOIN.md)을 참고하세요. 새 기능도 같은 `cofa_local` 서버에 있으므로 별도 MCP 서버를 추가하지 않습니다. 현재 세션의 도구 목록 갱신은 제공 환경 안내를 따르고, 새 도구가 보이지 않으면 같은 검사의 CLI를 사용합니다. 업데이트된 반도체 스킬과 기존 설치본이 달라 설치가 멈추면 기존 파일을 보존하고 최신 `.cofa-kit/skills/cofa-semiconductor/SKILL.md`를 직접 읽게 하세요.

v1.5.0으로 갱신할 때도 같은 원칙입니다. 현재 키트의 `skills/스킬이름/SKILL.md`를 직접 읽을 수 있습니다. 기존 설치본이 다르면 설치기는 충돌을 알리고 보존하므로 강제로 덮어쓰지 않습니다. 최신 완료 요약 지침도 현재 파일을 직접 읽으면 적용할 수 있습니다. MCP 서버 버전은 초기화 응답의 `serverInfo.version`으로 확인하며 현재 값은 `1.5.0`입니다. 실행 중인 서버의 재연결은 제공 환경의 안내를 따릅니다.

### 스킬·MCP 상태 점검

기존 `doctor`는 런타임 확인용으로 그대로 사용할 수 있습니다. 아래는 스킬·MCP 문제를 조사할 때만 쓰는 추가 옵션입니다.

```bash
python3 .cofa-kit/scripts/cofa.py doctor --workspace . --check-mcp
```

`--workspace .`만 주면 스킬을 비교하고, `--check-mcp`를 함께 주면 로컬 MCP도 점검합니다. 현재 작업 폴더를 지정하세요. Windows에서 `python`이 스토어 안내만 열면 설치된 Python 3.10+의 실제 경로나 `py -3.11`처럼 확인된 런처를 사용합니다.

| 출력 | 의미와 다음 행동 |
| --- | --- |
| `kit.skills[].status: current` | 배포 파일과 설치본 내용이 같음. 실제 Codex의 탐색 여부는 별도 확인 |
| `not_installed` | 선택형 설치가 없음. 키트의 SKILL.md를 직접 읽으면 됨 |
| `different` / `incomplete` | 내용 차이 / 파일 누락. 사용자 수정일 수 있으므로 보존하고 `source` 경로를 직접 읽기 |
| `error` | 경로·접근 오류. 연결된 경로는 읽지 않음. 오류 확인 후 기존 도구로 진행 |
| `kit.local_mcp.status: passed` | 임시 합성 CSV로 초기화·도구 6개 목록·실제 분석과 구조화 결과 확인 |
| `failed` / `not_checked` | 로컬 검사 실패 / 검사하지 않음. 실제 Cofa 연결 실패와 구분 |

종료코드 `0`은 요청한 로컬 점검에 문제가 없음, `1`은 차이·누락·검사 실패, `2`는 인수나 작업 경로 오류입니다. 차이·누락이 있어도 직접 파일 읽기로 진행할 수 있습니다. `--check-mcp`만 단독 사용하면 `--workspace` 누락 오류를 냅니다.

기존 스킬·설정·과제 데이터를 수정하지 않고 임시 자료만 생성·정리합니다. 비밀키나 원격 서버 설정을 읽지 않으며 네트워크 연결도 하지 않습니다. **실제 Cofa 클라이언트 연결·원격 Docs 연결·스킬 선택·과제 기능 성공은 별도 확인**입니다.

MCP의 JSON 결과는 `structuredContent`에도 담아 다시 문자열을 해석할 필요를 줄였습니다. 기존 텍스트 결과와 오류 상태는 유지하며 2025-03-26·2024-11-05 규격에서는 텍스트만 보냅니다. 기준: [MCP 구조화 결과](https://modelcontextprotocol.io/specification/2025-11-25/server/tools#structured-content), [버전 협상](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle#version-negotiation).

실행 명령이나 임의 코드, 파일 쓰기, 원격 요청 도구를 MCP로 노출하지 않습니다. 결과는 연결된 제공 Codex로 돌아갑니다. 제출 확정 후에는 사용하지 않습니다. 이 서버는 Cofa의 제출 상태를 조회하지 않으며 사용 중단을 자동 강제하는 장치가 아닙니다.

### Cofa MCP 탭을 사용할 때

```bash
python3 .cofa-kit/scripts/install.py --workspace . --mcp-json
```

현재 환경의 **실제 Python 경로와 실제 작업 경로**가 들어간 JSON을 출력합니다. 출력에는 `mcpServers.cofa_local.command`와 `args`가 들어갑니다. 참가자는 사전 체험에서 `mcpServers` 최상위 이름을 확인했습니다. 이는 전체 필드·HTTP 연결 지원까지 확인했다는 뜻은 아닙니다. PDF는 MCP 탭의 JSON 편집·저장을 설명합니다. 기존 `mcpServers` 안에 `cofa_local`만 추가하고, 빈 같은 구조의 설정이면 생성된 전체 JSON을 사용하세요. 실제 형식이 다르면 Cofa Helper로 확인하고 그동안 CLI를 사용합니다. 기존 설정을 지우거나 `mcpServers`를 두 번 중첩하지 마세요.

공식 문서 서버도 함께 준비하려면 위 명령 끝에 `--with-openai-docs`를 붙입니다. 로컬 `cofa_local`과 원격 `openai_docs` 두 항목을 출력할 뿐, 저장·연결·설치는 하지 않습니다. 원격 HTTP `url` 지원이 확인되고 참가자가 선택한 서버만 추가합니다. 연결 후에는 [SCENARIO의 선택 기준](../prompts/SCENARIO.md#필요한-스킬과-mcp-도구-고르기)으로 필요한 스킬·MCP 도구를 고르게 합니다. Docs 서버에는 시험 자료 없이 일반 공개 기술 질의만 보냅니다. [두 서버 구성 안내](MCP-PLUGINS.md#3-여러-서버를-준비하고-필요한-도구만-선택하기)

### 일반 Codex CLI에서 사용하는 표준 명령

제공 환경이 이 CLI 등록 방식을 안내하거나 허용할 때만 사용할 수 있는 대안입니다.

```bash
codex mcp add cofa_local -- python3 -u "$PWD/.cofa-kit/scripts/mcp_server.py" --workspace "$PWD"
codex mcp list
```

Codex 입력란에서는 `/mcp`로 상태를 확인합니다. 일반 Codex의 표준 방법을 확인한 것이며, Cofa가 이 경로를 지원한다고 보장하지 않습니다. 등록을 위해 관리자 설정이나 연결 프로세스를 수정하지 않습니다. 참고: [OpenAI MCP 설정 문서](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

연결 확인용 요청:

```text
cofa_local의 profile_csv로 .cofa-kit/examples/defects.csv를 요약해 줘.
샘플 행 수와 전체 행 수를 구분하고, 이 결과가 과제 정확성을 검증한 것은 아님을 밝혀 줘.
```

### MCP를 꼭 연결해야 하나?

아니요. 다음 CLI가 동일한 핵심 검사를 합니다.

```bash
python3 .cofa-kit/scripts/cofa.py profile .cofa-kit/examples/defects.csv
python3 .cofa-kit/scripts/cofa.py check --workspace .
```

설정에 2–3분 이상 막히면 CLI로 진행하는 것이 운영상 유리하다는 제안입니다. 연결 성공 자체가 평가 목표라는 근거는 없습니다. 설정 생성기의 기본 출력은 로컬 서버만 포함하며 원격 Docs 서버는 명시적으로 선택할 때만 추가합니다. [OpenAI Docs와 플러그인](MCP-PLUGINS.md)은 제공 환경의 지원·실제 필요·보낼 질의를 먼저 확인합니다. 여러 도구가 연결돼 있어도 현재 과제에 필요한 도구만 사용합니다.

## 5. Browser 확인

실제 과제가 웹 서비스를 요구할 때만 서버를 실행합니다. 플랫폼 내 Browser에서 포트와 경로를 지정하고 사람이 직접 기능을 확인합니다. 서버는 `0.0.0.0`에 바인딩해야 합니다. 예를 들어 기존 프로젝트가 Vite라면 프로젝트 스크립트를 확인한 뒤 `npm run dev -- --host 0.0.0.0`을 고려할 수 있습니다. 포트는 터미널이 출력한 실제 값을 사용합니다.

서버 터미널을 유지하고, 연결이 안 되면 **오류 로그 → 프로세스 생존 → 포트 → 바인딩 → 경로** 순서로 봅니다. 외부 터널·배포가 필요하지 않습니다. Browser 자동 조작을 추가하지 마세요. Computer Use 금지와 브라우저 테스트 도구의 구체적 경계가 별도 안내되지 않은 상황에서는 UI 수동 검증과 함수·API 테스트를 사용합니다.

## 6. 공개 저장소 게시와 시험 중 동작을 구분

준비 키트의 공개 게시는 **시험 전 개인 PC에서** 진행합니다. `docs/PUBLISH.md`를 보세요. 시험 중에는 공개본을 가져오기만 하고 시험 작업을 GitHub로 보내지 않습니다. 제출은 플랫폼의 제출 절차로 진행합니다.
