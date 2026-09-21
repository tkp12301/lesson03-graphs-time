import pandas as pd
import plotly.express as px
import streamlit as st

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)


# ---------------------------------------------------------------------------
# 데이터 불러오기
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="데이터를 불러오는 중...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL)
    # 하이픈 없는 여덟 자리 숫자(예: 20240101) -> 진짜 날짜(datetime)
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df.sort_values(["날짜", "순위"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 공통 도우미
# ---------------------------------------------------------------------------
def insight(text: str) -> None:
    """그래프 아래에 '이 그래프로 알 수 있는 것' 한 문장을 보여 주는 자리."""
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.info(text)


# ---------------------------------------------------------------------------
# 그래프 구역들
# 새 그래프를 추가할 때는 section_N_... 함수를 하나 만들고
# 맨 아래 SECTIONS 목록에 넣으면 됩니다.
# ---------------------------------------------------------------------------
def section_1_daily_audience(df: pd.DataFrame) -> None:
    st.subheader("1. 영화별 일관객 변화")
    st.caption("영화를 고르면 날짜별 일관객이 선 그래프로 나타납니다.")

    # 박스오피스 10위권에 오래 머문 영화가 위로 오도록 정렬
    movies = df["영화명"].value_counts().index.tolist()
    movie = st.selectbox("영화 선택", movies, key="s1_movie")

    movie_df = df[df["영화명"] == movie].sort_values("날짜")

    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"{movie} - 날짜별 일관객",
        labels={"날짜": "날짜", "일관객": "일관객(명)"},
    )
    fig.update_traces(
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>일관객: %{y:,}명<extra></extra>"
    )
    fig.update_layout(yaxis_tickformat=",")
    st.plotly_chart(fig)

    insight("(여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요.)")


# 구역 목록: (표시할 이름, 그려 주는 함수)
SECTIONS = [
    ("일관객 변화", section_1_daily_audience),
    # ("새 그래프 이름", section_2_...),
]


# ---------------------------------------------------------------------------
# 화면 구성
# ---------------------------------------------------------------------------
st.title("영화 데이터 그래프 도감 1 - 시간")
st.write("1년치 일별 박스오피스 10위권 기록으로 시간에 따른 변화를 살펴봅니다.")

try:
    data = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했어요. 인터넷 연결이나 주소를 확인해 주세요. ({e})")
    st.stop()

for i, (_, draw) in enumerate(SECTIONS):
    if i > 0:
        st.divider()
    draw(data)
