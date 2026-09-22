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


def section_2_top5_daily_audience(df: pd.DataFrame) -> None:
    st.subheader("2. 일관객 합계 상위 5편 비교")
    st.caption("범례의 영화 이름을 누르면 그 영화를 끄고 켤 수 있어요. 더블클릭하면 그 영화만 남아요.")

    # 기간 전체 일관객 합계가 가장 큰 5편
    top5 = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
    top_df = df[df["영화명"].isin(top5)].sort_values("날짜")

    fig = px.line(
        top_df,
        x="날짜",
        y="일관객",
        color="영화명",
        category_orders={"영화명": top5},  # 합계 순서대로 범례 정렬
        title="일관객 합계 상위 5편 - 날짜별 일관객",
        labels={"날짜": "날짜", "일관객": "일관객(명)", "영화명": "영화"},
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{x|%Y-%m-%d}<br>"
            "일관객: %{y:,}명<extra></extra>"
        )
    )
    fig.update_layout(yaxis_tickformat=",", legend_title_text="영화 (클릭해서 켜고 끄기)")
    st.plotly_chart(fig)

    insight("(여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요.)")


def section_3_daily_total_area(df: pd.DataFrame) -> None:
    st.subheader("3. 날짜별 10위권 일관객 합계")
    st.caption("그날 10위권 영화들의 일관객을 모두 더한 값이에요. 합계가 가장 컸던 3일을 표시했어요.")

    daily = df.groupby("날짜", as_index=False)["일관객"].sum()
    daily = daily.rename(columns={"일관객": "10위권 합계"}).sort_values("날짜")

    fig = px.area(
        daily,
        x="날짜",
        y="10위권 합계",
        title="날짜별 10위권 일관객 합계",
        labels={"날짜": "날짜", "10위권 합계": "10위권 일관객 합계(명)"},
    )
    fig.update_traces(
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>10위권 합계: %{y:,}명<extra></extra>"
    )

    # 합계가 가장 컸던 3일: 점으로 찍고 날짜를 적기
    top3 = daily.nlargest(3, "10위권 합계").sort_values("날짜")
    fig.add_scatter(
        x=top3["날짜"],
        y=top3["10위권 합계"],
        mode="markers+text",
        text=top3["날짜"].dt.strftime("%Y-%m-%d"),
        # 날짜가 가까운 날끼리 글자가 겹치지 않도록 왼쪽/가운데/오른쪽으로 나눔
        textposition=["top left", "top center", "top right"][: len(top3)],
        textfont=dict(size=13),
        marker=dict(size=11, color="crimson", line=dict(width=2, color="white")),
        cliponaxis=False,
        showlegend=False,
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>10위권 합계: %{y:,}명<extra></extra>",
    )
    # 글자가 그래프 밖으로 잘리지 않도록 위쪽 여유를 둠
    fig.update_yaxes(range=[0, daily["10위권 합계"].max() * 1.18], tickformat=",")
    st.plotly_chart(fig)

    insight("(여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요.)")


def section_4_top10_total_bar(df: pd.DataFrame) -> None:
    st.subheader("4. 일관객 합계 TOP 10")
    st.caption("막대에 마우스를 올리면 10위권에 든 날수도 함께 보여요.")

    summary = (
        df.groupby("영화명")
        .agg(일관객합계=("일관객", "sum"), 순위진입일수=("날짜", "nunique"))
        .nlargest(10, "일관객합계")
        .sort_values("일관객합계")  # 가장 큰 값이 위로 오도록(오름차순으로 넣으면 plotly가 아래->위로 그림)
        .reset_index()
    )

    fig = px.bar(
        summary,
        x="일관객합계",
        y="영화명",
        orientation="h",
        title="일관객 합계 TOP 10",
        labels={"일관객합계": "일관객 합계(명)", "영화명": "영화"},
        custom_data=["순위진입일수"],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "일관객 합계: %{x:,}명<br>"
            "10위권 진입 날수: %{customdata[0]}일<extra></extra>"
        )
    )
    fig.update_layout(xaxis_tickformat=",")
    st.plotly_chart(fig)

    insight("(여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요.)")


def section_5_month_weekday_heatmap(df: pd.DataFrame) -> None:
    st.subheader("5. 월×요일별 일관객 합계 히트맵")
    st.caption("색이 진할수록 그 월·요일의 일관객 합계가 많다는 뜻이에요.")

    tmp = df.copy()
    tmp["월"] = tmp["날짜"].dt.month
    weekday_order = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_map = dict(zip(range(7), weekday_order))  # 0=월요일 ... 6=일요일
    tmp["요일"] = tmp["날짜"].dt.weekday.map(weekday_map)

    pivot = (
        tmp.groupby(["월", "요일"])["일관객"]
        .sum()
        .unstack("요일")
        .reindex(columns=weekday_order)  # 월요일부터 일요일 순서로
        .sort_index()  # 1월부터 12월 순서로
    )

    fig = px.imshow(
        pivot,
        x=pivot.columns,
        y=[f"{m}월" for m in pivot.index],
        color_continuous_scale="Reds",
        aspect="auto",
        title="월×요일별 일관객 합계",
        labels={"x": "요일", "y": "월", "color": "일관객 합계"},
    )
    fig.update_traces(
        hovertemplate="%{y} %{x}요일<br>일관객 합계: %{z:,}명<extra></extra>"
    )
    fig.update_layout(coloraxis_colorbar_tickformat=",")
    st.plotly_chart(fig)

    insight("(여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요.)")


# 구역 목록: (표시할 이름, 그려 주는 함수)
SECTIONS = [
    ("일관객 변화", section_1_daily_audience),
    ("상위 5편 비교", section_2_top5_daily_audience),
    ("날짜별 합계", section_3_daily_total_area),
    ("합계 TOP 10", section_4_top10_total_bar),
    ("월×요일 히트맵", section_5_month_weekday_heatmap),
    # ("새 그래프 이름", section_6_...),
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
