import pandas as pd

data = { 
    "날짜": ["05-18", "05-19", "05-20", "05-21", "05-22"],
    "종가": [10000, 10200, 10500, 10300, 10600],
    "total_score": [15, 45, 65, 30, 75],
} # 최종합산점수표 입력
df = pd.DataFrame(data)

opinions = [] #의견 입력될 리시트
signals = [] #살지, 말지 정하는 신호 입력될 리스트


#데이터 가져와서 반복문으로 읽기
for i in range(len(df)):
    if i == 0:
        opinions.append("관망 (데이터 축적 중)")
        signals.append("HOLD")
        continue

#데이터 가져오기   
    current_score = df["total_score"].iloc[i]
    prev_score = df["total_score"].iloc[i - 1]

#전보다 올랐는지 기준으로
    is_rising = current_score > prev_score

#current_score, is_rising으로 판단
    if current_score >= 50 and is_rising == True :
        opinions.append("매수 (추세 상승 및 점수 우수)")
        signals.append("BUY")
    elif current_score <= 40 and is_rising == False :
        opinions.append("매도 (추세 하락 및 위험 구간)")
        signals.append("SELL")
    else :
        opinions.append("관망 (신호 불확실)")
        signals.append("HOLD")



df["최종투자의견"] = opinions
df["매매신호"] = signals

print(df)