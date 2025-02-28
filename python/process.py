import os
from services.llm_processor import LLMProcessor
from services.xml_processor import XMLParser

def process():
    # 테스트 모드로 LLMProcessor 인스턴스 생성
    llm_processor = LLMProcessor(test_mode=True)

    # 입력 경로 설정 (파일 또는 디렉토리)
    input_path = "/Users/munhyeokjun/Desktop/document/project/ailabs-llm-xml-transformer/data_xml_query_modified/1395456_tib5URoXuz_canvas_context.xml"
    output_directory_path = "/Users/munhyeokjun/Downloads"

    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_directory_path):
        os.makedirs(output_directory_path)

    # 입력 경로가 디렉토리인지 파일인지 확인
    if os.path.isdir(input_path):
        # 디렉토리인 경우 모든 XML 파일 처리
        process_directory(input_path, output_directory_path, llm_processor)
    elif os.path.isfile(input_path) and input_path.endswith(".xml"):
        # 단일 XML 파일인 경우 처리
        process_file(input_path, output_directory_path, llm_processor)
    else:
        print(f"오류: 입력 경로 '{input_path}'는 유효한 XML 파일 또는 디렉토리가 아닙니다.")

def process_directory(input_directory, output_directory, llm_processor):
    """디렉토리 내의 모든 XML 파일 처리"""
    xml_files = [f for f in os.listdir(input_directory) if f.endswith(".xml")]
    
    if not xml_files:
        print(f"경고: '{input_directory}' 디렉토리에 XML 파일이 없습니다.")
        return
    
    for xml_file in xml_files:
        input_file_path = os.path.join(input_directory, xml_file)
        output_file_path = os.path.join(output_directory, f"processed_{xml_file}")
        
        # XMLParser 인스턴스 생성 및 처리
        parser = XMLParser(input_file_path, llm_processor)
        parser.process(output_file_path)
        print(f"{xml_file} 처리 및 업데이트 완료")

def process_file(input_file, output_directory, llm_processor):
    """단일 XML 파일 처리"""
    file_name = os.path.basename(input_file)
    output_file_path = os.path.join(output_directory, f"processed_{file_name}")
    
    # XMLParser 인스턴스 생성 및 처리
    parser = XMLParser(input_file, llm_processor)
    parser.process(output_file_path)
    print(f"{file_name} 처리 및 업데이트 완료")