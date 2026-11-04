# CSV를 합치기 전에 행과 키 관계 확인하기

[시험 첫 화면](../README.md) · [전체 문서 지도](INDEX.md)

버전 1.2.0부터 제공하는 `data join-check`와 MCP `csv_join_audit`는 **두 CSV를 키로 결합할 때 예상되는 행 수와 키 유일성을 검사**한다. 실제 과제에 여러 CSV의 결합이 필요할 때 사용한다. 새 스킬을 설치할 필요 없이 기존 반도체 스킬과 함께 쓸 수 있다.

예를 들어 검사 집계 1행에 결함 기록 3행을 붙이면 검사 수가 세 번 반복될 수 있다. 이 도구는 그런 행 증가와 미매칭을 알려 준다. 결합 파일을 만들거나 중복을 제거하지 않으며, 검사 수·통과 수 합계 보존이나 업무상 올바른 키까지 판단하지 않는다.

## 1. 시험 전 로컬에서 합성 예제 실행

아래는 키트 루트의 일반 터미널에서 실행한다. 외부 패키지나 계정이 필요 없다.

```powershell
python scripts/cofa.py data join-check examples/joins/inspections.csv examples/joins/tool_map.csv --left-key lot_id,wafer_id --right-key lot_id,wafer_id --relationship many_to_one
```

왼쪽은 검사 3행, 오른쪽은 장비 기준표 3행이며 복합키가 모두 대응한다. 예상 결과는 `ok: true`, 종료코드 0, inner/left/right/full 결합 예상 행 수가 모두 3이다. 원본에서 `wafer_id`가 `001`인 행은 두 lot에 있으므로 `wafer_id` 하나만으로 전역 개체를 식별하지 않는다.

이번에는 오른쪽을 결함 사건 테이블로 바꾼다.

```powershell
python scripts/cofa.py data join-check examples/joins/inspections.csv examples/joins/defects.csv --left-key lot_id,wafer_id --right-key lot_id,wafer_id --relationship many_to_one
```

**이 명령은 종료코드 1로 실패해야 정상이다.** 오른쪽에 `L01/001` 키가 세 번 있으므로 오른쪽 키가 유일해야 하는 `many_to_one` 조건을 위반한다. 진단 JSON은 계속 출력된다.

| 확인할 출력 | 기대값 | 의미 |
| --- | ---: | --- |
| `left.rows` / `right.rows` | 3 / 5 | 원본 행 수 |
| `right.duplicate_keys` | 1 | 여러 번 등장하는 서로 다른 키의 개수 |
| `left.unmatched_rows` | 1 | 결함 기록과 매칭되지 않는 검사 행 |
| `right.unmatched_rows` | 1 | 검사 기록과 매칭되지 않는 결함 행 |
| `predicted_rows.inner` | 4 | 양쪽에 있는 키만 결합할 때 |
| `predicted_rows.left` | 5 | 왼쪽 미매칭 행도 남길 때 |
| `predicted_rows.right` | 5 | 오른쪽 미매칭 행도 남길 때 |
| `predicted_rows.full` | 6 | 양쪽 미매칭 행을 모두 남길 때 |

이 예에서 단순 left join 후 검사 수를 더하면 `100×3+10+50=360`이 된다. 원본 검사 수는 `100+10+50=160`이다. 이는 **별도 손계산**이며 도구가 합계를 계산한 결과가 아니다. 실제 구현에서는 분자·분모 총계도 따로 비교한다. [합성 기대값](../examples/joins/expected.json)

## 2. 관계를 어떤 기준으로 정하나

| `--relationship` | 검사하는 키 유일성 | 예 |
| --- | --- | --- |
| `one_to_one` | 왼쪽과 오른쪽 모두 유일 | 개체별 집계표 두 개 |
| `many_to_one` | 오른쪽이 유일 | 여러 검사 기록에 장비 기준표 붙이기 |
| `one_to_many` | 왼쪽이 유일 | 개체 목록에서 여러 사건으로 펼치기 |
| `many_to_many` | 유일성 조건을 요구하지 않음 | 의도적으로 정의한 다대다 관계 |

업무상 기대 관계를 먼저 정하고 옵션으로 명시한다. 실패를 숨기려고 `many_to_many`로 바꾸지 않는다. 다대다를 허용해도 행 수가 곱해질 수 있고 수량을 다시 합쳐도 되는지는 별도 판단이다. 유일성 검사는 매칭된 키뿐 아니라 **각 CSV 전체**에 적용한다. 이는 pandas의 관계 검사 구분과 같다. [pandas.merge 공식 문서](https://pandas.pydata.org/docs/reference/api/pandas.merge.html)

키는 원문 문자열로 비교한다. `001`과 `1`을 같게 만들거나 공백을 자동 제거하지 않는다. 빈 키·공백뿐인 키는 오류다. 헤더 중복, 필수 키 열 누락, 잘못된 CSV 행 너비도 거부한다. 빈 데이터에 정상 헤더만 있으면 행 수 0으로 계산하되, 실제 과제가 빈 입력을 허용하는지는 별도로 확인한다.

원본을 보존하면서 결함을 개체별로 먼저 집계할지, 결함 사건을 별도 화면으로 보여줄지, 미매칭을 어떻게 표시할지는 과제 요구와 실무자 확인으로 결정한다.

## 3. 시험 중 제공 Codex에서 요청

```text
$cofa-semiconductor
여러 CSV를 합치기 전에 실제 파일에서 각 행의 의미와 복합키, 기대 관계를 확인해 줘.
기준이 확인되면 키트의 data join-check로 키 중복·미매칭·예상 행 수를 검사해 줘.
그다음 실제 구현에서 결합 전후 고유 개체 수와 분자·분모 합계를 따로 비교해 줘.
원본을 유지하고, 업무상 이유 없이 중복을 제거하거나 관계 조건을 바꾸지 마.
```

CLI 경로는 과제 루트에서 `python3 .cofa-kit/scripts/cofa.py data join-check ...` 형태다. 두 입력 경로와 키 이름은 실제 파일에 맞춘다. Python 실행 이름이 `python`이면 바꿔 쓴다.

MCP가 이미 연결되고 도구 목록에 `csv_join_audit`가 있다면, 다음은 **Codex 입력란에 보내는 합성 예제 호출 요청**이다. MCP 탭에 넣는 서버 설정 JSON이 아니다.

```text
csv_join_audit 도구를 아래 인수로 호출해 줘.
left_path: .cofa-kit/examples/joins/inspections.csv
right_path: .cofa-kit/examples/joins/defects.csv
left_key: ["lot_id", "wafer_id"]
right_key: ["lot_id", "wafer_id"]
relationship: many_to_one
예상되는 관계 위반과 진단 내용을 설명해 줘. 이 예제는 실패가 정상이다.
```

## 4. 한도와 결과 읽기

CLI의 기본·최대 행 수는 각 파일 100,000, MCP는 각 파일 10,000이다. `--max-rows` 또는 MCP `max_rows`로 더 작은 한도를 지정할 수 있다. 한 파일이라도 한도를 넘으면 부분 결과를 전체 검사처럼 반환하지 않고 오류가 된다. `--encoding utf-8-sig`가 기본이며 `cp949`도 선택할 수 있다.

| 종료코드 | 의미 | 대응 |
| --- | --- | --- |
| 0 | 입력이 유효하고 선언한 키 관계 충족 | 미매칭·행 증가 경고와 업무 의미도 확인 |
| 1 | 입력은 유효하지만 선언한 키 관계 위반 | JSON의 `issues`와 양쪽 키 개수 확인 |
| 2 | 파일·열·인수·CSV·행 제한 오류 | 입력 조건부터 수정 |

`--output 새파일.json`으로 저장할 수 있으며 기존 파일을 덮어쓰지 않는다. MCP는 두 경로를 등록한 작업 폴더 안의 파일로 제한하고 파일을 쓰지 않는다. 도구의 정상 출력은 행·키 개수 중심이며 원본 키 값 목록이나 결합 데이터 전체를 반환하지 않는다.

이 도구는 완성된 조인 결과 파일을 검증하거나 수정하는 도구가 아니다. 키 관계와 예상 행 수를 확인한 뒤 **실제 결과의 정확성, 수량 보존, 제외 사유**를 별도로 검증한다.
