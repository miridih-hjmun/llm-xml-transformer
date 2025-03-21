"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.MiricanvasPage = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * 미리캔버스 페이지 조작을 위한 유틸리티 클래스
 */
class MiricanvasPage {
    constructor(page) {
        this.page = page;
    }
    /**
       * XML 문자열을 직접 처리합니다 (파일 읽기 없이 메모리에서 처리)
       *
       * @param positiveXml positive XML 문자열
       * @param negativeXml negative XML 문자열
       * @param pageIdx 페이지 인덱스
       */
    async processXmlString(positiveXml, negativeXml, pageIdx) {
        try {
            console.log(`XML 문자열 처리 중 (페이지 인덱스: ${pageIdx})...`);
            // 미리캔버스 스테이징 환경 접속
            await this.navigateToStaging();
            // 업데이트된 XML 문자열을 저장할 변수
            let updatedPositiveXml = '';
            let updatedNegativeXml = '';
            // XML 문자열 배열과 타입 배열 생성
            const xmlStrings = [positiveXml, negativeXml];
            const types = ['positive', 'negative'];
            // 각 XML 문자열을 순차적으로 처리
            for (let i = 0; i < xmlStrings.length; i++) {
                const xmlString = xmlStrings[i];
                const type = types[i];
                console.log(`${type.charAt(0).toUpperCase() + type.slice(1)} XML 처리 중...`);
                try {
                    // XML 문자열 로드
                    await this.loadXmlString(xmlString);
                    // 최신화된 XML 문자열 내보내기
                    const updatedXmlString = await this.exportPageSheetXmlString({ pageIdx: 0 });
                    // 타입에 따라 업데이트된 XML 저장
                    if (type === 'positive') {
                        updatedPositiveXml = updatedXmlString;
                    }
                    else {
                        updatedNegativeXml = updatedXmlString;
                    }
                    // 이미지 렌더링 및 저장
                    await this.renderAndSaveImage(pageIdx, type);
                }
                catch (error) {
                    console.error(`${type} XML 처리 중 오류 발생: ${error}`);
                    throw error;
                }
            }
            // 업데이트된 XML 파일 저장
            if (updatedPositiveXml && updatedNegativeXml) {
                await this.saveXmlFile(updatedPositiveXml, updatedNegativeXml, pageIdx);
            }
            console.log(`페이지 인덱스 ${pageIdx}의 XML 처리 완료`);
        }
        catch (error) {
            console.error(`XML 문자열 처리 중 오류 발생: ${error}`);
            throw error;
        }
    }
    /**
      * XML 파일을 처리합니다
      *
      * @param positiveXmlPath positive XML 파일 경로
      * @param negativeXmlPath negative XML 파일 경로
      */
    async processXmlFile(positiveXmlPath, negativeXmlPath) {
        try {
            console.log(`XML 파일 처리 중: ${path.basename(positiveXmlPath)}, ${path.basename(negativeXmlPath)}`);
            // XML 파일 읽기
            const positiveXml = fs.readFileSync(positiveXmlPath, 'utf-8');
            const negativeXml = fs.readFileSync(negativeXmlPath, 'utf-8');
            // 파일명에서 페이지 인덱스 추출
            const pageIdx = path.basename(positiveXmlPath).split('_')[0];
            // XML 문자열 처리 메서드 호출
            await this.processXmlString(positiveXml, negativeXml, pageIdx);
        }
        catch (error) {
            console.error(`XML 파일 처리 중 오류 발생: ${error}`);
            throw error;
        }
    }
    /**
       * XML 파일을 저장합니다
       *
       * @param positiveXml positive XML 문자열
       * @param negativeXml negative XML 문자열
       * @param pageIdx 페이지 인덱스
       */
    async saveXmlFile(positiveXml, negativeXml, pageIdx) {
        try {
            // 명령줄 인자로 전달된 출력 경로 사용 (환경 변수로 설정됨)
            const outputDir = process.env.OUTPUT_DIR || './output';
            // 페이지별 result 디렉토리 생성
            const resultDir = path.join(outputDir, 'result', pageIdx);
            fs.mkdirSync(resultDir, { recursive: true });
            // XML 파일 저장 (파일명 앞에 페이지 인덱스 추가)
            const positiveXmlPath = path.join(resultDir, `${pageIdx}_positive.xml`);
            const negativeXmlPath = path.join(resultDir, `${pageIdx}_negative.xml`);
            fs.writeFileSync(positiveXmlPath, positiveXml, 'utf-8');
            fs.writeFileSync(negativeXmlPath, negativeXml, 'utf-8');
            console.log(`XML 파일 저장 완료: ${resultDir}`);
        }
        catch (error) {
            console.error(`XML 파일 저장 중 오류 발생: ${error}`);
            throw error;
        }
    }
    /**
     * 미리캔버스 스테이징 환경에 접속합니다
     */
    async navigateToStaging() {
        const stagingUrl = process.env.STAGING7_URL || 'https://staging7.miricanvas.com';
        // 이미 로그인되어 있는지 확인
        const currentUrl = this.page.url();
        if (currentUrl.includes('miricanvas.com') && !currentUrl.includes('login')) {
            console.log('이미 미리캔버스에 접속되어 있습니다.');
            return;
        }
        console.log(`미리캔버스 스테이징 환경에 접속 중: ${stagingUrl}`);
        await this.page.goto(stagingUrl, { waitUntil: 'networkidle0' });
        // 로그인 페이지인지 확인
        const isLoginPage = await this.page.evaluate(() => {
            return window.location.href.includes('login');
        });
        if (isLoginPage) {
            await this.login();
        }
    }
    /**
     * 미리캔버스에 로그인합니다
     */
    async login() {
        const email = process.env.EMAIL;
        const password = process.env.PASSWORD;
        if (!email || !password) {
            throw new Error('로그인을 위한 이메일 또는 비밀번호가 설정되지 않았습니다.');
        }
        console.log(`${email} 계정으로 로그인 중...`);
        // 이메일 입력
        await this.page.type('input[type="email"]', email);
        // 비밀번호 입력
        await this.page.type('input[type="password"]', password);
        // 로그인 버튼 클릭
        await this.page.click('button[type="submit"]');
        // 로그인 완료 대기
        await this.page.waitForNavigation({ waitUntil: 'networkidle0' });
        console.log('로그인 완료');
    }
    /**
     * XML 문자열을 로드합니다
     *
     * @param xmlString XML 문자열
     */
    async loadXmlString(xmlString) {
        await this.page.evaluate(async (xml) => {
            await window.loadSheetByXmlString(xml);
        }, xmlString);
        console.log('XML 문자열이 로드되었습니다.');
    }
    /**
     * 현재 로드된 XML을 렌더링하고 이미지로 저장합니다
     *
     * @param pageIdx 페이지 인덱스
     * @param type 이미지 타입 (positive 또는 negative)
     */
    async renderAndSaveImage(pageIdx, type) {
        // 렌더링 옵션
        const renderOptions = {
            scale: 1,
            backgroundOpacityType: 'ONLY_WHITE'
        };
        // renderXmlString 메서드를 활용하여 페이지 렌더링
        const imageDataUrl = await this.renderXmlString(renderOptions);
        // 이미지 저장 경로 - XML 파일과 동일한 폴더에 저장 (파일명 앞에 페이지 인덱스 추가)
        const outputDir = process.env.OUTPUT_DIR || './output';
        const resultDir = path.join(outputDir, 'result', pageIdx);
        const imagePath = path.join(resultDir, `${pageIdx}_${type}.png`);
        // 디렉토리 생성
        fs.mkdirSync(resultDir, { recursive: true });
        // 이미지 저장
        const base64Data = imageDataUrl.replace(/^data:image\/png;base64,/, '');
        fs.writeFileSync(imagePath, Buffer.from(base64Data, 'base64'));
        console.log(`이미지 저장 완료: ${imagePath}`);
    }
    /**
     * 페이지가 로드될 때까지 기다립니다.
     * @param timeout 타임아웃 (밀리초)
     */
    async waitForPageLoad(timeout = 30000) {
        await this.page.waitForFunction(() => document.readyState === 'complete', { timeout });
        console.log('페이지가 로드되었습니다.');
    }
    /**
     * 페이지를 렌더링하고 결과를 반환합니다.
     * @param options 렌더링 옵션
     * @returns 렌더링된 결과 (일반적으로 이미지 데이터 URL)
     */
    async renderXmlString(options) {
        return await this.page.evaluate(async (opts) => {
            if (typeof window.renderPage !== 'function') {
                throw new Error('renderPage 함수를 찾을 수 없음');
            }
            return await window.renderPage(opts);
        }, options);
    }
    /**
     * 페이지 시트를 XML 문자열로 내보냅니다.
     * @param options 내보내기 옵션
     * @returns XML 문자열
     */
    async exportPageSheetXmlString(options) {
        const xmlString = await this.page.evaluate(async (opts) => {
            return window.exportPageSheetXmlString(opts);
        }, options);
        console.log('페이지 시트가 XML 문자열로 내보내졌습니다.');
        return xmlString;
    }
}
exports.MiricanvasPage = MiricanvasPage;
//# sourceMappingURL=page.js.map