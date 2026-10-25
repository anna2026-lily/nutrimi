import json
from datetime import date, timedelta

import gspread
import streamlit as st

st.set_page_config(page_title="Nutrimi", page_icon="💧", layout="wide")

# ==========================================
# CONFIGURAZIONE
# ==========================================
NOME_FOGLIO = "Nutrimi"
NOME_SCHEDA_DATI = "Dati"

CHIAVI = [
    "kcal", "prot", "carb", "zuccheri", "grassi", "fibre", "acqua", "sodio",
    "potassio", "calcio", "magnesio", "ferro", "vit_c", "vit_a", "vit_b6",
    "fosforo", "zinco", "manganese", "silicio",
]

# Valori per 100 g, nell'ordine di CHIAVI
DB_RAW = {
    "Acqua / Diluente": [0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Anacardi crudi": [553, 18.2, 30.2, 5.9, 43.8, 3.3, 5, 12, 660, 37, 292, 6.7, 0.5, 0, 0.42, 593, 5.8, 1.65, 2],
    "Barbabietola rossa": [43, 1.6, 9.6, 6.8, 0.2, 2, 87, 78, 325, 16, 23, 0.8, 4.9, 2, 0.07, 40, 0.35, 0.33, 0.6],
    "Broccoli": [34, 2.8, 7, 1.5, 0.4, 2.6, 89, 33, 316, 47, 21, 0.7, 89.2, 31, 0.18, 66, 0.4, 0.21, 1],
    "Brodo vegetale leggero": [5, 0.2, 1, 0.5, 0.1, 0.2, 98, 200, 50, 5, 3, 0.1, 1, 10, 0.02, 10, 0.05, 0.05, 0.5],
    "Burro di mandorle o arachidi": [600, 21, 20, 5, 54, 6, 1, 15, 600, 50, 180, 2.5, 0, 0, 0.2, 350, 2.9, 1.5, 1],
    "Carne di pollo (petto crudo)": [165, 31, 0, 0, 3.6, 0, 75, 74, 256, 15, 29, 0.9, 0, 0, 0.6, 228, 1, 0.02, 0.5],
    "Carote": [41, 0.9, 9.6, 4.7, 0.2, 2.8, 88, 69, 320, 33, 12, 0.3, 5.9, 835, 0.14, 35, 0.24, 0.14, 1.5],
    "Cetriolo": [15, 0.6, 3.6, 1.7, 0.1, 0.5, 95, 2, 147, 16, 13, 0.3, 2.8, 5, 0.04, 24, 0.2, 0.08, 0.8],
    "Curcuma in polvere": [354, 7.8, 64.9, 3.2, 9.9, 21.1, 10, 38, 2525, 183, 193, 41.4, 25.9, 0, 1.8, 268, 4.35, 7.83, 5],
    "Finocchio fresco/estratto": [31, 1.2, 7, 3.9, 0.2, 3.1, 90, 52, 414, 49, 17, 0.7, 12, 134, 0.05, 50, 0.2, 0.2, 1],
    "Kiwi": [61, 1.1, 14.7, 9, 0.5, 3, 83, 3, 312, 34, 17, 0.3, 92.7, 87, 0.06, 34, 0.14, 0.09, 0.5],
    "Latte di soia al naturale": [38, 3.3, 1.5, 1, 2, 0.5, 90, 40, 120, 120, 20, 0.5, 0, 0, 0.05, 45, 0.3, 0.1, 0.5],
    "Limone (succo)": [22, 0.4, 6.9, 2.5, 0.2, 0.3, 90, 1, 103, 6, 6, 0.1, 38.7, 0, 0.05, 16, 0.06, 0.03, 0.5],
    "Mandorle": [579, 21.1, 21.6, 4.4, 49.9, 12.5, 4, 1, 728, 264, 270, 3.7, 0, 0, 0.13, 474, 3.1, 2.2, 1.5],
    "Mela": [52, 0.3, 13.8, 10.4, 0.2, 2.4, 85, 1, 107, 6, 5, 0.1, 4.6, 3, 0.04, 11, 0.04, 0.04, 0.4],
    "Olio extravergine d'oliva": [884, 0, 0, 0, 100, 0, 0, 0, 0, 1, 0, 0.56, 0, 0, 0, 0, 0, 0, 0],
    "Pasta all'uovo (secca)": [375, 13.5, 70, 3, 4.5, 2.5, 10, 50, 160, 30, 45, 1.5, 0, 30, 0.15, 150, 1.5, 0.8, 2],
    "Pasta di semola (cruda)": [350, 12, 72, 3, 1.5, 2.7, 10, 6, 150, 20, 40, 1.2, 0, 0, 0.1, 130, 1, 0.7, 2],
    "Proteine in polvere (isolate)": [370, 82, 1.5, 1, 1, 0, 4, 150, 160, 400, 60, 1, 0, 0, 0, 250, 1, 0.2, 0.5],
    "Sedano fresco": [20, 0.7, 3, 1.4, 0.2, 1.6, 95, 80, 260, 40, 11, 0.2, 3.1, 22, 0.06, 24, 0.13, 0.1, 1],
    "Semi di chia": [486, 16.5, 42.1, 0, 30.7, 34.4, 8, 16, 407, 631, 335, 7.7, 1.6, 54, 0, 860, 4.6, 2.72, 2.5],
    "Semi di lino": [534, 18.3, 28.9, 1.6, 42.2, 27.3, 7, 30, 813, 255, 392, 5.7, 0.6, 0, 0.47, 642, 4.3, 2.48, 3],
    "Spinaci freschi": [23, 2.9, 3.6, 0.5, 0.4, 2.2, 91, 79, 558, 99, 79, 2.7, 28.1, 469, 0.2, 49, 0.5, 0.9, 2],
    "Tè verde (infuso)": [1, 0.2, 0.2, 0, 0, 0, 99, 1, 27, 0, 2, 0.02, 0, 0, 0, 2, 0.02, 0.2, 0.8],
    "Uovo intero fresco": [143, 12.6, 1.1, 1.1, 9.5, 0, 76, 142, 133, 50, 12, 1.8, 0, 140, 0.12, 198, 1.3, 0.03, 0.5],
    "Zenzero fresco": [80, 1.8, 17.8, 1.7, 0.8, 2, 79, 13, 415, 16, 43, 0.6, 5, 0, 0.16, 34, 0.34, 0.23, 1.5],
    "Zucchine (estratte/bollite)": [15, 1.2, 3, 2.5, 0.2, 1, 94, 1, 200, 16, 18, 0.4, 11, 20, 0.1, 38, 0.3, 0.2, 1.2],
}
DATABASE_INIZIALE = {
    nome: {k: float(v) for k, v in zip(CHIAVI, valori)}
    for nome, valori in DB_RAW.items()
}

MOBILITA_OPZIONI = ["Molto sedentaria / A letto", "Sedentaria leggera", "Attiva"]

DEFAULT_ANAGRAFICA = {
    "sesso": "Donna",
    "eta": 92,
    "altezza": 150.0,
    "peso": 55.0,
    "mobilita": "Molto sedentaria / A letto",
}

DEFAULT_OBIETTIVI = {
    "kcal": 1000.0, "prot": 55.0, "carb": 130.0, "zuccheri": 30.0,
    "grassi": 38.0, "fibre": 18.0, "acqua": 1500.0, "sodio": 1500.0,
    "potassio": 2500.0, "calcio": 1000.0, "magnesio": 300.0, "ferro": 10.0,
    "vit_c": 75.0, "vit_a": 700.0, "vit_b6": 1.2, "fosforo": 700.0,
    "zinco": 8.0, "manganese": 1.8, "silicio": 15.0,
}

# (chiave, etichetta, passo) per i target modificabili nella sidebar
CAMPI_TARGET = [
    ("potassio", "Potassio (mg)", 50.0),
    ("calcio", "Calcio (mg)", 50.0),
    ("magnesio", "Magnesio (mg)", 10.0),
    ("ferro", "Ferro (mg)", 0.5),
    ("fosforo", "Fosforo (mg)", 50.0),
    ("sodio", "Sodio (mg)", 50.0),
    ("zinco", "Zinco (mg)", 0.5),
    ("manganese", "Manganese (mg)", 0.1),
    ("silicio", "Silicio (mg)", 1.0),
    ("vit_c", "Vit. C (mg)", 5.0),
    ("vit_a", "Vit. A (mcg)", 50.0),
    ("vit_b6", "Vit. B6 (mg)", 0.1),
]
CAMPI_PRINCIPALI = [
    ("acqua", "Target Liquidi (ml)", 50.0),
    ("kcal", "Calorie (kcal)", 10.0),
    ("prot", "Proteine (g)", 1.0),
    ("carb", "Carboidrati (g)", 1.0),
    ("grassi", "Grassi (g)", 1.0),
    ("fibre", "Fibre (g)", 1.0),
]


def nuovo_utente():
    return {
        "registro": {},
        "obiettivi": dict(DEFAULT_OBIETTIVI),
        "anagrafica": dict(DEFAULT_ANAGRAFICA),
        "parametri_vitali": {},
    }


def calcola_target_automatici(sesso, eta, altezza, peso, mobilita):
    if sesso == "Uomo":
        bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
    else:
        bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161

    if mobilita == "Molto sedentaria / A letto":
        pal = 1.15
    elif mobilita == "Sedentaria leggera":
        pal = 1.3
    else:
        pal = 1.5

    kcal = max(round(bmr * pal, -1), 900.0)
    prot = round(peso * 1.2 if mobilita == "Attiva" else peso * 1.0, 1)
    grassi = round((kcal * 0.30) / 9.0, 1)
    carb = round((kcal - (prot * 4) - (grassi * 9)) / 4, 1)
    fibre = 18.0 if eta > 80 else 25.0
    acqua = max(round(peso * 30, -2), 1500.0)

    return {
        "kcal": float(kcal), "prot": float(prot), "carb": float(carb),
        "grassi": float(grassi), "fibre": float(fibre), "acqua": float(acqua),
    }


# ==========================================
# ARCHIVIO CONDIVISO SU GOOGLE SHEETS
# ==========================================
@st.cache_resource
def get_worksheet():
    gc = gspread.service_account_from_dict(json.loads(st.secrets["gcp_json"]))
    sh = gc.open(NOME_FOGLIO)
    try:
        return sh.worksheet(NOME_SCHEDA_DATI)
    except gspread.exceptions.WorksheetNotFound:
        return sh.add_worksheet(title=NOME_SCHEDA_DATI, rows=200, cols=1)


@st.cache_data(ttl=5, show_spinner=False)
def leggi_da_sheet():
    return "".join(get_worksheet().col_values(1))


def carica_dati():
    testo = leggi_da_sheet()
    if not testo:
        return {
            "database": {k: dict(v) for k, v in DATABASE_INIZIALE.items()},
            "ricette": {},
            "utenti": {"Anna": nuovo_utente()},
        }

    dati = json.loads(testo)
    dati.setdefault("database", {})
    dati.setdefault("ricette", {})
    dati.setdefault("utenti", {"Anna": nuovo_utente()})

    for nome, valori in DATABASE_INIZIALE.items():
        if nome not in dati["database"]:
            dati["database"][nome] = dict(valori)

    for u in dati["utenti"].values():
        u.setdefault("registro", {})
        u.setdefault("anagrafica", dict(DEFAULT_ANAGRAFICA))
        u.setdefault("parametri_vitali", {})
        obiettivi = u.setdefault("obiettivi", dict(DEFAULT_OBIETTIVI))
        for k, v in DEFAULT_OBIETTIVI.items():
            obiettivi.setdefault(k, v)
    return dati


def salva_dati(dati):
    testo = json.dumps(dati, ensure_ascii=False, separators=(",", ":"))
    # Una cella di Google Sheets accetta max 50.000 caratteri: spezzo in blocchi
    pezzi = [testo[i:i + 40000] for i in range(0, len(testo), 40000)]
    ws = get_worksheet()
    righe_prima = len(ws.col_values(1))
    ws.update(
        range_name="A1", values=[[p] for p in pezzi], value_input_option="RAW"
    )
    if righe_prima > len(pezzi):
        ws.batch_clear([f"A{len(pezzi) + 1}:A{righe_prima}"])
    leggi_da_sheet.clear()


# Ad ogni azione rileggo i dati condivisi (cache di 5 secondi)
st.session_state.dati = carica_dati()
dati_app = st.session_state.dati

st.title("💧 Calcolatore Nutrizionale e Salute (Multi-Utente)")

if st.sidebar.checkbox("🔄 Aggiornamento automatico (30 s)", value=False):
    from streamlit_autorefresh import st_autorefresh

    st_autorefresh(interval=30000, key="auto_refresh")

# ==========================================
# SIDEBAR: GESTIONE PROFILI E ANAGRAFICA
# ==========================================
st.sidebar.header("👤 Gestione Profili")
utenti_disponibili = list(dati_app["utenti"].keys())
utente_selezionato = st.sidebar.selectbox(
    "Seleziona Profilo Attivo", utenti_disponibili, key="sel_profilo"
)

nuovo_nome_utente = st.sidebar.text_input(
    "Aggiungi Nuovo Profilo", key="txt_nuovo_profilo"
)
if st.sidebar.button("Crea Profilo", key="btn_crea_profilo"):
    nome = nuovo_nome_utente.strip()
    if nome and nome not in dati_app["utenti"]:
        dati_app["utenti"][nome] = nuovo_utente()
        salva_dati(dati_app)
        st.sidebar.success(f"Profilo '{nome}' creato!")
        st.rerun()

st.sidebar.divider()

dati_utente = dati_app["utenti"][utente_selezionato]
registro_utente = dati_utente["registro"]
obiettivi_utente = dati_utente["obiettivi"]
anagrafica_utente = dati_utente["anagrafica"]
parametri_vitali_utente = dati_utente["parametri_vitali"]

# Quando cambio profilo, ricarico i widget con i dati di quel profilo
if st.session_state.get("profilo_caricato") != utente_selezionato:
    st.session_state["anag_sesso"] = anagrafica_utente.get("sesso", "Donna")
    st.session_state["anag_eta"] = int(anagrafica_utente.get("eta", 92))
    st.session_state["anag_alt"] = float(anagrafica_utente.get("altezza", 150.0))
    st.session_state["anag_peso"] = float(anagrafica_utente.get("peso", 55.0))
    mob = anagrafica_utente.get("mobilita", MOBILITA_OPZIONI[0])
    st.session_state["anag_mob"] = mob if mob in MOBILITA_OPZIONI else MOBILITA_OPZIONI[0]
    st.session_state["anag_ricalc"] = True
    for chiave, default in DEFAULT_OBIETTIVI.items():
        st.session_state[f"t_{chiave}"] = float(obiettivi_utente.get(chiave, default))
    st.session_state["profilo_caricato"] = utente_selezionato


def aggiorna_valori():
    if not st.session_state.get("anag_ricalc", True):
        return
    targ = calcola_target_automatici(
        st.session_state["anag_sesso"],
        int(st.session_state["anag_eta"]),
        float(st.session_state["anag_alt"]),
        float(st.session_state["anag_peso"]),
        st.session_state["anag_mob"],
    )
    for chiave, valore in targ.items():
        st.session_state[f"t_{chiave}"] = valore


with st.sidebar.expander(
    f"⚙️ Anagrafica e Target [{utente_selezionato}]", expanded=False
):
    st.markdown("**Dati Anagrafici:**")
    sesso_val = st.selectbox(
        "Sesso", ["Donna", "Uomo"], key="anag_sesso", on_change=aggiorna_valori
    )
    eta_val = st.number_input(
        "Età (anni)", step=1, key="anag_eta", on_change=aggiorna_valori
    )
    altezza_val = st.number_input(
        "Altezza (cm)", step=1.0, key="anag_alt", on_change=aggiorna_valori
    )
    peso_val = st.number_input(
        "Peso (kg)", step=0.5, key="anag_peso", on_change=aggiorna_valori
    )
    mobilita_val = st.selectbox(
        "Stile di vita / Mobilità",
        MOBILITA_OPZIONI,
        key="anag_mob",
        on_change=aggiorna_valori,
    )
    st.checkbox(
        "🔄 Ricalcolo automatico", key="anag_ricalc", on_change=aggiorna_valori
    )

    st.markdown("---")
    st.markdown("**Target Idrico e Mantenimento:**")
    target_nuovi = {}
    for chiave, etichetta, passo in CAMPI_PRINCIPALI:
        target_nuovi[chiave] = st.number_input(
            etichetta, step=passo, key=f"t_{chiave}"
        )

    st.markdown("**Minerali e Vitamine:**")
    for chiave, etichetta, passo in CAMPI_TARGET:
        target_nuovi[chiave] = st.number_input(
            etichetta, step=passo, key=f"t_{chiave}"
        )

    if st.button("💾 Salva Profilo"):
        dati_utente["anagrafica"] = {
            "sesso": sesso_val,
            "eta": int(eta_val),
            "altezza": float(altezza_val),
            "peso": float(peso_val),
            "mobilita": mobilita_val,
        }
        dati_utente["obiettivi"] = {
            **obiettivi_utente,
            **{k: float(v) for k, v in target_nuovi.items()},
        }
        salva_dati(dati_app)
        st.sidebar.success("Profilo salvato!")
        st.rerun()

st.info(f"Profilo attivo: **{utente_selezionato}**")

ingredienti_ordinati = sorted(dati_app["database"].keys())

# ==========================================
# SEZIONE 1: AGGIUNGI INGREDIENTE BASE
# ==========================================
st.subheader("1. Database Ingredienti Base (Condiviso)")

with st.expander("🔍 Mostra l'elenco completo degli alimenti in ordine alfabetico"):
    st.write(ingredienti_ordinati)

with st.form("form_ingrediente"):
    st.markdown("**Aggiungi un nuovo ingrediente personalizzato:**")
    nome_ing = st.text_input("Nome Ingrediente / Alimento")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Macronutrienti, Acqua & Fibre**")
        c_kcal = st.number_input("Calorie (kcal)", value=0.0, step=0.1)
        c_prot = st.number_input("Proteine (g)", value=0.0, step=0.1)
        c_carb = st.number_input("Carboidrati Totali (g)", value=0.0, step=0.1)
        c_zuccheri = st.number_input("di cui Zuccheri (g)", value=0.0, step=0.1)
        c_grassi = st.number_input("Grassi (g)", value=0.0, step=0.1)
        c_fibre = st.number_input("Fibre (g)", value=0.0, step=0.1)
        c_acqua = st.number_input("Acqua / Liquidi (ml per 100g)", value=0.0, step=1.0)
    with col2:
        st.markdown("**Minerali & Oligoelementi (mg)**")
        c_sodio = st.number_input("Sodio (mg)", value=0.0, step=0.1)
        c_potassio = st.number_input("Potassio (mg)", value=0.0, step=0.1)
        c_calcio = st.number_input("Calcio (mg)", value=0.0, step=0.1)
        c_magnesio = st.number_input("Magnesio (mg)", value=0.0, step=0.1)
        c_ferro = st.number_input("Ferro (mg)", value=0.0, step=0.1)
        c_fosforo = st.number_input("Fosforo (mg)", value=0.0, step=0.1)
        c_zinco = st.number_input("Zinco (mg)", value=0.0, step=0.01)
        c_manganese = st.number_input("Manganese (mg)", value=0.0, step=0.01)
        c_silicio = st.number_input("Silicio (mg)", value=0.0, step=0.1)
    with col3:
        st.markdown("**Vitamine Principali**")
        c_vit_c = st.number_input("Vit. C (mg)", value=0.0, step=0.1)
        c_vit_a = st.number_input("Vit. A (mcg)", value=0.0, step=0.1)
        c_vit_b6 = st.number_input("Vit. B6 (mg)", value=0.0, step=0.01)

    if st.form_submit_button("💾 Salva Nuovo Ingrediente nel Database"):
        if nome_ing.strip():
            dati_app["database"][nome_ing.strip()] = {
                "kcal": c_kcal, "prot": c_prot, "carb": c_carb,
                "zuccheri": c_zuccheri, "grassi": c_grassi, "fibre": c_fibre,
                "acqua": c_acqua, "sodio": c_sodio, "potassio": c_potassio,
                "calcio": c_calcio, "magnesio": c_magnesio, "ferro": c_ferro,
                "vit_c": c_vit_c, "vit_a": c_vit_a, "vit_b6": c_vit_b6,
                "fosforo": c_fosforo, "zinco": c_zinco,
                "manganese": c_manganese, "silicio": c_silicio,
            }
            salva_dati(dati_app)
            st.success(f"Ingrediente '{nome_ing}' salvato!")
            st.rerun()
        else:
            st.warning("Inserisci il nome dell'ingrediente.")

st.divider()

# ==========================================
# SEZIONE 2: COMPONI PIATTO / PASTO
# ==========================================
st.subheader(f"2. 🍳 Componi Piatto / Pasto per [{utente_selezionato}]")

# Il contatore cambia ad ogni salvataggio: i campi si azzerano da soli
n_reset = st.session_state.get("reset_n", 0)

nome_piatto = st.text_input(
    "Nome del Piatto / Preparazione (es. Brodo Vegetale)",
    key=f"inp_nome_piatto_{n_reset}",
)
data_piatto = st.date_input(
    "Seleziona la Data in cui consumi questo piatto",
    value=date.today(),
    key="inp_data_piatto",
)
data_str = str(data_piatto)

selected_ingredients = st.multiselect(
    "Seleziona gli ingredienti che compongono il piatto",
    ingredienti_ordinati,
    key=f"sel_ing_piatto_{n_reset}",
)
quantita_ingredienti = {}
volume_finale = 0.0
quantita_consumata = 0.0
preview_totali = {k: 0.0 for k in CHIAVI}

if selected_ingredients:
    st.markdown("##### ⚖️ Specifica le quantità iniziali per ogni ingrediente:")
    for ing in selected_ingredients:
        q = st.number_input(
            f"Quantità usata di '{ing}' (g o ml)",
            value=None,
            min_value=0.0,
            step=1.0,
            placeholder="0",
            key=f"qty_piatto_{ing}_{n_reset}",
        )
        quantita_ingredienti[ing] = float(q) if q else 0.0

    somma_qta_iniziale = sum(quantita_ingredienti.values())

    st.markdown("---")

    vol_in = st.number_input(
        "💧 Volume totale dopo la cottura (ml) [lascia vuoto se è uguale alla"
        " somma degli ingredienti; es. parti da 1500 e arrivi a 700, scrivi 700]",
        value=None,
        min_value=0.0,
        step=10.0,
        placeholder=f"vuoto = {somma_qta_iniziale:.0f}",
        key=f"inp_volume_finale_{n_reset}",
    )
    volume_finale = float(vol_in) if vol_in else float(somma_qta_iniziale)

    cons_in = st.number_input(
        "🍽️ Quantità consumata in questo pasto (ml o g) [lascia vuoto se"
        " consumi tutto]",
        value=None,
        min_value=0.0,
        step=10.0,
        placeholder=f"vuoto = {volume_finale:.0f}",
        key=f"inp_qta_consumata_{n_reset}",
    )
    quantita_consumata = float(cons_in) if cons_in else float(volume_finale)

    totali_ingredienti = {k: 0.0 for k in CHIAVI}
    db_base = dati_app["database"]
    for ing, qta in quantita_ingredienti.items():
        if qta > 0 and ing in db_base:
            fattore = float(qta) / 100.0
            for chiave in CHIAVI:
                totali_ingredienti[chiave] += float(db_base[ing].get(chiave, 0.0)) * fattore

    if volume_finale > 0 and quantita_consumata > 0:
        fattore_porzione = float(quantita_consumata) / float(volume_finale)
        preview_totali = {k: v * fattore_porzione for k, v in totali_ingredienti.items()}
    else:
        preview_totali = dict(totali_ingredienti)

    st.markdown("---")
    st.markdown("##### 🔍 **Anteprima Valori Nutrizionali per la Porzione Consumata:**")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("💧 Liquidi Porzione", f"{preview_totali['acqua']:.0f} ml")
        st.metric("Calorie", f"{preview_totali['kcal']:.1f} kcal")
    with p2:
        st.metric("Proteine", f"{preview_totali['prot']:.1f} g")
        st.metric("Carboidrati", f"{preview_totali['carb']:.1f} g")
    with p3:
        st.metric("Potassio", f"{preview_totali['potassio']:.1f} mg")
        st.metric("Calcio", f"{preview_totali['calcio']:.1f} mg")
    with p4:
        st.metric("Magnesio", f"{preview_totali['magnesio']:.1f} mg")
        st.metric("Ferro", f"{preview_totali['ferro']:.1f} mg")
    st.markdown("---")

if st.button("🚀 Calcola e Aggiungi Piatto al Riepilogo Giornaliero"):
    ha_quantita = any(q > 0 for q in quantita_ingredienti.values())
    if nome_piatto.strip() and ha_quantita:
        registro_utente.setdefault(data_str, {})
        registro_utente[data_str][nome_piatto.strip()] = {
            "ingredienti": quantita_ingredienti,
            "nutrienti": preview_totali,
            "volume_finale": volume_finale,
            "quantita_consumata": quantita_consumata,
        }
        salva_dati(dati_app)
        st.session_state["reset_n"] = n_reset + 1
        st.session_state["msg_piatto"] = (
            f"Piatto '{nome_piatto.strip()}' aggiunto per {utente_selezionato}"
            f" nel giorno {data_str}!"
        )
        st.rerun()
    else:
        st.warning(
            "Inserisci il nome del piatto e almeno un ingrediente con quantità"
            " maggiore di 0."
        )

if "msg_piatto" in st.session_state:
    st.success(st.session_state.pop("msg_piatto"))
# ==========================================
# SEZIONE 3: RIEPILOGO, PARAMETRI VITALI E TARGET
# ==========================================
st.subheader(f"3. 📊 Dashboard di Riepilogo e Controllo Target [{utente_selezionato}]")

data_scelta_storico = st.date_input(
    "Visualizza Giornata", value=date.today(), key="storico_data"
)
data_storico_str = str(data_scelta_storico)

vit_giorno = parametri_vitali_utente.get(data_storico_str, {})
chiave_vit = f"{utente_selezionato}|{data_storico_str}"
if st.session_state.get("ultima_chiave_vit") != chiave_vit:
    st.session_state["ultima_chiave_vit"] = chiave_vit
    st.session_state["p_sys_m"] = int(vit_giorno.get("press_sys_m", 0))
    st.session_state["p_dia_m"] = int(vit_giorno.get("press_dia_m", 0))
    st.session_state["p_puls_m"] = int(vit_giorno.get("puls_m", 0))
    st.session_state["p_sys_s"] = int(vit_giorno.get("press_sys_s", 0))
    st.session_state["p_dia_s"] = int(vit_giorno.get("press_dia_s", 0))
    st.session_state["p_puls_s"] = int(vit_giorno.get("puls_s", 0))
    st.session_state["sat_val"] = int(vit_giorno.get("saturazione", 0))

st.markdown("### 🩺 Parametri Vitali della Giornata")

with st.expander(
    f"📝 Inserisci / Modifica Parametri Vitali del {data_storico_str}", expanded=True
):
    cp1, cp2, cp3 = st.columns(3)
    with cp1:
        st.markdown("**🔴 Pressione Mattina**")
        p_sys_m = st.number_input("Sistolica / Max (mmHg)", min_value=0, step=1, key="p_sys_m")
        p_dia_m = st.number_input("Diastolica / Min (mmHg)", min_value=0, step=1, key="p_dia_m")
        p_puls_m = st.number_input("Pulsazioni (BPM)", min_value=0, step=1, key="p_puls_m")
    with cp2:
        st.markdown("**🌙 Pressione Sera**")
        p_sys_s = st.number_input("Sistolica / Max (mmHg) ", min_value=0, step=1, key="p_sys_s")
        p_dia_s = st.number_input("Diastolica / Min (mmHg) ", min_value=0, step=1, key="p_dia_s")
        p_puls_s = st.number_input("Pulsazioni (BPM) ", min_value=0, step=1, key="p_puls_s")
    with cp3:
        st.markdown("**🫁 Saturazione Ossigeno**")
        sat_val = st.number_input(
            "Saturazione (% SpO2)", min_value=0, max_value=100, step=1, key="sat_val"
        )

    if st.button("💾 Salva Parametri Vitali"):
        parametri_vitali_utente[data_storico_str] = {
            "press_sys_m": p_sys_m,
            "press_dia_m": p_dia_m,
            "puls_m": p_puls_m,
            "press_sys_s": p_sys_s,
            "press_dia_s": p_dia_s,
            "puls_s": p_puls_s,
            "saturazione": sat_val,
        }
        salva_dati(dati_app)
        st.success("Parametri vitali salvati con successo!")
        st.rerun()

if data_storico_str in parametri_vitali_utente:
    v_dat = parametri_vitali_utente[data_storico_str]
    m1, m2, m3 = st.columns(3)
    with m1:
        sys_m, dia_m, puls_m = v_dat.get("press_sys_m", 0), v_dat.get("press_dia_m", 0), v_dat.get("puls_m", 0)
        p_m_str = f"{sys_m}/{dia_m} mmHg" if sys_m > 0 and dia_m > 0 else "Non registrata"
        st.metric("Pressione Mattina", p_m_str, f"{puls_m} BPM" if puls_m > 0 else "")
    with m2:
        sys_s, dia_s, puls_s = v_dat.get("press_sys_s", 0), v_dat.get("press_dia_s", 0), v_dat.get("puls_s", 0)
        p_s_str = f"{sys_s}/{dia_s} mmHg" if sys_s > 0 and dia_s > 0 else "Non registrata"
        st.metric("Pressione Sera", p_s_str, f"{puls_s} BPM" if puls_s > 0 else "")
    with m3:
        sat_curr = v_dat.get("saturazione", 0)
        if sat_curr > 0:
            st.metric("Saturazione SpO2", f"{sat_curr}%")
            if sat_curr < 95:
                st.error("⚠️ Attenzione: Saturazione sotto il 95%")
        else:
            st.metric("Saturazione SpO2", "Non registrata")

st.markdown("---")


def calcola_totali_giorno(piatti_giorno):
    totali = {k: 0.0 for k in CHIAVI}
    for info in piatti_giorno.values():
        nutrienti = info.get("nutrienti", {})
        for chiave in CHIAVI:
            totali[chiave] += float(nutrienti.get(chiave, 0.0))
    return totali


piatti_oggi = registro_utente.get(data_storico_str, {})

if piatti_oggi:
    tot_oggi = calcola_totali_giorno(piatti_oggi)

    target_liquidi = obiettivi_utente.get("acqua", 1500.0)
    liquidi_assunti = tot_oggi.get("acqua", 0.0)
    diff_liquidi = target_liquidi - liquidi_assunti

    st.markdown("### 💧 Monitoraggio Idratazione Giornaliera")
    if diff_liquidi > 0:
        st.warning(
            f"**Liquidi Assunti:** {liquidi_assunti:.0f} ml / **Target:**"
            f" {target_liquidi:.0f} ml — **Mancano {diff_liquidi:.0f} ml**"
        )
    else:
        st.success(
            f"**Liquidi Assunti:** {liquidi_assunti:.0f} ml / **Target:**"
            f" {target_liquidi:.0f} ml — **Target Idrico Raggiunto!"
            f" (+{abs(diff_liquidi):.0f} ml)**"
        )

    st.markdown("---")
    st.markdown(f"### 📋 Dettaglio Piatti e Ingredienti del {data_storico_str}")

    for nome_p, info in list(piatti_oggi.items()):
        st.markdown(f"**🍽️ Piatto: {nome_p}**")
        vol_fin = info.get("volume_finale")
        qta_cons = info.get("quantita_consumata")
        if vol_fin and qta_cons:
            st.markdown(
                f"- *Volume totale pentola:* **{vol_fin} ml** | *Porzione"
                f" consumata:* **{qta_cons} ml**"
            )

        st.markdown("*Ingredienti utilizzati (ricetta di base):*")
        for ing, qta in info.get("ingredienti", {}).items():
            if qta > 0:
                st.markdown(f"   - **{ing}**: {qta} g/ml")

        n = info.get("nutrienti", {})
        with st.expander(f"🔍 Dettaglio nutrienti assunti per '{nome_p}'"):
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write(f"- Liquidi: {n.get('acqua', 0):.0f} ml")
                st.write(f"- Calorie: {n.get('kcal', 0):.1f} kcal")
                st.write(f"- Proteine: {n.get('prot', 0):.1f} g")
            with d2:
                st.write(f"- Carboidrati: {n.get('carb', 0):.1f} g")
                st.write(f"- Potassio: {n.get('potassio', 0):.1f} mg")
                st.write(f"- Calcio: {n.get('calcio', 0):.1f} mg")
            with d3:
                st.write(f"- Grassi: {n.get('grassi', 0):.1f} g")
                st.write(f"- Ferro: {n.get('ferro', 0):.1f} mg")
                st.write(f"- Magnesio: {n.get('magnesio', 0):.1f} mg")

        if st.button(
            f"🗑️ Rimuovi '{nome_p}'",
            key=f"del_{utente_selezionato}_{data_storico_str}_{nome_p}",
        ):
            del registro_utente[data_storico_str][nome_p]
            salva_dati(dati_app)
            st.rerun()
        st.markdown("---")

    st.markdown(
        "**Confronto Totale Giornaliero con gli Obiettivi di Mantenimento"
        f" ({data_storico_str}):**"
    )

    def mostra_confronto(nome_nutriente, unita, chiave_diz):
        assunto = tot_oggi[chiave_diz]
        target = obiettivi_utente.get(chiave_diz, DEFAULT_OBIETTIVI[chiave_diz])
        differenza = target - assunto
        if differenza > 0:
            st.warning(
                f"**{nome_nutriente}**: Assunti {assunto:.1f} {unita} / Target"
                f" {target:.1f} {unita} — **Mancano {differenza:.1f} {unita}**"
            )
        else:
            st.success(
                f"**{nome_nutriente}**: Assunti {assunto:.1f} {unita} / Target"
                f" {target:.1f} {unita} — **Target Raggiunto"
                f" (+{abs(differenza):.1f} {unita})**"
            )

    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.markdown("**Macronutrienti & Liquidi**")
        mostra_confronto("Liquidi/Acqua", "ml", "acqua")
        mostra_confronto("Calorie", "kcal", "kcal")
        mostra_confronto("Proteine", "g", "prot")
        mostra_confronto("Carboidrati", "g", "carb")
        mostra_confronto("Grassi", "g", "grassi")
        mostra_confronto("Fibre", "g", "fibre")
    with cc2:
        st.markdown("**Minerali Principali**")
        mostra_confronto("Potassio", "mg", "potassio")
        mostra_confronto("Calcio", "mg", "calcio")
        mostra_confronto("Magnesio", "mg", "magnesio")
        mostra_confronto("Ferro", "mg", "ferro")
        mostra_confronto("Fosforo", "mg", "fosforo")
        mostra_confronto("Sodio", "mg", "sodio")
    with cc3:
        st.markdown("**Oligoelementi & Vitamine**")
        mostra_confronto("Zinco", "mg", "zinco")
        mostra_confronto("Manganese", "mg", "manganese")
        mostra_confronto("Silicio", "mg", "silicio")
        mostra_confronto("Vit. C", "mg", "vit_c")
        mostra_confronto("Vit. A", "mcg", "vit_a")
        mostra_confronto("Vit. B6", "mg", "vit_b6")
else:
    st.info("Nessun piatto registrato per questa data.")

# ==========================================
# TREND E MEDIE
# ==========================================
st.markdown("---")
st.subheader(f"📈 Trend e Medie [{utente_selezionato}] (Ultimi 7 e 30 Giorni)")


def calcola_media_periodo(giorni_indietro):
    somma_tot = {k: 0.0 for k in CHIAVI}
    giorni_validi = 0
    oggi = date.today()
    for i in range(giorni_indietro):
        d_str = str(oggi - timedelta(days=i))
        if registro_utente.get(d_str):
            res_g = calcola_totali_giorno(registro_utente[d_str])
            for k in CHIAVI:
                somma_tot[k] += res_g[k]
            giorni_validi += 1
    if giorni_validi > 0:
        return {k: v / giorni_validi for k, v in somma_tot.items()}, giorni_validi
    return None, 0


media_7g, count_7g = calcola_media_periodo(7)
media_30g, count_30g = calcola_media_periodo(30)

ct1, ct2 = st.columns(2)
for colonna, media, conteggio, giorni in (
    (ct1, media_7g, count_7g, 7),
    (ct2, media_30g, count_30g, 30),
):
    with colonna:
        st.markdown(f"**Media {giorni} giorni ({conteggio} giorni registrati):**")
        if media:
            st.write(f"- Liquidi medi: **{media['acqua']:.0f} ml**")
            st.write(f"- Calorie medie: **{media['kcal']:.1f} kcal**")
            st.write(f"- Proteine medie: **{media['prot']:.1f} g**")
            st.write(f"- Potassio medio: **{media['potassio']:.1f} mg**")
        else:
            st.write(f"Dati insufficienti negli ultimi {giorni} giorni.")
