import streamlit as st

st.set_page_config(
    page_title="Calculadora de Precificação 3D",
    page_icon="🖨️",
    layout="wide"
)

st.title("🖨️ Calculadora de Precificação de Impressão 3D")
st.caption("Calcule o preço de venda da sua peça considerando todos os custos envolvidos.")

st.divider()

# =========================================================
# SIDEBAR - Parâmetros gerais / configuráveis do negócio
# =========================================================
st.sidebar.header("⚙️ Parâmetros Gerais")

st.sidebar.subheader("Energia")
potencia_impressora_w = st.sidebar.number_input(
    "Potência média da impressora (W)", min_value=0.0, value=350.0, step=10.0,
    help="Consumo médio durante a impressão (inclui hotend, mesa aquecida, eletrônica)."
)
tarifa_kwh = st.sidebar.number_input(
    "Tarifa de energia (R$/kWh)", min_value=0.0, value=0.89, step=0.01, format="%.2f"
)

st.sidebar.subheader("Desgaste da impressora")
valor_impressora = st.sidebar.number_input(
    "Valor da impressora (R$)", min_value=0.0, value=5414.90, step=50.0
)
vida_util_horas = st.sidebar.number_input(
    "Vida útil estimada (horas)", min_value=1.0, value=8000.0, step=100.0,
    help="Tempo total de uso esperado antes de precisar trocar/aposentar a impressora."
)
custo_manutencao_hora = st.sidebar.number_input(
    "Custo de manutenção (R$/hora de uso)", min_value=0.0, value=1.00, step=0.05, format="%.2f",
    help="Rateio de peças de reposição: bicos, correias, lubrificação, etc."
)

st.sidebar.subheader("Mão de obra")
custo_hora_trabalho = st.sidebar.number_input(
    "Custo da sua hora de trabalho (R$/h)", min_value=0.0, value=30.0, step=5.0,
    help="Usado para tempo de preparação, pós-processamento e acabamento manual."
)

st.sidebar.subheader("Margem e impostos")
margem_lucro_pct = st.sidebar.slider("Margem de lucro desejada (%)", 0, 300, 50)
impostos_pct = st.sidebar.slider("Impostos / taxas (%)", 0, 30, 0)

# =========================================================
# CORPO PRINCIPAL - Dados da peça
# =========================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧩 Dados da Peça")

    nome_peca = st.text_input("Nome da peça (opcional)", value="")

    tempo_impressao_h = st.number_input(
        "Tempo de impressão (horas)", min_value=0.0, value=2.0, step=0.25, format="%.2f"
    )

    tipo_peca = st.radio(
        "Tipo de peça",
        ["Monocromática", "Colorida / Multicor"],
        horizontal=True
    )

    if tipo_peca == "Monocromática":
        peso_filamento_g = st.number_input(
            "Peso do filamento (g)", min_value=0.0, value=50.0, step=5.0
        )
        preco_filamento_kg = st.number_input(
            "Preço do filamento (R$/kg)", min_value=0.0, value=120.0, step=5.0
        )
        custo_filamento = (peso_filamento_g / 1000) * preco_filamento_kg
        st.info(f"Custo de filamento: **R$ {custo_filamento:.2f}**")
        cores_detalhe = []
    else:
        st.caption("Informe o peso e o preço do filamento para cada cor utilizada.")
        n_cores = st.number_input("Número de cores/filamentos diferentes", min_value=2, max_value=10, value=2, step=1)
        cores_detalhe = []
        custo_filamento = 0.0
        peso_filamento_g = 0.0
        for i in range(int(n_cores)):
            c1, c2 = st.columns(2)
            with c1:
                peso_c = st.number_input(f"Peso cor {i+1} (g)", min_value=0.0, value=20.0, step=5.0, key=f"peso_{i}")
            with c2:
                preco_c = st.number_input(f"Preço cor {i+1} (R$/kg)", min_value=0.0, value=120.0, step=5.0, key=f"preco_{i}")
            custo_c = (peso_c / 1000) * preco_c
            custo_filamento += custo_c
            peso_filamento_g += peso_c
            cores_detalhe.append((peso_c, preco_c, custo_c))
        st.info(f"Custo total de filamento ({n_cores} cores): **R$ {custo_filamento:.2f}**")
        # Custo extra de troca de filamento (tempo/perda na troca de cor)
        custo_troca_cor = st.number_input(
            "Custo extra por troca de cor (R$, purga/perda de material por troca)",
            min_value=0.0, value=1.0, step=0.5,
            help="Cada troca de filamento gera purga de material. Estimativa por troca."
        )
        custo_trocas = custo_troca_cor * (n_cores - 1)

with col2:
    st.subheader("🎨 Finalização e Riscos")

    finalizacao_manual = st.checkbox("Peça terá finalização/acabamento manual?")
    tempo_finalizacao_min = 0.0
    if finalizacao_manual:
        tempo_finalizacao_min = st.number_input(
            "Tempo de finalização manual (minutos)", min_value=0.0, value=15.0, step=5.0,
            help="Ex: lixar, pintar, remover supports, colar peças."
        )
        custo_finalizacao = (tempo_finalizacao_min / 60) * custo_hora_trabalho
        st.info(f"Custo de finalização manual: **R$ {custo_finalizacao:.2f}**")
    else:
        custo_finalizacao = 0.0

    st.markdown("**Risco de perda / falha de impressão**")
    taxa_falha_pct = st.slider(
        "Taxa estimada de falhas (%)", 0, 50, 10,
        help="Percentual médio de impressões que falham e precisam ser refeitas. "
             "Esse custo é diluído no preço de todas as peças para compensar perdas."
    )

    st.markdown("**Custos extras**")
    custo_embalagem = st.number_input("Embalagem (R$)", min_value=0.0, value=2.0, step=0.5)
    custo_acessorios = st.number_input("Acessórios (imãs, parafusos, suportes, etc.) (R$)", min_value=0.0, value=0.0, step=0.5)
    outros_extras = st.number_input("Outros custos extras (R$)", min_value=0.0, value=0.0, step=0.5)

    tempo_preparo_min = st.number_input(
        "Tempo de preparo/setup antes da impressão (minutos)",
        min_value=0.0, value=10.0, step=5.0,
        help="Fatiamento, nivelamento de mesa, configuração, etc."
    )

st.divider()

# =========================================================
# CÁLCULOS
# =========================================================

# Energia
consumo_kwh = (potencia_impressora_w / 1000) * tempo_impressao_h
custo_energia = consumo_kwh * tarifa_kwh

# Desgaste da impressora (depreciação + manutenção)
custo_depreciacao_hora = valor_impressora / vida_util_horas if vida_util_horas > 0 else 0
custo_desgaste = (custo_depreciacao_hora + custo_manutencao_hora) * tempo_impressao_h

# Mão de obra (setup + finalização)
custo_setup = (tempo_preparo_min / 60) * custo_hora_trabalho
custo_mao_de_obra = custo_setup + custo_finalizacao

# Custo de filamento (já considera multicor + trocas, se aplicável)
custo_filamento_total = custo_filamento
if tipo_peca != "Monocromática":
    custo_filamento_total += custo_trocas

# Custos extras
custo_extras = custo_embalagem + custo_acessorios + outros_extras

# Soma dos custos diretos (antes do risco de falha)
custo_direto = (
    custo_filamento_total
    + custo_energia
    + custo_desgaste
    + custo_mao_de_obra
    + custo_extras
)

# Risco de perda: dilui o custo das falhas no preço das peças boas
# Se X% falham, para vender 1 peça boa preciso produzir 1/(1-X%) tentativas em média
fator_risco = 1 / (1 - (taxa_falha_pct / 100)) if taxa_falha_pct < 100 else None

if fator_risco:
    custo_com_risco = custo_direto * fator_risco
    custo_risco_valor = custo_com_risco - custo_direto
else:
    custo_com_risco = custo_direto
    custo_risco_valor = 0

# Impostos
custo_com_impostos = custo_com_risco * (1 + impostos_pct / 100)
valor_impostos = custo_com_impostos - custo_com_risco

# Margem de lucro
preco_final = custo_com_impostos * (1 + margem_lucro_pct / 100)
valor_lucro = preco_final - custo_com_impostos

# =========================================================
# RESULTADOS
# =========================================================
st.subheader("💰 Resultado da Precificação")

titulo_peca = nome_peca if nome_peca else "Peça"
st.markdown(f"### {titulo_peca}")

r1, r2, r3 = st.columns(3)
r1.metric("Custo direto total", f"R$ {custo_direto:.2f}")
r2.metric("Custo + risco + impostos", f"R$ {custo_com_impostos:.2f}")
r3.metric("Preço final sugerido", f"R$ {preco_final:.2f}")

with st.expander("📊 Ver detalhamento completo dos custos", expanded=True):
    st.markdown("**Composição do custo:**")

    detalhamento = {
        "Filamento": custo_filamento_total,
        "Energia": custo_energia,
        "Desgaste da impressora (depreciação + manutenção)": custo_desgaste,
        "Mão de obra (setup + finalização)": custo_mao_de_obra,
        "Custos extras (embalagem/acessórios/outros)": custo_extras,
    }

    for label, valor in detalhamento.items():
        st.write(f"- {label}: **R$ {valor:.2f}**")

    st.write(f"**Subtotal (custo direto): R$ {custo_direto:.2f}**")
    st.write(f"- Acréscimo por risco de falha ({taxa_falha_pct}%): **R$ {custo_risco_valor:.2f}**")
    st.write(f"- Impostos/taxas ({impostos_pct}%): **R$ {valor_impostos:.2f}**")
    st.write(f"**Custo total com risco e impostos: R$ {custo_com_impostos:.2f}**")
    st.write(f"- Margem de lucro ({margem_lucro_pct}%): **R$ {valor_lucro:.2f}**")
    st.success(f"**PREÇO FINAL DE VENDA: R$ {preco_final:.2f}**")

    if tipo_peca != "Monocromática" and cores_detalhe:
        st.markdown("---")
        st.markdown("**Detalhamento por cor:**")
        for i, (peso_c, preco_c, custo_c) in enumerate(cores_detalhe):
            st.write(f"- Cor {i+1}: {peso_c:.1f} g × R$ {preco_c:.2f}/kg = R$ {custo_c:.2f}")
        st.write(f"- Perda por trocas de filamento: **R$ {custo_trocas:.2f}**")

st.caption(
    "💡 Ajuste os parâmetros gerais na barra lateral (energia, desgaste da impressora, "
    "valor da sua hora de trabalho, margem de lucro e impostos) conforme a realidade do seu negócio."
)
