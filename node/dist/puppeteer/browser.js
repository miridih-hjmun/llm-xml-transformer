"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MiricanvasBrowser = void 0;
const puppeteer_1 = __importDefault(require("puppeteer"));
/**
 * 미리캔버스 스테이징 환경에 접속하기 위한 브라우저 관리 클래스
 */
class MiricanvasBrowser {
    constructor() {
        this.browser = null;
        this.page = null;
    }
    /**
       * 미리캔버스 사이트에 로그인합니다.
       * @private
       */
    async login() {
        if (!process.env.EMAIL || !process.env.PASSWORD) {
            throw new Error('EMAIL 또는 PASSWORD가 설정되지 않았습니다.');
        }
        this.page.setDefaultNavigationTimeout(60000);
        console.log('로그인 버튼을 클릭합니다');
        // await this.captureScreenshot('login_page2.png');
        await this.page.waitForSelector('#__next > div.sc-95e08388-0.ffiSBb > div.sc-a2279643-0.dAsjrO > div.sc-472c6800-0.jPwXFu > div:nth-child(1) > button', { visible: true, timeout: 60000 });
        await this.page.click('#__next > div.sc-95e08388-0.ffiSBb > div.sc-a2279643-0.dAsjrO > div.sc-472c6800-0.jPwXFu > div:nth-child(1) > button');
        console.log('로그인 버튼 클릭 완료.');
        await this.page.waitForSelector('#modal_portal_5 > div > div > div > div.sc-bb5ce5ec-3.cSztrY > div:nth-child(1) > div > div.sc-65378d54-0.cbRqVo > div.sc-971406e4-0.cCQbnd', { visible: true, timeout: 60000 });
        console.log('모달이 나타났습니다. 모달에서 버튼을 클릭합니다');
        await this.page.click('#modal_portal_5 > div > div > div > div.sc-bb5ce5ec-3.cSztrY > div:nth-child(1) > div > div.sc-65378d54-0.cbRqVo > div.sc-971406e4-0.cCQbnd');
        console.log('이메일로 로그인 버튼 클릭 완료.');
        await this.page.waitForSelector('#modal_portal_5 > div > div > div > div.sc-bb5ce5ec-3.cSztrY > div:nth-child(2) > div > form > div:nth-child(1) > div.sc-SQOaL.eMeVEB > input', { visible: true, timeout: 60000 });
        await this.page.type('#modal_portal_5 > div > div > div > div.sc-bb5ce5ec-3.cSztrY > div:nth-child(2) > div > form > div:nth-child(1) > div.sc-SQOaL.eMeVEB > input', process.env.EMAIL);
        console.log('이메일 입력 완료.');
        await this.page.waitForSelector('#modal_portal_5 > div > div > div > div.sc-bb5ce5ec-3.cSztrY > div:nth-child(2) > div > form > div:nth-child(2) > div.sc-SQOaL.eMeVEB > input', { visible: true, timeout: 60000 });
        await this.page.type('#modal_portal_5 > div > div > div > div.sc-bb5ce5ec-3.cSztrY > div:nth-child(2) > div > form > div:nth-child(2) > div.sc-SQOaL.eMeVEB > input', process.env.PASSWORD);
        console.log('비밀번호 입력 완료.');
        await this.page.click('#modal_portal_5 > div > div > div > div.sc-bb5ce5ec-3.cSztrY > div:nth-child(2) > div > form > button');
        console.log('로그인 버튼 클릭 완료.');
        await this.page.waitForSelector('#modal_portal_6 > div > div > div.sc-bb5ce5ec-1.kKvpKG > div > div.sc-1f7c4c9d-2.hWPack > button.sc-elDIKY.fSsWXG', { visible: true, timeout: 120000 });
        await this.page.click('#modal_portal_6 > div > div > div.sc-bb5ce5ec-1.kKvpKG > div > div.sc-1f7c4c9d-2.hWPack > button.sc-elDIKY.fSsWXG');
        console.log('로그인 상태 유지 버튼 클릭 완료.');
    }
    /**
     * 브라우저 인스턴스를 시작하고 스테이징 환경에 접속합니다.
     * @param headless 헤드리스 모드 여부 (기본값: false)
     * @returns 생성된 페이지 객체
     */
    async launch(headless = false) {
        // 브라우저 시작
        this.browser = await puppeteer_1.default.launch({
            headless,
            defaultViewport: null,
            args: [
                // '--no-first-run',
                // '--no-default-browser-check',
                // '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--window-size=1920,1080',
                '--no-sandbox',
                '--disable-gpu'
            ]
        });
        // 새 페이지 생성
        this.page = await this.browser.newPage();
        if (!process.env.STAGING7_URL) {
            throw new Error('STAGING7_URL이 설정되지 않았습니다.');
        }
        // 스테이징 환경으로 이동
        await this.page.goto(process.env.STAGING7_URL, {
            waitUntil: 'domcontentloaded'
        });
        console.log('스테이징 환경에 접속했습니다: staging7.miricanvas.com');
        // 페이지 로드 후 로그인 수행
        await this.login();
        return this.page;
    }
    /**
     * 현재 페이지 객체를 반환합니다.
     */
    getPage() {
        return this.page;
    }
    /**
     * 브라우저를 종료합니다.
     */
    async close() {
        if (this.browser) {
            await this.browser.close();
            this.browser = null;
            this.page = null;
            console.log('브라우저가 종료되었습니다.');
        }
    }
}
exports.MiricanvasBrowser = MiricanvasBrowser;
//# sourceMappingURL=browser.js.map