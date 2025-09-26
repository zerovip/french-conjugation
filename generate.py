import fitz  # PyMuPDF
import csv
import re
import json
import csv
import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from copy import deepcopy

@dataclass
class TextElement:
    text: str
    size: float
    bbox: Tuple[float, float, float, float]

class FrenchVerbExtractor:
    def __init__(self, pdf_path: str):
        self.doc = fitz.open(pdf_path)

        # 定义CSV表头
        self.csv_headers = [
            'verbe', 'indice', 'caracterisation',
            # INDICATIF
            'indicatif_present_1s', 'indicatif_present_2s', 'indicatif_present_3s',
            'indicatif_present_1p', 'indicatif_present_2p', 'indicatif_present_3p',
            'indicatif_passe_compose_1s', 'indicatif_passe_compose_2s', 'indicatif_passe_compose_3s',
            'indicatif_passe_compose_1p', 'indicatif_passe_compose_2p', 'indicatif_passe_compose_3p',
            'indicatif_imparfait_1s', 'indicatif_imparfait_2s', 'indicatif_imparfait_3s',
            'indicatif_imparfait_1p', 'indicatif_imparfait_2p', 'indicatif_imparfait_3p',
            'indicatif_plus_que_parfait_1s', 'indicatif_plus_que_parfait_2s', 'indicatif_plus_que_parfait_3s',
            'indicatif_plus_que_parfait_1p', 'indicatif_plus_que_parfait_2p', 'indicatif_plus_que_parfait_3p',
            'indicatif_passe_simple_1s', 'indicatif_passe_simple_2s', 'indicatif_passe_simple_3s',
            'indicatif_passe_simple_1p', 'indicatif_passe_simple_2p', 'indicatif_passe_simple_3p',
            'indicatif_passe_anterieur_1s', 'indicatif_passe_anterieur_2s', 'indicatif_passe_anterieur_3s',
            'indicatif_passe_anterieur_1p', 'indicatif_passe_anterieur_2p', 'indicatif_passe_anterieur_3p',
            'indicatif_futur_simple_1s', 'indicatif_futur_simple_2s', 'indicatif_futur_simple_3s',
            'indicatif_futur_simple_1p', 'indicatif_futur_simple_2p', 'indicatif_futur_simple_3p',
            'indicatif_futur_anterieur_1s', 'indicatif_futur_anterieur_2s', 'indicatif_futur_anterieur_3s',
            'indicatif_futur_anterieur_1p', 'indicatif_futur_anterieur_2p', 'indicatif_futur_anterieur_3p',
            # CONDITIONNEL
            'conditionnel_present_1s', 'conditionnel_present_2s', 'conditionnel_present_3s',
            'conditionnel_present_1p', 'conditionnel_present_2p', 'conditionnel_present_3p',
            'conditionnel_passe_1s', 'conditionnel_passe_2s', 'conditionnel_passe_3s',
            'conditionnel_passe_1p', 'conditionnel_passe_2p', 'conditionnel_passe_3p',
            # SUBJONCTIF
            'subjonctif_present_1s', 'subjonctif_present_2s', 'subjonctif_present_3s',
            'subjonctif_present_1p', 'subjonctif_present_2p', 'subjonctif_present_3p',
            'subjonctif_passe_1s', 'subjonctif_passe_2s', 'subjonctif_passe_3s',
            'subjonctif_passe_1p', 'subjonctif_passe_2p', 'subjonctif_passe_3p',
            'subjonctif_imparfait_1s', 'subjonctif_imparfait_2s', 'subjonctif_imparfait_3s',
            'subjonctif_imparfait_1p', 'subjonctif_imparfait_2p', 'subjonctif_imparfait_3p',
            'subjonctif_plus_que_parfait_1s', 'subjonctif_plus_que_parfait_2s', 'subjonctif_plus_que_parfait_3s',
            'subjonctif_plus_que_parfait_1p', 'subjonctif_plus_que_parfait_2p', 'subjonctif_plus_que_parfait_3p',
            # IMPERATIF
            'imperatif_present_2s', 'imperatif_present_1p', 'imperatif_present_2p',
            'imperatif_passe_2s', 'imperatif_passe_1p', 'imperatif_passe_2p',
            # INFINITIF
            'infinitif_present', 'infinitif_passe',
            # PARTICIPE
            'participe_present', 'participe_passe'
        ]

        # finished
        self.pdf_position = {
            "indicatif_present": (40, 145, 180, 285),
            "indicatif_passe_compose": (190, 145, 340, 285),
            "indicatif_imparfait": (40, 300, 180, 440),
            "indicatif_plus_que_parfait": (190, 300, 340, 440),
            "indicatif_passe_simple": (40, 460, 180, 600),
            "indicatif_passe_anterieur": (190, 460, 340, 600),
            "indicatif_futur_simple": (40, 615, 180, 760),
            "indicatif_futur_anterieur": (190, 615, 340, 760),
            "conditionnel_present": (40, 770, 180, 920),
            "conditionnel_passe": (190, 770, 340, 920),
            "subjonctif_present": (350, 145, 490, 285),
            "subjonctif_passe": (500, 145, 700, 285),
            "subjonctif_imparfait": (350, 305, 490, 440),
            "subjonctif_plus_que_parfait": (500, 305, 700, 440),
            "imperatif_present": (350, 455, 490, 560),
            "imperatif_passe": (500, 455, 700, 560),
            "infinitif_present": (350, 575, 490, 640),
            "infinitif_passe": (500, 575, 700, 640),
            "participe_present": (350, 655, 490, 740),
            "participe_passe": (500, 655, 700, 740),
        }

    # finished
    def combine_line(self, current_line, elements):
        # 每一行元素先按左端横坐标排序
        current_line.sort(key = lambda x: (x.bbox[0]))

        temp_elem = TextElement(
            text = "",
            size = 0.0,
            bbox = (0.0, 0.0, 0.0, 0.0)
        )

        for text_span in current_line:
            # 计算：当前横坐标左端 - 上一个元素块横坐标右端
            position_diff = text_span.bbox[0] - temp_elem.bbox[2]
            if position_diff > -1 and position_diff < 5:
                # 满足连缀条件，进行连缀合并
                if position_diff < 0.5:
                    temp_elem.text = f"{temp_elem.text}{text_span.text}" # 两个文字块是连着的，直接拼接
                else:
                    temp_elem.text = f"{temp_elem.text} {text_span.text}" # 两个文字块之间有一定间距，并利用这个间距作为空格
                temp_elem.size = max(temp_elem.size, text_span.size)
                temp_elem.bbox = (
                    temp_elem.bbox[0],
                    min(temp_elem.bbox[1], text_span.bbox[1]), # 上边沿纵坐标取两者中较小
                    text_span.bbox[2],
                    max(temp_elem.bbox[3], text_span.bbox[3]) # 下边沿纵坐标取两者中较大
                )
            else:
                # 不满足连缀条件，把 temp_elem 存入 elements
                if temp_elem.text != "":
                    elements.append(deepcopy(temp_elem))
                temp_elem.text = text_span.text
                temp_elem.size = text_span.size
                temp_elem.bbox = text_span.bbox

        if temp_elem.text != "":
            elements.append(deepcopy(temp_elem))

    # finished
    def extract_text_elements(self, page) -> List[TextElement]:
        """提取页面所有文字元素"""
        elements = []
        blocks = page.get_text("dict")
        current_line = []
        current_y_position = 0.0
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        if text:
                            if abs(current_y_position - span["bbox"][1]) > 5:
                                self.combine_line(current_line, elements)
                                current_line = []
                            current_line.append(TextElement(
                                text = text,
                                size = span["size"],
                                bbox = span["bbox"]
                            ))
                            current_y_position = span["bbox"][1]
        if len(current_line) > 0:
            self.combine_line(current_line, elements)

        print(elements)
        return elements

    # doing
    def extract_verb_info(self, page_num: int) -> Optional[Dict]:
        """从单页提取动词信息"""
        page = self.doc[page_num]
        elements = self.extract_text_elements(page)

        if not elements:
            return None

        # 提取基本信息
        verb_info = {}

        # 1. 提取indice (绿色圆圈中的数字)
        verb_info['indice'] = self.extract_indice(elements)

        # 2. 提取动词名称
        verb_info['verbe'] = self.extract_verb_name(elements)

        # 3. 提取特征描述
        verb_info['caracterisation'] = self.extract_caracterisation(elements)

        # 4. 提取变位表格
        conjugations = self.extract_conjugations(elements)
        verb_info.update(conjugations)

        return verb_info

    # finished
    def extract_indice(self, elements: List[TextElement]) -> str:
        """提取左上角绿色圆圈中的数字"""
        for element in elements[:10]:  # 通常在前几个元素中
            if element.text.isdigit() and len(element.text) <= 3:
                return element.text
        return ""

    # finished
    def extract_verb_name(self, elements: List[TextElement]) -> str:
        """提取动词名称（通常是最大的黑色文字）"""
        candidates = []
        for element in elements:
            if (element.size >= 20 and  # 字体较大
                len(element.text) > 3 and  # 长度合理
                element.text.isalpha()):  # 只包含字母
                candidates.append((element.size, element.text))

        if candidates:
            candidates.sort(reverse=True)
            return candidates[0][1]
        return ""

    # todo
    def extract_caracterisation(self, elements: List[TextElement]) -> str:
        """提取动词特征描述"""
        verb_name = self.extract_verb_name(elements)

        for i, element in enumerate(elements):
            if element.text == verb_name and i + 1 < len(elements):
                # 查找动词名称下方的描述
                next_element = elements[i + 1]
                if next_element.bbox[1] > element.bbox[1]:  # 在下方
                    return next_element.text
        return ""

    # todo：按照 self.pdf_position 来提取. for 循环遍历所有的 elements，判断位置
    def extract_conjugations(self, elements: List[TextElement]) -> Dict:
        """提取所有变位"""
        conjugations = {header: "" for header in self.csv_headers[3:]}  # 跳过前3个基本信息字段

        # 定义各个时态的关键词
        tense_keywords = {
            'PRÉSENT': 'present',
            'PASSÉ COMPOSÉ': 'passe_compose',
            'IMPARFAIT': 'imparfait',
            'PLUS-QUE-PARFAIT': 'plus_que_parfait',
            'PASSÉ SIMPLE': 'passe_simple',
            'PASSÉ ANTÉRIEUR': 'passe_anterieur',
            'FUTUR SIMPLE': 'futur_simple',
            'FUTUR ANTÉRIEUR': 'futur_anterieur',
            'CONDITIONNEL PRÉSENT': 'conditionnel_present',
            'CONDITIONNEL PASSÉ': 'conditionnel_passe'
        }

        # 定义人称模式
        person_patterns = [
            (r'^je\s+', '1s'), (r'^j\'', '1s'),
            (r'^tu\s+', '2s'),
            (r'^il/elle\s+', '3s'), (r'^qu\'il/elle\s+', '3s'),
            (r'^nous\s+', '1p'), (r'^que nous\s+', '1p'),
            (r'^vous\s+', '2p'), (r'^que vous\s+', '2p'),
            (r'^ils/elles\s+', '3p'), (r'^qu\'ils/elles\s+', '3p'),
            (r'^que je\s+', '1s'), (r'^que j\'', '1s'),
            (r'^que tu\s+', '2s')
        ]

        current_mode = ""
        current_tense = ""

        i = 0
        while i < len(elements):
            element = elements[i]
            text = element.text.upper()

            # 识别语态
            if "INDICATIF" in text:
                current_mode = "indicatif"
            elif "SUBJONCTIF" in text:
                current_mode = "subjonctif"
            elif "IMPÉRATIF" in text:
                current_mode = "imperatif"
            elif "INFINITIF" in text:
                current_mode = "infinitif"
            elif "PARTICIPE" in text:
                current_mode = "participe"

            # 识别时态
            for keyword, tense_key in tense_keywords.items():
                if keyword in text:
                    current_tense = tense_key
                    break

            # 提取变位
            if current_mode and element.text.strip():

                if current_mode == "infinitif":
                    if "PRÉSENT" in elements[max(0, i-2):i+3]:
                        conjugations['infinitif_present'] = element.text
                    elif "PASSÉ" in [e.text.upper() for e in elements[max(0, i-2):i+3]]:
                        conjugations['infinitif_passe'] = element.text

                elif current_mode == "participe":
                    if "PRÉSENT" in [e.text.upper() for e in elements[max(0, i-2):i+3]]:
                        conjugations['participe_present'] = element.text
                    elif "PASSÉ" in [e.text.upper() for e in elements[max(0, i-2):i+3]]:
                        conjugations['participe_passe'] = element.text

                elif current_mode == "imperatif":
                    # 命令式特殊处理
                    if current_tense:
                        if not any(pattern[0] for pattern in person_patterns if re.match(pattern[0], element.text.lower())):
                            # 简单形式的命令式
                            if i + 2 < len(elements):
                                conjugations[f'{current_mode}_{current_tense}_2s'] = element.text
                                conjugations[f'{current_mode}_{current_tense}_1p'] = elements[i+1].text
                                conjugations[f'{current_mode}_{current_tense}_2p'] = elements[i+2].text
                                i += 2

                else:
                    # 其他语态的人称变位
                    for pattern, person in person_patterns:
                        if re.match(pattern, element.text.lower()):
                            if current_mode and current_tense:
                                # 提取动词部分（去除人称代词）
                                verb_part = re.sub(pattern, '', element.text, flags=re.IGNORECASE).strip()
                                if verb_part:
                                    field_name = f'{current_mode}_{current_tense}_{person}'
                                    if field_name in conjugations:
                                        conjugations[field_name] = verb_part
                            break

            i += 1

        return conjugations

    def extract_all_verbs(self, start_page: int = 9, end_page: int = 119) -> List[Dict]:
        """提取所有动词（跳过52、53页）"""
        all_verbs = []

        for page_num in range(start_page, end_page + 1):
            if page_num in [51, 52]:  # PDF页码从0开始，所以52、53页对应51、52
                continue

            print(f"正在处理第 {page_num + 1} 页...")

            try:
                verb_info = self.extract_verb_info(page_num)
                if verb_info and verb_info.get('verbe'):
                    all_verbs.append(verb_info)
                    print(f"  提取动词: {verb_info['verbe']}")
            except Exception as e:
                print(f"  处理第 {page_num + 1} 页时出错: {e}")

        return all_verbs

    def save_to_csv(self, verbs: List[Dict], output_file: str):
        """保存到CSV文件"""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_headers)
            writer.writeheader()

            for verb in verbs:
                # 确保所有字段都存在
                row = {header: verb.get(header, "") for header in self.csv_headers}
                writer.writerow(row)

    def close(self):
        """关闭文档"""
        self.doc.close()

class CSVAttributeManager:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = {}
        self.elements = []
        self.attributes = []
        self._load_data()

    def _load_data(self):
        """从CSV文件加载数据到内存"""
        if not os.path.exists(self.csv_file):
            # 如果文件不存在，创建空的数据结构
            self.data = {}
            self.elements = []
            self.attributes = []
            return

        with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)

            if not rows:
                self.data = {}
                self.elements = []
                self.attributes = []
                return

            # 第一行是属性名（第一列为空）
            self.attributes = rows[0][1:]

            # 读取数据
            self.elements = []
            self.data = {}

            for row in rows[1:]:
                if row:  # 跳过空行
                    element = row[0]
                    self.elements.append(element)
                    self.data[element] = {}

                    for i, attr_value in enumerate(row[1:]):
                        if i < len(self.attributes):
                            attr_name = self.attributes[i]
                            self.data[element][attr_name] = attr_value

    def _save_data(self):
        """将数据保存回CSV文件"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # 写入属性行
            writer.writerow([''] + self.attributes)

            # 写入数据行
            for element in self.elements:
                row = [element]
                for attr in self.attributes:
                    row.append(self.data.get(element, {}).get(attr, ''))
                writer.writerow(row)

    def read_attribute(self, element, attribute):
        """读取指定元素的指定属性值"""
        if element not in self.data:
            raise ValueError(f"元素 '{element}' 不存在")

        if attribute not in self.attributes:
            raise ValueError(f"属性 '{attribute}' 不存在")

        return self.data[element].get(attribute, '')

    def write_attribute(self, element, attribute, value):
        """写入指定元素的指定属性值"""
        # 如果元素不存在，创建新元素
        if element not in self.data:
            self.elements.append(element)
            self.data[element] = {}

        # 如果属性不存在，添加到属性列表
        if attribute not in self.attributes:
            self.attributes.append(attribute)
            # 为所有现有元素添加这个新属性
            for existing_element in self.elements:
                if existing_element != element:
                    self.data[existing_element][attribute] = ''

        # 设置属性值
        self.data[element][attribute] = str(value)
        self._save_data()

    def add_element(self, element):
        """添加新元素"""
        if element in self.data:
            raise ValueError(f"元素 '{element}' 已存在")

        self.elements.append(element)
        self.data[element] = {attr: '' for attr in self.attributes}
        self._save_data()

    def add_attribute(self, attribute):
        """添加新属性"""
        if attribute in self.attributes:
            raise ValueError(f"属性 '{attribute}' 已存在")

        self.attributes.append(attribute)
        for element in self.elements:
            self.data[element][attribute] = ''
        self._save_data()

    def get_all_elements(self):
        """获取所有元素列表"""
        return self.elements.copy()

    def get_all_attributes(self):
        """获取所有属性列表"""
        return self.attributes.copy()

    def get_element_data(self, element):
        """获取元素的所有属性数据"""
        if element not in self.data:
            raise ValueError(f"元素 '{element}' 不存在")
        return self.data[element].copy()

    def delete_element(self, element):
        """删除元素"""
        if element not in self.data:
            raise ValueError(f"元素 '{element}' 不存在")

        self.elements.remove(element)
        del self.data[element]
        self._save_data()

    def delete_attribute(self, attribute):
        """删除属性"""
        if attribute not in self.attributes:
            raise ValueError(f"属性 '{attribute}' 不存在")

        self.attributes.remove(attribute)
        for element in self.elements:
            if attribute in self.data[element]:
                del self.data[element][attribute]
        self._save_data()

def main():
    # 使用示例
    pdf_path = "bescherelle.pdf"
    output_csv = "french_verbs_conjugations.csv"

    print("开始提取法语动词变位...")

    extractor = FrenchVerbExtractor(pdf_path)

    try:
        # 提取所有动词
        verbs = extractor.extract_all_verbs(start_page=28, end_page=29)  # 第10页到第120页

        print(f"\n总共提取了 {len(verbs)} 个动词")

        # 保存到CSV
        extractor.save_to_csv(verbs, output_csv)
        print(f"结果已保存到 {output_csv}")

        # 显示前几个动词的信息
        for i, verb in enumerate(verbs[:3]):
            print(f"\n动词 {i+1}: {verb['verbe']}")
            print(f"  序号: {verb['indice']}")
            print(f"  特征: {verb['caracterisation']}")
            print(f"  现在时第一人称单数: {verb.get('indicatif_present_1s', 'N/A')}")

    except Exception as e:
        print(f"处理过程中出错: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
