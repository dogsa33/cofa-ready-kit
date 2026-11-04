# Cofa Ready Kit 상세 사용 설명서

> 시험 첫 화면: [README](../README.md) · 전체 문서 목차: [INDEX](INDEX.md)

**상세 참고가 필요할 때만 읽는 문서다. 시작은 README 한 곳에서 한다.** 이 문서는 설치·CLI·기록 도구의 사용법을 찾아볼 때 참고한다. README 통합 요청이 도구 준비와 필요한 스킬 읽기를 연결하며, 설치·MCP 연결이 막혀도 기존 도구로 진행한다. 키트는 실제 과제의 정답이나 완성 앱을 제공하지 않는다.

**스킬을 이름으로 호출하는 방법이 궁금할 때 [여러 스킬 사용법](SKILLS-BEGINNER.md)을 읽는다.** 터미널과 Codex 입력란 구분, 선택형 설치, 두 스킬을 한 요청에 넣는 방법을 설명한다.

**시험 당일에는 [README](../README.md)의 다운로드 → 파일 열기 → 시작 요청 순서를 따른다.** [진행·제출 상세 참고](EXAM-PLAYBOOK.md)는 화면 위치와 이후 확인 순서를 설명한다. 아래 설치·CLI 명령은 미리 연습하거나 특정 기능이 필요할 때 참고하는 선택형 상세 설명이다. 기본 진행에 설치나 MCP 연결은 필수가 아니다.

## 1. 먼저 읽는 순서와 입력 위치

CLI와 작업 기록 도구를 시험 전 직접 연습하려면 이 문서의 1–5장을 사용한다. 반도체 데이터가 실제 과제에 등장하면 [반도체 도구 실습](SEMICONDUCTOR-WALKTHROUGH.md)을 읽는다. 시험 운영은 [규칙 요약](RULES.md)과 [당일 시간표](DAY-PLAN.md), 전체 명령 옵션은 [CLI 설명](TOOLS.md)을 참고한다.

| 화면 | 입력할 내용 | 예 |
| --- | --- | --- |
| 시험 전 개인 PC의 PowerShell | Windows에서 실행할 셸 명령 | `python scripts/cofa.py doctor` |
| 시험 당일 Cofa 안의 터미널 | 제공 작업 환경의 셸 명령. 아래 실전 예제는 Bash 기준 | `python3 .cofa-kit/scripts/cofa.py doctor` |
| 터미널에서 연 Codex 입력란 | AI에게 할 자연어 요청, `/status`, `/model`, `$cofa-triage` | “README를 읽고 필수조건을 정리해 줘.” |
| Cofa 파일 편집기 | Python 코드, JSON, 문서 내용 | `requirements.json` 수정 |
| Cofa Browser | 사람이 포트·경로를 맞추고 화면 직접 조작 | 버튼 클릭, 잘못된 입력 확인 |
| Cofa 업무 메신저 | 참가자가 직접 실무자 또는 Helper에게 질문 | 업무 기준 확인 또는 제출 방법 문의 |

**`$cofa-triage`는 PowerShell 명령이 아니다.** PowerShell에 입력하면 변수로 해석될 수 있다. 먼저 터미널에서 `codex`를 실행한 뒤 Codex 입력란에 적는다. 반대로 `python3 ...`는 일반적으로 터미널 명령이다. Codex에게 그 명령을 실행해 달라고 요청할 수도 있지만, 두 입력란을 혼동하지 않는다.

## 2. 시험 전 PC에서 준비물 확인하기

### 2-1. 키트 폴더 열기

이미 다운로드한 저장소가 있다면 해당 폴더에서 PowerShell을 연다. `README.md`, `scripts`, `skills`가 있는 위치가 **키트 루트**다. 다음 명령은 그 위치에서 실행한다.

```powershell
Get-Location
Get-ChildItem
python --version
python scripts/cofa.py doctor
```

Python 3.10 이상이고 출력의 `python_supported`가 `true`인지 확인한다. `versions`에 없는 실행 프로그램은 `null`로 나올 수 있다. 시험 전 PC에 Codex CLI가 없더라도 키트의 데이터 검사와 기록 기능은 연습할 수 있다. `doctor`는 설치된 실행 파일의 버전만 확인한다. Cofa 접속, 도구 허용, 모델 응답, MCP 연결을 검증하는 명령은 아니다.

**2026-10-30 로컬 리허설에서 실제로 발견한 차이:** 이 Windows PC의 Git Bash에서는 `python3 --version`이 실패했고 `python --version`은 3.10.7을 반환했다. `python3.exe`라는 파일이 검색돼도 실행 가능한 Python이라는 뜻은 아니다. 시험 당일 제공 환경에서도 먼저 버전 명령을 실행하고, 성공한 이름을 이후 명령에 일관되게 사용한다. 이 결과는 Cofa의 Python 이름이나 운영체제를 확인한 것이 아니다.

처음 받는 경우에만, 원하는 상위 폴더에서 다음을 실행한다.

```powershell
git clone https://github.com/ripplelover/cofa-ready-kit.git
Set-Location cofa-ready-kit
python scripts/cofa.py doctor
```

### 2-2. 이미 받은 복사본 업데이트

기존 키트 폴더에서 수정 상태를 확인하고 공개 저장소의 새 버전을 가져온다.

```powershell
git status --short
git pull --ff-only
```

직접 수정한 파일이 있거나 업데이트가 거부되면 삭제·초기화·강제 덮어쓰기를 하지 않는다. 기존 복사본을 그대로 보존하고 새 폴더로 다시 받는 방법이 있다.

```powershell
git clone https://github.com/ripplelover/cofa-ready-kit.git ../cofa-ready-kit-updated
```

새 폴더를 사용한다면 이후 명령도 새 키트 경로를 기준으로 실행한다. 업데이트는 공개 준비 도구를 내려받는 동작이다. 시험 중 작업물을 보내는 `git push`와 다르다.

### 2-3. 키트 자체 검사와 데이터 요약

```powershell
python -m unittest discover -s tests -v
python scripts/cofa.py profile examples/defects.csv
python scripts/cofa.py profile examples/requests.json --format json
```

첫 명령은 **키트 코드의 테스트**다. 시험 당일 만드는 과제 결과물을 검사한 것으로 기록하면 안 된다. 운영체제의 심볼릭 링크 권한 등으로 일부 검사가 `skipped`로 표시되면 그 이유를 읽는다. 데이터 요약에서는 행 수·표본 범위·결측·중복을 보고, 열 이름만으로 데이터 의미를 단정하지 않는다.

## 3. 15분 정도로 핵심 사용 흐름 익히기

아래는 시험 전 개인 PC에서 하는 **합성 연습**이다. 짧은 함수를 만들어 `init → run → 확인 → 상태 수정 → check → report`의 연결을 익힌다. 실제 시험의 요구사항이나 제출 파일명과 무관하다.

### 3-1. 별도의 연습 작업 폴더 만들기

키트 루트의 PowerShell에서 실행한다.

```powershell
python scripts/cofa.py init --workspace work/manual-practice
python scripts/cofa.py check --workspace work/manual-practice
$LASTEXITCODE
```

`init`은 다음 파일을 만든다.

```text
work/manual-practice/
├── requirements.json
└── decision-log.jsonl
```

처음 `check`는 **종료코드 1로 실패해야 정상**이다. 아직 실제 요구사항으로 바꾸지 않았고 완료 선언이나 증거도 없기 때문이다. `init`을 다시 실행하면 기존 파일을 덮어쓰지 않으려고 종료코드 2로 중단한다. 다시 연습하려면 `work/manual-practice-2`처럼 새 경로를 사용한다.

### 3-2. 합성 요구사항을 적기

편집기로 `work/manual-practice/requirements.json`을 열어 다음 내용으로 수정하고 저장한다. 이는 방금 만든 연습 파일이므로 변경해도 된다. 실제 과제의 기존 파일을 같은 이유로 덮어쓰지는 않는다.

```json
{
  "required_files": ["counter.py", "tests/test_counter.py"],
  "criteria": [
    {
      "id": "R1",
      "requirement": "None과 빈 문자열·공백 문자열을 제외한 값의 개수를 센다. 숫자 0과 False는 존재하는 값이다.",
      "priority": "must",
      "status": "todo",
      "evidence": []
    }
  ]
}
```

필드의 뜻은 다음과 같다.

| 필드 | 무엇을 적는가 |
| --- | --- |
| `required_files` | 해당 작업 폴더를 기준으로 반드시 있어야 하는 파일 경로 |
| `id` | 기록과 테스트를 연결할 고유한 이름. 예: `R1`, `R2` |
| `requirement` | 관찰 가능한 완료 조건과 중요한 경계값 |
| `priority` | `must`, `should`, `could` 중 하나 |
| `status` | `todo`, `in_progress`, `verified`, `blocked` 중 하나 |
| `evidence` | 실제로 존재하는 구현·검증 파일의 작업 폴더 기준 상대 경로 |

`../`로 작업 폴더 밖을 가리키거나 절대 경로를 넣지 않는다. 이 예제의 `counter.py`는 키트 루트가 아니라 **`work/manual-practice/counter.py`**를 의미한다.

### 3-3. 작은 구현과 실제 테스트 파일 만들기

편집기에서 `work/manual-practice/counter.py`를 만들고 저장한다.

```python
def count_present(values):
    return sum(
        value is not None
        and (not isinstance(value, str) or bool(value.strip()))
        for value in values
    )
```

`work/manual-practice/tests` 폴더를 만든 뒤 그 안에 `test_counter.py`를 만들고 저장한다.

```python
import unittest
from counter import count_present


class CountPresentTests(unittest.TestCase):
    def test_missing_and_nonempty_values(self):
        self.assertEqual(count_present([None, "", "  ", "A"]), 1)

    def test_zero_and_false_are_present(self):
        self.assertEqual(count_present([0, False, "0"]), 3)

    def test_empty_input(self):
        self.assertEqual(count_present([]), 0)
```

세 검사는 빈값 처리, 흔한 `if value` 오류, 빈 입력을 각각 확인한다. 단지 파일이 존재하는지만 검사하지 않는다. 실제 과제에서는 이 코드를 가져다 답안으로 쓰는 것이 아니라, **해당 과제의 요구를 확인하는 테스트를 따로 만든다.**

### 3-4. 실제 검사 실행을 증거로 남기기

계속 **키트 루트의 PowerShell**에서 실행한다.

```powershell
python scripts/cofa.py run --workspace work/manual-practice --id R1 --timeout 30 -- python -m unittest discover -s tests -v
```

여기에서 헷갈리기 쉬운 부분은 `tests`의 기준이다. `run`은 `--workspace`에 지정한 폴더로 이동한 상태에서 `--` 뒤의 명령을 실행한다. 따라서 이 명령은 키트의 `tests`가 아니라 **`work/manual-practice/tests`**를 검사한다.

정상 실행에서는 출력에 `ok: true`, `exit_code: 0`, `timed_out: false`가 표시된다. 출력의 `evidence_directory`가 실제 기록 폴더다. 그 아래에 `result.json`, `stdout.txt`, `stderr.txt`가 생기며 `decision-log.jsonl`에도 검사 기록이 추가된다. `unittest`의 결과는 `stderr.txt`에 기록될 수 있다. stderr에 글자가 있다는 이유만으로 실패라고 보지 말고 종료코드와 검사 결과를 함께 읽는다.

`run`은 `status`를 자동 변경하지 않는다. 이어서 검사하면 아직 실패하는 것이 정상이다.

```powershell
python scripts/cofa.py check --workspace work/manual-practice
$LASTEXITCODE
```

출력의 `issues`에 미완료 필수조건이 남고 종료코드는 1이다. 이는 테스트 실행 성공과 요구사항 검토를 구분하기 위한 동작이다.

### 3-5. 결과를 읽은 뒤에만 완료 상태로 바꾸기

방금 실행한 `result.json`과 검사 출력을 읽고 세 테스트가 실제로 실행·통과했는지 확인한다. 구현도 요구사항과 비교한다. 확인한 뒤 `requirements.json`의 R1만 다음과 같이 수정한다.

1. `status`를 `verified`로 바꾼다.
2. `evidence`에 `counter.py`, `tests/test_counter.py`를 넣는다.
3. 방금 출력된 `evidence_directory` 뒤에 `/result.json`을 붙인 **실제 경로**도 추가한다. 예를 들어 출력이 `evidence/20261030T000000Z-ab12cd34`였다면 `evidence/20261030T000000Z-ab12cd34/result.json`이다. 이 예시 시각·문자열을 그대로 복사하지 않는다.

실패했거나 아직 읽지 않은 결과를 `verified`로 바꾸지 않는다. Codex에게 갱신을 맡길 때도 “방금 실행한 R1 검증 결과를 읽고, 통과 범위를 확인한 뒤 그 실제 증거 경로만 연결해 줘”처럼 범위를 정한다.

### 3-6. 판단과 보고서 만들기

```powershell
python scripts/cofa.py log --workspace work/manual-practice --kind decision --summary "None과 공백 문자열을 누락으로 취급하고 0과 False는 유효한 값으로 유지했다." --evidence counter.py tests/test_counter.py
python scripts/cofa.py check --workspace work/manual-practice
$LASTEXITCODE
python scripts/cofa.py report --workspace work/manual-practice --output work/manual-practice/evidence-summary.md
```

이제 `check`는 `ok: true`, 종료코드 0을 반환해야 한다. 보고서는 `work/manual-practice/evidence-summary.md`에 생긴다. 같은 `--output` 경로로 다시 쓰면 덮어쓰기 방지 때문에 종료코드 2가 난다. 갱신본은 `evidence-summary-2.md`처럼 새 경로로 저장하거나, 검토 후 편집기로 기존 문서를 수정한다.

**`check` 통과는 구조 확인이다.** 파일과 근거 경로가 있고 완료로 선언됐다는 뜻이지, 코드가 모든 입력에서 정확하다는 보증은 아니다. `report` 역시 기록을 정리할 뿐 그 내용을 독립적으로 증명하지 않는다.

## 4. 시험 당일 Cofa 작업 공간에 가져오기

이 절의 Bash 명령은 **Cofa가 제공한 터미널**에서 실행한다. 시험 전 PC에서 실행해 둔 것과 별개다. 필요한 외부 자료는 제공된 AI를 통해 가져오며, 개인 파일 업로드나 외부 브라우저 직접 접근에 의존하지 않는다. 아래 명령을 제공 Codex에 실행해 달라고 요청해도 된다.

### 4-1. 현재 과제 루트 확인

```bash
pwd
ls -la
```

과제 README와 제공 파일이 있는 폴더인지 확인한다. 이후 `--workspace .`의 `.`은 이 **과제 루트**를 뜻한다. `.cofa-kit`은 도구를 내려받는 하위 폴더이며 제출물 작업 폴더가 아니다.

```text
현재 과제 루트/
├── README.md                  실제 과제 안내
├── 제공된 데이터·코드/...       실제 과제 파일
├── .cofa-kit/                 공개 준비 키트
│   ├── scripts/cofa.py
│   └── skills/...
├── .agents/skills/...         선택한 설치 방식으로 복사된 스킬
├── requirements.json          충돌 없을 때 생성하는 개인 보조 기록
└── decision-log.jsonl          개인 보조 기록
```

위의 보조 기록 파일은 공식 제출 양식이 아니다. 공식 파일명과 제출 형식은 실제 과제 안내를 따른다.

### 4-2. 처음 가져오는 경우

```bash
git clone --depth 1 https://github.com/ripplelover/cofa-ready-kit.git .cofa-kit
python3 .cofa-kit/scripts/cofa.py doctor
python3 .cofa-kit/scripts/install.py --workspace . --dry-run
python3 .cofa-kit/scripts/install.py --workspace .
```

`python3`이 없으면 `python --version`으로 3.10 이상인지 확인한 뒤 명령의 `python3`을 `python`으로 바꾼다. 둘 다 없으면 제공 환경을 무리하게 바꾸지 말고 스킬 파일을 직접 읽게 하는 방식으로 진행한다.

### 4-3. `.cofa-kit`이 이미 있는 경우

기존 폴더에 다시 `git clone`하지 않는다. 먼저 상태를 읽고 공개본 업데이트를 가져온다.

```bash
git -C .cofa-kit status --short
git -C .cofa-kit pull --ff-only
python3 .cofa-kit/scripts/install.py --workspace . --dry-run
python3 .cofa-kit/scripts/install.py --workspace .
```

`git pull --ff-only`는 공개 준비 도구를 내려받는 동작이며 시험 작업을 업로드하는 명령이 아니다. 충돌이나 로컬 수정으로 업데이트가 실패하면 `reset --hard`, 파일 삭제, 강제 덮어쓰기를 하지 않는다. 도구 없이 진행하거나 기존 폴더를 보존한 채 별도 이름으로 공개본을 받는다. 예: `.cofa-kit-v2`. 이 경우 직접 읽기·CLI 경로도 모두 그 이름으로 바꾼다.

설치기는 내용이 같은 기존 스킬을 유지하고 없는 스킬만 추가한다. 반도체 스킬이 새로 추가된 업데이트라면 기존 네 스킬을 그대로 두고 새 스킬을 복사할 수 있다. **기존 스킬 내용과 다르면 설치를 중단한다.** 사용자 수정이나 이전 버전을 자동 덮어쓰지 않는 동작이다. 시간을 들여 수동 병합하는 대신 다음 직접 읽기 요청을 사용할 수 있다.

```text
.cofa-kit/skills/cofa-triage/SKILL.md를 읽고 현재 과제에 적용해 줘.
기존 .agents/skills의 파일은 수정하거나 덮어쓰지 마.
```

Clone이나 공개본 다운로드가 차단되면 다른 접속 경로로 우회하지 않는다. Helper 또는 문제 신고로 확인하고 기본 제공 Codex로 과제 작업을 계속한다.

## 5. 실전에서 전체 흐름 사용하기

### 5-1. 제공 Codex 열기와 첫 요청

터미널에 다음을 입력한다.

```bash
codex
```

그다음 **Codex 입력란**에서 `/status`, `/model`을 실행해 실제 제공된 모델을 확인한다. 공식 안내의 허용 모델을 고르고 Astra나 개인 AI 연결을 추가하지 않는다. 모델 ID를 인터넷에서 찾아 강제로 입력할 필요가 없다.

```text
$cofa-triage
현재 과제 README와 제공 파일부터 읽어 줘.
사용자 문제, 필수 제출물·경로, 완료 기준, 제약을 출처와 함께 정리해 줘.
명시된 사실과 가정을 구분하고 답에 따라 구현이 달라지는 질문만 골라 줘.
실무자에게는 내가 직접 질문할게. 확정된 부분의 점검은 진행해 줘.
내 남은 시간은 응시 화면 기준으로 [직접 확인한 값]분이다.
```

`[직접 확인한 값]`은 실제 숫자로 바꾼다. 첫 답변에서 필수 제출물과 목표가 맞는지 본인이 확인한다. 틀린 문제 정의를 그대로 둔 상태에서 코딩 속도만 높이지 않는다.

### 5-2. 보조 기록 초기화

과제 루트에 `requirements.json`, `decision-log.jsonl`이 없는지 확인한 뒤 일반 터미널에서 실행한다.

```bash
python3 .cofa-kit/scripts/cofa.py init --workspace .
```

생성된 예시 R1을 실제 README에서 확인한 조건으로 바꾼다. `required_files` 역시 실제 과제의 필수 경로로 작성한다. 질문에 대한 실무자 답변과 가정은 구분해 기록한다.

```text
방금 만든 requirements.json을 실제 과제 README 기준으로 채워 줘.
각 조건에 확인 가능한 동작이나 값, 필수 여부를 적고 아직은 todo로 둬.
공식 제출 파일명은 README의 요구를 따르고 임의 파일명을 강제하지 마.
```

**파일명 충돌이 있으면:** 기존 파일을 보존한다. `check`와 `report`는 별도로 만든 `cofa-requirements.json`을 `--manifest cofa-requirements.json`으로 읽을 수 있다. 그러나 현재 `run`은 `requirements.json`에 있는 ID를 사용하며, `report`는 별도 manifest를 지정해도 `decision-log.jsonl`을 키트의 기록 형식으로 읽는다. 기존 `decision-log.jsonl`이 다른 용도의 파일이면 `report`까지 호환된다고 가정하지 않는다. 이 경우 `check`만 별도 manifest로 사용하거나 일반 터미널로 과제 테스트를 실행하고 기존 과제의 기록 형식에 결과를 남긴다. 기존 파일을 키트 형식으로 바꾸거나 지우지 않는다. 보조 도구를 쓰기 위해 과제 구조를 바꿀 필요는 없다.

### 5-3. 구현과 검증을 작은 단위로 연결

```text
$cofa-build
가장 중요한 미충족 필수조건 하나를 입력부터 출력까지 연결해 줘.
기존 스택과 실행법을 유지하고, 완료 후 그 조건을 확인하는 검사를 실행해 줘.
무엇을 만들었는지와 실제로 무엇을 검증했는지를 구분해서 알려 줘.
```

검사 명령은 과제 스택에 맞게 선택한다. 다음은 **과제 루트에 실제 Python 테스트 폴더가 있을 때만** 쓰는 예다.

```bash
python3 .cofa-kit/scripts/cofa.py run --workspace . --id R1 --timeout 60 -- python3 -m unittest discover -s tests -v
```

과제가 JavaScript이고 `package.json`에 일회성 `test` 스크립트가 있다면 그 실제 명령을 선택한다. 테스트 실행기가 watch 모드로 계속 떠 있는 명령이나 개발 서버를 `run`에 넣지 않는다. `run` 자체는 셸을 추가하지 않는다. 하지만 명령줄에 그대로 쓴 `|`, `>`, `&&`는 바깥 PowerShell·Bash가 먼저 처리할 수 있으므로 위 명령 뒤에 붙이지 않는다. 복잡한 검사는 명시적인 작은 검사 스크립트로 정리하고 그 파일을 실행한다.

검사 후 증거를 읽고 해당 조건만 `verified`로 바꾼다. 핵심 화면은 사용자가 플랫폼 Browser에서 직접 확인하고 사실대로 기록한다. 자동 Browser 조작은 사용하지 않는다.

### 5-4. 실제 판단 기록

```bash
python3 .cofa-kit/scripts/cofa.py log --workspace . --kind assumption --summary "집계 단위가 미확정이므로 실무자에게 확인할 예정이다."
```

위 문장은 **실제로 그런 상황일 때만** 기록한다. 확인을 받았다면 답변 내용과 그에 따른 선택을 `decision`으로 남긴다. 기록을 만들기 위해 하지 않은 질문·판단·실패를 꾸미지 않는다.

### 5-5. 제출 전 점검

```bash
python3 .cofa-kit/scripts/cofa.py check --workspace .
python3 .cofa-kit/scripts/cofa.py report --workspace . --output cofa-evidence-summary.md
```

보고서의 출력 경로는 **현재 터미널 위치 기준**, manifest 안의 파일 경로는 **`--workspace` 기준**이다. 두 기준을 기억한다. `check`의 `issues`를 읽고 필수 파일 누락·빈 파일·미완료·없는 증거 경로를 수정한다. `warnings`는 선택 조건의 남은 문제일 수 있으며 무시하고 완료로 꾸미지 않는다.

```text
$cofa-verify
실제 과제 안내와 현재 파일을 비교해 제출 전 누락을 점검해 줘.
필수 실패와 실제 미검증 항목을 먼저 알려 주고 남은 시간 안에 최소 수정해 줘.
보고서가 코드와 실행 결과에 맞는지도 확인해 줘.
내가 직접 Browser와 저장 상태를 확인할 항목을 짧게 알려 줘.
제출 버튼은 내가 직접 누를게.
```

최종 제출 문서는 실제 과제의 요구 형식으로 정리한다. 키트 보고서 파일을 만들었다는 이유만으로 공식 제출물이 완성된 것은 아니다. 저장 충돌을 해결하고 필수 파일 경로와 저장 완료를 확인한다. 제출 확정 뒤에는 파일을 수정할 수 없다.

## 6. 반도체 데이터 도구는 언제 쓰는가

실제 과제에 수율·불량·설비·공정 측정 자료가 있을 때 [반도체 실습](SEMICONDUCTOR-WALKTHROUGH.md)과 [반도체 요청문](../prompts/SEMICONDUCTOR.md)을 사용한다. 반도체 해커톤이라는 이유만으로 모든 과제에 SPC나 수율 계산을 붙이지 않는다.

현재 도구는 선택한 검사 모집단의 개수 기준 통과율 집계와 고정 기준 구간을 사용하는 I-MR 점검을 지원한다. 전체 제조·출하 수율을 자동 계산하는 기능은 아니다. 합성 예제로 CLI를 익힌 다음 실제 데이터의 열·단위·기간·집계 수준이 맞는지 확인한다. 도구 출력은 원인 확정, 제품 합격 판정, 공식 채점 결과가 아니다.

## 7. MCP는 선택해서 연결하기

MCP를 연결하지 않아도 위 CLI로 모든 기본 흐름을 진행할 수 있다. 필요한 경우 다음 명령으로 **현재 환경에 맞는 JSON**을 출력한다.

```bash
python3 .cofa-kit/scripts/install.py --workspace . --mcp-json
```

정확한 연결 절차는 [SETUP의 MCP 설명](SETUP.md#4-선택형-로컬-mcp)을 따른다. Cofa 탭의 형식이 출력 JSON과 같은지 확인하고 기존 설정을 보존하며 필요한 항목만 추가한다. 형식이 다르거나 연결이 반복 실패하면 CLI로 계속 진행한다. 연결 오류를 우회하려고 개인 키·외부 AI·별도 프록시를 추가하지 않는다.

공개 OpenAI 문서 서버도 준비하려면 위 명령에 `--with-openai-docs`를 붙인다. 원격 HTTP 지원·규칙을 확인한 뒤 두 서버를 연결하는 [상세 절차](MCP-PLUGINS.md#3-여러-서버를-준비하고-필요한-도구만-선택하기)를 따른다. 연결 뒤 README의 시작 요청을 보내면 스킬·도구를 과제에 맞게 선택한다. 원격 문서 질의에는 시험 자료를 포함하지 않는다.

로컬 MCP는 지정 작업 폴더 안의 검사·요약 도구다. `workspace_check`, `profile_csv`와 반도체 도구가 연결 목록에 실제로 보이는지 확인한 다음 요청한다. CLI 테스트가 성공했다고 실제 Cofa MCP 연결이 성공했다고 말할 수는 없다.

## 8. 시간에 따라 무엇을 요청할까

아래는 준비 키트의 운영 제안이다. 공식 타이머와 실제 과제의 필수조건을 우선한다.

| 남은 과제 시간 | 우선할 요청 | 피할 일 |
| --- | --- | --- |
| 약 180–160분 | README·파일 조사, 요구사항, 중요한 업무 질문 | 실제 문제를 읽기 전 스택·대시보드 결정 |
| 약 160–100분 | 핵심 입력→결과 흐름 구현, 작은 검증 | 기능을 많이 벌리고 하나도 끝내지 않기 |
| 약 100–45분 | 필수조건 확장, 집계·예외·통합 검증 | 이미 확인된 부분의 반복 설명과 재작성 |
| 약 45–25분 | 실패 수정, 누락된 증거와 사용법 정리 | 새 라이브러리·새 MCP·새 인프라 추가 |
| 약 25–10분 | 최종 점검, 본인의 선택·한계 이해 | 하지 않은 검증을 완료로 선언 |
| 마지막 10분 | 저장·필수 경로·제출 미리보기 확인 | 큰 구조 변경 |

짧고 좋은 요청은 **목적 + 범위 + 완료 조건 + 확인 방법**이 들어 있다. 예: “R2의 날짜 경계 처리를 수정하고 마지막 날 데이터가 포함되는 사례와 다음 날 제외 사례를 실행해 줘.” 대화가 길어졌으면 [RESUME](../prompts/RESUME.md), 같은 오류가 반복되면 [RESCUE](../prompts/RESCUE.md)를 사용한다.

본인 설명 연습은 제출 확정 전에 [PRACTICE](../prompts/PRACTICE.md)로 한다. AI가 먼저 모범답안을 쓰게 하지 말고 본인이 선택 이유·검증·한계를 설명한다. **실제 후속 서술형에서는 AI·Skill·MCP를 사용하지 않고 직접 답한다.**

## 9. 자주 만나는 오류와 복구

| 증상 | 뜻과 다음 행동 |
| --- | --- |
| `can't open file .../scripts/cofa.py` | 현재 위치 또는 키트 경로가 다르다. `pwd`/`Get-Location`과 파일 목록부터 확인한다. |
| `python3: command not found` | `python --version` 확인 후 지원 버전이면 명령만 바꾼다. 개인 AI 인증을 추가하지 않는다. |
| `Refusing to overwrite existing file` | 기존 파일 보호 동작이다. 연습이면 새 폴더, 결과 출력이면 새 파일명을 사용한다. |
| `existing skill differs` | 이미 설치한 스킬의 내용이 다르다. 삭제·덮어쓰기 없이 최신 키트의 `SKILL.md` 직접 읽기를 사용한다. |
| `--id must identify a criterion` | 그 `--workspace`의 `requirements.json`에 ID가 없다. 작업 폴더와 ID를 확인한다. |
| `Ran 0 tests`, `no tests collected`, 전부 skipped | 실질적인 검증이 아니다. 실제 과제 테스트 경로와 테스트 파일 이름을 확인한다. |
| 명령은 성공했는데 `check` 실패 | `run`은 상태를 자동으로 바꾸지 않는다. 실제 결과를 확인하고 상태·근거·필수 파일을 점검한다. |
| UTF-8 디코딩 오류 | 원본 인코딩을 확인한다. 한글 Windows CSV라면 `--encoding cp949`가 맞는지 검토한다. 임의로 문자를 버리지 않는다. |
| 표본만 읽었다는 출력 | `--max-rows` 범위 안의 요약이다. 전체 결과인 것처럼 해석하지 않는다. |
| 근거 파일 경로가 없다는 오류 | 경로는 키트 위치가 아니라 `--workspace` 기준이다. 실제 `evidence_directory`를 사용한다. |
| MCP 오류 | 같은 기능을 CLI에서 실행한다. 연결 실패와 데이터 입력 오류를 구분한다. |
| Browser가 안 열림 | 서버 오류 → 실행 유지 → 실제 포트 → `0.0.0.0` → 경로 순서로 본다. 서버 탭을 유지한다. |
| 플랫폼·감독 반복 오류 | 발생 시각·단계·직전 동작·오류 문구로 문제 신고한다. 타이머가 정지된다고 가정하지 않는다. |

`check` 종료코드는 0=구조 통과, 1=미완료·누락, 2=잘못된 입력·경로다. `run`은 0=실행 관찰상 성공, 1=실패·시간 초과·인식된 무효 테스트, 2=입력 오류다. 종료코드 확인은 PowerShell에서 `$LASTEXITCODE`, Bash에서 직후 `echo $?`를 사용한다.

## 10. 사용 준비가 됐는지 직접 확인

- 시험 전 합성 연습에서 처음 `check` 실패와 실제 검증 후 통과를 모두 확인했다.
- 키트 루트와 과제 루트, 터미널과 Codex 입력란을 구분한다.
- 실제 과제 파일명은 README에서 찾고, 키트의 예시 이름을 강제하지 않는다.
- Skill 자동 발견이 안 되면 파일 경로로 읽게 할 수 있다.
- MCP가 없어도 CLI로 계속 작업할 수 있다.
- 무엇을 구현했고 무엇을 실제 검증했는지 자기 말로 설명할 수 있다.
- 제출 확정과 최종 완료가 다른 단계이며, 후속 서술형에서는 AI를 사용하지 않는다.

규칙 근거는 [RULES.md](RULES.md), 설치 세부 사항은 [SETUP.md](SETUP.md), 지원 옵션과 제한은 [TOOLS.md](TOOLS.md)에 모아 두었다. 실제 시험 당일 공지와 과제 안내가 우선한다.
