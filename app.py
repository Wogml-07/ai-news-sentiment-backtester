import streamlit as st
import requests
from bs4 import BeautifulSoup

# ==========================================
# [기능 1] 네이버 뉴스 크롤링 함수 (순수 파이썬)
# ==========================================
def crawl_naver_news(search_keyword):
    # 네이버 뉴스 검색 URL (최신순 정렬)
    url = f"https://search.naver.com/search.naver?where=news&query={search_keyword}&sm=tab_smr&pd=0"

    # 봇(Bot) 차단을 막기 위한 브라우저 흉내용 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # HTML에서 'news_tit'이라는 클래스 방(뉴스 제목)을 다 찾아라!
        news_titles = soup.select("a.news_tit")

        news_list = []
        # 최신 뉴스 상위 5개만 긁어오기
        for title in news_titles[:5]:
            news_list.append({
                "title": title.get_text(), # 뉴스 제목 글자 추출
                "link": title["href"]      # 뉴스 링크 추출
            })
        return news_list
    except Exception as e:
        return []

# ==========================================
# [기능 2] Streamlit 웹 화면 꾸미기 (순수 파이썬)
# ==========================================
st.set_page_config(page_title="AI 뉴스 감성분석기", layout="centered")

st.title("📈 AI 뉴스 감성 분석 백테스터")
st.caption("인공지능개론 기말 프로젝트 - 팀원 1 데이터 수집기 창")

# 텍스트 입력창 (사용자가 주식 이름을 입력하는 곳)
stock_name = st.text_input("분석할 주식 종목명을 입력하세요:", value="삼성전자")

# 버튼을 누르면 밑에 크롤링 코드가 작동함
if st.button("뉴스 수집 및 분석 시작", type="primary"):
    st.subheader(f"🔍 '{stock_name}' 관련 최신 뉴스 수집 결과")

    # 로딩 애니메이션 띄우기
    with st.spinner("네이버 뉴스에서 실시간 데이터를 가져오는 중..."):
        captured_news = crawl_naver_news(stock_name)

    if captured_news:
        # 긁어온 뉴스를 화면에 하나씩 예쁘게 출력
        for i, news in enumerate(captured_news, 1):
            with st.container():
                st.markdown(f"**[{i}] {news['title']}**")
                st.caption(f"[뉴스 링크 바로가기]({news['link']})")
                st.write("---")

        # 🔥 [매우 중요] 팀원 2(AI 담당)에게 넘겨줄 파이썬 리스트 구조 예시
        raw_titles = [news['title'] for news in captured_news]
        st.info(f"🤖 **팀원 2(AI)에게 전달할 데이터 바구니:** {raw_titles}")
    else:
        st.error("뉴스를 가져오지 못했습니다. 종목명을 다시 확인해주세요.")
