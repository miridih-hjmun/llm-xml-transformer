# XML 변환 및 LLM 처리 도구

Python을 사용한 XML 문서 변환 및 LLM 프롬프트 처리 도구입니다. 이 도구는 XML 문서에서 텍스트를 추출하고, LLM API를 통해 처리한 후, 결과를 다시 XML 문서에 삽입합니다.

## 주요 기능

- XML 문서에서 `<TEXT>` 및 `<SIMPLE_TEXT>` 태그의 텍스트 추출
- 추출된 텍스트를 LLM API를 통해 처리
- 처리된 텍스트를 원본 XML 구조에 맞게 다시 삽입
- 변환된 XML파일 및 이미지(PNG)파일 추출

## 필수 요구사항

- Python 3.9
- Node.js 14.0 이상 (Node.js 통합이 필요한 경우)
- npm 6.0 이상 (Node.js 통합이 필요한 경우)

## 설치 방법

소스 코드에서 설치하는 방법을 권장합니다:

```bash
# 저장소 클론 (서브모듈 포함)
git clone --recurse-submodules https://github.com/miridih-hjmun/llm-xml-transformer.git
cd llm-xml-transformer

# 필요한 패키지 설치
pip install -r requirements.txt
```

> 참고: 이 프로젝트는 `pyproject.toml`과 `package_setup.py` 두 가지 설정 파일을 포함하고 있습니다. `package_setup.py`는 이전 버전과의 호환성을 위해 유지되고 있습니다.

## 의존성

이 라이브러리는 다음과 같은 외부 의존성을 가지고 있으며, 설치 시 자동으로 설치됩니다:

```
openai>=0.27.0
python-dotenv>=0.19.0
requests>=2.28.0
langchain<0.2.0
pydantic<2.0.0
PyYAML>=6.0
```
## 환경 변수 설정

**중요**: 이 도구를 사용하기 위해서는 반드시 `.env` 파일을 생성하고 OpenAI API 키를 설정해야 합니다. `.env` 파일은 보안 정보를 포함하고 있어 Git 저장소에 포함되지 않으므로, 사용자가 직접 생성해야 합니다.

### .env 파일 생성 방법

1. python 디렉토리에서 .env 생성
2. 아래 형식에 맞춰 필요한 환경 변수를 설정합니다.
```
# OpenAI API 키 (필수)
OPENAI_API_KEY=your_openai_api_key
```

3. node 디렉토리에서 .env 생성
4. 아래 형식에 맞춰 필요한 환경 변수를 설정합니다.
```
# 미리캔버스 접근 정보
STAGING7_URL=puppeteer를 이용할 미캔 스테이징 주소
EMAIL=your_email
PASSWORD=your_password
```
(puppeteer로 미캔에 접근하기 위해서 필수)

5. prompt/ailabs-context-aware-retrieval-eval-dataset/src 디렉토리에서 .env 생성
6. 아래 형식에 맞춰 필요한 환경 변수를 설정합니다.
```
# LANGSMITH 관련키 (필수)
LANGSMITH_API_KEY=your_api_key
LANGSMITH_PROJECT=your_projectname
```

### 환경 변수 설명

- `OPENAI_API_KEY`: OpenAI API를 사용하기 위한 API 키입니다. 
- `EMAIL`: 미리캔버스 계정의 이메일 주소입니다.
- `PASSWORD`: 미리캔버스 계정의 비밀번호입니다.
- `LANGSMITH_API_KEY`: LANGSMITH_API를 사용하기 위한 API 키입니다.
- `LANGSMITH_PROJECT`: 해당 프로젝트 명입니다.

### 주의사항

- `.env` 파일은 절대로 공유하거나 Git 저장소에 커밋하지 마세요.
- 각 개발 환경마다 별도의 `.env` 파일을 생성해야 합니다.
- 환경 변수가 올바르게 설정되지 않으면 도구가 정상적으로 작동하지 않을 수 있습니다.
- 입력 및 출력 경로는 명령줄 인자로만 지정할 수 있으며, 환경 변수로 설정할 수 없습니다.


## 사용 방법

### 명령줄에서 실행

다음 명령어로 프로그램을 실행할 수 있습니다:

```bash
# 기본 실행 (필수 인자: --input, --output)
python -m python.main --input /path/to/input --output /path/to/output

# 또는 짧은 옵션 사용
python -m python.main -i /path/to/input -o /path/to/output
```

### 옵션 설명

- `--input`, `-i`: 입력 파일 또는 디렉토리 경로 (필수)
- `--output`, `-o`: 출력 디렉토리 경로 (필수)

## 개발 환경 설정

### Node.js 의존성 설치 (필요한 경우)

```bash
cd node
npm install
npm run build
```