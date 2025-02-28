import xml.etree.ElementTree as ET
import json
from services.llm_processor import LLMProcessor

class XMLParser:
    def __init__(self, file_path, llm_processor=None):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.llm_processor = llm_processor

    def process(self, output_path):
        prompted_text_info_list = self.request_prompt()
        self.update_xml(prompted_text_info_list)
        self.save_xml(output_path)
    
    def request_prompt(self):
        """텍스트를 추출하고 시뮬레이션된 응답을 생성"""
        text_info_list = self.extract_text()
        prompted_text_info_list = []

        for text, tbpe_id in text_info_list:
            prompted_text = self.llm_processor.prompt_text(text)
            prompted_text_info_list.append((prompted_text, tbpe_id))
            
        return prompted_text_info_list    
    
    def extract_text(self):
        """XML에서 <SIMPLE_TEXT> 또는 <TEXT> 태그의 텍스트와 TbpeId를 추출"""
        text_tag_info = []

        # SIMPLE_TEXT 태그에서 텍스트와 TbpeId 추출
        for simple_text_tag in self.root.findall(".//SIMPLE_TEXT"):
            text_body = simple_text_tag.find(".//TextBody")
            if text_body is not None and text_body.text:
                try:
                    json_data = json.loads(text_body.text)
                    texts = self.extract_texts_from_json_structure(json_data)
                    tbpe_id = simple_text_tag.get('TbpeId')
                    text_tag_info.extend((text, tbpe_id) for text in texts)
                except json.JSONDecodeError:
                    continue

        # TEXT 태그에서 텍스트와 TbpeId 추출
        for text_tag in self.root.findall(".//TEXT"):
            text = text_tag.text
            tbpe_id = text_tag.get('TbpeId')
            if text is not None:
                text_tag_info.append((text, tbpe_id))

        return text_tag_info

    def extract_texts_from_json_structure(self, json_data):
        """재귀적으로 JSON 구조를 탐색하여 모든 텍스트(t 필드) 추출"""
        text = []
        if isinstance(json_data, list):
            for item in json_data:
                text.extend(self.extract_texts_from_json_structure(item))
        elif isinstance(json_data, dict):
            if "t" in json_data and isinstance(json_data["t"], str):
                text.append(json_data["t"])
            if "c" in json_data:
                text.extend(self.extract_texts_from_json_structure(json_data["c"]))
        return text
        
    def update_xml(self, response_list):
        """시뮬레이션된 응답을 XML에 적용"""
        # 파일 버전 확인 (TEXT 태그가 있는지 SIMPLE_TEXT 태그가 있는지)
        has_text_tag = len(self.root.findall(".//TEXT")) > 0
        has_simple_text_tag = len(self.root.findall(".//SIMPLE_TEXT")) > 0
        
        for prompted_text, tbpe_id in response_list:
            if has_text_tag:
                # TEXT 태그 버전 처리
                self.update_text_tag(prompted_text, tbpe_id)
            elif has_simple_text_tag:
                # SIMPLE_TEXT 태그 버전 처리
                self.update_simple_text_tag(prompted_text, tbpe_id)
            else:
                print(f"지원되지 않는 XML 형식입니다. TbpeId: {tbpe_id}")

    def update_text_tag(self, prompted_text, tbpe_id):
        """TEXT 태그 업데이트 및 TextData 태그 삭제"""
        for text_tag in self.root.findall(".//TEXT"):
            if text_tag.get('TbpeId') == tbpe_id:
                text_tag.text = prompted_text
                # TextData 태그 삭제
                self.remove_renderPos_tag(text_tag, "TextData")
                print(f"TEXT 태그 업데이트 완료: {tbpe_id}")

    def update_simple_text_tag(self, prompted_text, tbpe_id):
        """SIMPLE_TEXT 태그 업데이트 및 RenderPos 태그 삭제"""
        for simple_text_tag in self.root.findall(".//SIMPLE_TEXT"):
            if simple_text_tag.get('TbpeId') == tbpe_id:
                text_body = simple_text_tag.find("TextBody")
                if text_body is not None:
                    try:
                        # 기존 JSON 구조를 파싱
                        json_data = json.loads(text_body.text)
                        # JSON 구조 내의 특정 텍스트를 업데이트
                        self.update_text_json_structure(json_data, prompted_text)
                        # 업데이트된 JSON 구조를 다시 문자열로 변환하여 저장
                        text_body.text = json.dumps(json_data, ensure_ascii=False)
                        
                        # RenderPos 태그 삭제
                        self.remove_renderPos_tag(simple_text_tag, "RenderPos")
                        print(f"SIMPLE_TEXT 태그 업데이트 완료: {tbpe_id}")
                    except json.JSONDecodeError as e:
                        print(f"JSON 파싱 오류: {e}")
                        continue

    def update_text_json_structure(self, json_data, new_text):
        """JSON 구조 내의 텍스트를 업데이트"""
        if isinstance(json_data, dict):
            # "c" 키가 있고 그 값이 리스트인 경우
            if "c" in json_data and isinstance(json_data["c"], list):
                # "c" 리스트의 각 항목에 대해
                for i, item in enumerate(json_data["c"]):
                    # 항목이 문자열인 경우 업데이트
                    if isinstance(item, str):
                        json_data["c"][i] = new_text
                    # 항목이 딕셔너리나 리스트인 경우 재귀적으로 처리
                    else:
                        self.update_text_json_structure(item, new_text)
            # "t" 키가 "r"이고 "c" 키가 있는 경우 (텍스트 배열을 포함하는 특별한 경우)
            elif "t" in json_data and json_data["t"] == "r" and "c" in json_data and isinstance(json_data["c"], list):
                # 텍스트 배열을 새 텍스트로 업데이트
                json_data["c"] = [new_text]
        # json_data가 리스트인 경우
        elif isinstance(json_data, list):
            # 리스트의 각 항목에 대해 재귀적으로 처리
            for item in json_data:
                if isinstance(item, (dict, list)):
                    self.update_text_json_structure(item, new_text)

    def remove_renderPos_tag(self, parent_tag, renderPos_tag):
        """랜더링 태그 삭제"""
        child_tag = parent_tag.find(renderPos_tag)
        if child_tag is not None:
            parent_tag.remove(child_tag)
            print(f"{renderPos_tag} 태그 삭제 완료")

    def save_xml(self, output_path):
        """수정된 XML 저장"""
        self.tree.write(output_path, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    parser = XMLParser("input.xml")
    texts = parser.extract_text()
    print(texts)
    parser.save_xml("output.xml")
