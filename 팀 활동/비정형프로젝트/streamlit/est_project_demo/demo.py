import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# 페이지 설정
st.set_page_config(
    page_title="키워드 트렌드 분석",
    page_icon="📊",
    layout="wide"
)

# 세션 상태 초기화
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# 제목
st.title("🔍 키워드 트렌드 분석 도구")
st.markdown("---")

# 사이드바 - 검색 설정
with st.sidebar:
    st.header("검색 설정")
    
    # 키워드 입력
    keyword = st.text_input("키워드 입력", placeholder="예: 인공지능, 챗GPT")
    
    # 검색 필터
    st.subheader("검색 필터")
    platform = st.multiselect(
        "플랫폼 선택",
        ["네이버 블로그", "네이버 카페", "인스타그램", "유튜브"],
        default=["네이버 블로그"]
    )
    
    date_range = st.date_input(
        "기간 설정",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )
    
    # 크롤링 옵션
    st.subheader("크롤링 옵션")
    max_results = st.slider("최대 결과 수", 10, 500, 100)
    headless_mode = st.checkbox("백그라운드 실행 (Headless)", value=True)
    
    # 검색 버튼
    search_button = st.button("🔍 검색 시작", type="primary", use_container_width=True)
    
    # 검색 기록
    if st.session_state.search_history:
        st.markdown("---")
        st.subheader("최근 검색")
        for hist in st.session_state.search_history[-5:]:
            if st.button(hist, key=f"hist_{hist}", use_container_width=True):
                keyword = hist

# 메인 영역
if search_button and keyword:
    # 검색 기록 추가
    if keyword not in st.session_state.search_history:
        st.session_state.search_history.append(keyword)
    
    # 로딩 표시
    with st.spinner(f"'{keyword}' 키워드를 분석 중입니다..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 단계별 진행 시뮬레이션
        status_text.text("1/4 데이터 크롤링 중...")
        progress_bar.progress(25)
        time.sleep(0.5)
        
        status_text.text("2/4 빈도수 분석 중...")
        progress_bar.progress(50)
        time.sleep(0.5)
        
        status_text.text("3/4 감정 분석 중...")
        progress_bar.progress(75)
        time.sleep(0.5)
        
        status_text.text("4/4 추세 분석 중...")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        progress_bar.empty()
        status_text.empty()
    
    # 결과 표시
    st.success(f"✅ '{keyword}' 분석 완료!")
    
    # 탭으로 결과 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 요약", "📈 트렌드", "😊 감정분석", "📝 원본데이터"])
    
    with tab1:
        st.header("분석 요약")
        
        # 메트릭 카드
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 게시글", "1,247", delta="12%", delta_color="normal")
        with col2:
            st.metric("일평균 게시", "42", delta="-5%", delta_color="inverse")
        with col3:
            st.metric("긍정 비율", "68%", delta="8%", delta_color="normal")
        with col4:
            st.metric("트렌드", "상승", delta="15%", delta_color="normal")
        
        st.markdown("---")
        
        # LLM 요약
        st.subheader("🤖 AI 요약")
        summary_box = st.container(border=True)
        with summary_box:
            st.markdown(f"""
            **'{keyword}' 키워드 분석 결과**
            
            최근 30일간 '{keyword}' 관련 게시글이 **12% 증가**하며 상승 추세를 보이고 있습니다.
            
            **주요 발견사항:**
            - 전체 감정 중 **68%가 긍정적**이며, 특히 지난 주에 긍정 비율이 급증했습니다
            - 주요 언급 플랫폼은 네이버 블로그(45%), 인스타그램(30%), 유튜브(25%) 순입니다
            - 가장 많이 연관된 키워드: "활용법", "추천", "장단점", "비교"
            
            **추세 분석:**
            - 초반 대비 현재 언급량이 **15% 증가**했으며, 특히 주말에 활동이 집중됩니다
            - 부정적 의견은 주로 "가격", "접근성" 관련 내용이 대부분입니다
            """)
    
    with tab2:
        st.header("시간별 트렌드")
        
        # 샘플 데이터 생성 (실제로는 크롤링 데이터 사용)
        dates = pd.date_range(start=date_range[0], end=date_range[1], freq='D')
        trend_data = pd.DataFrame({
            'date': dates,
            'count': [30 + i*2 + (i%7)*5 for i in range(len(dates))]
        })
        
        # 트렌드 차트
        fig = px.line(trend_data, x='date', y='count', 
                     title=f"'{keyword}' 일별 게시글 수",
                     labels={'date': '날짜', 'count': '게시글 수'})
        fig.update_traces(line_color='#1f77b4', line_width=3)
        fig.update_layout(hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        # 플랫폼별 분포
        col1, col2 = st.columns(2)
        
        with col1:
            platform_data = pd.DataFrame({
                'platform': ['네이버 블로그', '인스타그램', '유튜브', '네이버 카페'],
                'count': [560, 374, 312, 1]
            })
            fig2 = px.pie(platform_data, values='count', names='platform',
                         title='플랫폼별 분포')
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            hourly_data = pd.DataFrame({
                'hour': list(range(24)),
                'count': [20, 15, 10, 8, 5, 10, 25, 45, 60, 55, 50, 48, 
                         52, 58, 62, 70, 75, 80, 85, 70, 60, 50, 40, 30]
            })
            fig3 = px.bar(hourly_data, x='hour', y='count',
                         title='시간대별 게시 패턴',
                         labels={'hour': '시간', 'count': '게시글 수'})
            st.plotly_chart(fig3, use_container_width=True)
    
    with tab3:
        st.header("감정 분석")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 감정 분포
            sentiment_data = pd.DataFrame({
                'sentiment': ['긍정', '중립', '부정'],
                'count': [848, 274, 125],
                'color': ['#00D26A', '#FFB340', '#FF4B4B']
            })
            
            fig4 = go.Figure(data=[go.Bar(
                x=sentiment_data['sentiment'],
                y=sentiment_data['count'],
                marker_color=sentiment_data['color'],
                text=sentiment_data['count'],
                textposition='auto',
            )])
            fig4.update_layout(title='감정 분포', showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            # 시간별 감정 추이
            sentiment_trend = pd.DataFrame({
                'date': dates,
                'positive': [20 + i*1.5 for i in range(len(dates))],
                'neutral': [8 + i*0.3 for i in range(len(dates))],
                'negative': [2 + i*0.2 for i in range(len(dates))]
            })
            
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(x=sentiment_trend['date'], y=sentiment_trend['positive'],
                                     name='긍정', line=dict(color='#00D26A', width=2)))
            fig5.add_trace(go.Scatter(x=sentiment_trend['date'], y=sentiment_trend['neutral'],
                                     name='중립', line=dict(color='#FFB340', width=2)))
            fig5.add_trace(go.Scatter(x=sentiment_trend['date'], y=sentiment_trend['negative'],
                                     name='부정', line=dict(color='#FF4B4B', width=2)))
            fig5.update_layout(title='일별 감정 추이', hovermode='x unified')
            st.plotly_chart(fig5, use_container_width=True)
        
        # 주요 키워드
        st.subheader("감정별 주요 키워드")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**긍정 키워드**")
            positive_keywords = pd.DataFrame({
                '키워드': ['추천', '좋아요', '최고', '유용', '만족'],
                '빈도': [245, 198, 156, 142, 107]
            })
            st.dataframe(positive_keywords, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("**중립 키워드**")
            neutral_keywords = pd.DataFrame({
                '키워드': ['사용', '방법', '기능', '정보', '확인'],
                '빈도': [189, 145, 132, 98, 87]
            })
            st.dataframe(neutral_keywords, hide_index=True, use_container_width=True)
        
        with col3:
            st.markdown("**부정 키워드**")
            negative_keywords = pd.DataFrame({
                '키워드': ['비싸다', '어렵다', '불편', '오류', '실망'],
                '빈도': [78, 65, 54, 43, 38]
            })
            st.dataframe(negative_keywords, hide_index=True, use_container_width=True)
    
    with tab4:
        st.header("원본 데이터")
        
        # 샘플 크롤링 데이터
        sample_data = pd.DataFrame({
            '날짜': pd.date_range(end=datetime.now(), periods=20, freq='H'),
            '플랫폼': ['네이버 블로그', '인스타그램', '유튜브', '네이버 카페'] * 5,
            '제목': [f'{keyword} 관련 게시글 {i+1}' for i in range(20)],
            '감정': ['긍정', '긍정', '중립', '부정', '긍정'] * 4,
            '조회수': [100 + i*50 for i in range(20)]
        })
        
        # 필터
        col1, col2 = st.columns(2)
        with col1:
            platform_filter = st.multiselect(
                "플랫폼 필터",
                options=sample_data['플랫폼'].unique(),
                default=sample_data['플랫폼'].unique()
            )
        with col2:
            sentiment_filter = st.multiselect(
                "감정 필터",
                options=sample_data['감정'].unique(),
                default=sample_data['감정'].unique()
            )
        
        # 필터링된 데이터
        filtered_data = sample_data[
            (sample_data['플랫폼'].isin(platform_filter)) &
            (sample_data['감정'].isin(sentiment_filter))
        ]
        
        st.dataframe(filtered_data, use_container_width=True, hide_index=True)
        
        # 데이터 다운로드
        csv = filtered_data.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f"{keyword}_분석결과_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    # 초기 화면
    st.info("👈 왼쪽 사이드바에서 키워드를 입력하고 검색을 시작하세요!")
    
    # 사용 가이드
    with st.expander("📖 사용 가이드"):
        st.markdown("""
        ### 사용 방법
        1. **키워드 입력**: 분석하고 싶은 키워드를 입력하세요
        2. **플랫폼 선택**: 크롤링할 플랫폼을 선택하세요
        3. **기간 설정**: 분석할 기간을 설정하세요
        4. **검색 시작**: 버튼을 클릭하여 분석을 시작하세요
        
        ### 주요 기능
        - 📊 **요약**: AI가 분석한 전체 트렌드 요약
        - 📈 **트렌드**: 시간별, 플랫폼별 추세 분석
        - 😊 **감정분석**: 긍정/부정/중립 감정 분포
        - 📝 **원본데이터**: 크롤링한 실제 데이터 확인 및 다운로드
        """)
    
    # 샘플 키워드 제안
    st.subheader("🔥 인기 키워드")
    cols = st.columns(4)
    sample_keywords = ["ChatGPT", "AI", "파이썬", "데이터분석"]
    for col, kw in zip(cols, sample_keywords):
        col.button(kw, use_container_width=True, key=f"sample_{kw}")

# 푸터
st.markdown("---")
st.caption("💡 Tip: 여러 키워드를 비교하려면 각각 검색한 후 결과를 저장하세요.")