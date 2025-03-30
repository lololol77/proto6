import sqlite3
import streamlit as st
import os

# DB 연결 함수 (job_matching_fixed.db)
def connect_db():
    db_path = os.path.join(os.getcwd(), 'job_matching_fixed.db')  # 현재 작업 디렉토리에서 찾기
    conn = sqlite3.connect(db_path)
    return conn

# 구인자/구직자 입력 내역 별도 DB 연결 (user_data.db)
def connect_user_db():
    db_path = os.path.join(os.getcwd(), 'user_data.db')  # 현재 작업 디렉토리에서 찾기
    conn = sqlite3.connect(db_path)
    return conn

# 구인자 입력 내역 저장 함수 (일자리)
def save_job_posting(job_title, abilities):
    conn = connect_user_db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS job_postings (id INTEGER PRIMARY KEY, title TEXT, abilities TEXT)")
    cur.execute("INSERT INTO job_postings (title, abilities) VALUES (?, ?)", (job_title, ", ".join(abilities)))
    conn.commit()
    conn.close()

# 구직자 입력 내역 저장 함수 (프로필)
def save_job_seeker(name, disability, severity):
    conn = connect_user_db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS job_seekers (id INTEGER PRIMARY KEY, name TEXT, disability TEXT, severity TEXT)")
    cur.execute("INSERT INTO job_seekers (name, disability, severity) VALUES (?, ?, ?)", (name, disability, severity))
    conn.commit()
    conn.close()

# 점수 계산 함수 (동그라미: 2점, 세모: 1점, 엑스: 부적합)
def calculate_score(abilities, disability_type):
    score = 0
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT ability_id, disability_id, suitability FROM matching WHERE disability_id=?", (disability_type,))
    matching_data = cur.fetchall()

    for ability in abilities:
        is_invalid = False  # 하나라도 X가 있으면 부적합으로 처리
        for entry in matching_data:
            if entry[0] == ability:  # 능력명 일치
                if entry[2] == '○':  # 동그라미: 2점
                    score += 2
                elif entry[2] == '△':  # 세모: 1점
                    score += 1
                elif entry[2] == 'X':  # 엑스: 부적합
                    is_invalid = True  # 하나라도 X가 있으면 부적합 처리
                    break
        if is_invalid:
            return "부적합"  # 하나라도 X가 있으면 부적합 처리
    return score

# Streamlit UI
st.title("장애인 일자리 매칭 시스템")

role = st.selectbox("사용자 역할 선택", ["구직자", "구인자"])

if role == "구직자":
    name = st.text_input("이름 입력")
    disability = st.selectbox("장애유형", ["시각장애", "청각장애", "지체장애", "뇌병변장애", "언어장애", "안면장애", "신장장애", "심장장애", "간장애", "호흡기장애", "장루·요루장애", "뇌전증장애", "지적장애", "자폐성장애", "정신장애"])
    severity = st.selectbox("장애 정도", ["심하지 않은", "심한"])
    if st.button("매칭 결과 보기"):
        save_job_seeker(name, disability, severity)
        conn = connect_user_db()
        cur = conn.cursor()
        cur.execute("SELECT title, abilities FROM job_postings")
        jobs = cur.fetchall()
        st.write("### 적합한 일자리 목록:")
        
        # 점수 계산하고 부적합한 일자리는 제외
        for job in jobs:
            abilities = job[1].split(", ")
            score = calculate_score(abilities, disability)  # 점수 계산
            if score == "부적합":
                st.write(f"- {job[0]}: 부적합")
            else:
                st.write(f"- {job[0]}: {score}점")
        
        conn.close()

elif role == "구인자":
    job_title = st.text_input("일자리 제목 입력")
    abilities = st.multiselect("필요한 능력 선택", ["주의력", "아이디어 발상 및 논리적 사고", "기억력", "지각능력", "수리능력", "공간능력", "언어능력", "지구력", "유연성 · 균형 및 조정", "체력", "움직임 통제능력", "정밀한 조작능력", "반응시간 및 속도", "청각 및 언어능력", "시각능력"])
    
    if st.button("매칭 결과 보기"):
        save_job_posting(job_title, abilities)
        st.success("구인자 정보가 저장되었습니다!")
        st.write("일자리 제목:", job_title)
        st.write("필요 능력:", ", ".join(abilities))  # 능력 리스트를 쉼표로 구분해서 표시

# 유료 서비스 여부 확인
if st.button("대화 종료"):
    if role == "구직자":
        use_service = st.radio("유료 취업준비 서비스 이용하시겠습니까?", ["네", "아니요"])
    else:
        use_service = st.radio("유료 직무개발 서비스 이용하시겠습니까?", ["네", "아니요"])
    if use_service == "네":
        st.write("서비스를 이용해 주셔서 감사합니다!")
    else:
        st.write("대화를 종료합니다.")
