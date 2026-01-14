import streamlit as st
import pandas as pd
import os
import json
import random
import urllib.parse
from LLMResponse import LLMResponse

# ==========================================
# [함수 1] 안전하게 통계 수치를 가져오는 함수
# ==========================================
def get_safe_stat(series):
    """ 데이터가 비어있어도 에러 없이 '데이터 없음'을 반환하여 IndexError 방지 """
    if series is not None and not series.empty:
        try:
            # 인덱스가 존재할 경우에만 0번째 값을 가져옴
            return f"{series.index[0]} ({series.iloc[0]} 회)"
        except (IndexError, KeyError):
            return "분석 데이터 부족"
    return "데이터 없음 (0회)"

# ==========================================
# [함수 2] 태그 기반 실제 이미지 검색 및 출력
# ==========================================
def display_recommend_image(user_input):
    """ fashion_data.json에서 키워드 일치도가 가장 높은 스냅샷 출력 """
    json_path = 'fashion_data.json'
    
    # 파일 존재 여부 확인
    if not os.path.exists(json_path):
        st.warning("⚠️ 'fashion_data.json' 파일을 찾을 수 없습니다.")
        return
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except Exception as e:
        st.error(f"⚠️ JSON 로드 오류: {e}")
        return

    # 사용자 입력 키워드 분리 (예: 가을뮤트, 추움, 데이트)
    user_keywords = user_input.split()
    matched_items = []

    # 태그 매칭 로직
    for item in metadata:
        all_tags = " ".join(item.get('tags', []))
        # 입력된 단어 중 몇 개가 태그에 포함되는지 점수 계산
        score = sum(1 for kw in user_keywords if kw in all_tags)
        if score > 0:
            matched_items.append((score, item))

    # 결과가 있을 경우 출력
    if matched_items:
        # 점수가 가장 높은 것들 중 랜덤 선택
        matched_items.sort(key=lambda x: x[0], reverse=True)
        best_score = matched_items[0][0]
        top_list = [i for s, i in matched_items if s == best_score]
        selected = random.choice(top_list)
        
        # 경로 보정 및 이미지 출력
        img_path = selected['image_path'].replace('\\', '/')
        
        if os.path.exists(img_path):
            st.divider()
            st.markdown("### 📸 데이터 기반 실제 스타일링 추천")
            st.image(img_path, caption=f"추천 스냅 (태그: {', '.join(selected['tags'][:3])}...)")
            st.info(f"💡 이 코디는 선택하신 조건({user_input})과 {best_score}개의 태그가 일치합니다.")
            st.write(f"🔗 [무신사 스냅 상세 보기]({selected['url']})")
        else:
            st.warning(f"⚠️ 이미지 파일이 경로에 없습니다: {img_path}")
    else:
        st.info("💡 준비된 데이터 중 현재 조건과 일치하는 스냅 사진이 없습니다.")

# ==========================================
# [설정] 페이지 디자인 및 레이아웃
# ==========================================
st.set_page_config(page_title="LookXpertM Pro", layout="wide", page_icon="👗")

# 커스텀 CSS (카드 디자인 및 타이틀)
st.markdown("""
    <style>
    .report-card { background-color: #F8FAFC; padding: 25px; border-radius: 15px; border: 1px solid #E2E8F0; text-align: center; height: 180px; }
    .report-label { font-size: 0.9rem; color: #64748B; font-weight: 700; text-transform: uppercase; margin-bottom: 10px; }
    .report-value { font-size: 1.5rem; color: #2563EB; font-weight: 850; line-height: 1.3; }
    .main-title { text-align: center; font-size: 3.5rem; font-weight: 850; color: #4F46E5; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">lookXpertM</p>', unsafe_allow_html=True)

# LLM 봇 초기화 (세션 상태 유지하여 성능 최적화)
if 'bot' not in st.session_state:
    st.session_state.bot = LLMResponse()
bot = st.session_state.bot

# ==========================================
# [사이드바] 사용자 입력 컨트롤러
# ==========================================
w = st.sidebar.selectbox("🌡️ 날씨", ["추움", "보통", "더움", "한파"])
s = st.sidebar.selectbox("📍 상황", ["출근", "데이트", "캐주얼", "여행"])
t = st.sidebar.selectbox("🌈 톤", ["가을뮤트", "봄웜톤", "겨울쿨톤", "여름쿨톤"])
user_query = f"{t} {w} {s} 코디"

# ==========================================
# [메인 화면] 기능 탭 구성
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["✨ 스마트 추천", "🛍️ 쇼핑몰 연동", "🔗 트렌드 링크", "🎥 영상 & 트렌드"])

with tab1:
    if st.button("🚀 실시간 트렌드 분석 추천", use_container_width=True, type="primary"):
        with st.spinner("AI가 트렌드 데이터를 분석하고 리포트를 생성 중입니다..."):
            
            # 1. LLMResponse로부터 분석 데이터 가져오기
            # response 구조: (리포트문구, items_series, colors_series, materials_series)
            response = bot.GetLLMResponse(
                userInput = user_query,
                model_name = "gpt-4o-mini"
            )
            
            # 2. 상단 통계 카드 출력 (IndexError 방지 로직 적용)
            m1, m2, m3 = st.columns(3)
            with m1: 
                st.markdown(f'<div class="report-card"><div class="report-label">TOP ITEMS</div><div class="report-value">{get_safe_stat(response[1])}</div></div>', unsafe_allow_html=True)
            with m2: 
                st.markdown(f'<div class="report-card"><div class="report-label">TOP COLOURS</div><div class="report-value">{get_safe_stat(response[2])}</div></div>', unsafe_allow_html=True)
            with m3: 
                st.markdown(f'<div class="report-card"><div class="report-label">TOP MATERIALS</div><div class="report-value">{get_safe_stat(response[3])}</div></div>', unsafe_allow_html=True)

            # 3. 실제 패션 데이터(JSON) 기반 이미지 검색 결과 출력
            display_recommend_image(user_query)

            # 4. AI 리포트 전문 출력
            st.divider()
            st.subheader("📋 AI 스타일 전문가 리포트")
            st.markdown(response[0])

# 나머지 탭 기능 (외부 링크 연동)
with tab2:
    q = urllib.parse.quote(user_query)
    sc1, sc2, sc3 = st.columns(3)
    sc1.link_button("무신사", f"https://www.musinsa.com/search/goods?q={q}", use_container_width=True)
    sc2.link_button("지그재그", f"https://zigzag.kr/search?keyword={q}", use_container_width=True)
    sc3.link_button("29CM", f"https://search.29cm.co.kr/?keyword={q}", use_container_width=True)

with tab3:
    st.link_button("📰 VOGUE 매거진", "https://www.vogue.co.kr/fashion/fashion-trend/", use_container_width=True)
    st.link_button("📰 ELLE 매거진", "https://www.elle.co.kr/fashion/trends", use_container_width=True)

with tab4:
    cv1, cv2 = st.columns(2)
    cv1.link_button("🎬 유튜브 검색", f"https://www.youtube.com/results?search_query={urllib.parse.quote(user_query)}+추천", use_container_width=True)
    cv2.link_button("🔬 패션넷", "https://www.fashionnet.or.kr/trend/trend-now/", use_container_width=True)