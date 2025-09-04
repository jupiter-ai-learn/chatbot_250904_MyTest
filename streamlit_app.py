import streamlit as st
import time
from datetime import datetime
import openai
import os

# 언어별 텍스트 설정
LANGUAGES = {
    "한국어": {
        "title": "🧳 여행 챗봇",
        "language_label": "언어 선택:",
        "destination_label": "여행지 선택:",
        "chat_placeholder": "여행에 대해 궁금한 것을 물어보세요...",
        "send_button": "전송",
        "clear_button": "대화 초기화",
        "welcome_message": "안녕하세요! 저는 여행 도우미 챗봇입니다. 선택하신 여행지에 대해 무엇이든 물어보세요!",
        "destinations": {
            "서울": "서울",
            "대전": "대전", 
            "대구": "대구",
            "부산": "부산"
        }
    },
    "English": {
        "title": "🧳 Travel Chatbot",
        "language_label": "Select Language:",
        "destination_label": "Select Destination:",
        "chat_placeholder": "Ask me anything about your travel...",
        "send_button": "Send",
        "clear_button": "Clear Chat",
        "welcome_message": "Hello! I'm your travel assistant chatbot. Feel free to ask me anything about your selected destination!",
        "destinations": {
            "서울": "Seoul",
            "대전": "Daejeon",
            "대구": "Daegu", 
            "부산": "Busan"
        }
    },
    "中文": {
        "title": "🧳 旅行聊天机器人",
        "language_label": "选择语言:",
        "destination_label": "选择目的地:",
        "chat_placeholder": "请询问关于旅行的任何问题...",
        "send_button": "发送",
        "clear_button": "清除对话",
        "welcome_message": "您好！我是您的旅行助手聊天机器人。请随时询问关于您选择的目的地的任何问题！",
        "destinations": {
            "서울": "首尔",
            "대전": "大田",
            "대구": "大邱",
            "부산": "釜山"
        }
    },
    "日本語": {
        "title": "🧳 旅行チャットボット",
        "language_label": "言語を選択:",
        "destination_label": "目的地を選択:",
        "chat_placeholder": "旅行について何でもお聞きください...",
        "send_button": "送信",
        "clear_button": "チャットをクリア",
        "welcome_message": "こんにちは！私はあなたの旅行アシスタントチャットボットです。選択した目的地について何でもお聞きください！",
        "destinations": {
            "서울": "ソウル",
            "대전": "大田",
            "대구": "大邱",
            "부산": "釜山"
        }
    }
}

# 여행지별 정보 데이터베이스
DESTINATION_INFO = {
    "서울": {
        "한국어": {
            "attractions": ["경복궁", "명동", "홍대", "강남", "북촌한옥마을", "남산타워", "동대문"],
            "food": ["김치찌개", "불고기", "비빔밥", "치킨", "떡볶이", "한정식"],
            "transport": "지하철 1-9호선, 버스, 택시가 잘 발달되어 있습니다.",
            "weather": "사계절이 뚜렷하며, 봄과 가을이 여행하기 좋습니다."
        },
        "English": {
            "attractions": ["Gyeongbokgung Palace", "Myeongdong", "Hongdae", "Gangnam", "Bukchon Hanok Village", "N Seoul Tower", "Dongdaemun"],
            "food": ["Kimchi Jjigae", "Bulgogi", "Bibimbap", "Korean Fried Chicken", "Tteokbokki", "Korean Traditional Meal"],
            "transport": "Well-developed subway lines 1-9, buses, and taxis are available.",
            "weather": "Four distinct seasons, spring and autumn are the best times to visit."
        },
        "中文": {
            "attractions": ["景福宫", "明洞", "弘大", "江南", "北村韩屋村", "南山塔", "东大门"],
            "food": ["泡菜汤", "烤肉", "拌饭", "炸鸡", "年糕", "韩定食"],
            "transport": "地铁1-9号线、公交车、出租车交通发达。",
            "weather": "四季分明，春秋两季最适合旅游。"
        },
        "日本語": {
            "attractions": ["景福宮", "明洞", "弘大", "江南", "北村韓屋村", "Nソウルタワー", "東大門"],
            "food": ["キムチチゲ", "プルコギ", "ビビンバ", "チキン", "トッポッキ", "韓定食"],
            "transport": "地下鉄1-9号線、バス、タクシーが発達しています。",
            "weather": "四季がはっきりしており、春と秋が旅行に最適です。"
        }
    },
    "대전": {
        "한국어": {
            "attractions": ["엑스포과학공원", "대청호", "계룡산국립공원", "한밭수목원", "대전오월드"],
            "food": ["성심당 튀김소보로", "대전 칼국수", "충청도 향토음식"],
            "transport": "지하철 1호선과 버스 교통이 편리합니다.",
            "weather": "내륙 기후로 여름은 덥고 겨울은 춥습니다."
        },
        "English": {
            "attractions": ["Expo Science Park", "Daecheong Lake", "Gyeryongsan National Park", "Hanbat Arboretum", "Daejeon O-World"],
            "food": ["Sungsimdang Fried Soboro", "Daejeon Kalguksu", "Chungcheong Local Cuisine"],
            "transport": "Convenient subway line 1 and bus transportation.",
            "weather": "Continental climate with hot summers and cold winters."
        },
        "中文": {
            "attractions": ["世博科学公园", "大清湖", "鸡龙山国立公园", "韩밭树木园", "大田O-World"],
            "food": ["圣心堂炸面包", "大田刀削面", "忠清道乡土料理"],
            "transport": "地铁1号线和公交车交通便利。",
            "weather": "内陆气候，夏季炎热，冬季寒冷。"
        },
        "日本語": {
            "attractions": ["エキスポ科学公園", "大清湖", "鶏龍山国立公園", "ハンバッ樹木園", "大田Oワールド"],
            "food": ["聖心堂揚げソボロ", "大田カルグクス", "忠清道郷土料理"],
            "transport": "地下鉄1号線とバス交通が便利です。",
            "weather": "内陸気候で夏は暑く冬は寒いです。"
        }
    },
    "대구": {
        "한국어": {
            "attractions": ["동성로", "서문시장", "팔공산", "앞산공원", "김광석다시그리기길"],
            "food": ["대구 찜갈비", "막창", "동인동 찜갈비", "납작만두"],
            "transport": "지하철 1-3호선과 버스가 운행됩니다.",
            "weather": "분지 지형으로 여름이 매우 덥습니다."
        },
        "English": {
            "attractions": ["Dongseongno", "Seomun Market", "Palgongsan", "Apsan Park", "Kim Gwangseok Street"],
            "food": ["Daegu Steamed Ribs", "Makchang", "Dongin-dong Steamed Ribs", "Flat Dumplings"],
            "transport": "Subway lines 1-3 and buses are available.",
            "weather": "Basin topography makes summers very hot."
        },
        "中文": {
            "attractions": ["东城路", "西门市场", "八公山", "앞山公园", "金光石重绘街"],
            "food": ["大邱蒸排骨", "烤肠", "东仁洞蒸排骨", "扁饺子"],
            "transport": "地铁1-3号线和公交车运营。",
            "weather": "盆地地形，夏季非常炎热。"
        },
        "日本語": {
            "attractions": ["東城路", "西門市場", "八公山", "앞山公園", "キム・グァンソク通り"],
            "food": ["大邱蒸しカルビ", "マクチャン", "東仁洞蒸しカルビ", "平たい餃子"],
            "transport": "地下鉄1-3号線とバスが運行しています。",
            "weather": "盆地地形で夏は非常に暑いです。"
        }
    },
    "부산": {
        "한국어": {
            "attractions": ["해운대해수욕장", "광안리해수욕장", "감천문화마을", "자갈치시장", "태종대", "부산타워"],
            "food": ["돼지국밥", "밀면", "씨앗호떡", "회", "부산어묵"],
            "transport": "지하철 1-4호선, 버스, 해운대 해변열차가 있습니다.",
            "weather": "해양성 기후로 온화하며 여름 휴양지로 인기입니다."
        },
        "English": {
            "attractions": ["Haeundae Beach", "Gwangalli Beach", "Gamcheon Culture Village", "Jagalchi Market", "Taejongdae", "Busan Tower"],
            "food": ["Pork Soup Rice", "Milmyeon", "Seed Hotteok", "Raw Fish", "Busan Fish Cake"],
            "transport": "Subway lines 1-4, buses, and Haeundae Beach Train are available.",
            "weather": "Maritime climate, mild and popular summer resort destination."
        },
        "中文": {
            "attractions": ["海云台海水浴场", "广安里海水浴场", "甘川文化村", "札嘎其市场", "太宗台", "釜山塔"],
            "food": ["猪肉汤饭", "冷面", "种子糖饼", "生鱼片", "釜山鱼糕"],
            "transport": "地铁1-4号线、公交车、海云台海滩列车。",
            "weather": "海洋性气候温和，是受欢迎的夏季度假胜地。"
        },
        "日本語": {
            "attractions": ["海雲台ビーチ", "広安里ビーチ", "甘川文化村", "チャガルチ市場", "太宗台", "釜山タワー"],
            "food": ["豚クッパ", "ミルミョン", "種ホットク", "刺身", "釜山かまぼこ"],
            "transport": "地下鉄1-4号線、バス、海雲台ビーチトレインがあります。",
            "weather": "海洋性気候で温暖、夏のリゾート地として人気です。"
        }
    }
}

def get_system_prompt(destination, language):
    """언어와 목적지에 따른 시스템 프롬프트 생성"""
    dest_info = DESTINATION_INFO.get(destination, {}).get(language, {})
    
    if language == "한국어":
        return f"""당신은 {destination} 여행 전문 가이드입니다. 다음 정보를 바탕으로 친절하고 도움이 되는 답변을 해주세요:

주요 관광지: {', '.join(dest_info.get('attractions', []))}
대표 음식: {', '.join(dest_info.get('food', []))}
교통 정보: {dest_info.get('transport', '')}
날씨 정보: {dest_info.get('weather', '')}

사용자의 질문에 대해 구체적이고 실용적인 정보를 제공하며, 추가 질문을 유도하는 친근한 톤으로 답변해주세요."""
    elif language == "English":
        return f"""You are a travel guide specialist for {destination}. Please provide helpful and friendly responses based on the following information:

Major attractions: {', '.join(dest_info.get('attractions', []))}
Representative foods: {', '.join(dest_info.get('food', []))}
Transportation info: {dest_info.get('transport', '')}
Weather info: {dest_info.get('weather', '')}

Provide specific and practical information for user questions, and respond in a friendly tone that encourages further questions."""
    elif language == "中文":
        return f"""您是{destination}的旅游专业向导。请根据以下信息提供有用和友好的回答：

主要景点：{', '.join(dest_info.get('attractions', []))}
代表性美食：{', '.join(dest_info.get('food', []))}
交通信息：{dest_info.get('transport', '')}
天气信息：{dest_info.get('weather', '')}

请为用户问题提供具体实用的信息，并以友好的语调回答，鼓励进一步提问。"""
    elif language == "日本語":
        return f"""{destination}の旅行専門ガイドです。以下の情報に基づいて、親切で役立つ回答をしてください：

主要観光地：{', '.join(dest_info.get('attractions', []))}
代表的な料理：{', '.join(dest_info.get('food', []))}
交通情報：{dest_info.get('transport', '')}
天気情報：{dest_info.get('weather', '')}

ユーザーの質問に対して具体的で実用的な情報を提供し、さらなる質問を促すフレンドリーなトーンで回答してください。"""

def get_chatbot_response(messages, destination, language):
    """OpenAI GPT-4o Mini를 사용한 챗봇 응답 생성"""
    try:
        # OpenAI API 키 확인 (Streamlit secrets 우선, 환경변수 대체)
        api_key = st.secrets.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            if language == "한국어":
                return "OpenAI API 키가 설정되지 않았습니다. 사이드바에서 API 키를 입력하거나 환경변수 OPENAI_API_KEY를 설정해주세요."
            elif language == "English":
                return "OpenAI API key is not set. Please enter your API key in the sidebar or set the OPENAI_API_KEY environment variable."
            elif language == "中文":
                return "未设置OpenAI API密钥。请在侧边栏输入API密钥或设置OPENAI_API_KEY环境变量。"
            elif language == "日本語":
                return "OpenAI APIキーが設定されていません。サイドバーでAPIキーを入力するか、OPENAI_API_KEY環境変数を設定してください。"
        
        # OpenAI 클라이언트 초기화
        client = openai.OpenAI(api_key=api_key)
        
        # 시스템 프롬프트 생성
        system_prompt = get_system_prompt(destination, language)
        
        # 메시지 구성 (시스템 메시지 + 대화 히스토리)
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend(messages)
        
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        if language == "한국어":
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
        elif language == "English":
            return f"Sorry, an error occurred while generating the response: {str(e)}"
        elif language == "中文":
            return f"抱歉，生成回答时发生错误：{str(e)}"
        elif language == "日本語":
            return f"申し訳ございません。回答生成中にエラーが発生しました：{str(e)}"

def main():
    st.set_page_config(
        page_title="Travel Chatbot",
        page_icon="🧳",
        layout="wide"
    )
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "language" not in st.session_state:
        st.session_state.language = "한국어"
    if "destination" not in st.session_state:
        st.session_state.destination = "서울"
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = bool(st.secrets.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY'))
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # OpenAI API 키 설정
        st.subheader("🔑 OpenAI API Key")
        api_key_input = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            value=st.secrets.get('OPENAI_API_KEY', '') or os.getenv('OPENAI_API_KEY', ''),
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        if api_key_input:
            os.environ['OPENAI_API_KEY'] = api_key_input
            st.session_state.api_key_set = True
            st.success("✅ API Key set successfully!")
        elif not st.session_state.api_key_set:
            st.warning("⚠️ Please enter your OpenAI API Key to use the chatbot.")
        
        st.divider()
        
        # 언어 선택
        language = st.selectbox(
            "Language / 언어 / 语言 / 言語:",
            ["한국어", "English", "中文", "日本語"],
            index=["한국어", "English", "中文", "日본語"].index(st.session_state.language)
        )
        
        # 언어가 변경되면 세션 상태 업데이트
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
        
        # 현재 언어의 텍스트 가져오기
        texts = LANGUAGES[language]
        
        # 여행지 선택
        destination = st.selectbox(
            texts["destination_label"],
            ["서울", "대전", "대구", "부산"],
            format_func=lambda x: texts["destinations"][x],
            index=["서울", "대전", "대구", "부산"].index(st.session_state.destination)
        )
        
        # 여행지가 변경되면 세션 상태 업데이트
        if destination != st.session_state.destination:
            st.session_state.destination = destination
            st.rerun()
        
        # 대화 초기화 버튼
        if st.button(texts["clear_button"], use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # 메인 화면
    st.title(texts["title"])
    st.markdown(f"**{texts['destination_label']}** {texts['destinations'][destination]}")
    
    # 채팅 히스토리 표시
    chat_container = st.container()
    
    with chat_container:
        # 환영 메시지 (대화가 비어있을 때만)
        if not st.session_state.messages:
            with st.chat_message("assistant"):
                st.write(texts["welcome_message"])
        
        # 기존 메시지들 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input(texts["chat_placeholder"]):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(prompt)
        
        # 챗봇 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # OpenAI API를 사용하여 응답 생성
                response = get_chatbot_response(st.session_state.messages, destination, language)
                st.write(response)
        
        # 챗봇 응답 추가
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # 화면 새로고침
        st.rerun()

if __name__ == "__main__":
    main()
