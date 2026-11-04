# 시험 전 공개 저장소 게시

[시험 첫 화면](../README.md) · [전체 문서 지도](INDEX.md)

목표 저장소: `https://github.com/ripplelover/cofa-ready-kit`

이 문서는 **시험 전 개인 PC에서 범용 준비 키트를 게시하는 절차**입니다. 시험 중 작업 파일·문제·결과물을 GitHub로 보내는 데 사용하지 않습니다. 공개로 게시되기 전에는 다른 환경에서 Clone할 수 없습니다.

## 연결된 GitHub가 있는 경우

GitHub 연결이 완료되면 이 키트의 준비된 소스만 대상으로 `ripplelover/cofa-ready-kit`을 public으로 생성하고 게시할 수 있습니다. 원본 PDF, `.private/`, `.local-tools/`, `work/`, `dist/`, 환경변수 파일은 공개 대상이 아닙니다.

## 직접 게시하는 경우

1. 시험 전 개인 브라우저에서 [GitHub 새 저장소](https://github.com/new)를 엽니다.
2. Owner를 `ripplelover`, 이름을 `cofa-ready-kit`, 공개 범위를 **Public**으로 정합니다.
3. README·라이선스·gitignore 자동 생성은 선택하지 않고 빈 저장소를 만듭니다. 이 키트에 이미 있습니다.
4. 로컬 Cofa 폴더의 터미널에서 저장소 경로를 확인합니다.

```powershell
git rev-parse --show-toplevel
git status --short
```

표시 경로가 이번 `Cofa` 폴더인지 확인합니다. 상위 사용자 폴더의 Git 저장소가 나오면 진행하지 말고 이번 폴더의 독립 저장소 상태부터 확인하세요.

아직 로컬 커밋이 없다면 명시된 준비 파일만 추가합니다.

```powershell
git add .gitignore AGENTS.md LICENSE README.md cofa_kit docs examples prompts scripts skills tests
git diff --cached --stat
git commit -m "Add Cofa preparation skills and local evidence tools"
```

`git remote -v`로 현재 원격을 확인합니다. `origin`이 없는 경우에만 추가합니다.

```powershell
git remote add origin https://github.com/ripplelover/cofa-ready-kit.git
git push -u origin main
```

Git이 인증을 요청하면 본인의 GitHub 계정으로 로그인합니다. 비밀번호·토큰을 이 저장소나 대화에 붙여 넣지 않습니다. 이미 다른 `origin`이 있으면 덮어쓰지 말고 주소부터 확인합니다. 원격에 기존 커밋이 있어서 push가 거절되면 force push하지 않고 해당 내용을 확인합니다.

GitHub CLI가 이미 설치·로그인되어 있고 원격 저장소를 아직 만들지 않았다면 일반적인 대안은 다음과 같습니다.

```powershell
gh auth status
gh repo create ripplelover/cofa-ready-kit --public --source . --remote origin --push
```

이 대안은 아직 원격·origin이 없는 준비 완료 저장소에서만 사용합니다. 두 생성 방법을 모두 실행할 필요가 없습니다.

## 공개 후 확인

- 로그인하지 않은 접근으로 README와 `skills/cofa-triage/SKILL.md`를 읽을 수 있는지 확인합니다.
- 빈 연습 폴더에 `git clone --depth 1 https://github.com/ripplelover/cofa-ready-kit.git`을 실행해 다운로드를 검증합니다.
- 그 복사본에서 `python -m unittest discover -s tests -v`를 실행합니다.
- 사전 체험에서는 Cofa가 제공하는 환경 안에서 실제 Clone·스킬 읽기·짧은 명령을 확인합니다.

아카이브가 필요하면 `python scripts/package.py`를 실행합니다. `dist/cofa-ready-kit.zip`에는 명시적으로 선정한 준비 소스만 들어갑니다. 이 ZIP은 개인 백업·공개 소스 배포용이며 개인 PC 파일 업로드 제한을 우회하는 수단이 아닙니다.
