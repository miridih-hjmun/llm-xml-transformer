import { MiricanvasBrowser } from './puppeteer/browser';
import { MiricanvasPage } from './puppeteer/page';
import * as dotenv from 'dotenv';
import * as fs from 'fs';
const path = require('path');

// 명령줄 인자 파싱
const args = process.argv.slice(2);
let dataFilePath = '';
let outputPath = '';

// 명령줄 인자 처리
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--data' && i + 1 < args.length) {
    dataFilePath = args[i + 1];
    i++;
  } else if (args[i] === '--output' && i + 1 < args.length) {
    outputPath = args[i + 1];
    i++;
  }
}

// 환경 변수 로드
console.log('현재 디렉토리 경로:', __dirname);
const envPath = path.resolve(__dirname, '../.env');
console.log('.env 파일 경로:', envPath);
dotenv.config({ path: envPath });

// 환경 변수 로드 상태 확인
console.log('환경 변수 로드 상태:', {
  EMAIL: process.env.EMAIL ? '설정됨' : '설정되지 않음',
  PASSWORD: process.env.PASSWORD ? '설정됨' : '설정되지 않음',
  STAGING7_URL: process.env.STAGING7_URL ? '설정됨' : '설정되지 않음'
});

/**
 * Python에서 전달받은 XML 처리 결과 데이터 로드
 */
function loadXmlResults(filePath: string): any {
  try {
    if (!fs.existsSync(filePath)) {
      throw new Error(`데이터 파일을 찾을 수 없습니다: ${filePath}`);
    }
    
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(fileContent);
  } catch (error) {
    console.error('XML 결과 데이터 로드 중 오류 발생:', error);
    throw error;
  }
}

/**
 * 메인 함수 - 앱 실행 시작점
 */
async function main() {
  console.log('미리캔버스 스테이징 환경 접속 및 XML 처리를 시작합니다.');
  
  // 명령줄 인자 확인
  if (!dataFilePath || !outputPath) {
    console.error('오류: --data 및 --output 인자가 필요합니다.');
    console.log('사용법: node app.js --data <xml_results.json 경로> --output <출력 디렉토리>');
    process.exit(1);
  }
  
  console.log(`데이터 파일: ${dataFilePath}`);
  console.log(`출력 디렉토리: ${outputPath}`);
  
  // XML 처리 결과 데이터 로드
  let xmlResults;
  try {
    xmlResults = loadXmlResults(dataFilePath);
    console.log(`XML 처리 결과 로드 완료: ${xmlResults.processed_files.length}개 파일 처리됨`);
  } catch (error) {
    console.error('XML 결과 데이터 로드 실패:', error);
    process.exit(1);
  }
  
  const browser = new MiricanvasBrowser();
  
  try {
    // 브라우저 시작 및 페이지 로드 (헤드리스 모드 여부 선택)
    // 디버깅이 필요하면 false로 설정하여 GUI 모드로 실행
    const headless = process.env.HEADLESS === 'true';
    const page = await browser.launch(headless);
    
    // 페이지 로드 확인
    console.log('페이지 타이틀:', await page.title());
    
    // MiricanvasPage 인스턴스 생성
    const miriPage = new MiricanvasPage(page);
    
    // XML 파일 처리
    for (const processedFile of xmlResults.processed_files) {
      console.log(`파일 처리 중: ${processedFile.file} (번호: ${processedFile.page_idx})`);
      
      // XML 문자열 직접 사용 (파일 읽기 대신)
      if (processedFile.positive_xml && processedFile.negative_xml) {
        // 메모리에서 직접 XML 문자열 처리
        await miriPage.processXmlString(
          processedFile.positive_xml, 
          processedFile.negative_xml, 
          processedFile.page_idx
        );
      } else {
        console.warn(`경고: ${processedFile.file}에 XML 문자열이 없습니다.`);
      }
    }
    
    console.log('모든 작업이 성공적으로 완료되었습니다.');
  } catch (error) {
    console.error('작업 중 오류가 발생했습니다:', error);
  } finally {
    // 브라우저 종료
    await browser.close();
  }
}

// 앱 실행
main().catch(error => {
  console.error('앱 실행 중 예상치 못한 오류가 발생했습니다:', error);
  process.exit(1);
});
