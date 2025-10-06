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
            'participe_present', 'participe_passe', 'participe_passe_compose',
            # OTHERS
            'notes', 'labels',
        ]

        self.pdf_position = {
            'indicatif_present': (40, 145, 180, 285),
            'indicatif_passe_compose': (180, 145, 340, 285),
            'indicatif_imparfait': (40, 300, 180, 440),
            'indicatif_plus_que_parfait': (180, 300, 340, 440),
            'indicatif_passe_simple': (40, 460, 180, 600),
            'indicatif_passe_anterieur': (180, 460, 340, 600),
            'indicatif_futur_simple': (40, 615, 180, 760),
            'indicatif_futur_anterieur': (180, 615, 340, 760),
            'conditionnel_present': (40, 770, 180, 925),
            'conditionnel_passe': (180, 770, 340, 925),
            'subjonctif_present': (350, 145, 500, 285),
            'subjonctif_passe': (495, 145, 700, 285),
            'subjonctif_imparfait': (350, 305, 500, 440),
            'subjonctif_plus_que_parfait': (500, 305, 700, 440),
            'imperatif_present_2s': (350, 500, 500, 525),
            'imperatif_present_1p': (350, 520, 500, 542),
            'imperatif_present_2p': (350, 540, 500, 560),
            'imperatif_passe_2s': (495, 500, 700, 525),
            'imperatif_passe_1p': (495, 520, 700, 542),
            'imperatif_passe_2p': (495, 540, 700, 560),
            'infinitif_present': (350, 623, 500, 650),
            'infinitif_passe': (495, 623, 700, 650),
            'participe_present': (350, 705, 500, 725),
            'participe_passe': (495, 705, 700, 725),
            'participe_passe_compose': (495, 720, 700, 750),
        }

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
            if position_diff > -1 and position_diff < 5 and text_span.text[:5] != "qu’il":
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
                        text = self.sustitude_illegal_str(span["text"])
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

        # print(elements)
        return elements

    def helper_print_unicode(self, string):
        unicode_list = []
        for char in string:
            unicode_list.append(f'\\u{ord(char):04x}')
        return "".join(unicode_list)

    def sustitude_illegal_str(self, string):
        string_list = []
        for char in string:
            if f'\\u{ord(char):04x}' == '\\ufb01':
                # print(f"===substitude string: {string}, char: {char}")
                string_list.append("fi")
            elif f'\\u{ord(char):04x}' == '\\ufb02':
                # print(f"===substitude string: {string}, char: {char}")
                string_list.append("fl")
            elif f'\\u{ord(char):04x}' == '\\ue61e':
                # 这个 unicode 比较复杂，有的时候是 fi，有的时候是大圆点
                fi_word_list = [
                    "\ue61enir", "\ue61enis", "\ue61enirai", "\ue61enissons", "\ue61enisse",
                    "con\ue61ere", "décon\ue61et",
                ]
                ff_word_list = [
                    "aabuler", "aadir", "aaiblir", "s’aairer", "aaisser", "aaler", "aamer",
                    "aaner", "aéager", "aecter", "aectionner", "aérer", "aermer", "aermir",
                    "aoler", "aouager", "aouiller", "aour(r)ager", "aranchir", "aréter",
                    "ariander", "arioler", "aronter", "aubler", "aûter", "agrier", "assoier",
                    "baer", "baladodiuser", "bier", "bleer", "bluer", "bouer", "bouonner",
                    "chauer", "chionner", "chirer", "corer", "coier", "déchionner", "déchirer",
                    "décorer", "décoier", "se dédiérencier", "dégrier", "diamer", "diérencier",
                    "diérentier", "diérer", "diormer", "diracter", "diuser", "ébourier", "étouer",
                    "échauer", "éclaer", "eacer", "eaner", "earer", "earoucher", "eectuer",
                    "eéminer", "eeuiller", "eondrer", "s’eorcer", "eranger", "erayer", "eriter",
                    "eulger", "eumer", "euser", "s’empirer", "encorer", "engourer", "s’entregreer",
                    "s’esclaer", "étoer", "ﬁeer", "gaer", "graer", "greer", "grier", "grionner",
                    "indiérencier", "indiérer", "jaer", "oenser", "orir", "ousquer", "piaer",
                    "pirer", "pouer", "préchauer", "radiodiuser", "se rebier", "rechauer",
                    "réchauer", "recoier", "rediuser", "regreer", "resurchauer", "soier", "sourir",
                    "staer", "suoquer", "surchauer", "surgreer", "taer", "télédiuser", "truer",
                ]
                if any(element in string for element in fi_word_list):
                    string_list.append("fi")
                elif any(element in string for element in ff_word_list):
                    string_list.append("ff")
                else:
                    # if len(string) != 1:
                    #     print(f"===ccc substitude string: {string}, char: {char}")
                    string_list.append(" ")
            elif f'\\u{ord(char):04x}' == '\\ue61b':
                # 这个 unicode 比较复杂，有的时候是 fl，有的时候是 ffi
                fl_word_list = [
                    "circon\ue61bexe", "in\ue61buence", "ré\ue61béchi",
                ]
                if any(element in string for element in fl_word_list):
                    string_list.append("fl")
                else:
                    # 93 页
                    string_list.append("ffi")
            elif f'\\u{ord(char):04x}' == '\\ue61d':
                # 这个 unicode 比较复杂，有的时候是 fl，有的时候是 ffi，有的时候是右箭头
                ffi_word_list = [
                    "su\ue61dre", "ra\ue61dner", "para\ue61dner", "su\ue61dxer", "réa\ue61drmer",
                    "o\ue61dcialiser", "o\ue61dcier", "gra\ue61dter", "e\ue61dler", "e\ue61dlocher",
                    "désa\ue61dlier", "bou\ue61dr", "a\ue61dcher", "a\ue61dler", "a\ue61dlier",
                    "a\ue61dner", "a\ue61drmer",
                ]
                fi_word_list = [
                    "\ue61dnir",
                ]
                if any(element in string for element in ffi_word_list):
                    # 93 页 suffire
                    string_list.append("ffi")
                elif any(element in string for element in fi_word_list):
                    string_list.append("fi")#raﬂer
                else:
                    # if len(string) != 1:
                    #     print(f"===eee substitude string: {string}, char: {char}")
                    string_list.append("->")
            elif f'\\u{ord(char):04x}' == '\\ue61f':
                # 这个 unicode 比较复杂，有的时候是向右的箭头，有的时候是空格，有的时候是 ff，还有的时候是 fi
                ff_word_list = [
                    "su\ue61fîmes", "su\ue61fîtes", "su\ue61fît", "su\ue61fi", "o\ue61frir", "sou\ue61frir",
                    "e\ue61frayer", "indi\ue61férer", "bier", "dégrier",
                ]
                fi_word_list = [
                    "in\ue61fnitif", "\ue61fnal", "\ue61fgées", "\ue61fguré", "a\ue61fn", "\ue61fn",
                    "\ue61fnale",
                ]
                if any(element in string for element in ff_word_list):
                    string_list.append("ff")
                elif any(element in string for element in fi_word_list):
                    string_list.append("fi")
                else:
                    # if len(string) != 1:
                    #     print(f"===fff substitude string: {string}, char: {char}")
                    string_list.append(" ")
            elif f'\\u{ord(char):04x}' == '\\ue61c':
                ffl_word_list = [
                    "aeurer", "aiger", "aouer", "auer", "diuer", "eanquer", "eeurer", "eeurir",
                    "s’eorer", "euer", "euver", "essouer", "insuer", "sier", "sioter", "souer",
                    "soueter",
                ]
                if any(element in string for element in ffl_word_list):
                    string_list.append("ffl")
                else:
                    # if len(string) != 1:
                    #     print(f"===ggg substitude string: {string}, char: {char}")
                    string_list.append(" ")

            else:
                string_list.append(char)
        return "".join(string_list)

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
        if page_num == 71 and verb_info['indice'] == '60' and verb_info['verbe'] == 'asseoir':
            verb_info['verbe'] = f"{verb_info['verbe']}(1)"
        if page_num == 72 and verb_info['indice'] == '61' and verb_info['verbe'] == 'asseoir':
            verb_info['verbe'] = f"{verb_info['verbe']}(2)"

        # 3. 提取特征描述
        verb_info['caracterisation'] = self.extract_caracterisation(elements)
        # print(f"caracterisation: {verb_info['caracterisation']}")
        # print(f"caracterisation: {self.helper_print_unicode(verb_info['caracterisation'])}")

        # 4. 提取变位表格
        conjugations = self.extract_conjugations(elements)
        verb_info.update(conjugations)
        if conjugations['infinitif_present'] != verb_info['verbe']:
            # 把 unicode 和字符都打出来，帮助定位需要哪些替换，好写在 sustitude_illegal_str 里
            print(f"infinitif_present: {conjugations['infinitif_present']}, and verbe: {verb_info['verbe']}.")
            print(f"infinitif_present: {self.helper_print_unicode(conjugations['infinitif_present'])}, "
                  f"and verbe: {self.helper_print_unicode(verb_info['verbe'])}.")
            if verb_info['verbe'] == "": # 如果第 2 步没有提取到动词名称，则把不定时现在时当作动词名称
                verb_info['verbe'] = conjugations['infinitif_present']

        # 5. 笔记和标签创建
        verb_info['notes'] = ""
        verb_info['labels'] = ""

        return verb_info

    def extract_indice(self, elements: List[TextElement]) -> str:
        """提取左上角绿色圆圈中的数字"""
        for element in elements:
            if (element.text.isdigit() and
                len(element.text) <= 3 and
                element.size > 20):
                return element.text
        return ""

    def extract_verb_name(self, elements: List[TextElement]) -> str:
        """提取动词名称"""
        for element in elements:
            if (element.size >= 30 and
                len(element.text) > 3 and
                element.bbox[1] > 25 and
                element.bbox[3] < 75):
                return element.text
        return ""

    def extract_caracterisation(self, elements: List[TextElement]) -> str:
        """提取动词特征描述"""
        blocks = []
        for element in elements:
            if (element.size > 14 and element.size < 17 and
                element.bbox[1] > 75 and element.bbox[3] < 120 and
                element.bbox[2] < 450):
                if element.text.strip() == "":
                    blocks.append("|")
                else:
                    blocks.append(element.text.strip())
        return " ".join(blocks)

    def decide_tense_by_position(self, element) -> str:
        for tense, position in self.pdf_position.items():
            if (element.bbox[0] > position[0] and
                element.bbox[1] > position[1] and
                element.bbox[2] < position[2] and
                element.bbox[3] < position[3]):
                return tense
        return ""

    def extract_conjugations(self, elements: List[TextElement]) -> Dict:
        """提取所有变位"""
        conjugations = {}
        for header in self.csv_headers[3: -2]:
            conjugations[header] = ""
            conjugations[f"{header}_audio"] = ""

        for element in elements:
            # print("================================================")
            # print(f"element:{element}")
            tense = self.decide_tense_by_position(element)
            # print(f"tense:{tense}")
            if tense == "":
                continue

            non_person_tenses = [
                "imperatif_present_2s", "imperatif_present_1p", "imperatif_present_2p",
                "imperatif_passe_2s",   "imperatif_passe_1p",   "imperatif_passe_2p",
                "infinitif_present",    "infinitif_passe",      "participe_present",
                "participe_passe",      "participe_passe_compose",
            ]
            if tense in non_person_tenses:
                conjugations[tense] = element.text
                continue

            person_patterns = [
                ("je",        "1s"), ("j’",   "1s"), ("tu",   "2s"),
                ("il/elle",   "3s"), ("nous", "1p"), ("vous", "2p"),
                ("ils/elles", "3p"), ("n.",   "1p"), ("v.",   "2p"),
                ("que je",       "1s"), ("que j’",   "1s"), ("que tu",   "2s"),
                ("qu’il/elle",   "3s"), ("que nous", "1p"), ("que vous", "2p"),
                ("qu’ils/elles", "3p"), ("que n.",   "1p"), ("que v.",   "2p"),
                ("ils (elles)",  "3p"), ("il (elle)", "3s"), ("qu’ils (elles)", "3p"),
                ("qu’il (elle)", "3s"),
                ("ils", "3p"), ("il", "3s"), ("qu’ils", "3p"), ("qu’il", "3s"),
            ]
            for pattern, person in person_patterns:
                # print(f"pattern:{pattern}, person:{person}")
                if element.text.startswith(pattern):
                    # print("ok, update")
                    conjugations[f'{tense}_{person}'] = element.text
                    break
                else:
                    continue

        # print(conjugations)
        return conjugations

    def extract_all_verbs(self, start_page: int = 10, end_page: int = 116) -> List[Dict]:
        """提取所有动词"""
        all_verbs = []

        for page_num in range(start_page, end_page + 1):
            if page_num in [41, 42]:  # PDF页码从0开始，所以52、53页对应51、52
                continue

            print(f"正在处理第 {page_num} 页...")

            try:
                verb_info = self.extract_verb_info(page_num)
                if verb_info and verb_info.get('verbe'):
                    all_verbs.append(verb_info)
                    print(f"  提取动词: {verb_info['verbe']}")
            except Exception as e:
                print(f"  处理第 {page_num} 页时出错: {e}")

        return all_verbs

    def combine_repertoire_line(self, current_line, elements):
        # 每一行元素先按左端横坐标排序
        current_line.sort(key = lambda x: (x.bbox[0]))

        temp_elem = TextElement(
            text = "",
            size = 0.0,
            bbox = (0.0, 0.0, 0.0, 0.0)
        )

        for text_span in current_line:
            if temp_elem.text == "":
                temp_elem = text_span
                continue

            if text_span.size < 10:
                temp_elem.text = f"{temp_elem.text} ({text_span.text})"
            else:
                temp_elem.text = f"{temp_elem.text}...{text_span.text}"
            temp_elem.size = max(temp_elem.size, text_span.size)
            temp_elem.bbox = (
                temp_elem.bbox[0],
                min(temp_elem.bbox[1], text_span.bbox[1]),
                text_span.bbox[2],
                max(temp_elem.bbox[3], text_span.bbox[3])
            )

        if temp_elem.text != "":
            elements.append(deepcopy(temp_elem))

    def extract_repertoire_elements(self, page) -> List[TextElement]:
        """提取目录页的动词信息"""
        elements = []
        blocks = page.get_text("dict")
        current_line = []
        current_y_position = 0.0
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = self.sustitude_illegal_str(span["text"]).strip()
                        if text:
                            if abs(current_y_position - span["bbox"][1]) > 10:
                                self.combine_repertoire_line(current_line, elements)
                                current_line = []
                            current_line.append(TextElement(
                                text = text,
                                size = span["size"],
                                bbox = span["bbox"]
                            ))
                            current_y_position = span["bbox"][1]
        if len(current_line) > 0:
            self.combine_repertoire_line(current_line, elements)

        # print(elements)
        return elements

    def add_label(self, label_string):
        label_list = []
        string_split = label_string.split(",")
        for label in string_split:
            label = label.strip()
            if label == "T":
                label_list.append("T_transitif_direct")
            elif label == "Ti":
                label_list.append("Ti_transitif_indirect")
            elif label == "I":
                label_list.append("I_intransitif")
            elif label == "Esp":
                label_list.append("Esp_verbe_essentiellement_pronominal")
            elif label == "P":
                label_list.append("P_forme_pronominale")
            elif label == "imp.":
                label_list.append("imp._impersonnel")
            elif label == "D":
                label_list.append("D_défectif")
            else:
                label_list.append(label.replace(" ", "_"))

        return " ".join(label_list)


    def extract_verbs_from_repertoire(self, page_num: int, all_verbs: List[Dict]):
        """从动词库中提取所有动词"""
        page = self.doc[page_num]
        elements = self.extract_repertoire_elements(page)
        # print(elements)

        if not elements:
            return

        temp_verb_info = {
            'verbe': '',
            'caracterisation': '',
            'notes': '',
            'labels': '',
        }
        pattern = (r'^(?:(\d+)\.{3})?'
            r'([a-zA-ZÀ-ÿ\u00E0-\u00FC\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF’\s\-\(\)\*]+)'
            r'\.{4,}\s*([a-zA-Z\.\s,]+)$')

        duplicate_num = 0
        for element in elements:
            if element.bbox[1] > 940 or element.bbox[0] > 680 or element.bbox[3] < 60:
                continue  # 页码、侧面标题、顶部首位锚点
            if element.size > 30:
                continue  # 首字母

            match = re.match(pattern, element.text)

            if not match:
                # 没有匹配上，说明是下面的单词的注释
                element.text = element.text.replace("....", ". ").replace("...", " ")
                if temp_verb_info['verbe'] != '':
                    if temp_verb_info['notes'] != '':
                        temp_verb_info['notes'] += f"\n{element.text}"
                    else:
                        temp_verb_info['notes'] = element.text
                else:
                    print(f"===没有匹配上，但此时没有单词。text: {element.text}, unicode: {self.helper_print_unicode(element.text)}")

            else:
                # print(f"(1): {match.group(1)}, (2): {match.group(2)}, (3): {match.group(3)}, text: {element.text}")

                duplicate_verbes = [
                    # 这些单词在动词库中是重复的
                    "barder", "partir", "repartir", "ressortir", "saillir", "sortir",
                ]
                if match.group(2) in duplicate_verbes:
                    duplicate_num += 1
                else:
                    duplicate_num = 0

                # 如果匹配上了，先把上一个临时的 temp_verb_info 保存起来
                if temp_verb_info['verbe'] != '':
                    all_verbs.append(deepcopy(temp_verb_info))

                temp_verb_info = {
                    'verbe': f"{match.group(2)}({duplicate_num})" if duplicate_num != 0 else match.group(2),
                    'caracterisation': match.group(1),
                    'notes': '',
                    'labels': self.add_label(match.group(3)),
                }

        if temp_verb_info['verbe'] != '':
            all_verbs.append(deepcopy(temp_verb_info))

    def extract_from_repertoire(self, start_page: int = 188, end_page: int = 256) -> List[Dict]:
        """提取动词库"""
        all_verbs = []

        for page_num in range(start_page, end_page + 1):
            print(f"正在处理第 {page_num} 页...")

            try:
                self.extract_verbs_from_repertoire(page_num, all_verbs)
            except Exception as e:
                print(f"  处理第 {page_num} 页时出错: {e}")

        # print(all_verbs)
        return all_verbs

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
    pdf_path = "bescherelle.pdf"
    output_csv = "french_verbs_conjugations.csv"

    extractor = FrenchVerbExtractor(pdf_path)
    manager = CSVAttributeManager(output_csv)

    print("开始提取法语动词变位...")

    try:
        # 提取所有动词，10-116
        verbs = extractor.extract_all_verbs(start_page=10, end_page=116)
        print(f"\n总共提取了 {len(verbs)} 个动词")

        # 保存到CSV
        for verb in verbs:
            element = verb['verbe']
            for attr_name, attr_value in verb.items():
                if attr_name == 'verbe':
                    continue
                manager.write_attribute(element, attr_name, attr_value)
        # 特殊的表格特殊处理
        manager.write_attribute("être aimé", "subjonctif_imparfait_1p", "que nous fussions aimé(e)s")
        manager.write_attribute("être aimé", "subjonctif_imparfait_3p", "qu’ils/elles fussent aimé(e)s")
        manager.write_attribute("être aimé", "subjonctif_plus_que_parfait_1p", "que nous eussions été aimé(e)s")
        manager.write_attribute("être aimé", "subjonctif_plus_que_parfait_3p", "qu’ils/elles eussentétéaimé(e)s")
        # manager.read_attribute(element, attribute)
        print(f"结果已保存到 {output_csv}")

        # 提取目录页，188 - 256 页
        all_verbs = extractor.extract_from_repertoire(start_page=188, end_page=256)

        # 保存目录页结果到 CSV
        for verb_from_repertoire in all_verbs:
            element = verb_from_repertoire['verbe']
            try:
                indice_from_csv = manager.read_attribute(element, 'indice')
                if indice_from_csv != verb_from_repertoire['caracterisation']:
                    print(f"表格中存在 {element}，表格中的 indice 是 {indice_from_csv} 但目录中的是 {verb_from_repertoire['caracterisation']}")

                if verb_from_repertoire['labels']:
                    manager.write_attribute(element, 'labels', verb_from_repertoire['labels'])
                if verb_from_repertoire['notes']:
                    manager.write_attribute(element, 'notes', verb_from_repertoire['notes'])

            except ValueError:  # 元素不存在，添加进表格中
                if verb_from_repertoire['caracterisation']:
                    manager.write_attribute(element, 'caracterisation', verb_from_repertoire['caracterisation'])
                if verb_from_repertoire['labels']:
                    manager.write_attribute(element, 'labels', verb_from_repertoire['labels'])
                if verb_from_repertoire['notes']:
                    manager.write_attribute(element, 'notes', verb_from_repertoire['notes'])

        # 统计基础动词变位的常用次数
        # stat_dict = {}
        # for i in range(105):
        #     stat_dict[str(i + 1)] = 1

        # for verb_from_repertoire in all_verbs:
        #     if verb_from_repertoire['caracterisation']:
        #         stat_dict[verb_from_repertoire['caracterisation']] += 1

        # print(sorted(stat_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True))



        ##########################################################################
        # 上面完成了 PDF 相关的工作，接下来针对 CSV 进行补充调整
        ##########################################################################

        # 到网上查询其他单词


        # 获取发音并填充

        # 其他修复
        # all_verbs = extractor.extract_from_repertoire(start_page=188, end_page=256)
        # conjugation_csv = "conjugations_to_anki.csv"
        # conjugation_manager = CSVAttributeManager(conjugation_csv)

        # cnt = 0
        # for verb_from_repertoire in all_verbs:
        #     element = verb_from_repertoire['verbe'].strip()
        #     try:
        #         indice_from_csv = conjugation_manager.read_attribute(element, 'indice')
        #         # 能读到，说明是 105 个基础动词
        #         # print(element)
        #         # cnt += 1
        #         conjugation_manager.write_attribute(element, 'labels', verb_from_repertoire['labels'])
        #         conjugation_manager.write_attribute(element, 'notes', verb_from_repertoire['notes'])
        #     except ValueError:
        #         # 读不到，不是基础动词，跳过
        #         continue
        # print(cnt)

    except Exception as e:
        print(f"处理过程中出错: {e}")

if __name__ == "__main__":
    main()

"""
这个脚本现在不能处理好需要手工处理的：

- 105 个基础动词中唯一一个嘘音 h 因为在目录库中带 * 不能识别为同一个，需要手动让它带星，并更新 labels
- 有一些指向 61/62 的目录库中的动词，算上它自己一共有两个，会被处理成上一个单词的 notes，需要手动删掉上一个单词的 notes 并再加一行

这些是空的，需要手动处理：
【x】empty: verb = faillir, indice = 46, attr = conditionnel_present_3s
【x】empty: verb = pouvoir, indice = 55, attr = participe_present
【x】empty: verb = pouvoir, indice = 55, attr = participe_passe
【x】empty: verb = échoir, indice = 67, attr = conditionnel_present_3s
【x】empty: verb = échoir, indice = 67, attr = conditionnel_passe_3p
【x】empty: verb = déchoir, indice = 68, attr = indicatif_futur_simple_3s
【x】empty: verb = déchoir, indice = 68, attr = conditionnel_present_3s
【x】empty: verb = déchoir, indice = 68, attr = conditionnel_passe_3p
【x】empty: verb = déchoir, indice = 68, attr = participe_passe
【x】empty: verb = clore, indice = 105, attr = participe_present
【x】empty: verb = clore, indice = 105, attr = participe_passe
"""
