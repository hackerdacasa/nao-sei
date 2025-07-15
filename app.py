import yfinance as yf
import pandas as pd
import ta
import streamlit as st
import matplotlib.pyplot as plt

# Título
st.title("📊 Sinais de Trading Automáticos (IQ Option Style)")

# Seleção de ativo
ativo = st.selectbox("Escolha o ativo:", ["EURUSD=X", "BTC-USD", "AAPL", "ETH-USD"])

# Coletar dados
dados = yf.download(ativo, period='7d', interval='1h')
dados.dropna(inplace=True)

# Verificar se os dados são válidos
if not dados.empty and 'Close' in dados.columns:
    # Garantir que a coluna 'Close' seja numérica
    dados['Close'] = pd.to_numeric(dados['Close'], errors='coerce')

    # Garantir que o número de dados é suficiente para calcular o RSI
    if len(dados) >= 14:
        dados['RSI'] = ta.momentum.RSIIndicator(dados['Close']).rsi()
    else:
        dados['RSI'] = pd.Series([None] * len(dados))  # Coloca NaN se não houver dados suficientes
else:
    dados['RSI'] = pd.Series([None] * len(dados))  # Coloca NaN se não houver dados

# Indicadores técnicos
dados['MM20'] = dados['Close'].rolling(window=20).mean()
macd = ta.trend.MACD(dados['Close'])
dados['MACD'] = macd.macd()
dados['MACD_signal'] = macd.macd_signal()

# Última linha
ultimo = dados.iloc[-1]

# Sinal
sinal = "⏸️ AGUARDAR"
justificativa = []

if ultimo['RSI'] < 30 and ultimo['Close'] > ultimo['MM20'] and ultimo['MACD'] > ultimo['MACD_signal']:
    sinal = "✅ COMPRAR"
    justificativa.append("RSI < 30 (sobrevendido)")
    justificativa.append("Preço > MM20 (tendência positiva)")
    justificativa.append("MACD cruzamento positivo")
elif ultimo['RSI'] > 70 and ultimo['Close'] < ultimo['MM20'] and ultimo['MACD'] < ultimo['MACD_signal']:
    sinal = "🚫 VENDER"
    justificativa.append("RSI > 70 (sobrecomprado)")
    justificativa.append("Preço < MM20 (tendência negativa)")
    justificativa.append("MACD cruzamento negativo")
else:
    justificativa.append("Sem confirmação clara dos indicadores")

# Resultado
st.subheader(f"Ativo: {ativo}")
st.metric("Preço atual", f"{ultimo['Close']:.4f}")
st.write(f"📊 RSI: {ultimo['RSI']:.2f}")
st.write(f"📈 Sinal Gerado: {sinal}")
st.write("📌 Justificativas:")
for item in justificativa:
    st.markdown(f"- {item}")

# Gráfico de preço + MM20
st.subheader("📉 Gráfico de Preço e MM20")
fig, ax = plt.subplots()
ax.plot(dados['Close'], label='Preço')
ax.plot(dados['MM20'], label='MM20', linestyle='--')
ax.set_title("Preço vs Média Móvel")
ax.legend()
st.pyplot(fig)

# Gráfico RSI
st.subheader("📈 RSI")
fig2, ax2 = plt.subplots()
ax2.plot(dados['RSI'], color='purple')
ax2.axhline(30, color='green', linestyle='--')
ax2.axhline(70, color='red', linestyle='--')
ax2.set_title("RSI - Índice de Força Relativa")
st.pyplot(fig2)
