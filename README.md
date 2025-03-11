# XML 변환 및 LLM 처리 도구

Python과 Node.js를 통합한 XML 변환 및 LLM 처리 도구입니다.

## 설치 방법

### GitHub에서 직접 설치

```bash
pip install git+https://github.com/yourusername/ailabs-llm-xml-transformer.git
```

## 사용 방법

### 명령줄에서 실행

```bash
xml-transformer --input /path/to/input --output /path/to/output
```

### 옵션 설명

- `--input`, `-i`: 입력 파일 또는 디렉토리 경로 (필수)
- `--output`, `-o`: 출력 디렉토리 경로 (필수)

## 환경 변수 설정

`.env` 파일을 생성하여 다음 환경 변수를 설정

```
# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key

# 미리캔버스 계정 정보
EMAIL=your_email
PASSWORD=your_password


## 개발 환경 설정

### 필수 요구사항

- Python 3.8 이상
- Node.js 14.0 이상
- npm 6.0 이상

### Node.js 의존성 설치

```bash
cd node
npm install
npm run build
``` 