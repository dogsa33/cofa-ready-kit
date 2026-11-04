# CLI 사용 예제

[시험 첫 화면](../README.md) · [전체 문서 지도](INDEX.md)

아래는 저장소 루트에서 사용하는 예제입니다. Cofa 작업 공간에서는 `python scripts/cofa.py`를 `python3 .cofa-kit/scripts/cofa.py`로 바꾸세요. 모든 결과는 로컬 파일·터미널에만 남습니다. 도구 이름이나 출력은 공식 채점 기준이 아닙니다.

## 요구사항을 먼저 적기

도구 준비 상태를 확인하려면 `python scripts/cofa.py doctor --workspace . --check-mcp`를 선택적으로 실행합니다. 설치 스킬 차이·누락과 합성 자료를 이용한 로컬 MCP 실행만 확인합니다. 실제 연결 상태와는 별개이며 [결과 해석](SETUP.md#스킬mcp-상태-점검)을 참고하세요.

```bash
python scripts/cofa.py init --workspace work/practice
```

새 폴더에 `requirements.json`, `decision-log.jsonl`을 만듭니다. 기존 파일이 있으면 덮어쓰지 않습니다. 생성한 요구사항은 의도적으로 `todo`이므로 검사에 실패해야 정상입니다. 실제 과제에서는 다음처럼 **README의 요구사항으로 교체**합니다.

```json
{
  "required_files": ["README.md", "analysis.csv"],
  "criteria": [
    {
      "id": "R1",
      "requirement": "실제 과제가 요구한 계산과 예외 처리 조건",
      "priority": "must",
      "status": "todo",
      "evidence": []
    }
  ]
}
```

위 파일명과 요구사항은 예시일 뿐입니다. 기준마다 사용자가 볼 수 있는 행동 또는 값으로 완료 조건을 적으세요. 예: '대시보드 완성'보다 '필터 적용 시 전체 건수와 표의 행 수가 같고 결과 0건 메시지가 보인다'가 검증하기 쉽습니다.

`priority`는 `must/should/could`, `status`는 `todo/in_progress/verified/blocked` 중 하나입니다. 실제 확인을 마친 뒤에만 `verified`로 바꾸고, 구현 파일과 검증 기록 경로를 `evidence`에 연결하세요. 검증을 안 했거나 실패했다면 상태를 맞게 유지합니다.

## 데이터의 모양 확인

```bash
python scripts/cofa.py profile examples/defects.csv
python scripts/cofa.py profile examples/requests.json --format json
python scripts/cofa.py profile examples/defects.csv --max-rows 3 --output work/profile-sample.json
```

출력 경로의 부모 폴더는 먼저 만들어야 합니다. `--output`은 기존 파일을 덮어쓰지 않습니다. 한글 Windows CSV가 UTF-8로 열리지 않으면 파일 인코딩을 확인한 뒤 `--encoding cp949`를 명시합니다.

요약은 데이터 이해의 출발점입니다. 숫자처럼 보이는 ID·우편번호를 실제 수치로 해석할지는 따로 판단합니다. 기본 최대 10,000행이고, 표본을 읽은 경우 그 범위를 밝힙니다. JSON은 최대 20MiB이며 전체 파일을 파싱한 뒤 레코드 표본을 요약합니다. 큰 파일은 제공 환경에서 목적에 맞는 스트리밍 도구를 선택하세요.

## 판단과 검증을 남기기

```bash
python scripts/cofa.py log --workspace work/practice --kind assumption --summary "빈 값의 처리 규칙이 미확정. 실무자에게 확인할 예정."
python scripts/cofa.py log --workspace work/practice --kind decision --summary "실무자 확인 후 빈 수량은 합산에서 제외하고 누락 건수를 별도 표시한다."
```

실제로 확인하지 않은 답변·테스트를 기록하지 마세요. 직접 입력한 `test` 기록은 사용자의 진술이며 도구가 실행했다는 뜻이 아닙니다. 실제 명령의 실행 결과를 남기려면 `run`을 사용합니다.

v1.2.1부터 기존 `decision-log.jsonl` 형식을 쓰기 전에 확인합니다. 다른 프로젝트의 동명 로그이거나 손상된 형식이면 원본을 바꾸지 않고 오류로 중단합니다. `run`도 이 검사를 명령 실행 전에 합니다. 정상 JSONL의 마지막 줄바꿈만 빠졌다면 분리해서 이어 씁니다. 충돌하면 기존 파일을 삭제하지 말고 프로젝트 자체 기록을 사용하거나 별도 연습 작업 폴더를 선택하세요. 여러 프로세스가 동시에 같은 로그에 쓰는 용도는 지원하지 않습니다.

```bash
python scripts/cofa.py run --workspace work/practice --id R1 --timeout 30 -- python -m unittest discover -s tests -v
```

위 명령의 `tests`는 **work/practice 안의 실제 과제 테스트**여야 합니다. 증거 폴더에 실행 명령, 종료코드, 소요시간, 제한된 stdout/stderr가 기록됩니다. 일회성 테스트·빌드·분석 명령에 사용하고 개발 서버처럼 계속 실행되는 명령에는 쓰지 마세요. 임의 명령의 네트워크 행동을 차단하는 보안 샌드박스는 아닙니다. 허용된 로컬 검사만 실행하세요.

`run`의 `--id`는 해당 작업 폴더의 `requirements.json`에 존재하는 ID여야 합니다. 결과는 `evidence/<UTC시각-고유값>/result.json`, `stdout.txt`, `stderr.txt`에 저장되고 `decision-log.jsonl`에 연결됩니다. 출력은 기본적으로 스트림마다 앞부분 65,536바이트까지 보존하며 `--max-output-bytes`로 1,024~1,048,576바이트 사이에서 조정합니다. 원래 출력 바이트를 보존하므로 프로그램에 따라 텍스트 인코딩이 UTF-8이 아닐 수 있습니다.

v1.2.2는 실제 요약 판정에 사용한 끝부분도 `stdout.tail.txt`, `stderr.tail.txt`에 **각 최대 16,384바이트** 보존합니다. 앞부분 외에 최대 32,768바이트가 추가됩니다. `result.json`의 `tail_capture.streams`에 경로·저장 바이트 수·관측 출력에서의 `[시작, 끝)` 범위를 기록합니다. `tail_capture.complete`는 파이프를 끝까지 관측했는지이며 전체 출력을 저장했다는 뜻은 아닙니다. 잘린 중간 출력은 복원할 수 없고, 끝부분 첫 줄이 중간에서 잘렸을 수 있으면 그 줄은 판정에서 제외합니다.

`run`은 요구사항을 자동으로 `verified`로 바꾸지 않습니다. 일반적인 unittest/pytest 요약과 **Node TAP·spec 요약**에서 테스트 0개·전부 skip·실패를 발견하면 하위 명령이 0으로 끝나도 성공으로 취급하지 않습니다. Node의 전부 TODO 또는 skip+TODO만 있는 경우도 성공이 아닙니다. Jest·Vitest·사용자 정의 리포터까지 감지한다는 뜻은 아닙니다. 인식되지 않은 출력은 `recognized: null`이므로 실제 테스트 개수·결과를 직접 읽으세요. 여러 실행을 합치거나 출력이 잘린 경우도 직접 검토가 필요합니다. `ok: true`는 실행 관찰상 성공이며 요구사항 충족을 보장하지 않습니다.

Node 23부터 기본 출력은 spec입니다. v1.4.0은 전체 요약과 색상 코드를 처리하고 `node_tap` / `node_spec`으로 구분합니다. 출력 형식을 고정하려면 `node --test --test-reporter=tap`처럼 명시할 수 있습니다. [Node 공식 리포터 안내](https://nodejs.org/docs/latest-v24.x/api/test.html#test-reporters)

보존한 끝부분에서 완전한 요약이 둘 이상 발견되면 `test_summary.ambiguous: true`, `ok: false`, CLI 종료코드 1로 표시합니다. `summaries`의 각 요약에 스트림과 근거 파일이 연결됩니다. **각 끝부분 16,384바이트 밖의 요약까지 모두 탐지하는 것은 아닙니다.** 여러 검사를 한 명령으로 묶어 마지막 종료코드만 반환하지 말고 검사별로 실행하세요. 출력 안의 고립된 단어나 들여쓴 예시 문구는 테스트 실행 증거로 취급하지 않습니다.

검증 뒤 코드·입력·설정을 수정하거나 여러 작업을 통합했다면 영향받는 검사를 다시 실행하세요. 이 키트가 모든 소스의 해시를 추적해 오래된 증거를 자동 무효화하지는 않습니다. timeout은 직접 실행한 자식 프로세스를 종료하지만 자손 프로세스 전체 종료를 보장하지 않습니다.

## 제출 전 구조 검사

아래 구조 검사는 파일 존재·사용자 선언을 확인합니다. 실행한 코드와 현재 코드의 내용 비교가 필요하면 다음 절의 선택형 추적을 함께 사용합니다.

```bash
python scripts/cofa.py check --workspace work/practice
python scripts/cofa.py report --workspace work/practice --output work/practice/evidence-summary.md
```

`check`는 필수 파일이 존재하고 비어 있지 않은지, `must` 요구사항이 `verified`로 선언됐는지, 근거 파일이 실제 작업 폴더 안에 존재하고 비어 있지 않은지 확인합니다. 완료로 선언한 필수 요구사항에 근거 경로가 하나도 없어도 실패합니다. `should/could`의 미완료·근거 누락은 `warnings`에 표시되며 그것만으로 종료코드가 1이 되지는 않습니다. 파일 내용의 진실성이나 테스트 품질을 판정하지 않습니다. 빈 요구사항 목록, 필수 파일 누락, 미완료 필수 항목을 정상 통과로 취급하지 않습니다.

`evidence`에는 실행 정보를 담은 `result.json`과 필요한 구현·검증 파일을 연결하세요. 아무것도 출력하지 않은 명령의 `stdout.txt`나 `stderr.txt`는 정상적으로 빈 파일일 수 있으므로 무조건 근거 목록에 넣을 필요는 없습니다. 각 경로는 `--workspace` 폴더 기준 상대 경로이며, 상위 폴더 이동이나 작업 폴더 밖으로 향하는 심볼릭 링크는 허용하지 않습니다. MCP 검사에서 오류가 나오면 같은 `check` 명령을 터미널에서 실행해 `issues`와 입력 오류를 구분할 수 있습니다.

`report`는 현재 요구사항과 실제 기록을 Markdown으로 정리합니다. 자동 생성된 문서를 공식 제출 문서로 그대로 삼지 말고, 과제가 지정한 형식에 맞게 검토·정리하세요. 계획과 실제 구현이 다르면 이유와 현재 상태를 분명히 적습니다.

| 종료코드 | `check` | 의미 |
|---|---|---|
| 0 | 구조 검사 통과 | 기능 정확성은 별도 확인 |
| 1 | 누락·미완료 | 출력의 issues를 해결 |
| 2 | 입력 오류 | 경로·JSON 형식·사용법 확인 |

`run`의 종료코드는 0이면 실행 관찰상 성공, 1이면 실행 실패·시간 초과·인식된 무효 테스트 결과, 2이면 입력·파일 처리 오류입니다. 0도 요구사항 충족을 보증하지 않습니다. `report --output` 역시 기존 파일을 덮어쓰지 않으므로 새 경로를 지정하세요.

정확한 전체 옵션은 `python scripts/cofa.py --help`와 하위 명령의 `--help`를 사용합니다.

## 검증한 파일이 바뀌었는지 확인하기

v1.3.0의 선택 기능입니다. **테스트 통과 후 코드를 수정하고 예전 성공 로그를 그대로 쓰는 실수**를 줄입니다. 이미 키트의 `requirements.json`과 `run`을 사용하는 경우에 적용하며, 이 기능 때문에 기존 프로젝트에 새 기록 형식을 강제하지 않습니다.

Codex에는 다음처럼 요청할 수 있습니다.

```text
이미 키트 run으로 검사를 기록하고 있다면 관련 코드·테스트·입력 중
기존 파일을 --watch로 지정해 실행 전후 상태도 기록해 줘.
이후 파일이 바뀌면 예전 통과 기록을 재사용하지 말고 필요한 검사를 다시 실행해 줘.
파일이 같다는 판정과 테스트 성공·요구사항 충족은 따로 확인해 줘.
```

아래는 **실제 프로젝트가 해당 파일과 일회성 `npm test`를 사용하고, 실제 조건 ID `R1`을 이미 기록한 경우**의 형식 예입니다. 파일·ID·명령은 실제 과제에 맞춥니다. `--watch`는 명령 구분자 `--` **앞**에서 반복합니다.

```bash
python3 .cofa-kit/scripts/cofa.py run --workspace . --id R1 --watch src/orders.ts --watch tests/orders.test.ts -- npm test
```

출력의 `evidence_directory`에서 실제 실행 폴더를 확인합니다. 아래의 `실제실행폴더`를 그 값에 맞게 바꿉니다.

```bash
python3 .cofa-kit/scripts/cofa.py evidence check --workspace . --result evidence/실제실행폴더/result.json
```

MCP로 같은 비교를 할 때의 도구 인수 예입니다. **설정 JSON이 아니라 이미 연결된 도구 호출의 인수**입니다.

```json
{"result_path": "evidence/실제실행폴더/result.json"}
```

제공 Codex에 “`evidence_freshness`로 이 실제 실행 기록의 추적 파일을 비교해 줘”라고 요청하면 됩니다. MCP는 읽기만 하며 이 도구로 테스트를 실행하거나 기록을 생성하지 않습니다.

| CLI 결과 | 뜻 | 다음 행동 |
| --- | --- | --- |
| 0 | 지정 파일이 기록과 같고 실행 중 변경이 검출되지 않음 | `execution_ok`와 실제 검사 결과·요구사항도 별도 확인 |
| 1 | 변경·누락·불안정 또는 실행 중 변경을 발견 | 영향받는 실제 검사를 새로 실행 |
| 2 | 추적 없는 기록, 깨진 형식, 잘못된 경로·옵션 등 | 정상으로 간주하지 않고 입력·기록 방식을 확인 |

최대 32개·총 32MiB의 기존 일반 파일을 SHA-256과 크기로 비교합니다. 경로는 작업 폴더 기준이며 심볼릭 링크·Windows 재분석 지점은 허용하지 않습니다. 파일 크기나 수정 시각만 같다고 동일하게 판정하지 않습니다. 생성되는 로그·캐시·출력보다 실제 검사의 근거가 되는 코드·테스트·입력을 선택하세요.

추적하지 않은 파일·패키지·외부 서비스 상태, 관측 사이에 바뀌었다가 원상복구된 모든 변화까지 증명하지 않습니다. 파일이 같아도 이전 테스트는 실패했을 수 있습니다. 결과 파일은 서명되지 않으므로 위조 방지 기능이 아니며, `watched_files`나 결과를 편집해 통과로 만들지 않습니다. 기존 `check`와 `report`가 이 검사를 자동으로 대신 실행하는 것도 아닙니다.

## 반도체 검사 집계·계측 데이터

버전 1.1.0부터 다음 두 명령을 제공합니다. 먼저 열의 의미, 검사 모집단, 개체 키, 공정 조건을 확인하세요.

```bash
python scripts/cofa.py semi yield examples/semiconductor/yield_clean.csv --group-by tool_id --key lot_id,wafer_id
python scripts/cofa.py semi spc examples/semiconductor/measurements.csv --value-col value --time-col timestamp --baseline-count 25
```

`semi yield`는 검사 수로 가중한 통과율을 계산하고 복합키 중복·잘못된 수량을 거부합니다. `semi spc`는 한 계열의 앞부분으로 I-MR 기준을 계산하고 이후 관측만 비교합니다. 두 명령 모두 행 수 한도를 넘으면 부분 결과를 전체 집계처럼 반환하지 않고 오류를 냅니다. CLI 최대 행 수는 100,000, MCP는 10,000입니다.

실습의 예상 출력, 실제 데이터의 열 이름 매핑, 오류 대응, MCP 호출 예시는 [반도체 실행 실습](SEMICONDUCTOR-WALKTHROUGH.md)에 있습니다. 결과의 업무 의미와 통계적 한계는 [반도체 안내](SEMICONDUCTOR.md)를 함께 읽으세요. `--output`은 다른 도구와 마찬가지로 새로운 파일에만 씁니다.

## 두 CSV의 키 관계 검사

버전 1.2.0부터 실제 결합 전에 키 중복·미매칭·예상 행 증가를 확인할 수 있습니다.

```bash
python scripts/cofa.py data join-check examples/joins/inspections.csv examples/joins/tool_map.csv --left-key lot_id,wafer_id --right-key lot_id,wafer_id --relationship many_to_one
```

`--relationship`은 필수이며 `one_to_one`, `many_to_one`, `one_to_many`, `many_to_many` 중 실제 기대 관계를 지정합니다. 선택 옵션은 `--encoding utf-8-sig|cp949`, `--max-rows`(각 파일 최대 100,000), `--output 새파일.json`입니다. 정상 관계는 0, 관계 위반은 진단 JSON과 종료코드 1, 입력 오류는 2입니다. 실제 조인·원본 수정·자동 중복 제거·숫자 합계 보존 검사는 수행하지 않습니다. MCP의 같은 도구는 `csv_join_audit`이며 각 파일 최대 10,000행입니다. [정상·실패 예제와 인수 설명](DATA-JOIN.md)
