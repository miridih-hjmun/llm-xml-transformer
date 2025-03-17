# XML 변환 및 LLM 처리 도구

Python을 사용한 XML 문서 변환 및 LLM 프롬프트 처리 도구입니다. 이 도구는 XML 문서에서 텍스트를 추출하고, LLM API를 통해 처리한 후, 결과를 다시 XML 문서에 삽입합니다.

## 주요 기능

- XML 문서에서 `<TEXT>` 및 `<SIMPLE_TEXT>` 태그의 텍스트 추출
- 추출된 텍스트를 LLM API를 통해 처리
- 처리된 텍스트를 원본 XML 구조에 맞게 다시 삽입
- 변환된 XML파일 및 이미지(PNG)파일 추출

## 설치 방법

### pip를 통한 설치 (권장)

pip를 통해 설치하면 필요한 모든 의존성이 자동으로 설치됩니다:

```bash
pip install ailabs-llm-xml-transformer
```

### GitHub에서 직접 설치

GitHub에서 직접 설치할 때도 의존성이 자동으로 설치됩니다:

```bash
pip install git+https://github.com/yourusername/ailabs-llm-xml-transformer.git
```

### 소스 코드에서 설치

소스 코드를 다운로드하여 설치하는 경우:

```bash
# 저장소 클론
git clone https://github.com/yourusername/ailabs-llm-xml-transformer.git
cd ailabs-llm-xml-transformer

# 의존성 설치
pip install -r requirements.txt

```

## 의존성

이 라이브러리는 다음과 같은 외부 의존성을 가지고 있으며, 설치 시 자동으로 설치됩니다:

```
openai>=0.27.0
python-dotenv>=0.19.0
requests>=2.28.0
```

## 사용 방법

### 명령줄에서 실행

이 도구는 명령줄 인자를 통해 입력 및 출력 경로를 지정하여 실행합니다:

```bash
# 기본 실행 (필수 인자: --input, --output)
xml-transformer --input /path/to/input --output /path/to/output

# 또는 짧은 옵션 사용
xml-transformer -i /path/to/input -o /path/to/output

```

### 옵션 설명

- `--input`, `-i`: 입력 파일 또는 디렉토리 경로 (필수)
- `--output`, `-o`: 출력 디렉토리 경로 (필수)

## 환경 변수 설정

**중요**: 이 도구를 사용하기 위해서는 반드시 `.env` 파일을 생성하고 OpenAI API 키를 설정해야 합니다. `.env` 파일은 보안 정보를 포함하고 있어 Git 저장소에 포함되지 않으므로, 사용자가 직접 생성해야 합니다.

### .env 파일 생성 방법

1. python 디렉토리에서 .env 생성
2. 아래 형식에 맞춰 필요한 환경 변수를 설정합니다.
- OpenAI API 키 (필수)
OPENAI_API_KEY=your_openai_api_key

3. node 디렉토리에서 .env 생성
4. 아래 형식에 맞춰 필요한 환경 변수를 설정합니다.
- STAGING7_URL=puppeteer를 이용할 미캔 스테이징 주소
- EMAIL=your_email
- PASSWORD=your_password
(puppeteer로 미캔에 접근하기 위해서 필수)

### 환경 변수 설명

- `OPENAI_API_KEY`: OpenAI API를 사용하기 위한 API 키입니다. 
- `EMAIL`: 미리캔버스 계정의 이메일 주소입니다.
- `PASSWORD`: 미리캔버스 계정의 비밀번호입니다.

### 주의사항

- `.env` 파일은 절대로 공유하거나 Git 저장소에 커밋하지 마세요.
- 각 개발 환경마다 별도의 `.env` 파일을 생성해야 합니다.
- 환경 변수가 올바르게 설정되지 않으면 도구가 정상적으로 작동하지 않을 수 있습니다.
- 입력 및 출력 경로는 명령줄 인자로만 지정할 수 있으며, 환경 변수로 설정할 수 없습니다.

## 개발 환경 설정

### 필수 요구사항

- Python 3.8 이상
- Node.js 14.0 이상 (Node.js 통합이 필요한 경우)
- npm 6.0 이상 (Node.js 통합이 필요한 경우)

### 의존성 설치

개발을 위한 의존성 설치:

```bash
pip install -r requirements.txt
```

### Node.js 의존성 설치 (필요한 경우)

```bash
cd node
npm install
npm run build
```

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 