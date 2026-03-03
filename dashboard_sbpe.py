# ==========================================================
# SBPE – OUTIL DE GESTION DU SYSTEME ELECTRIQUE
# Direction Technique – Service SPAO
# VERSION PROVISOIRE
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

# ==========================================================
# ENTETE
# ==========================================================

col_logo, col_title = st.columns([1,5])

with col_logo:
    st.image("logo_sbpe.png", width=140)

with col_title:
    st.markdown("## SBPE – OUTIL DE GESTION DU SYSTEME ELECTRIQUE")
    st.markdown("Direction Technique – Service SPAO")
    st.write("Date :", datetime.now().strftime("%d %B %Y - %H:%M"))

st.markdown("---")

# ==========================================================
# LECTURE DONNEES
# ==========================================================

file_path = "MODELE_DECISIONNEL_SBPE_DYNAMIQUE_24H.xlsx"

input_data = pd.read_excel(file_path, sheet_name="INPUT_24H").fillna(0)
Alerte_Réseau = pd.read_excel(file_path, sheet_name="SCENARIOS_DYNAMIQUES").fillna(0)

input_data.columns = input_data.columns.str.strip()
Alerte_Réseau.columns = Alerte_Réseau.columns.str.strip().str.replace(" ", "_")

activation_col = next((c for c in Alerte_Réseau.columns if "Activation" in c), None)

# ==========================================================
# 1️⃣ SELECTION HEURE
# ==========================================================

heure = st.radio(
    "Sélection Heure d'Analyse",
    list(range(24)),
    horizontal=True
)

st.markdown(f"# {heure}h00")

row_selection = input_data[input_data["Heure"] == heure]

if row_selection.empty:
    st.error("Aucune donnée disponible pour cette heure.")
    st.stop()

row = row_selection.iloc[0]

# ==========================================================
# DONNEES RESEAU
# ==========================================================

Charge_VRA = float(row["Charge_VRA"])
Charge_TCN = float(row["Charge_TCN"])
Charge_Totale = Charge_VRA + Charge_TCN

Prod_MG1_VRA = float(row["MG1 VRA"])
Prod_MG1_TCN = float(row["MG1 TCN"])

RES_VRA = float(row["Reserve_MG1 VRA"])
RES_TCN = float(row["Reserve_MG1 TCN"])

VRA_import = float(row["VRA"])
PARAS = float(row["PARAS"])
TRANSCORP = float(row["TRANSCORP"])
SOLAIRE = float(row["SOLAIRE"])

MG1_VRA_max = 72
MG1_TCN_max = 55

# ==========================================================
# APPLICATION ALERTES (DYNAMIQUE EXCEL)
# ==========================================================

Alerte_Réseau_Actives = []

for _, scen in Alerte_Réseau.iterrows():

    if str(scen.get(activation_col)).strip() in ["1", "1.0"]:

        hd = int(scen.get("Heure_Debut", 0))
        hf = int(scen.get("Heure_Fin", 0))

        if hd <= heure <= hf:

            nom_alerte = scen.get("Alerte_Réseau")

            if pd.notna(nom_alerte):
                Alerte_Réseau_Actives.append(str(nom_alerte))

            new_val = float(scen.get("Nouvelle_Disponibilite_MW", 0))

            if nom_alerte == "Limitation_VRA":
                VRA_import = new_val

            elif nom_alerte == "Limitation_TCN_PARAS":
                PARAS = new_val

            elif nom_alerte == "Limitation_TCN_TRANSCORP":
                TRANSCORP = new_val

            elif nom_alerte == "Chute_Drastique_Solaire":
                SOLAIRE = new_val

# ==========================================================
# MOTEUR
# ==========================================================

import_effectif = min(PARAS + TRANSCORP, 225)

offre_nat_tcn = SOLAIRE + import_effectif + Prod_MG1_TCN
offre_nat_vra = VRA_import + Prod_MG1_VRA

gap_tcn = Charge_TCN - offre_nat_tcn
gap_vra = Charge_VRA - offre_nat_vra

mg1_tcn = 0
mg1_vra = 0
transfert = 0
delestage_vra = 0
delestage_tcn = 0

if gap_tcn > 0:
    delta = min(RES_TCN, MG1_TCN_max - Prod_MG1_TCN, gap_tcn)
    mg1_tcn += delta
    gap_tcn -= delta

if gap_vra > 0:
    delta = min(RES_VRA, MG1_VRA_max - Prod_MG1_VRA, gap_vra)
    mg1_vra += delta
    gap_vra -= delta

reserve_restante_tcn = min(RES_TCN, MG1_TCN_max - Prod_MG1_TCN) - mg1_tcn

if Alerte_Réseau_Actives and gap_vra > 0 and reserve_restante_tcn > 0:
    transfert = min(gap_vra, reserve_restante_tcn)
    gap_vra -= transfert
    mg1_tcn += transfert

if gap_vra > 0:
    delestage_vra = gap_vra

if gap_tcn > 0:
    delestage_tcn = gap_tcn

activation_total = mg1_vra + mg1_tcn
delestage_total = delestage_vra + delestage_tcn

# ==========================================================
# 1️⃣ BANDEAU HEURE
# ==========================================================

st.markdown(f"""
<div style="
    background:#003366;
    color:white;
    padding:20px;
    border-radius:10px;
    text-align:center;
    font-size:36px;
    font-weight:800;">
    Heure d'analyse : {heure}h00
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# 2️⃣ ALERTE RESEAU
# ==========================================================

if Alerte_Réseau_Actives:
    st.markdown(f"""
    <div style="
        background:#B71C1C;
        color:white;
        padding:15px;
        border-radius:10px;
        font-size:22px;
        font-weight:700;
        text-align:center;">
        ⚠ ALERTE RÉSEAU : {" | ".join(Alerte_Réseau_Actives)}
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="
        background:#1B5E20;
        color:white;
        padding:15px;
        border-radius:10px;
        font-size:22px;
        font-weight:700;
        text-align:center;">
        ✔ Aucune alerte active
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# 3️⃣ DECISION OPERATIONNELLE
# ==========================================================

actions = []

if mg1_vra > 0:
    actions.append(f"Monter MG1 VRA {round(mg1_vra,1)} MW")

if mg1_tcn > 0:
    actions.append(f"Monter MG1 TCN {round(mg1_tcn,1)} MW")

if transfert > 0:
    actions.append(f"Transfert {round(transfert,1)} MW")

if delestage_total > 0:
    actions.append(f"Délestage {round(delestage_total,1)} MW")

decision_text = " | ".join(actions) if actions else "Aucune action requise"

st.markdown(f"""
<div style="
    background:#0D47A1;
    color:white;
    padding:18px;
    border-radius:10px;
    font-size:22px;
    font-weight:700;
    text-align:center;">
    🎯 DECISION OPERATIONNELLE : {decision_text}
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# 4️⃣ KPI NATIONAUX
# ==========================================================

col1, col2, col3, col4 = st.columns(4)

def kpi_box(title, value):
    return f"""
    <div style="
        background:#F5F7FA;
        padding:25px;
        border-radius:12px;
        text-align:center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
        <div style="font-size:16px; color:#555;">{title}</div>
        <div style="font-size:38px; font-weight:900; color:#003366;">
            {value}
        </div>
    </div>
    """

col1.markdown(kpi_box("Charge Nationale (MW)", round(Charge_Totale,1)), unsafe_allow_html=True)
col2.markdown(kpi_box("Activation MG1 (MW)", round(activation_total,1)), unsafe_allow_html=True)
col3.markdown(kpi_box("Transfert (MW)", round(transfert,1)), unsafe_allow_html=True)
col4.markdown(kpi_box("Délestage (MW)", round(delestage_total,1)), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# 5️⃣ DONNEES DETAILLEES PAR ILOT
# ==========================================================

col_vra, col_tcn = st.columns(2)

with col_vra:
    st.markdown("### ÎLOT VRA")
    st.write("Charge :", round(Charge_VRA,1), "MW")
    st.write("Import VRA :", round(VRA_import,1), "MW")
    st.write("Production MG1 :", round(Prod_MG1_VRA_base,1), "MW")
    st.write("Réserve :", round(RES_VRA,1), "MW")
    st.write("Délestage :", round(delestage_vra,1), "MW")

with col_tcn:
    st.markdown("### ÎLOT TCN")
    st.write("Charge :", round(Charge_TCN,1), "MW")
    st.write("Import PARAS :", round(PARAS,1), "MW")
    st.write("Import TRANSCORP :", round(TRANSCORP,1), "MW")
    st.write("Production MG1 :", round(Prod_MG1_TCN_base,1), "MW")
    st.write("Production solaire :", round(SOLAIRE,1), "MW")
    st.write("Réserve :", round(RES_TCN,1), "MW")
    st.write("Délestage :", round(delestage_tcn,1), "MW")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# 6️⃣ GRAPHIQUE 24H
# ==========================================================

fig = go.Figure()

fig.add_trace(go.Bar(x=input_data["Heure"], y=input_data["MG1 VRA"], name="MG1 VRA"))
fig.add_trace(go.Bar(x=input_data["Heure"], y=input_data["MG1 TCN"], name="MG1 TCN"))
fig.add_trace(go.Bar(x=input_data["Heure"], y=input_data["PARAS"], name="PARAS"))
fig.add_trace(go.Bar(x=input_data["Heure"], y=input_data["TRANSCORP"], name="TRANSCORP"))
fig.add_trace(go.Bar(x=input_data["Heure"], y=input_data["SOLAIRE"], name="Solaire"))

fig.add_trace(go.Scatter(
    x=input_data["Heure"],
    y=input_data["Charge_horaire"],
    mode="lines+markers",
    name="Charge"
))

fig.update_layout(barmode="stack", template="plotly_white")


st.plotly_chart(fig, use_container_width=True)

