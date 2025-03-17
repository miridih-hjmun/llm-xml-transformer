import xml.etree.ElementTree as ET
import json
import os
import io
import sys
import re

# workflow.py 파일 경로 설정 (환경 변수 또는 상대 경로 사용)
WORKFLOW_PATH = os.environ.get(
    "WORKFLOW_PATH", 
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "prompt", "ailabs-context-aware-retrieval-eval-dataset", "src")
)

# workflow.py 모듈 경로를 sys.path에 추가
if WORKFLOW_PATH not in sys.path:
    sys.path.append(WORKFLOW_PATH)

# process_text 함수 임포트
from workflow import process_text

class XMLParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()

    def generate_xml_string(self):
        """
        XML 파일을 한 번만 처리하여 positive와 negative 결과를 모두 얻습니다.
        
        Returns:
            tuple: (positive_xml_string, negative_xml_string) - positive와 negative XML 문자열
        """
        # 원본 XML 파일에서 텍스트 추출
        text_info_list = self.extract_text()
        text_list = [text for text, _ in text_info_list]
        tbpe_id_list = [tbpe_id for _, tbpe_id in text_info_list]
        
        if not text_list:
            return "", ""
        
        # 텍스트 리스트를 \\+\\ 구분자로 연결
        combined_text = ""
        for i, text in enumerate(text_list):
            if i > 0:
                combined_text += "\\+\\"
            combined_text += text
        
        # 새 어댑터의 process_text 함수에 결합된 텍스트 전달 (API 한 번만 호출)
        try:
            processed_result = process_text(combined_text)
            print(f"프롬프트 처리 결과: {processed_result}")
        except Exception as e:
            print(f"프롬프트 처리 중 오류 발생: {e}")
            return "", ""
        
        # Positive 결과 처리
        positive_text_info_list = self.extract_processed_texts(processed_result, text_list, tbpe_id_list, "positive")
        self.update_xml(positive_text_info_list)
        positive_xml_string = self.xml_to_string()
        
        # 원본 XML 파일을 다시 로드 (변경된 내용을 초기화)
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()
        
        # Negative 결과 처리
        negative_text_info_list = self.extract_processed_texts(processed_result, text_list, tbpe_id_list, "negative")
        self.update_xml(negative_text_info_list)
        negative_xml_string = self.xml_to_string()
        
        # 원본 XML 파일을 다시 로드 (변경된 내용을 초기화)
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()
        
        return positive_xml_string, negative_xml_string

    def xml_to_string(self):
        """XML 트리를 문자열로 변환"""
        output = io.StringIO()
        self.tree.write(output, encoding='unicode', xml_declaration=True)
        return output.getvalue()

    def extract_processed_texts(self, processed_result, text_list, tbpe_id_list, doc_type="positive"):
        """
        process_text 함수의 결과에서 텍스트를 추출하고 TbpeId와 매핑합니다.
        
        Args:
            processed_result: process_text 함수의 결과 (딕셔너리 형태)
            text_list: 원본 텍스트 리스트
            tbpe_id_list: TbpeId 리스트
            doc_type: 문서 유형 ("positive" 또는 "negative")
            
        Returns:
            list: (텍스트, TbpeId) 튜플의 리스트
        """
        prompted_text_info_list = []
        
        try:
            # 딕셔너리 형태로 결과가 반환된 경우
            if isinstance(processed_result, dict):
                # positive 또는 negative 텍스트 선택
                if doc_type == "negative":
                    processed_text = processed_result.get("hard_negative_document", "")
                else:  # positive
                    processed_text = processed_result.get("positive_document", "")
                
                # 처리된 텍스트를 개행 문자(\n)로 분리
                processed_text_list = processed_text.split("\\+\\")
                processed_text_list = [text.strip() for text in processed_text_list if text.strip()]
                
                # 분리된 텍스트 수가 원본 텍스트 수와 다를 경우
                if len(processed_text_list) != len(text_list):
                    print(f"분리된 텍스트 개수({len(processed_text_list)})와 원래 텍스트 개수({len(text_list)})가 다릅니다.")
                    # 텍스트 수가 더 많은 경우, 원본 텍스트 수에 맞게 조정
                    if len(processed_text_list) > len(text_list):
                        processed_text_list = processed_text_list[:len(text_list)]
                    
                    # 텍스트 수가 더 적은 경우, 부족한 부분은 원본 텍스트로 채움
                    elif len(processed_text_list) < len(text_list):
                        for i in range(len(processed_text_list), len(text_list)):
                            processed_text_list.append(text_list[i])
                else:
                    print(f"분리된 텍스트 개수({len(processed_text_list)})와 원래 텍스트 개수({len(text_list)})가 같습니다.")
                
                # 텍스트와 TbpeId 매핑 (백슬래시 제거 추가)
                for i, (processed_text, tbpe_id) in enumerate(zip(processed_text_list, tbpe_id_list)):
                    # 백슬래시(\) 제거 - 예: \example\ -> example
                    # 개선된 정규식 패턴: 백슬래시 뒤에 오는 문자를 보존하고 백슬래시만 제거
                    # 1. \\+\\ 패턴은 그대로 유지 (구분자)
                    # 2. \\n 패턴은 \n으로 변환 (개행 문자)
                    # 3. 나머지 백슬래시는 제거
                    cleaned_text = processed_text
                    # 개행 문자 처리
                    cleaned_text = re.sub(r'\\n', '\n', cleaned_text)
                    # 백슬래시 제거 (구분자 패턴 제외)
                    cleaned_text = re.sub(r'\\(?![+\\])', '', cleaned_text)
                    # 남은 \\+\\ 구분자 제거
                    cleaned_text = re.sub(r'\\[+]\\', '', cleaned_text)
                    
                    prompted_text_info_list.append((cleaned_text, tbpe_id))
                    print(f"프롬프트된 텍스트 {i+1}: {cleaned_text}")
            
            # 딕셔너리가 아닌 경우 (문자열인 경우)
            else:
                # 원본 텍스트 유지
                print("딕셔너리가 아닌 경우 원본 텍스트를 유지합니다.")
                for i, (text, tbpe_id) in enumerate(zip(text_list, tbpe_id_list)):
                    # 백슬래시(\) 제거 - 개선된 방식 적용
                    cleaned_text = text
                    # 개행 문자 처리
                    cleaned_text = re.sub(r'\\n', '\n', cleaned_text)
                    # 백슬래시 제거 (구분자 패턴 제외)
                    cleaned_text = re.sub(r'\\(?![+\\])', '', cleaned_text)
                    # 남은 \\+\\ 구분자 제거
                    cleaned_text = re.sub(r'\\[+]\\', '', cleaned_text)
                    
                    prompted_text_info_list.append((cleaned_text, tbpe_id))
                    print(f"원본 텍스트 {i+1}: {cleaned_text}")
        
        except Exception as e:
            # 오류 발생 시 원본 텍스트 유지
            print(f"오류 발생: {e}")
        
        return prompted_text_info_list
    
    def extract_text(self):
        """XML에서 <SIMPLE_TEXT> 또는 <TEXT> 태그의 텍스트와 TbpeId를 추출하고 형식을 변환합니다."""
        text_tag_info = []

        # SIMPLE_TEXT 태그에서 텍스트와 TbpeId 추출
        for simple_text_tag in self.root.findall(".//SIMPLE_TEXT"):
            text_body = simple_text_tag.find(".//TextBody")
            if text_body is not None and text_body.text:
                try:
                    json_data = json.loads(text_body.text)
                    texts = self.extract_texts_from_json_structure(json_data)
                    tbpe_id = simple_text_tag.get('TbpeId')
                    
                    # 텍스트 리스트가 비어있지 않은 경우에만 처리
                    if texts:
                        # 텍스트 리스트를 공백으로 결합
                        combined_text = ' '.join([text for text in texts if text is not None])
                        
                        # \xa0 문자를 공백으로 대체
                        combined_text = combined_text.replace('\xa0', ' ')
                        
                        # 개행 문자를 \\n 로 대체
                        formatted_text = combined_text.replace("\n", "\\n")
                        
                        # 결합된 텍스트와 TbpeId를 리스트에 추가
                        text_tag_info.append((formatted_text, tbpe_id))
                except json.JSONDecodeError:
                    continue

        # TEXT 태그에서 텍스트와 TbpeId 추출
        for text_tag in self.root.findall(".//TEXT"):
            # TEXT 태그 내부의 Text 하위 태그 찾기
            text_subtag = text_tag.find("Text")
            if text_subtag is not None and text_subtag.text is not None:
                text = text_subtag.text
            else:
                # 하위 태그가 없거나 텍스트가 없으면 TEXT 태그 자체의 텍스트 사용
                text = text_tag.text
            
            tbpe_id = text_tag.get('TbpeId')
            if text is not None:
                # \xa0 문자를 공백으로 대체
                text = text.replace('\xa0', ' ')
                
                # 개행 문자를 \\n 로 대체
                formatted_text = text.replace("\n", "\\n")
                text_tag_info.append((formatted_text, tbpe_id))

        return text_tag_info

    def extract_texts_from_json_structure(self, json_data):
        """
        재귀적으로 JSON 구조를 탐색하여 텍스트 추출
        SIMPLE_TEXT 태그의 TextBody에 있는 JSON 구조에서 실제 텍스트만 추출

        """
        # 결과 텍스트를 저장할 리스트
        result = []
        
        # 리스트인 경우 각 항목에 대해 재귀 호출
        if isinstance(json_data, list):
            for item in json_data:
                result.extend(self.extract_texts_from_json_structure(item))
        
        # 딕셔너리인 경우
        elif isinstance(json_data, dict):
            # 텍스트 노드 처리 ("t"가 "r"이고 "c"에 문자열 리스트가 있는 경우)
            if json_data.get("t") == "r" and "c" in json_data and isinstance(json_data["c"], list):
                # "c" 리스트의 각 항목이 문자열인 경우 텍스트로 추가
                for item in json_data["c"]:
                    if isinstance(item, str):
                        result.append(item)
                    else:
                        # 문자열이 아닌 경우 재귀 처리
                        result.extend(self.extract_texts_from_json_structure(item))
            
            # 다른 노드는 "c" 필드만 재귀적으로 처리
            elif "c" in json_data:
                result.extend(self.extract_texts_from_json_structure(json_data["c"]))
        
        return result
        
    def update_xml(self, text_info_list):
        """
        XML을 응답 리스트를 기반으로 업데이트합니다.
        
        Args:
            response_list: (텍스트, TbpeId) 튜플의 리스트
            
        Returns:
            Element: 업데이트된 XML 루트 요소
        """
        # TEXT 태그 확인
        text_tags = self.root.findall(".//TEXT")
        simple_text_tags = self.root.findall(".//SIMPLE_TEXT")
        
        if not text_tags and not simple_text_tags:
            return self.root
        
        # 응답 리스트를 TbpeId를 키로 하는 딕셔너리로 변환
        text_info_dict = {}
        for text, tbpe_id in text_info_list:
            text_info_dict[tbpe_id] = text
        
        # TEXT 태그 업데이트
        for text_tag in text_tags:
            tbpe_id = text_tag.get("TbpeId")
            if tbpe_id in text_info_dict:
                self.update_text_tag(text_tag, text_info_dict[tbpe_id])
        
        # SIMPLE_TEXT 태그 업데이트
        for simple_text_tag in simple_text_tags:
            tbpe_id = simple_text_tag.get("TbpeId")
            if tbpe_id in text_info_dict:
                self.update_simple_text_tag(simple_text_tag, text_info_dict[tbpe_id])
        
        return self.root
    
    def update_text_tag(self, text_tag, new_text):
        """
        TEXT 태그의 내용을 업데이트합니다.
        
        Args:
            text_tag: TEXT 태그 요소
            new_text: 새로운 텍스트
            
        Returns:
            None
        """
        # Text 태그 찾기
        text_node = text_tag.find("Text")
        
        # Text 태그가 있으면 내용 업데이트
        if text_node is not None:
            text_node.text = new_text
            # TextData 태그와 RenderPos 태그 제거
            self.remove_textData_tag(text_tag)
            self.remove_renderPos_tag(text_tag)
        else:
            # Text 태그가 없으면 TEXT 태그 직접 업데이트
            text_tag.text = new_text
    
    def update_simple_text_tag(self, simple_text_tag, new_text):
        """
        SIMPLE_TEXT 태그의 내용을 업데이트합니다.
        
        Args:
            simple_text_tag: SIMPLE_TEXT 태그 요소
            new_text: 새로운 텍스트
            
        Returns:
            None
        """
        tbpe_id = simple_text_tag.get("TbpeId")
        
        # TextBody 태그 찾기
        text_body = simple_text_tag.find("TextBody")
        
        if text_body is None:
            print(f"TextBody 태그를 찾을 수 없음 (TbpeId: {tbpe_id})")
            return
        
        try:
            # TextBody 태그의 JSON 데이터 파싱
            json_data = json.loads(text_body.text)
            
            # JSON 구조 업데이트 (기존 메서드 활용)
            updated_json = self.update_text_json_structure(json_data, new_text)
            
            # 업데이트된 JSON 데이터를 문자열로 변환하여 설정
            text_body.text = json.dumps(updated_json, ensure_ascii=False)
            
            # RenderPos 태그 제거 (XML 태그로서 제거)
            render_pos = simple_text_tag.find("RenderPos")
            if render_pos is not None:
                simple_text_tag.remove(render_pos)
                print(f"RenderPos 태그 제거 완료 (TbpeId: {tbpe_id})")
            
        except (json.JSONDecodeError, TypeError) as e:
            # JSON 파싱 오류 시 텍스트 직접 설정
            print(f"JSON 파싱 오류: {e}")
    
    def update_text_json_structure(self, json_data, new_text):
        """
        JSON 구조에서 텍스트를 업데이트합니다.
        두 가지 구조를 모두 처리합니다:
        1. 최상위 c키 -> 여러 문단 -> 텍스트 노드
        2. 최상위 c키 -> 첫 번째 항목 -> c키 -> 텍스트 노드
        
        Args:
            json_data: JSON 데이터 (딕셔너리)
            new_text: 새로운 텍스트
            
        Returns:
            dict: 업데이트된 JSON 데이터
        """
        # 최상위 c키가 있고 리스트인지 확인
        if "c" in json_data and isinstance(json_data["c"], list):
            # 구조 1: 모든 문단 처리
            for paragraph in json_data["c"]:
                # 문단이 딕셔너리인지 확인
                if isinstance(paragraph, dict) and "c" in paragraph and isinstance(paragraph["c"], list):
                    # 문단 내 텍스트 노드 찾기
                    for i, item in enumerate(paragraph["c"]):
                        # "t"가 "r"이고 "c"가 리스트인 항목 찾기 (텍스트 노드)
                        if isinstance(item, dict) and item.get("t") == "r" and "c" in item and isinstance(item["c"], list):
                            # 텍스트 노드의 내용을 새 텍스트로 업데이트
                            item["c"] = [new_text]
                            # 첫 번째 텍스트 노드만 업데이트하고 나머지는 유지
                            break
            
            # 구조 2: 첫 번째 항목이 딕셔너리인지 확인 (이전 구조 지원)
            if len(json_data["c"]) > 0 and isinstance(json_data["c"][0], dict):
                # 첫 번째 항목의 c키가 있고 리스트인지 확인
                if "c" in json_data["c"][0] and isinstance(json_data["c"][0]["c"], list):
                    # c키 리스트에서 딕셔너리 항목 찾기
                    dict_nodes = []
                    for i, item in enumerate(json_data["c"][0]["c"]):
                        if isinstance(item, dict) and "c" in item and isinstance(item["c"], list):
                            dict_nodes.append(i)
                    
                    # 딕셔너리 노드가 있으면
                    if dict_nodes:
                        # 첫 번째 딕셔너리 노드 업데이트
                        first_index = dict_nodes[0]
                        json_data["c"][0]["c"][first_index]["c"] = [new_text]
        
        return json_data
    
    def remove_textData_tag(self, parent_tag):
        """
        TextData 태그를 제거합니다.
        
        Args:
            parent_tag: 부모 태그 요소
            
        Returns:
            None
        """
        text_data_tag = parent_tag.find("TextData")
        if text_data_tag is not None:
            parent_tag.remove(text_data_tag)
    
    def remove_renderPos_tag(self, parent_tag):
        """
        RenderPos 태그를 제거합니다.
        
        Args:
            parent_tag: 부모 태그 요소
            
        Returns:
            None
        """
        render_pos_tag = parent_tag.find("RenderPos")
        if render_pos_tag is not None:
            parent_tag.remove(render_pos_tag)

    def save_xml(self, output_path):
        """수정된 XML 저장"""
        self.tree.write(output_path, encoding="utf-8", xml_declaration=True)
