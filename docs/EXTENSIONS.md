# 외부 MCP와 플러그인 바로 사용하기

[첫 화면](../README.md) · [전체 지도](INDEX.md) · [검증 기록](VALIDATION.md)

외부 MCP를 추가할 수 있다는 사용자 확인을 반영해 **서버 선택·직접 주소 추가·기존 설정 합치기·플러그인 설치**를 지원한다. Cofa의 설정 화면은 참가자가 저장하고, Codex에는 연결된 도구 중 필요한 것을 고르게 한다.

## 1. 필요한 외부 MCP 고르기

일반 터미널의 실제 과제 폴더에서 실행한다. 다음은 로컬 검사 도구에 Context7과 DeepWiki를 더하는 예다.

```bash
python3 .cofa-kit/scripts/install.py --workspace . --mcp-json --mcp-preset context7 --mcp-preset deepwiki
```

출력된 `mcpServers` 항목을 Cofa MCP 탭에 추가·저장한다. 명령은 설정 후보만 출력하며 서버 연결·설정 저장·스킬 설치를 하지 않는다. 이미 있는 설정은 2번처럼 합친다.

| 옵션 값 | 서버 이름 | 도움이 되는 작업 | 공식 연결 문서 |
| --- | --- | --- | --- |
| `openai-docs` | `openai_docs` | 공개 OpenAI/Codex 문서 | [OpenAI](https://developers.openai.com/learn/docs-mcp) |
| `microsoft-learn` | `microsoft_learn` | Python·.NET·Azure 등 Microsoft Learn 문서 | [Microsoft](https://learn.microsoft.com/en-us/training/support/mcp) |
| `deepwiki` | `deepwiki` | 공개 GitHub 프로젝트의 구조·문서 읽기 | [Devin](https://docs.devin.ai/work-with-devin/deepwiki-mcp) |
| `context7` | `context7` | 라이브러리별 현재 사용법·버전별 문서 찾기 | [Context7](https://context7.com/docs/clients/codex) |

`--mcp-preset`을 반복하면 여러 서버를 선택한다. 기존 `--with-openai-docs`도 그대로 동작한다. 옵션이 없으면 로컬 서버만 출력한다. 모두 연결해야 하는 것은 아니며 실제 과제에 필요한 문서 종류로 고른다.

2026-11-04 개발 PC에서는 네 서버 모두 키 없이 초기화·도구 목록·공개 질의 호출을 확인했다. 이 관찰은 영구 무인증·무제한 이용이나 Cofa 연결을 보장하지 않는다. Context7 공식 설치는 OAuth/API 키도 안내한다. `401/403`이면 인증 조건, `429`이면 사용량 제한을 확인하고 제공 환경이 허용하는 연결 절차를 따른다. URL에 키를 붙이거나 시험 환경에 개인 API 키를 추가하지 않는다.

## 2. 원하는 주소 또는 기존 설정 사용하기

목록에 없는 서버도 HTTPS 주소로 추가할 수 있다. 아래 주소는 실제로 사용할 서버 주소로 바꾼다.

```bash
python3 .cofa-kit/scripts/install.py --workspace . --mcp-json --remote-mcp my_docs=https://docs.example.com/mcp
```

`--remote-mcp`도 반복할 수 있다. 이름은 영문자로 시작하는 영문·숫자·밑줄·하이픈 64자 이내다. `cofa_local`은 로컬 도구 이름으로 예약되어 있다. URL에는 사용자 정보·비밀키·쿼리·프래그먼트를 넣지 않는다. 인증이 필요한 서버는 클라이언트의 별도 인증 설정을 사용한다.

기존 MCP JSON을 `mcp-existing.json` 같은 로컬 파일에 보관했다면 다음으로 합친다.

```bash
python3 .cofa-kit/scripts/install.py --workspace . --mcp-json --merge-mcp mcp-existing.json --mcp-preset context7
```

원본은 수정하지 않고 합친 JSON만 출력한다. 기존 서버·상위 설정을 보존하고, 같은 이름의 설정이 다르면 오류로 알려 준다. 중복 JSON 키도 조용히 덮어쓰지 않는다. 원본 파일로 출력을 다시 리다이렉트하면 셸이 먼저 원본을 지울 수 있으므로 **입력 파일과 같은 경로에 `>`로 저장하지 않는다.** 인증 정보가 들어 있는 기존 설정과 합친 출력은 공개 저장소에 넣지 않는다.

MCP 탭 대신 Codex CLI 등록을 사용하는 환경에서는 다음처럼 한 서버씩 등록할 수도 있다.

```bash
codex mcp add microsoft_learn --url https://learn.microsoft.com/api/mcp
codex mcp add deepwiki --url https://mcp.deepwiki.com/mcp
codex mcp add context7 --url https://mcp.context7.com/mcp
codex mcp list
```

이미 같은 이름으로 등록되어 있으면 기존 항목을 먼저 확인한다. MCP 탭 방식과 CLI 방식을 중복 실행할 필요는 없다.

## 3. 이 키트를 플러그인으로 설치하기

키트에 `plugin.json`, 호환용 `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`을 포함했다. 여섯 스킬을 하나의 플러그인으로 설치할 수 있다. 외부 MCP는 1~2번에서 별도로 고르므로 플러그인 설치만으로 원격 서버를 전부 연결하지 않는다.

먼저 현재 Cofa CLI의 지원을 확인한다.

```bash
python3 .cofa-kit/scripts/cofa.py doctor --check-plugins
```

`kit.plugins.status`가 `supported`이면 설치 명령이 있다는 뜻이다. 설치 성공 여부는 아직 확인한 것이 아니다. 다음은 이미 받은 `.cofa-kit`을 등록하고 설치하는 실제 명령이다.

```bash
codex plugin marketplace add ./.cofa-kit
codex plugin add cofa-ready-kit@cofa-ready
codex plugin list --json
```

키트를 따로 받지 않은 일반 환경에서는 첫 명령을 `codex plugin marketplace add ripplelover/cofa-ready-kit --ref main`으로 바꿀 수 있다. 설치 목록에서 `cofa-ready-kit@cofa-ready`의 설치·활성 상태를 확인하고 새 대화에서 스킬을 확인한다. 기존 대화와 작업 파일을 지우지 않는다.

이 플러그인은 스킬·참조 파일을 묶는다. 시작 요청은 여전히 `.cofa-kit/README.md`에서 복사한다. `scripts/install.py`의 스킬 복사 방식과 플러그인 방식을 함께 쓰면 같은 이름의 스킬이 둘 보일 수 있으므로 한 방식을 선택한다. 이미 있는 사용자 스킬을 자동 삭제하지 않는다.

`unavailable`은 해당 CLI가 없거나 필수 명령을 지원하지 않는 경우, `failed`는 도움말 실행 오류·시간 초과다. Cofa의 CLI를 교체하지 말고 스킬 직접 읽기와 MCP 연결을 사용한다. 키트 코드로 플랫폼에 없는 플러그인 기능을 만들 수는 없다.

## 4. 다른 플러그인도 설치하고 싶다면

공식 제공자의 marketplace·플러그인 이름을 확인하고 같은 방식으로 설치한다. 예를 들어 Context7 공식 문서가 안내하는 명령은 다음과 같다.

```bash
codex plugin marketplace add upstash/context7
codex plugin add context7@context7-marketplace
```

Context7 플러그인은 문서 스킬과 hosted MCP를 묶고 OAuth 로그인을 안내한다. 위의 인증 없는 MCP 연결 검사와는 다른 설치 경로다. 제공 환경에서 해당 로그인을 허용할 때 사용하며, 본 키트에서는 이 타사 플러그인의 설치·인증을 실측하지 않았다. MCP로 이미 연결했다면 같은 연결을 중복 추가할 필요는 없다. [공식 설치 안내](https://context7.com/docs/clients/codex)

다른 플러그인도 포함된 스킬·MCP·훅과 인증 요구를 먼저 읽는다. 설치 요청이 이미 있으면 같은 범위의 준비를 반복 승인받지 않고 진행하되, 추가 로그인·권한이 필요하면 그 단계만 사용자에게 안내한다. 시험 문제·코드·로그의 외부 전송, 외부 모델에 과제 답안 요청, UI 자동 조작은 현재 과제 규칙에 따라 구분한다.

## 5. 연결된 도구를 Codex가 고르게 하기

```text
아직 제출 확정 전이야. .cofa-kit/prompts/SCENARIO.md를 읽고 진행해 줘.
연결된 로컬·외부 MCP와 설치한 플러그인 중 현재 작업에 필요한 것만 골라 써 줘.
라이브러리 문서는 Context7, Microsoft 문서는 Microsoft Learn,
공개 GitHub 문서·구조는 DeepWiki, OpenAI 문서는 OpenAI Docs를 우선 검토해 줘.
원격에는 일반 공개 기술 질의만 보내고 실제 도구 이름·입력 조건은 현재 목록에서 확인해 줘.
연결 실패나 인증 제한이 있으면 이유를 짧게 알려 주고 가능한 기존 도구로 계속해 줘.
작업이 끝나면 무엇을 왜 어떻게 했고 무엇을 확인했는지 쉬운 말로 짧게 요약해 줘.
```

DeepWiki의 문서 읽기와 AI 질의 도구는 구별한다. 문서 읽기를 우선하고 실제 문제의 해결을 외부 AI에 맡기지 않는다. 도구 이름은 버전에 따라 다를 수 있다. 제출 확정 뒤에는 AI·MCP·플러그인 사용을 중단한다.

## 참고한 공개 자료와 판단

- [Cofa 공식 소개](https://www.getcofa.com/ko/probe): 제공 환경과 작업 기록을 평가하는 플랫폼 설명. 특정 CLI 버전이나 모든 플러그인의 지원을 보증하는 자료는 아니다.
- [참가자 후기](https://velog.io/@sjyoung/SK-하이닉스-AI-해커톤-2026-2차-예선-To-Be-Continued): 2026-10-31 Cofa 이용·접속 장애 경험을 확인했다. MCP·플러그인 설치 성공을 입증하는 후기는 아니므로 호환성 근거로 쓰지 않았다.
- [bbambbubba/cofa-probe](https://github.com/bbambbubba/cofa-probe): 범용 준비 도구이며 README도 실제 Cofa 호환성은 미검증이라고 밝힌다.
- [itssosunny/cofa-loop-graph](https://github.com/itssosunny/cofa-loop-graph): 플러그인 marketplace·설치 예를 확인했다. 외부 설치 스크립트는 실행하지 않았고, 형식은 [OpenAI 공식 패키징](https://developers.openai.com/plugins/build/plugins)과 현재 CLI 도움말로 확인했다.

2026-11-04에 개발 PC의 격리된 Codex 환경에서 **우리 키트 플러그인 설치·여섯 스킬 포함**을 실제 확인했다. Cofa 안에서의 플러그인 설치는 아직 별도 확인 대상이다.
