# 반도체 데이터 도구 실습: 분모가 있는 수율과 고정 기준 I-MR

[시험 첫 화면](../README.md) · [전체 문서 지도](INDEX.md)

이 실습의 CSV와 숫자는 모두 **제작자가 만든 합성 예제**다. 실제 공정 데이터·시험 문제·정답이 아니다. 목적은 실제 자료가 주어졌을 때 열의 의미와 계산 기준을 확인하고, 도구 결과를 수작업으로 검증할 수 있도록 연습하는 것이다.

기본 시작은 [README](../README.md)를 따른다. 이 문서는 도구를 직접 연습하고 싶을 때만 읽는다. 개념과 적용 판단은 [반도체 스킬](../skills/cofa-semiconductor/SKILL.md), 요청문은 [SEMICONDUCTOR](../prompts/SEMICONDUCTOR.md)를 참고한다. 실제 과제에 반도체 측정·검사 데이터가 없으면 이 기능을 억지로 사용하지 않는다.

## 1. 준비와 예제 파일

시험 전 개인 PC에서는 **키트 루트의 PowerShell**에서 다음을 실행한다.

```powershell
python scripts/cofa.py doctor
python scripts/cofa.py semi --help
```

`semi`가 없다고 나오면 받은 키트의 버전을 확인한다. 기존 복사본 업데이트와 설치된 스킬 보존 방법은 [MANUAL 2장·4장](MANUAL.md)을 따른다. 기존 설치 내용이 현재 키트와 모두 동일할 때만 설치기가 빠진 스킬을 추가한다. 충돌하면 기존 파일을 보존하고 현재 키트의 `SKILL.md`를 직접 읽게 한다.

| 파일 | 용도 |
| --- | --- |
| `examples/semiconductor/yield_clean.csv` | 분모가 서로 다른 세 검사 기록 |
| `examples/semiconductor/yield_dirty.csv` | 같은 검사 키가 중복된 두 기록. 거부 동작 확인용 |
| `examples/semiconductor/measurements.csv` | 하나의 합성 측정 계열. 기준 25개와 이후 관측 3개 |
| `examples/semiconductor/expected.json` | 사람이 비교할 기대 수치. 실제 분석 출력과 별개 |

## 2. 예제 A: 검사 수량을 반영한 통과율

### 2-1. CSV의 의미부터 읽기

`yield_clean.csv`에는 다음 세 기록이 있다.

| lot_id | wafer_id | tool_id | tested | passed |
| --- | --- | --- | ---: | ---: |
| L001 | W01 | TOOL-A | 100 | 99 |
| L001 | W02 | TOOL-A | 2 | 1 |
| L002 | W01 | TOOL-B | 10 | 8 |

이 예제에서 `tested`는 검사한 개수, `passed`는 그중 통과한 개수다. `lot_id`와 `wafer_id`의 조합이 한 검사 기록을 구분한다. **실제 데이터도 이 의미와 키를 가진다고 가정하면 안 된다.** 같은 웨이퍼의 재검사·다른 공정 단계·다른 검사 항목이 있으면 기록 단위부터 확인한다.

### 2-2. 명령 실행

시험 전 키트 루트의 **PowerShell**:

```powershell
python scripts/cofa.py semi yield examples/semiconductor/yield_clean.csv --group-by tool_id --key lot_id,wafer_id
```

시험 중 공개 키트를 `.cofa-kit`으로 받은 **Cofa 과제 루트의 Bash**에서 같은 합성 연습을 실행할 경우:

```bash
python3 .cofa-kit/scripts/cofa.py semi yield .cofa-kit/examples/semiconductor/yield_clean.csv --group-by tool_id --key lot_id,wafer_id
```

명령의 의미는 다음과 같다.

| 옵션 | 의미 |
| --- | --- |
| `--group-by tool_id` | 설비별로 검사·통과 수량을 합산 |
| `--key lot_id,wafer_id` | 각 기록의 유일성을 두 열의 조합으로 확인 |
| `--tested-col tested` | 검사 개수 열. 생략하면 `tested` |
| `--passed-col passed` | 통과 개수 열. 생략하면 `passed` |
| `--encoding cp949` | 실제 파일이 해당 인코딩일 때만 지정 |
| `--output 새파일.json` | JSON 결과를 새 파일로 저장. 기존 파일은 덮어쓰지 않음 |

### 2-3. 손계산과 출력 비교

계산은 `통과 개수 합 / 검사 개수 합 × 100`이다.

| 범위 | 계산 | 기대 `pass_rate_pct` |
| --- | --- | ---: |
| TOOL-A | `(99 + 1) / (100 + 2) × 100` | 약 98.039216 |
| TOOL-B | `8 / 10 × 100` | 80.0 |
| 전체 | `108 / 112 × 100` | 약 96.428571 |

TOOL-A의 행별 통과율 99%와 50%를 단순 평균하면 74.5%가 된다. 그것은 여기서 요구한 **검사 개수 기준의 통과율**과 다르다. 두 행의 분모가 다르기 때문이다. 업무 목표가 웨이퍼별 평균이라면 다른 지표를 요구하는 것이므로 먼저 정의를 확인해야 한다.

출력에서 설비별 값은 `groups` 안에 있고 설비 이름은 `group.tool_id`에 있다. 전체는 `totals`다. `pass_rate`는 0–1 비율이고 `pass_rate_pct`는 0–100 백분율이다. 필드 이름이 `yield_pct`는 아니다.

이 수치만으로 전체 제조 수율, 출하 수율, 설비가 불량의 원인이라고 말하지 않는다. 도구는 선택한 검사 모집단의 통과율을 계산한다. 검사 대상의 범위와 제품·레시피·기간 차이는 별도로 확인해야 한다.

### 2-4. 중복을 조용히 합산하지 않는지 확인

시험 전 PowerShell에서 실행한다.

```powershell
python scripts/cofa.py semi yield examples/semiconductor/yield_dirty.csv --group-by tool_id --key lot_id,wafer_id
$LASTEXITCODE
```

기대 결과는 `duplicate composite key` 오류와 **종료코드 2**다. 이 파일의 같은 lot·wafer 두 행을 임의로 평균 내거나 마지막 행만 선택하지 않는다. 중복이 단순 오류인지 재검사인지, 최초 검사·최종 검사 중 무엇을 사용할지 업무 규칙을 먼저 확인해야 한다. 오류를 없애기 위해 의미 없는 행 번호를 키에 추가하면 중복 검사 의미를 확인하지 못한 채 합산할 수 있다.

도구는 빈 검사·통과 수량, 음수·소수 개수, `passed > tested`, 누락된 그룹·키를 거부한다. 검사 개수가 0인 그룹의 통과율은 `null`이며 0% 또는 100%로 채우지 않는다. 불량 **이벤트 수**는 불량 **개체 수**와 다를 수 있으므로 이 도구의 `passed` 대신 임의 변환해 넣지 않는다.

## 3. 예제 B: 기준 구간을 고정한 I-MR 관측 점검

### 3-1. 어디에 쓰는 계산인가

하나의 비교 가능한 측정 계열에서 앞부분을 기준 구간으로 정하고, 그 뒤의 관측을 같은 한계로 살펴보는 연습이다. 기준 구간의 평균과 인접 관측 차이를 이용한다. 이 도구는 관리한계 밖의 점을 검토 신호로 표시하며 공정 원인이나 제품 합격 여부를 확정하지 않는다.

I 차트의 식은 NIST가 설명하는 개별 측정 관리도 식을 따른다. 인접 차이 `MR = |현재 값 − 직전 값|`의 기준 구간 평균을 `MRbar`라고 하면 I 관리한계는 `기준 평균 ± 3 × MRbar / 1.128`이다. [NIST Individuals Control Charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc322.htm)

이 키트는 앞의 `baseline_count`개만 기준 계산에 사용하고 이후 값을 넣어 기준을 다시 맞추지 않는다. MR 상한은 구현상 `3.267 × MRbar`, 하한은 0이다. 적용 수식과 반환값은 [semiconductor.py](../cofa_kit/semiconductor.py), 합성 기대값은 [expected.json](../examples/semiconductor/expected.json)에서 확인할 수 있다.

### 3-2. 예제 계열과 명령

`measurements.csv`의 열은 `timestamp`, `tool_id`, `metric`, `unit`, `value`다. **이 예제에는 `recipe` 열이 없다.** 실제 데이터에 없는 열을 `--series-cols`로 지정하면 오류가 난다.

앞 25개 값은 10, 11이 번갈아 나타나며 마지막 기준값은 10이다. 이후 세 값은 14, 10, 10.5다. 이는 수치를 확인하기 쉬운 합성 입력이며, 25개가 있다는 사실이나 이 교대 패턴이 공정 안정성을 증명하지 않는다.

시험 전 키트 루트의 **PowerShell**:

```powershell
python scripts/cofa.py semi spc examples/semiconductor/measurements.csv --value-col value --time-col timestamp --baseline-count 25 --series-cols tool_id,metric,unit
```

시험 중 `.cofa-kit`을 받은 **Cofa 과제 루트의 Bash**:

```bash
python3 .cofa-kit/scripts/cofa.py semi spc .cofa-kit/examples/semiconductor/measurements.csv --value-col value --time-col timestamp --baseline-count 25 --series-cols tool_id,metric,unit
```

`--series-cols`의 열 값은 파일 전체에서 같아야 한다. 서로 다른 설비·측정 항목·단위를 한 계열로 합쳐 계산하는 오류를 줄이는 장치다. 실제 데이터에 제품·레시피·챔버 등의 중요한 식별 열이 있다면 검토해서 지정한다. 생략 시에는 데이터에 존재하는 알려진 식별 열을 확인하지만, 자동 선택만으로 동질성이 보장되는 것은 아니다.

### 3-3. 기대 출력 읽기

`baseline` 값은 다음과 같아야 한다. 마지막 소수 자리는 부동소수점 표시로 조금 다를 수 있다.

| 출력 필드 | 기대값 |
| --- | ---: |
| `count` | 25 |
| `mean` | 10.48 |
| `mr_bar` | 1.0 |
| `i_lcl` | 약 7.820426 |
| `i_ucl` | 약 13.139574 |
| `mr_lcl` | 0.0 |
| `mr_ucl` | 3.267 |

`evaluation`에는 기준 이후 세 관측만 나타난다. `row_number`는 헤더를 제외한 데이터 행을 1부터 센 번호다.

| 데이터 행 | 값 | 직전 값과 차이 | `i_signal` | `mr_signal` |
| --- | ---: | ---: | --- | --- |
| 26 | 14.0 | 4.0 | `true` | `true` |
| 27 | 10.0 | 4.0 | `false` | `true` |
| 28 | 10.5 | 0.5 | `false` | `false` |

26번째 관측은 값 14가 I 상한을 넘으며, 마지막 기준값 10과의 차이 4도 MR 상한을 넘는다. 27번째는 값 10 자체는 I 한계 안에 있지만 직전 값 14에서의 변화량 4는 MR 상한을 넘는다. 28번째는 두 조건 모두 신호가 없다. 즉 값의 위치와 인접 변화량을 서로 다른 관점으로 본다.

### 3-4. 출력의 한계까지 읽기

- 결과의 `status: exploratory`는 탐색적 점검이라는 뜻이다. 출하 승인이나 원인 확정이 아니다.
- 기준 구간에서 `MRbar`가 0이면 `status: indeterminate`이고 한계·신호가 `null`이다. 변화가 전혀 없는 기준만으로 이후 데이터가 정상이라고 단정하지 않는다.
- 기준값이 20개 미만이면 경고한다. 20이라는 수는 이 키트의 주의 기준이며 공식 합격 기준이나 통계적 충분성 보증이 아니다. 최소 입력은 3개다.
- 결측을 0으로 채우지 않으며 유한하지 않은 숫자는 거부한다. 날짜는 ISO 형식과 엄격한 시간 증가를 요구한다. 같은 시각이나 시간대 오프셋 혼합을 조용히 정리하지 않는다.
- 관측 간격이 일정하지 않으면 경고한다. 도구가 공백 구간을 보간하거나 공정 변경점을 자동으로 나누지는 않는다.
- 같은 설비라도 제품·레시피·측정 단위·운영 조건이 다르면 한 계열인지 다시 판단한다. 자기상관이나 분포·표본 설계도 도구가 자동으로 해결하지 않는다.
- 현재 구현은 표시된 I·MR 한계 초과 조건만 계산한다. 모든 런 규칙, 다변량 탐지, 공정능력지수, 사양 한계 판정을 수행한 것으로 설명하지 않는다.

## 4. 실제 과제에 적용하기 전에 묻는 질문

실무자에게 확인할 질문은 실제 README에서 답을 찾지 못했고 계산이 달라지는 항목에 집중한다.

| 확인 내용 | 바뀌는 판단 |
| --- | --- |
| 한 행은 웨이퍼·다이·로트·검사 이벤트 중 무엇인가? | 집계 단위와 중복 키 |
| 검사·통과·불량 수의 분모가 같은가? | 통과율 계산이 가능한지 |
| 재검사는 어떤 기준으로 처리하는가? | 최초·최종·별도 표시 여부 |
| 제품·레시피·설비·기간 차이가 있는가? | 비교 가능한 그룹과 계열 |
| 기준 구간은 어떤 업무 근거로 정하는가? | 이후 관측을 섞지 않는 기준 설정 |
| 신호가 나왔을 때 사용자에게 필요한 것은 무엇인가? | 검토 목록·근거·다음 확인 제안의 형태 |
| 사양 한계나 품질 판정 기준이 따로 있는가? | 관리한계와 합격 기준의 구분 |

질문을 자동으로 메신저에 보내지 않는다. 참가자가 플랫폼에서 직접 확인한다. 답이 없으면 중요한 가정을 명시하고 근거 없는 인과·품질 판정을 유보한다.

여러 CSV를 키로 합치는 과제라면 [두 CSV 조인 검사 실습](DATA-JOIN.md)도 확인한다. 검사 집계와 결함 사건을 결합할 때 예상 행 증가를 찾고, 실제 분자·분모 합계는 따로 비교한다.

## 5. 결과 저장과 검증 기록 연결

시험 전 PowerShell에서 결과를 파일로 보려면 먼저 출력 폴더를 만들고 새 파일명으로 저장한다.

```powershell
New-Item -ItemType Directory -Force work/semi-practice
python scripts/cofa.py semi yield examples/semiconductor/yield_clean.csv --group-by tool_id --key lot_id,wafer_id --output work/semi-practice/yield-result.json
python scripts/cofa.py semi spc examples/semiconductor/measurements.csv --value-col value --time-col timestamp --baseline-count 25 --series-cols tool_id,metric,unit --output work/semi-practice/spc-result.json
```

같은 파일명으로 반복하면 덮어쓰기 방지 오류가 난다. 새 파일명을 사용한다. 반도체 두 명령의 `--max-rows`는 기본 100,000이며 이를 넘으면 **부분 결과를 반환하지 않고 거부**한다. 일반 `profile`의 표본 요약과 다르다. 잘린 데이터를 전체 수율로 보고하는 일을 줄이려는 동작이다.

실제 과제에서는 결과 JSON이 있다는 사실만으로 요구사항을 `verified`로 바꾸지 않는다. 작은 수작업 기대값과 대조하고 중복·분모 0·결측 등 해당 과제에 중요한 실패 입력을 확인한다. 필요하면 [전체 설명서의 `run` 흐름](MANUAL.md)에 따라 실제 검증 명령과 근거를 남긴다. 합성 fixture 검사 성공을 실제 과제 데이터 검증으로 기록하지 않는다.

## 6. Codex에 요청하는 방법

과제 수행 단계의 제공 Codex에서 사용한다.

```text
.cofa-kit/skills/cofa-semiconductor/SKILL.md를 읽고 현재 데이터에 적용할지 판단해 줘.
먼저 README와 실제 파일에서 행 단위, 분모, 중복 키, 재검사 의미, 단위와 시간을 확인해 줘.
확정되지 않은 것은 가정으로 표시하고 계산을 바꿀 질문만 제안해 줘.
수율이면 검사 개수 가중 여부, SPC면 한 계열과 기준 구간 근거를 먼저 설명해 줘.
도구가 맞는 경우에만 실행하고 손계산 가능한 사례와 실제 결과를 대조해 줘.
검토 신호를 제품 불합격이나 원인 확정으로 표현하지 마.
```

MCP가 실제 연결돼 있다면 `semiconductor_yield`, `spc_monitor` 도구를 사용할 수 있다. CLI와 마찬가지로 지정 작업 폴더 안의 자료만 읽고 결과를 제공 Codex로 반환한다. 도구 목록에 없다면 연결을 고치느라 시간을 쓰지 말고 위 CLI로 계속한다.

### MCP를 연결한 경우의 구체적인 요청

아래는 **Codex 입력란**에 넣을 요청이다. 경로는 MCP를 등록할 때 지정한 작업 폴더 기준이며, 키트를 `.cofa-kit`으로 받은 Cofa 과제 루트를 가정한다. JSON을 MCP 설정 전체에 붙여 넣는 절차가 아니다.

```text
semiconductor_yield 도구를 아래 인수로 호출해 줘.
path: .cofa-kit/examples/semiconductor/yield_clean.csv
group_by: ["tool_id"]
key: ["lot_id", "wafer_id"]
tested_col: tested
passed_col: passed
결과에서 TOOL-A의 100/102와 전체 108/112를 확인하고,
이 합성 자료만으로 설비 우수성이나 불량 원인을 확정할 수 없는 이유를 설명해 줘.
```

```text
spc_monitor 도구를 아래 인수로 호출해 줘.
path: .cofa-kit/examples/semiconductor/measurements.csv
value_col: value
time_col: timestamp
baseline_count: 25
series_cols: ["tool_id", "metric", "unit"]
26~28번째 데이터 행의 I/MR 신호를 각각 읽고,
27번째는 I 신호 없이 MR 신호만 나타나는 이유를 실제 값으로 설명해 줘.
```

MCP는 기본·최대 10,000행이고, 반도체 도구는 이를 초과하면 부분 결과 대신 오류를 반환한다. 더 큰 허용된 로컬 자료는 CLI의 명시적인 행 수 한도 안에서 분석한다. 도구 이름·인수가 맞아도 파일이 없으면 작업 폴더와 상대 경로부터 확인한다. 새 버전 도구가 목록에 보이지 않으면 제공 환경의 연결 안내를 따르고, 그동안 CLI를 사용한다.

**후속 서술형 단계에서는 이 프롬프트·스킬·MCP를 사용하지 않는다.** 제출 전에는 “왜 이 분모와 기준 구간을 선택했는가, 무엇을 검증했는가, 무엇까지는 말할 수 없는가”를 본인의 말로 설명해 본다.
