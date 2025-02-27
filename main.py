from services.xml_processor import XMLParser
from services.llm_processor import LLMProcessor

def main():
    # 테스트 모드로 LLMProcessor 인스턴스 생성
    llm_processor = LLMProcessor(test_mode=True)

    # XMLParser 인스턴스 생성 및 LLMProcessor 주입
    parser = XMLParser("/Users/munhyeokjun/Desktop/document/project/ailabs-llm-xml-transformer/data_xml_query_modified/1395456_tib5URoXuz_canvas_context.xml")
    parser.llm_processor = llm_processor

    # XML 처리 및 업데이트
    parser.process("/Users/munhyeokjun/Downloads/output.xml")
    print("XML 처리 및 업데이트 완료")
    
if __name__ == "__main__":
    main()
