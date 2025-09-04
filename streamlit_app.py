import streamlit as st
import requests
import openai
import os
from datetime import datetime
import json
from typing import List, Dict, Any

# 페이지 설정
st.set_page_config(
    page_title="뉴스 챗봇",
    page_icon="📰",
    layout="wide"
)

def get_news_from_newsapi(keyword: str, api_key: str) -> List[Dict[str, Any]]:
    """NewsAPI를 사용하여 뉴스 검색"""
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': keyword,
            'language': 'ko',
            'sortBy': 'publishedAt',
            'pageSize': 10,
            'apiKey': api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('articles', [])
    
    except Exception as e:
        st.error(f"뉴스 검색 중 오류가 발생했습니다: {str(e)}")
        return []

def get_news_from_guardian(keyword: str, api_key: str) -> List[Dict[str, Any]]:
    """Guardian API를 사용하여 뉴스 검색 (대체 API)"""
    try:
        url = "https://content.guardianapis.com/search"
        params = {
            'q': keyword,
            'page-size': 10,
            'show-fields': 'thumbnail,trailText,headline',
            'api-key': api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        
        for item in data.get('response', {}).get('results', []):
            article = {
                'title': item.get('webTitle', ''),
                'description': item.get('fields', {}).get('trailText', ''),
                'url': item.get('webUrl', ''),
                'urlToImage': item.get('fields', {}).get('thumbnail', ''),
                'source': {'name': 'The Guardian'},
                'publishedAt': item.get('webPublicationDate', '')
            }
            articles.append(article)
        
        return articles
    
    except Exception as e:
        st.error(f"Guardian API 뉴스 검색 중 오류가 발생했습니다: {str(e)}")
        return []

def get_mock_news(keyword: str) -> List[Dict[str, Any]]:
    """API 키가 없을 때 사용할 모의 뉴스 데이터"""
    mock_articles = [
        {
            'title': f'{keyword} 관련 최신 뉴스 1',
            'description': f'{keyword}에 대한 중요한 소식이 전해졌습니다. 관련 업계에서는 이번 발표가 향후 시장에 큰 영향을 미칠 것으로 예상한다고 밝혔습니다.',
            'url': 'https://example.com/news1',
            'urlToImage': 'https://via.placeholder.com/300x200?text=News+1',
            'source': {'name': '뉴스 소스 1'},
            'publishedAt': '2024-01-15T10:00:00Z'
        },
        {
            'title': f'{keyword} 관련 최신 뉴스 2',
            'description': f'{keyword} 분야의 새로운 동향이 발표되었습니다. 전문가들은 이러한 변화가 긍정적인 결과를 가져올 것이라고 전망하고 있습니다.',
            'url': 'https://example.com/news2',
            'urlToImage': 'https://via.placeholder.com/300x200?text=News+2',
            'source': {'name': '뉴스 소스 2'},
            'publishedAt': '2024-01-15T09:30:00Z'
        },
        {
            'title': f'{keyword} 관련 최신 뉴스 3',
            'description': f'{keyword}와 관련된 정책 변화가 논의되고 있습니다. 이번 변화는 많은 사람들에게 직접적인 영향을 미칠 것으로 예상됩니다.',
            'url': 'https://example.com/news3',
            'urlToImage': 'https://via.placeholder.com/300x200?text=News+3',
            'source': {'name': '뉴스 소스 3'},
            'publishedAt': '2024-01-15T09:00:00Z'
        }
    ]
    
    # 키워드에 따라 10개까지 확장
    extended_articles = []
    for i in range(10):
        article = mock_articles[i % len(mock_articles)].copy()
        article['title'] = f'{keyword} 관련 최신 뉴스 {i+1}'
        article['description'] = f'{keyword}에 대한 뉴스 {i+1}번입니다. ' + article['description'][:80] + '...'
        article['urlToImage'] = f'https://via.placeholder.com/300x200?text=News+{i+1}'
        extended_articles.append(article)
    
    return extended_articles

def truncate_text(text: str, max_length: int = 100) -> str:
    """텍스트를 지정된 길이로 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def display_news_grid(articles: List[Dict[str, Any]]):
    """뉴스를 그리드 형태로 표시"""
    if not articles:
        st.warning("검색된 뉴스가 없습니다.")
        return
    
    # 2열 그리드로 뉴스 표시
    for i in range(0, len(articles), 2):
        col1, col2 = st.columns(2)
        
        # 첫 번째 열
        if i < len(articles):
            with col1:
                display_news_card(articles[i], i)
        
        # 두 번째 열
        if i + 1 < len(articles):
            with col2:
                display_news_card(articles[i + 1], i + 1)

def display_news_card(article: Dict[str, Any], index: int):
    """개별 뉴스 카드 표시"""
    with st.container():
        st.markdown("---")
        
        # 썸네일 이미지
        if article.get('urlToImage'):
            try:
                st.image(article['urlToImage'], width=300)
            except:
                st.image('https://via.placeholder.com/300x200?text=No+Image', width=300)
        else:
            st.image('https://via.placeholder.com/300x200?text=No+Image', width=300)
        
        # 제목
        st.subheader(article.get('title', '제목 없음'))
        
        # 출처
        source_name = article.get('source', {}).get('name', '출처 불명')
        st.caption(f"📰 출처: {source_name}")
        
        # 발행일
        published_at = article.get('publishedAt', '')
        if published_at:
            try:
                date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
                st.caption(f"🕒 {formatted_date}")
            except:
                st.caption(f"🕒 {published_at}")
        
        # 내용 요약 (100자)
        description = article.get('description', '내용 없음')
        truncated_description = truncate_text(description, 100)
        st.write(truncated_description)
        
        # 원문 링크
        if article.get('url'):
            st.markdown(f"[원문 보기]({article['url']})")

def get_chatbot_response(messages: List[Dict[str, str]], news_context: str) -> str:
    """OpenAI를 사용한 챗봇 응답 생성"""
    try:
        # API 키 확인
        api_key = st.secrets.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "OpenAI API 키가 설정되지 않았습니다. 사이드바에서 API 키를 입력하거나 환경변수 OPENAI_API_KEY를 설정해주세요."
        
        # OpenAI 클라이언트 초기화
        client = openai.OpenAI(api_key=api_key)
        
        # 시스템 프롬프트 생성
        system_prompt = f"""당신은 뉴스 분석 전문가입니다. 다음 뉴스 정보를 바탕으로 사용자의 질문에 답변해주세요:

{news_context}

위 뉴스들을 참고하여 정확하고 유용한 정보를 제공하며, 출처를 명시해주세요. 
뉴스에 없는 내용에 대해서는 일반적인 지식을 바탕으로 도움이 되는 답변을 해주세요."""

        # 메시지 구성
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
        return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"

def main():
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "news_articles" not in st.session_state:
        st.session_state.news_articles = []
    if "current_keyword" not in st.session_state:
        st.session_state.current_keyword = ""
    
    # 사이드바
    with st.sidebar:
        st.header("🔍 뉴스 검색")
        
        # API 키 설정
        st.subheader("🔑 API Keys")
        
        # OpenAI API 키
        openai_key = st.text_input(
            "OpenAI API Key:",
            type="password",
            value=st.secrets.get('OPENAI_API_KEY', '') or os.getenv('OPENAI_API_KEY', ''),
            help="챗봇 기능을 위한 OpenAI API 키"
        )
        if openai_key:
            os.environ['OPENAI_API_KEY'] = openai_key
        
        # NewsAPI 키
        news_api_key = st.text_input(
            "NewsAPI Key (선택사항):",
            type="password",
            value=st.secrets.get('NEWS_API_KEY', '') or os.getenv('NEWS_API_KEY', ''),
            help="실제 뉴스 검색을 위한 NewsAPI 키 (없으면 모의 데이터 사용)"
        )
        
        st.divider()
        
        # 키워드 입력
        keyword = st.text_input(
            "관심 키워드를 입력하세요:",
            value=st.session_state.current_keyword,
            placeholder="예: 인공지능, 경제, 스포츠"
        )
        
        # 검색 버튼
        if st.button("🔍 뉴스 검색", use_container_width=True):
            if keyword:
                with st.spinner("뉴스를 검색하고 있습니다..."):
                    if news_api_key:
                        articles = get_news_from_newsapi(keyword, news_api_key)
                    else:
                        articles = get_mock_news(keyword)
                    
                    st.session_state.news_articles = articles
                    st.session_state.current_keyword = keyword
                    st.session_state.messages = []  # 새 검색 시 채팅 초기화
                    st.rerun()
            else:
                st.warning("키워드를 입력해주세요.")
        
        # 채팅 초기화 버튼
        if st.button("💬 채팅 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # 메인 화면
    st.title("📰 뉴스 챗봇")
    
    if st.session_state.current_keyword:
        st.subheader(f"'{st.session_state.current_keyword}' 관련 최신 뉴스")
        
        # 뉴스와 채팅을 나란히 배치
        news_col, chat_col = st.columns([3, 2])
        
        with news_col:
            st.markdown("### 📰 뉴스 목록")
            display_news_grid(st.session_state.news_articles)
        
        with chat_col:
            st.markdown("### 💬 뉴스 챗봇")
            
            # 채팅 히스토리 표시
            chat_container = st.container()
            with chat_container:
                if not st.session_state.messages:
                    with st.chat_message("assistant"):
                        st.write(f"안녕하세요! '{st.session_state.current_keyword}' 관련 뉴스에 대해 궁금한 것이 있으시면 언제든 물어보세요!")
                
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
            
            # 사용자 입력
            if prompt := st.chat_input("뉴스에 대해 궁금한 것을 물어보세요..."):
                # 사용자 메시지 추가
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # 사용자 메시지 표시
                with st.chat_message("user"):
                    st.write(prompt)
                
                # 뉴스 컨텍스트 생성
                news_context = ""
                for i, article in enumerate(st.session_state.news_articles):
                    news_context += f"\n뉴스 {i+1}:\n"
                    news_context += f"제목: {article.get('title', '')}\n"
                    news_context += f"출처: {article.get('source', {}).get('name', '')}\n"
                    news_context += f"내용: {truncate_text(article.get('description', ''), 200)}\n"
                
                # 챗봇 응답 생성
                with st.chat_message("assistant"):
                    with st.spinner("답변을 생성하고 있습니다..."):
                        response = get_chatbot_response(st.session_state.messages, news_context)
                        st.write(response)
                
                # 챗봇 응답 추가
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    else:
        st.info("좌측 사이드바에서 관심 키워드를 입력하고 검색 버튼을 눌러주세요.")
        
        # 사용법 안내
        st.markdown("""
        ## 📋 사용법
        
        1. **API 키 설정**: 사이드바에서 OpenAI API 키를 입력하세요 (필수)
        2. **NewsAPI 키**: 실제 뉴스 검색을 원하면 NewsAPI 키를 입력하세요 (선택사항)
        3. **키워드 입력**: 관심있는 키워드를 입력하고 검색하세요
        4. **뉴스 확인**: 최신 뉴스 10개가 그리드 형태로 표시됩니다
        5. **챗봇 질문**: 우측 채팅창에서 뉴스에 대해 질문하세요
        
        ## 🔑 API 키 발급 방법
        
        - **OpenAI API**: [OpenAI Platform](https://platform.openai.com/api-keys)
        - **NewsAPI**: [NewsAPI.org](https://newsapi.org/register) (무료 계정 가능)
        """)

if __name__ == "__main__":
    main()
