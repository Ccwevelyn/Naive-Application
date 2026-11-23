# -*- coding: utf-8 -*-
"""Build data.js from every QS 2026 university that has an exact rank.

QS 2026 ranks 1 through 697 individually. From 701-710 onward the published
place is a band, and those schools are left out.
"""
import csv
import io
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FSR_PATH = Path(r"C:\Users\Asus\.cursor\projects\c-Users-Asus-Desktop-Naive-Appliation\agent-tools\60d3b105-65bd-4271-8ca3-de6b8dc083c7.txt")
ZH_RANKED_PATH = Path(r"C:\Users\Asus\.cursor\projects\c-Users-Asus-Desktop-Naive-Appliation\agent-tools\e6266c7f-7bae-4a74-bf6e-7c63db4ec05a.txt")
ZH_PDF_PATH = Path(r"C:\Users\Asus\.cursor\projects\c-Users-Asus-Desktop-Naive-Appliation\agent-tools\0b4afdd0-1fe1-4132-aa3b-c97bf009592d.txt")
ZH_TSV_PATH = ROOT / "zh_names.tsv"
SETTLE_PATH = ROOT / "settle.tsv"
SETTLE_KEYS = {"town", "city", "downtown", "district", "rural"}
REGION_LABELS = {
    "美国", "英国", "瑞士", "新加坡", "中国香港", "中国", "中国大陆", "中国内地", "澳大利亚", "荷兰", "法国",
    "加拿大", "日本", "韩国", "比利时", "中国台湾", "中国澳门", "新西兰", "沙特阿拉伯", "马来西亚",
    "瑞典", "爱尔兰", "丹麦", "芬兰", "意大利", "印度", "卡塔尔", "挪威", "西班牙", "阿根廷", "智利",
    "墨西哥", "印度尼西亚", "南非", "奥地利", "巴西", "阿拉伯联合酋长国", "阿联酋", "哈萨克斯坦", "德国",
    "俄罗斯", "以色列", "泰国", "葡萄牙", "希腊", "波兰", "捷克", "匈牙利", "爱沙尼亚", "立陶宛",
    "斯洛伐克", "斯洛文尼亚", "卢森堡", "冰岛", "塞浦路斯", "白俄罗斯", "伊朗", "黎巴嫩", "约旦", "阿曼",
    "科威特", "巴林", "土耳其", "巴基斯坦", "菲律宾", "越南", "文莱", "孟加拉国", "孟加拉", "乌兹别克斯坦",
    "阿塞拜疆", "埃及", "秘鲁", "哥伦比亚", "哥斯达黎加", "乌拉圭", "北塞浦路斯",
}
THE_PATH = Path(r"C:\Users\Asus\.cursor\projects\c-Users-Asus-Desktop-Naive-Appliation\agent-tools\f8aa0715-1602-4fd8-b28c-0becbb072729.txt")
US_PATH = Path(r"C:\Users\Asus\.cursor\projects\c-Users-Asus-Desktop-Naive-Appliation\agent-tools\13b6f82a-edee-40a7-8e21-1429b5afa856.txt")
PLACES = {
    "United States of America": ("us", "us", "美国", "United States"),
    "United Kingdom": ("gb", "uk", "英国", "United Kingdom"),
    "Ireland": ("ie", "ie", "爱尔兰", "Ireland"),
    "Switzerland": ("ch", "eu", "瑞士", "Switzerland"),
    "Germany": ("de", "eu", "德国", "Germany"),
    "France": ("fr", "eu", "法国", "France"),
    "Netherlands": ("nl", "eu", "荷兰", "Netherlands"),
    "Belgium": ("be", "eu", "比利时", "Belgium"),
    "Sweden": ("se", "eu", "瑞典", "Sweden"),
    "Denmark": ("dk", "eu", "丹麦", "Denmark"),
    "Finland": ("fi", "eu", "芬兰", "Finland"),
    "Norway": ("no", "eu", "挪威", "Norway"),
    "Italy": ("it", "eu", "意大利", "Italy"),
    "Spain": ("es", "eu", "西班牙", "Spain"),
    "Portugal": ("pt", "eu", "葡萄牙", "Portugal"),
    "Austria": ("at", "eu", "奥地利", "Austria"),
    "Greece": ("gr", "eu", "希腊", "Greece"),
    "Poland": ("pl", "eu", "波兰", "Poland"),
    "Czechia": ("cz", "eu", "捷克", "Czechia"),
    "Hungary": ("hu", "eu", "匈牙利", "Hungary"),
    "Estonia": ("ee", "eu", "爱沙尼亚", "Estonia"),
    "Lithuania": ("lt", "eu", "立陶宛", "Lithuania"),
    "Slovakia": ("sk", "eu", "斯洛伐克", "Slovakia"),
    "Slovenia": ("si", "eu", "斯洛文尼亚", "Slovenia"),
    "Luxembourg": ("lu", "eu", "卢森堡", "Luxembourg"),
    "Iceland": ("is", "eu", "冰岛", "Iceland"),
    "Cyprus": ("cy", "eu", "塞浦路斯", "Cyprus"),
    "Belarus": ("by", "eu", "白俄罗斯", "Belarus"),
    "Canada": ("ca", "ca", "加拿大", "Canada"),
    "Australia": ("au", "au", "澳大利亚", "Australia"),
    "New Zealand": ("nz", "nz", "新西兰", "New Zealand"),
    "Singapore": ("sg", "sg", "新加坡", "Singapore"),
    "Hong Kong SAR, China": ("hk", "hk", "中国香港", "Hong Kong"),
    "Macao SAR, China": ("mo", "mo", "中国澳门", "Macau"),
    "China (Mainland)": ("cn", "cn", "中国大陆", "Mainland China"),
    "Taiwan": ("tw", "tw", "中国台湾", "Taiwan"),
    "Japan": ("jp", "jp", "日本", "Japan"),
    "Republic of Korea": ("kr", "kr", "韩国", "South Korea"),
    "Malaysia": ("my", "my", "马来西亚", "Malaysia"),
    "India": ("in", "in", "印度", "India"),
    "Saudi Arabia": ("sa", "me", "沙特阿拉伯", "Saudi Arabia"),
    "Qatar": ("qa", "me", "卡塔尔", "Qatar"),
    "United Arab Emirates": ("ae", "me", "阿联酋", "United Arab Emirates"),
    "Israel": ("il", "me", "以色列", "Israel"),
    "Iran (Islamic Republic of)": ("ir", "me", "伊朗", "Iran"),
    "Lebanon": ("lb", "me", "黎巴嫩", "Lebanon"),
    "Jordan": ("jo", "me", "约旦", "Jordan"),
    "Oman": ("om", "me", "阿曼", "Oman"),
    "Kuwait": ("kw", "me", "科威特", "Kuwait"),
    "Bahrain": ("bh", "me", "巴林", "Bahrain"),
    "Northern Cyprus": ("nc", "me", "北塞浦路斯", "Northern Cyprus"),
    "Argentina": ("ar", "latam", "阿根廷", "Argentina"),
    "Chile": ("cl", "latam", "智利", "Chile"),
    "Mexico": ("mx", "latam", "墨西哥", "Mexico"),
    "Brazil": ("br", "latam", "巴西", "Brazil"),
    "Colombia": ("co", "latam", "哥伦比亚", "Colombia"),
    "Peru": ("pe", "latam", "秘鲁", "Peru"),
    "Costa Rica": ("cr", "latam", "哥斯达黎加", "Costa Rica"),
    "Uruguay": ("uy", "latam", "乌拉圭", "Uruguay"),
    "Indonesia": ("id", "asia", "印度尼西亚", "Indonesia"),
    "Thailand": ("th", "asia", "泰国", "Thailand"),
    "Kazakhstan": ("kz", "asia", "哈萨克斯坦", "Kazakhstan"),
    "Türkiye": ("tr", "asia", "土耳其", "Turkey"),
    "Pakistan": ("pk", "asia", "巴基斯坦", "Pakistan"),
    "Philippines": ("ph", "asia", "菲律宾", "Philippines"),
    "Viet Nam": ("vn", "asia", "越南", "Vietnam"),
    "Brunei Darussalam": ("bn", "asia", "文莱", "Brunei"),
    "Bangladesh": ("bd", "asia", "孟加拉国", "Bangladesh"),
    "Uzbekistan": ("uz", "asia", "乌兹别克斯坦", "Uzbekistan"),
    "Azerbaijan": ("az", "asia", "阿塞拜疆", "Azerbaijan"),
    "South Africa": ("za", "af", "南非", "South Africa"),
    "Egypt": ("eg", "af", "埃及", "Egypt"),
    "Russian Federation": ("ru", "eu", "俄罗斯", "Russia"),
}

REGION_ORDER = [
    ("cn", "中外合办", "Joint programs"),
    ("hk", "中国香港", "Hong Kong"),
    ("mo", "中国澳门", "Macau"),
    ("tw", "中国台湾", "Taiwan"),
    ("us", "美国", "United States"),
    ("ca", "加拿大", "Canada"),
    ("latam", "拉美", "Latin America"),
    ("uk", "英国", "United Kingdom"),
    ("ie", "爱尔兰", "Ireland"),
    ("eu", "欧陆", "Continental Europe"),
    ("jp", "日本", "Japan"),
    ("kr", "韩国", "South Korea"),
    ("sg", "新加坡", "Singapore"),
    ("my", "马来西亚", "Malaysia"),
    ("in", "印度", "India"),
    ("asia", "亚洲其他", "Other Asia"),
    ("au", "澳大利亚", "Australia"),
    ("nz", "新西兰", "New Zealand"),
    ("me", "中东", "Middle East"),
    ("af", "非洲", "Africa"),
]

# Independent Sino-foreign joint universities. Regular mainland universities are left out.
# QS gives XJTLU a band, not an exact place. The others are not in the QS 2026 world list.
JOINT = [
    {"id": "cuhk-shenzhen", "zh": "香港中文大学（深圳）", "en": "The Chinese University of Hong Kong, Shenzhen"},
    {"id": "hkust-guangzhou", "zh": "香港科技大学（广州）", "en": "The Hong Kong University of Science and Technology (Guangzhou)"},
    {"id": "xjtlu", "zh": "西交利物浦大学", "en": "Xi'an Jiaotong-Liverpool University", "qsBand": "1001–1200"},
    {"id": "nottingham-ningbo", "zh": "宁波诺丁汉大学", "en": "University of Nottingham Ningbo China"},
    {"id": "nyu-shanghai", "zh": "上海纽约大学", "en": "NYU Shanghai"},
    {"id": "duke-kunshan", "zh": "昆山杜克大学", "en": "Duke Kunshan University"},
    {"id": "wenzhou-kean", "zh": "温州肯恩大学", "en": "Wenzhou-Kean University"},
    {"id": "uic-zhuhai", "zh": "北京师范大学-香港浸会大学联合国际学院", "en": "Beijing Normal University-Hong Kong Baptist University United International College"},
    {"id": "gtiit", "zh": "广东以色列理工学院", "en": "Guangdong Technion-Israel Institute of Technology"},
    {"id": "smbu", "zh": "深圳北理莫斯科大学", "en": "Shenzhen MSU-BIT University"},
]

ZH_BY_EN = {
    "Koc University": "科奇大学",
    "Massachusetts Institute of Technology (MIT)": "麻省理工学院",
    "Imperial College London": "帝国理工学院",
    "Stanford University": "斯坦福大学",
    "University of Oxford": "牛津大学",
    "Harvard University": "哈佛大学",
    "University of Cambridge": "剑桥大学",
    "ETH Zurich (Swiss Federal Institute of Technology)": "苏黎世联邦理工学院",
    "National University of Singapore (NUS)": "新加坡国立大学",
    "UCL (University College London)": "伦敦大学学院",
    "California Institute of Technology (Caltech)": "加州理工学院",
    "The University of Hong Kong": "香港大学",
    "Nanyang Technological University, Singapore (NTU Singapore)": "南洋理工大学",
    "University of Chicago": "芝加哥大学",
    "Peking University": "北京大学",
    "University of Pennsylvania": "宾夕法尼亚大学",
    "Cornell University": "康奈尔大学",
    "Tsinghua University": "清华大学",
    "University of California, Berkeley (UCB)": "加州大学伯克利分校",
    "The University of Melbourne": "墨尔本大学",
    "The University of New South Wales": "新南威尔士大学",
    "Yale University": "耶鲁大学",
    "École Polytechnique Fédérale de Lausanne": "洛桑联邦理工学院",
    "Technical University of Munich": "慕尼黑工业大学",
    "Johns Hopkins University": "约翰斯·霍普金斯大学",
    "Princeton University": "普林斯顿大学",
    "The University of Sydney": "悉尼大学",
    "McGill University": "麦吉尔大学",
    "PSL University": "巴黎文理研究大学",
    "University of Toronto": "多伦多大学",
    "Fudan University": "复旦大学",
    "King's College London (KCL)": "伦敦国王学院",
    "Australian National University": "澳大利亚国立大学",
    "The Chinese University of Hong Kong": "香港中文大学",
    "University of Edinburgh": "爱丁堡大学",
    "The University of Manchester": "曼彻斯特大学",
    "Monash University": "蒙纳士大学",
    "The University of Tokyo": "东京大学",
    "Columbia University": "哥伦比亚大学",
    "Seoul National University": "首尔国立大学",
    "University of British Columbia": "不列颠哥伦比亚大学",
    "Institut Polytechnique de Paris": "巴黎理工学院",
    "Northwestern University": "西北大学",
    "The University of Queensland": "昆士兰大学",
    "The Hong Kong University of Science and Technology": "香港科技大学",
    "University of Michigan-Ann Arbor": "密歇根大学安娜堡分校",
    "University of California, Los Angeles (UCLA)": "加州大学洛杉矶分校",
    "Delft University of Technology": "代尔夫特理工大学",
    "Shanghai Jiao Tong University": "上海交通大学",
    "Zhejiang University": "浙江大学",
    "Yonsei University": "延世大学",
    "University of Bristol": "布里斯托大学",
    "Carnegie Mellon University": "卡内基梅隆大学",
    "The University of Amsterdam": "阿姆斯特丹大学",
    "The Hong Kong Polytechnic University": "香港理工大学",
    "New York University (NYU)": "纽约大学",
    "London School of Economics and Political Science (LSE)": "伦敦政治经济学院",
    "Kyoto University": "京都大学",
    "Ludwig-Maximilians-Universität München": "慕尼黑大学",
    "Universiti Malaya (UM)": "马来亚大学",
    "KU Leuven": "鲁汶大学",
    "Korea University": "高丽大学",
    "Duke University": "杜克大学",
    "City University of Hong Kong": "香港城市大学",
    "National Taiwan University (NTU)": "台湾大学",
    "The University of Auckland": "奥克兰大学",
    "University of California, San Diego (UCSD)": "加州大学圣地亚哥分校",
    "King Fahd University of Petroleum & Minerals": "法赫德国王石油与矿产大学",
    "University of Texas at Austin": "德克萨斯大学奥斯汀分校",
    "Brown University": "布朗大学",
    "Université Paris-Saclay": "巴黎萨克雷大学",
    "University of Illinois at Urbana-Champaign": "伊利诺伊大学厄巴纳-香槟分校",
    "Lund University": "隆德大学",
    "Sorbonne University (merged from Paris IV & UPMC)": "索邦大学",
    "The University of Warwick": "华威大学",
    "Trinity College Dublin, The University of Dublin": "都柏林三一学院",
    "University of Birmingham": "伯明翰大学",
    "The University of Western Australia": "西澳大学",
    "KTH Royal Institute of Technology": "皇家理工学院",
    "University of Glasgow": "格拉斯哥大学",
    "Ruprecht-Karls-Universität Heidelberg": "海德堡大学",
    "University of Washington": "华盛顿大学",
    "Adelaide University": "阿德莱德大学",
    "Pennsylvania State University": "宾夕法尼亚州立大学",
    "Universidad de Buenos Aires": "布宜诺斯艾利斯大学",
    "Tokyo Institute of Technology": "东京工业大学",
    "University of Leeds": "利兹大学",
    "University of Southampton": "南安普敦大学",
    "Boston University": "波士顿大学",
    "Freie Universität Berlin": "柏林自由大学",
    "Purdue University": "普渡大学",
    "The University of Osaka": "大阪大学",
    "The University of Sheffield": "谢菲尔德大学",
    "Uppsala University": "乌普萨拉大学",
    "Durham University": "杜伦大学",
    "University of Alberta": "阿尔伯塔大学",
    "University of Technology Sydney": "悉尼科技大学",
    "The University of Nottingham": "诺丁汉大学",
    "Karlsruhe Institute of Technology (KIT)": "卡尔斯鲁厄理工学院",
    "Politecnico di Milano": "米兰理工大学",
    "University of Zurich (UZH)": "苏黎世大学",
    "University of Copenhagen": "哥本哈根大学",
    "Pohang University of Science And Technology (POSTECH)": "浦项科技大学",
    "Nanjing University": "南京大学",
    "Utrecht University": "乌得勒支大学",
    "Lomonosov Moscow State University": "莫斯科国立大学",
    "Rheinisch-Westfälische Technische Hochschule Aachen": "亚琛工业大学",
    "Technical University of Denmark": "丹麦技术大学",
    "Universidade de São Paulo (USP)": "圣保罗大学",
    "Tohoku University": "东北大学",
    "Queen Mary University of London (QMUL)": "伦敦玛丽女王大学",
    "University of Wisconsin-Madison": "威斯康星大学麦迪逊分校",
    "Qatar University": "卡塔尔大学",
    "University of St Andrews": "圣安德鲁斯大学",
    "Aalto University": "阿尔托大学",
    "University of California, Davis": "加州大学戴维斯分校",
    "Pontificia Universidad Católica de Chile": "智利天主教大学",
    "University of Helsinki": "赫尔辛基大学",
    "University College Dublin": "都柏林大学",
    "Leiden University": "莱顿大学",
    "Rice University": "莱斯大学",
    "University of Oslo": "奥斯陆大学",
    "University of Waterloo": "滑铁卢大学",
    "Georgia Institute of Technology": "佐治亚理工学院",
    "Indian Institute of Technology Delhi (IITD)": "印度理工学院德里分校",
    "RMIT University": "皇家墨尔本理工大学",
    "Sungkyunkwan University": "成均馆大学",
    "Universiti Kebangsaan Malaysia (UKM)": "马来西亚国立大学",
    "Sapienza University of Rome": "罗马大学",
    "Indian Institute of Technology Bombay (IITB)": "印度理工学院孟买分校",
    "Humboldt-Universität zu Berlin": "柏林洪堡大学",
    "Aarhus University": "奥胡斯大学",
    "University of Bath": "巴斯大学",
    "University of Science and Technology of China": "中国科学技术大学",
    "Universiti Putra Malaysia (UPM)": "马来西亚博特拉大学",
    "Universiti Sains Malaysia (USM)": "马来西亚理科大学",
    "Universidad Nacional Autónoma de México (UNAM)": "墨西哥国立自治大学",
    "Newcastle University": "纽卡斯尔大学",
    "Alma Mater Studiorum - University of Bologna": "博洛尼亚大学",
    "Macquarie University": "麦考瑞大学",
    "Eindhoven University of Technology": "埃因霍芬理工大学",
    "Erasmus University Rotterdam": "鹿特丹伊拉斯姆斯大学",
    "University of North Carolina, Chapel Hill": "北卡罗来纳大学教堂山分校",
    "King Saud University": "沙特国王大学",
    "Texas A&M University": "得克萨斯农工大学",
    "Technische Universität Berlin": "柏林工业大学",
    "University of Southern California": "南加州大学",
    "Stockholm University": "斯德哥尔摩大学",
    "University of Groningen": "格罗宁根大学",
    "University of Liverpool": "利物浦大学",
    "University of Cape Town": "开普敦大学",
    "Western University": "韦仕敦大学",
    "University of Vienna": "维也纳大学",
    "Universiti Teknologi Malaysia (UTM)": "马来西亚工艺大学",
    "Wageningen University & Research": "瓦赫宁根大学",
    "University of Exeter": "埃克塞特大学",
    "University of Geneva": "日内瓦大学",
    "Lancaster University": "兰卡斯特大学",
    "University of Basel": "巴塞尔大学",
    "Hanyang University": "汉阳大学",
    "University of Barcelona": "巴塞罗那大学",
    "Michigan State University": "密歇根州立大学",
    "Ghent University": "根特大学",
    "King Abdul Aziz University (KAU)": "阿卜杜勒阿齐兹国王大学",
    "Nagoya University": "名古屋大学",
    "Chalmers University of Technology": "查尔姆斯理工大学",
    "Al-Farabi Kazakh National University": "哈萨克国立大学",
    "Washington University in St. Louis": "圣路易斯华盛顿大学",
    "University of Montreal": "蒙特利尔大学",
    "University of York": "约克大学",
    "Hokkaido University": "北海道大学",
    "Kyushu University": "九州大学",
    "Universitat Autónoma de Barcelona": "巴塞罗那自治大学",
    "Arizona State University": "亚利桑那州立大学",
    "McMaster University": "麦克马斯特大学",
    "Universidad de Chile": "智利大学",
    "National Tsing Hua University": "国立清华大学",
    "Khalifa University of Science and Technology": "哈利法大学",
    "Tongji University": "同济大学",
    "University of California, Santa Barbara (UCSB)": "加州大学圣巴巴拉分校",
    "Indian Institute of Technology Madras (IITM)": "印度理工学院马德拉斯分校",
    "Cardiff University": "卡迪夫大学",
    "Emory University": "埃默里大学",
    "Curtin University": "科廷大学",
    "University of Bern": "伯尔尼大学",
    "University of Wollongong": "伍伦贡大学",
    "Wuhan University": "武汉大学",
    "Tecnológico de Monterrey (ITESM)": "蒙特雷科技大学",
    "University Complutense Madrid": "马德里康普顿斯大学",
    "UNIVERSITAS INDONESIA": "印度尼西亚大学",
    "Ohio State University": "俄亥俄州立大学",
    "Queen's University, Ontario": "女王大学",
    "Université Catholique de Louvain (UCL)": "法语鲁汶天主教大学",
    "Universität Hamburg": "汉堡大学",
    "University of Reading": "雷丁大学",
    "Vrije Universiteit Amsterdam": "阿姆斯特丹自由大学",
    "Waseda University": "早稻田大学",
    "University of Otago": "奥塔哥大学",
    "Vienna University of Technology": "维也纳技术大学",
    "National Yang Ming Chiao Tung University": "国立阳明交通大学",
    "Queen's University Belfast": "贝尔法斯特女王大学",
    "University of Macau": "澳门大学",
    "Macau University of Science and Technology": "澳门科技大学",
}

def fold(text):
    text = text.lower().replace("–", " ").replace("—", " ").replace("’", "").replace("'", "").replace("´", "")
    text = text.replace("&", " and ")
    swaps = str.maketrans({
        "ä": "a", "ö": "o", "ü": "u", "ß": "ss", "é": "e", "è": "e", "ê": "e", "ë": "e",
        "á": "a", "à": "a", "â": "a", "ã": "a", "å": "a", "í": "i", "ì": "i", "î": "i",
        "ï": "i", "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ú": "u", "ù": "u", "û": "u",
        "ñ": "n", "ç": "c", "č": "c", "š": "s", "ž": "z", "ý": "y", "ø": "o", "æ": "ae",
        "œ": "oe",
    })
    return text.translate(swaps)


def norm(value):
    text = fold(value)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    stop = {"the"}
    return " ".join(word for word in text.split() if word not in stop)


ALIASES = {
    "UCL (University College London)": ["UCL", "University College London"],
    "Ludwig-Maximilians-Universität München": ["LMU Munich", "University of Munich"],
    "Universiti Malaya (UM)": ["University of Malaya"],
    "King Fahd University of Petroleum & Minerals": ["KFUPM", "King Fahd University of Petroleum and Minerals"],
    "Universidad de Buenos Aires": ["University of Buenos Aires"],
    "Tokyo Institute of Technology": ["Institute of Science Tokyo"],
    "Freie Universität Berlin": ["Free University of Berlin"],
    "Rheinisch-Westfälische Technische Hochschule Aachen": ["RWTH Aachen University"],
    "Universidade de São Paulo (USP)": ["University of São Paulo", "University of Sao Paulo"],
    "Humboldt-Universität zu Berlin": ["Humboldt University of Berlin"],
    "Universidad Nacional Autónoma de México (UNAM)": ["National Autonomous University of Mexico"],
    "Technische Universität Berlin": ["Technical University of Berlin"],
    "King Abdul Aziz University (KAU)": ["King Abdulaziz University"],
    "University of Montreal": ["Université de Montréal", "Universite de Montreal"],
    "UNIVERSITAS INDONESIA": ["University of Indonesia"],
    "Universität Hamburg": ["University of Hamburg"],
    "Sorbonne University (merged from Paris IV & UPMC)": ["Sorbonne Universite", "Sorbonne University"],
    "Ruprecht-Karls-Universität Heidelberg": ["Heidelberg University", "Universität Heidelberg"],
    "Pennsylvania State University": ["Penn State (Main campus)"],
    "Purdue University": ["Purdue University West Lafayette", "Purdue University--West Lafayette"],
    "Yonsei University": ["Yonsei University (Seoul campus)"],
    "Sungkyunkwan University": ["Sungkyunkwan University (SKKU)"],
    "Queen's University, Ontario": ["Queen's University", "Queen’s University"],
    "Khalifa University of Science and Technology": ["Khalifa University"],
    "PSL University": ["Paris Sciences et Lettres – PSL Research University Paris", "PSL Research University Paris (ComUE)"],
    "Politecnico di Milano": ["Polytechnic University of Milan"],
    "Pontificia Universidad Católica de Chile": ["Pontificia Universidad Catolica de Chile"],
    "Universitat Autónoma de Barcelona": ["Autonomous University of Barcelona"],
    "Université Catholique de Louvain (UCL)": ["University Catholique of Louvain"],
    "École Polytechnique Fédérale de Lausanne": ["Ecole Polytechnique Federale de Lausanne", "École Polytechnique Federale of Lausanne", "EPFL"],
    "Adelaide University": ["University of Adelaide"],
    "The University of Osaka": ["Osaka University"],
    "University Complutense Madrid": ["Complutense University of Madrid"],
    "Qatar University": ["University of Qatar"],
}


def score_num(token):
    token = token.strip().replace(",", "")
    if "–" in token or "-" in token:
        parts = re.split(r"[–-]", token)
        nums = []
        for part in parts:
            try:
                nums.append(float(part))
            except ValueError:
                pass
        if len(nums) == 2:
            return (nums[0] + nums[1]) / 2
        if len(nums) == 1:
            return nums[0]
        return None
    try:
        return float(token)
    except ValueError:
        return None


def parse_fsr():
    text = FSR_PATH.read_text(encoding="utf-8-sig")
    start = text.find("2026 Rank,")
    rows = []
    for row in csv.DictReader(io.StringIO(text[start:])):
        name = (row.get("Institution Name") or "").strip()
        raw = (row.get("FSR SCORE") or "").strip()
        if not name or not raw:
            continue
        try:
            score = float(raw)
        except ValueError:
            continue
        rows.append({"name": name, "key": norm(name), "faculty": score})
    return rows


def parse_qs():
    """Keep a school only when QS published an exact place, not a band."""
    text = FSR_PATH.read_text(encoding="utf-8-sig")
    start = text.find("2026 Rank,")
    rows = []
    skipped = []
    for row in csv.DictReader(io.StringIO(text[start:])):
        raw = (row.get("2026 Rank") or "").strip().lstrip("=")
        if not raw.isdigit():
            continue
        name = re.sub(r"\s+", " ", (row.get("Institution Name") or "")).strip()
        country = re.sub(r"\s+", " ", (row.get("Country/Territory") or "")).strip()
        if not name:
            continue
        if country not in PLACES:
            skipped.append(country)
            continue
        if any(item["en"] == name for item in rows):
            continue
        rows.append({"qs": int(raw), "en": name, "country": country})
    if skipped:
        print("skipped countries", sorted(set(skipped)))
    return rows


def is_school_zh(text):
    if text in REGION_LABELS or re.fullmatch(r"\d+", text):
        return False
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def parse_zh_ranked(path):
    if not path.exists():
        return []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    index = 0
    while index < len(lines) - 2:
        if re.fullmatch(r"\d+", lines[index]) and re.search(r"[A-Za-z]", lines[index + 1]) and is_school_zh(lines[index + 2]):
            english = lines[index + 1]
            rows.append({"name": english, "zh": lines[index + 2], "key": norm(english)})
            index += 3
            continue
        index += 1
    return rows


def parse_zh_tsv(path):
    if not path or not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if "\t" not in line:
            continue
        english, chinese = line.split("\t", 1)
        english, chinese = english.strip(), chinese.strip()
        if english and is_school_zh(chinese):
            rows.append({"name": english, "zh": chinese, "key": norm(english)})
    return rows


def parse_zh_pdf(path):
    if not path or not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 4 or not parts[0].isdigit() or not is_school_zh(parts[1]):
            continue
        english = re.sub(r"\s+", " ", parts[2]).strip()
        if re.search(r"[A-Za-z]", parts[3]) or not re.search(r"[A-Za-z]", english):
            continue
        rows.append({"name": english, "zh": parts[1], "key": norm(english)})
    return rows


def parse_rank_token(token):
    token = token.strip().replace(",", "")
    if not token or token.lower() == "unranked":
        return None
    if "–" in token or "-" in token:
        parts = re.split(r"[–-]", token)
        nums = [int(part) for part in parts if part.strip().isdigit()]
        if nums:
            return nums[0]
        return None
    return int(token) if token.isdigit() else None


def parse_the():
    rows = []
    for line in THE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("2026,"):
            continue
        cols = next(csv.reader([line]))
        if len(cols) < 11:
            continue
        rank = parse_rank_token(cols[2])
        if rank is None:
            continue
        rows.append({
            "rank": rank,
            "name": cols[3],
            "env": score_num(cols[7]),
            "industry": score_num(cols[9]),
            "key": norm(cols[3]),
        })
    return rows


def parse_usnews():
    rows = []
    for line in US_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 2 or not parts[0][:1].isdigit():
            continue
        rank = parse_rank_token(parts[0])
        if rank is None:
            continue
        rows.append({"rank": rank, "name": parts[1], "key": norm(parts[1])})
    return rows


def bare_norm(value):
    return norm(re.sub(r"\([^)]*\)", " ", value))


def lookup(name, rows):
    candidates = [name] + ALIASES.get(name, [])
    keys = set()
    for candidate in candidates:
        keys.add(norm(candidate))
        keys.add(bare_norm(candidate))
    hits = [row for row in rows if row["key"] in keys or bare_norm(row["name"]) in keys]
    if hits:
        hits.sort(key=lambda row: (abs(len(bare_norm(row["name"]).split()) - len(bare_norm(name).split())),))
        return hits[0]
    key = norm(name)
    key_tokens = set(key.split())
    best = None
    best_score = 0
    for row in rows:
        other_tokens = set(row["key"].split())
        if len(key_tokens) < 2 or len(other_tokens) < 2:
            continue
        inter = key_tokens & other_tokens
        union = key_tokens | other_tokens
        jaccard = len(inter) / len(union)
        smaller, larger = (key_tokens, other_tokens) if len(key_tokens) <= len(other_tokens) else (other_tokens, key_tokens)
        score = jaccard
        if len(smaller) >= 3 and smaller <= larger:
            score = max(score, 0.9 + 0.1 * jaccard)
        if score > best_score:
            best_score = score
            best = row
    if best_score >= 0.88:
        return best
    return None


def slug(name, used):
    base = re.sub(r"[^a-z0-9]+", "-", norm(name)).strip("-") or "school"
    candidate = base
    number = 2
    while candidate in used:
        candidate = f"{base}-{number}"
        number += 1
    used.add(candidate)
    return candidate


def load_settle():
    mapping = {}
    if not SETTLE_PATH.exists():
        return mapping
    for line in SETTLE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#") or "\t" not in line:
            continue
        english, setting = line.split("\t", 1)
        setting = setting.strip()
        if setting in SETTLE_KEYS:
            mapping[english.strip()] = setting
    return mapping


def main():
    qs_rows = parse_qs()
    settle_map = load_settle()
    fsr_pool = parse_fsr()
    zh_pool = parse_zh_ranked(ZH_RANKED_PATH) + parse_zh_pdf(ZH_PDF_PATH) + parse_zh_tsv(ZH_TSV_PATH)
    the_pool = parse_the()
    us_pool = parse_usnews()
    schools = []
    used = set()
    missed_the = []
    missed_us = []
    for row in qs_rows:
        key = norm(row["en"])
        zh = ZH_BY_EN.get(row["en"])
        if not zh:
            named = lookup(row["en"], zh_pool)
            zh = named["zh"] if named else row["en"]
        code, region = PLACES[row["country"]][:2]
        if region == "cn":
            continue
        the = lookup(row["en"], the_pool)
        us = lookup(row["en"], us_pool)
        fsr = lookup(row["en"], fsr_pool)
        if the is None:
            missed_the.append(row["en"])
        if us is None:
            missed_us.append(row["en"])
        schools.append({
            "id": slug(row["en"], used),
            "zh": zh,
            "en": row["en"],
            "region": region,
            "country": code,
            "qs": row["qs"],
            "the": None if the is None else the["rank"],
            "usnews": None if us is None else us["rank"],
            "researchEnv": None if the is None else the["env"],
            "industry": None if the is None else the["industry"],
            "faculty": None if fsr is None else fsr["faculty"],
            "setting": settle_map.get(row["en"], "unknown"),
        })
    for item in JOINT:
        schools.append({
            "id": item["id"],
            "zh": item["zh"],
            "en": item["en"],
            "region": "cn",
            "country": "cn",
            "qs": None,
            "qsBand": item.get("qsBand"),
            "the": None,
            "usnews": None,
            "researchEnv": None,
            "industry": None,
            "faculty": None,
            "setting": settle_map.get(item["en"], "unknown"),
        })
    present = {school["region"] for school in schools}
    regions = [{"id": rid, "zh": zh, "en": en} for rid, zh, en in REGION_ORDER if rid in present]
    places = {}
    for code, _region, zh, en in PLACES.values():
        if any(school["country"] == code for school in schools):
            places[code] = {"zh": zh, "en": en}
    payload = {"regions": regions, "places": places, "schools": schools}
    text = "window.NAIVE = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (ROOT / "data.js").write_text(text, encoding="utf-8")
    report = {
        "schools": len(schools),
        "missed_the": missed_the,
        "missed_us": missed_us,
        "sample": [{"en": s["en"], "zh": s["zh"], "qs": s["qs"], "the": s["the"], "us": s["usnews"]} for s in schools],
    }
    (ROOT / "build_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    english_only = [school["en"] for school in schools if school["zh"] == school["en"]]
    exact = [school["qs"] for school in schools if isinstance(school["qs"], int)]
    print(f"schools {len(schools)} last_exact {exact[-1] if exact else None} zh_ranked {len(zh_pool)} english_only {len(english_only)}")
    print("missed THE", len(missed_the))
    print("missed US", len(missed_us))
    for name in missed_the:
        print(" THE", name)
    for name in missed_us:
        print(" US", name)


if __name__ == "__main__":
    main()
