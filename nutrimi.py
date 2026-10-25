import json
from datetime import date, timedelta

import gspread
import streamlit as st

st.set_page_config(
    page_title="Nutrimi",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Caratteri più grandi, pulsanti larghi, niente scorrimento laterale
st.markdown(
    """
<style>
html { font-size: 19px; }
.block-container { padding: 1rem 0.9rem 4rem 0.9rem; max-width: 720px; }
.stButton > button, .stFormSubmitButton > button {
    width: 100%; min-height: 3rem; font-size: 1.05rem;
}
input, textarea { font-size: 1.05rem !important; }
div[role="radiogroup"] { gap: 0.3rem 0.8rem; }
</style>
""",
    unsafe_allow_html=True,
)

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

CAMPI_PRINCIPALI = [
    ("acqua", "Target Liquidi (ml)", 50.0),
    ("kcal", "Calorie (kcal)", 10.0),
    ("prot", "Proteine (g)", 1.0),
    ("carb", "Carboidrati (g)", 1.0),
    ("grassi", "Grassi (g)", 1.0),
    ("fibre", "Fibre (g)", 1.0),
]
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
CAMPI_INGREDIENTE = [
    ("kcal", "Calorie (kcal)", 0.1),
    ("prot", "Proteine (g)", 0.1),
    ("carb", "Carboidrati totali (g)", 0.1),
    ("zuccheri", "di cui Zuccheri (g)", 0.1),
    ("grassi", "Grassi (g)", 0.1),
    ("fibre", "Fibre (g)", 0.1),
    ("acqua", "Acqua / Liquidi (ml per 100g)", 1.0),
    ("sodio", "Sodio (mg)", 0.1),
    ("potassio", "Potassio (mg)", 0.1),
    ("calcio", "Calcio (mg)", 0.1),
    ("magnesio", "Magnesio (mg)", 0.1),
    ("ferro", "Ferro (mg)", 0.1),
    ("fosforo", "Fosforo (mg)", 0.1),
    ("zinco", "Zinco (mg)", 0.01),
    ("manganese", "Manganese (mg)", 0.01),
    ("silicio", "Silicio (mg)", 0.1),
    ("vit_c", "Vit. C (mg)", 0.1),
    ("vit_a", "Vit. A (mcg)", 0.1),
    ("vit_b6", "Vit. B6 (mg)", 0.01),
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


def calcola_totali_giorno(piatti_giorno):
    totali = {k: 0.0 for k in CHIAVI}
    for info in piatti_giorno.values():
        nutrienti = info.get("nutrienti", {})
        for chiave in CHIAVI:
            totali[chiave] += float(nutrienti.get(chiave, 0.0))
    return totali


# Ad ogni azione rileggo i dati condivisi (cache di 5 secondi)
dati_app = carica_dati()

# ==========================================
# INTESTAZIONE: PROFILO E MENU A PAGINE
# ==========================================
st.title("💧 Nutrimi")

utenti_disponibili = list(dati_app["utenti"].keys())
utente_selezionato = st.selectbox(
    "👤 Profilo", utenti_disponibili, key="sel_profilo"
)

PAGINE = ["🍳 Pasto", "📊 Oggi", "🩺 Vitali", "📈 Medie", "🥕 Alimenti", "👤 Profilo"]
pagina = st.radio(
    "Pagina", PAGINE, horizontal=True, key="pagina", label_visibility="collapsed"
)
st.divider()

if st.session_state.get("auto_ref") and pagina in ("📊 Oggi", "📈 Medie"):
    from streamlit_autorefresh import st_autorefresh

    st_autorefresh(interval=30000, key="auto_refresh")

dati_utente = dati_app["utenti"][utente_selezionato]
registro_utente = dati_utente["registro"]
obiettivi_utente = dati_utente["obiettivi"]
anagrafica_utente = dati_utente["anagrafica"]
parametri_vitali_utente = dati_utente["parametri_vitali"]
ingredienti_ordinati = sorted(dati_app["database"].keys())

# ==========================================
# PAGINA: PASTO
# ==========================================
if pagina == "🍳 Pasto":
    st.subheader("Componi piatto / pasto")

    if "msg_piatto" in st.session_state:
        st.success(st.session_state.pop("msg_piatto"))

    # Il contatore cambia ad ogni salvataggio: i campi si azzerano da soli
    n_reset = st.session_state.get("reset_n", 0)

    nome_piatto = st.text_input(
        "Nome del piatto (es. Brodo vegetale)", key=f"inp_nome_piatto_{n_reset}"
    )
    data_piatto = st.date_input(
        "Data del pasto", value=date.today(), key="inp_data_piatto"
    )
    data_str = str(data_piatto)

    selected_ingredients = st.multiselect(
        "Ingredienti del piatto",
        ingredienti_ordinati,
        key=f"sel_ing_piatto_{n_reset}",
    )
    quantita_ingredienti = {}
    volume_finale = 0.0
    quantita_consumata = 0.0
    preview_totali = {k: 0.0 for k in CHIAVI}

    if selected_ingredients:
        st.markdown("##### ⚖️ Quantità di ogni ingrediente")
        for ing in selected_ingredients:
            q = st.number_input(
                f"{ing} (g o ml)",
                value=None,
                min_value=0.0,
                step=1.0,
                placeholder="0",
                key=f"qty_piatto_{ing}_{n_reset}",
            )
            quantita_ingredienti[ing] = float(q) if q else 0.0

        somma_qta_iniziale = sum(quantita_ingredienti.values())

        vol_in = st.number_input(
            "💧 Volume totale dopo la cottura (ml). Lascia vuoto se è uguale"
            " alla somma degli ingredienti; se parti da 1500 e arrivi a 700,"
            " scrivi 700.",
            value=None,
            min_value=0.0,
            step=10.0,
            placeholder=f"vuoto = {somma_qta_iniziale:.0f}",
            key=f"inp_volume_finale_{n_reset}",
        )
        volume_finale = float(vol_in) if vol_in else float(somma_qta_iniziale)

        cons_in = st.number_input(
            "🍽️ Quantità consumata ora (ml o g). Lascia vuoto se consumi tutto.",
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

        st.markdown("##### 🔍 Anteprima della porzione consumata")
        a1, a2 = st.columns(2)
        with a1:
            st.metric("💧 Liquidi", f"{preview_totali['acqua']:.0f} ml")
            st.metric("Proteine", f"{preview_totali['prot']:.1f} g")
            st.metric("Potassio", f"{preview_totali['potassio']:.1f} mg")
            st.metric("Magnesio", f"{preview_totali['magnesio']:.1f} mg")
        with a2:
            st.metric("Calorie", f"{preview_totali['kcal']:.1f} kcal")
            st.metric("Carboidrati", f"{preview_totali['carb']:.1f} g")
            st.metric("Calcio", f"{preview_totali['calcio']:.1f} mg")
            st.metric("Ferro", f"{preview_totali['ferro']:.1f} mg")

    if st.button("🚀 Aggiungi piatto al riepilogo"):
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
                f"Piatto '{nome_piatto.strip()}' aggiunto per"
                f" {utente_selezionato} nel giorno {data_str}!"
            )
            st.rerun()
        else:
            st.warning(
                "Inserisci il nome del piatto e almeno un ingrediente con"
                " quantità maggiore di 0."
            )

# ==========================================
# PAGINA: OGGI (RIEPILOGO GIORNALIERO)
# ==========================================
elif pagina == "📊 Oggi":
    st.subheader("Riepilogo della giornata")

    data_scelta = st.date_input(
        "Giornata", value=date.today(), key="data_giorno"
    )
    data_str = str(data_scelta)
    piatti_oggi = registro_utente.get(data_str, {})

    if not piatti_oggi:
        st.info("Nessun piatto registrato per questa data.")
    else:
        tot_oggi = calcola_totali_giorno(piatti_oggi)

        target_liquidi = obiettivi_utente.get("acqua", 1500.0)
        liquidi_assunti = tot_oggi.get("acqua", 0.0)
        diff_liquidi = target_liquidi - liquidi_assunti

        st.markdown("### 💧 Idratazione")
        if diff_liquidi > 0:
            st.warning(
                f"**Assunti:** {liquidi_assunti:.0f} ml su {target_liquidi:.0f} ml"
                f" — **mancano {diff_liquidi:.0f} ml**"
            )
        else:
            st.success(
                f"**Assunti:** {liquidi_assunti:.0f} ml su {target_liquidi:.0f} ml"
                f" — **target raggiunto (+{abs(diff_liquidi):.0f} ml)**"
            )

        st.markdown("### 📋 Piatti")
        for nome_p, info in list(piatti_oggi.items()):
            with st.expander(f"🍽️ {nome_p}"):
                vol_fin = info.get("volume_finale")
                qta_cons = info.get("quantita_consumata")
                if vol_fin and qta_cons:
                    st.write(f"Volume totale: **{vol_fin:.0f} ml** — porzione consumata: **{qta_cons:.0f} ml**")
                st.markdown("*Ingredienti:*")
                for ing, qta in info.get("ingredienti", {}).items():
                    if qta > 0:
                        st.write(f"- {ing}: {qta:g} g/ml")
                n = info.get("nutrienti", {})
                st.markdown("*Nutrienti assunti:*")
                st.write(f"- Liquidi: {n.get('acqua', 0):.0f} ml")
                st.write(f"- Calorie: {n.get('kcal', 0):.1f} kcal")
                st.write(f"- Proteine: {n.get('prot', 0):.1f} g")
                st.write(f"- Carboidrati: {n.get('carb', 0):.1f} g")
                st.write(f"- Grassi: {n.get('grassi', 0):.1f} g")
                st.write(f"- Potassio: {n.get('potassio', 0):.1f} mg")
                st.write(f"- Calcio: {n.get('calcio', 0):.1f} mg")
                st.write(f"- Magnesio: {n.get('magnesio', 0):.1f} mg")
                st.write(f"- Ferro: {n.get('ferro', 0):.1f} mg")
                if st.button(
                    f"🗑️ Rimuovi '{nome_p}'",
                    key=f"del_{utente_selezionato}_{data_str}_{nome_p}",
                ):
                    del registro_utente[data_str][nome_p]
                    salva_dati(dati_app)
                    st.rerun()

        st.markdown("### 🎯 Confronto con gli obiettivi")

        def mostra_confronto(nome_nutriente, unita, chiave):
            assunto = tot_oggi[chiave]
            target = obiettivi_utente.get(chiave, DEFAULT_OBIETTIVI[chiave])
            differenza = target - assunto
            if differenza > 0:
                st.warning(
                    f"**{nome_nutriente}**: {assunto:.1f} / {target:.1f} {unita}"
                    f" — mancano {differenza:.1f} {unita}"
                )
            else:
                st.success(
                    f"**{nome_nutriente}**: {assunto:.1f} / {target:.1f} {unita}"
                    f" — raggiunto (+{abs(differenza):.1f} {unita})"
                )

        with st.expander("Macronutrienti e liquidi", expanded=True):
            mostra_confronto("Liquidi", "ml", "acqua")
            mostra_confronto("Calorie", "kcal", "kcal")
            mostra_confronto("Proteine", "g", "prot")
            mostra_confronto("Carboidrati", "g", "carb")
            mostra_confronto("Grassi", "g", "grassi")
            mostra_confronto("Fibre", "g", "fibre")
        with st.expander("Minerali"):
            mostra_confronto("Potassio", "mg", "potassio")
            mostra_confronto("Calcio", "mg", "calcio")
            mostra_confronto("Magnesio", "mg", "magnesio")
            mostra_confronto("Ferro", "mg", "ferro")
            mostra_confronto("Fosforo", "mg", "fosforo")
            mostra_confronto("Sodio", "mg", "sodio")
        with st.expander("Oligoelementi e vitamine"):
            mostra_confronto("Zinco", "mg", "zinco")
            mostra_confronto("Manganese", "mg", "manganese")
            mostra_confronto("Silicio", "mg", "silicio")
            mostra_confronto("Vit. C", "mg", "vit_c")
            mostra_confronto("Vit. A", "mcg", "vit_a")
            mostra_confronto("Vit. B6", "mg", "vit_b6")

# ==========================================
# PAGINA: VITALI
# ==========================================
elif pagina == "🩺 Vitali":
    st.subheader("Parametri vitali")

    data_v = st.date_input("Giornata", value=date.today(), key="data_vitali")
    data_v_str = str(data_v)
    vit_giorno = parametri_vitali_utente.get(data_v_str, {})

    chiave_vit = f"{utente_selezionato}|{data_v_str}"
    if st.session_state.get("chiave_vit_caricata") != chiave_vit or "p_sys_m" not in st.session_state:
        st.session_state["chiave_vit_caricata"] = chiave_vit
        st.session_state["p_sys_m"] = int(vit_giorno.get("press_sys_m", 0))
        st.session_state["p_dia_m"] = int(vit_giorno.get("press_dia_m", 0))
        st.session_state["p_puls_m"] = int(vit_giorno.get("puls_m", 0))
        st.session_state["p_sys_s"] = int(vit_giorno.get("press_sys_s", 0))
        st.session_state["p_dia_s"] = int(vit_giorno.get("press_dia_s", 0))
        st.session_state["p_puls_s"] = int(vit_giorno.get("puls_s", 0))
        st.session_state["sat_val"] = int(vit_giorno.get("saturazione", 0))

    st.markdown("**🔴 Pressione mattina**")
    p_sys_m = st.number_input("Sistolica / Max (mmHg)", min_value=0, step=1, key="p_sys_m")
    p_dia_m = st.number_input("Diastolica / Min (mmHg)", min_value=0, step=1, key="p_dia_m")
    p_puls_m = st.number_input("Pulsazioni (BPM)", min_value=0, step=1, key="p_puls_m")

    st.markdown("**🌙 Pressione sera**")
    p_sys_s = st.number_input("Sistolica / Max (mmHg) ", min_value=0, step=1, key="p_sys_s")
    p_dia_s = st.number_input("Diastolica / Min (mmHg) ", min_value=0, step=1, key="p_dia_s")
    p_puls_s = st.number_input("Pulsazioni (BPM) ", min_value=0, step=1, key="p_puls_s")

    st.markdown("**🫁 Saturazione ossigeno**")
    sat_val = st.number_input(
        "Saturazione (% SpO2)", min_value=0, max_value=100, step=1, key="sat_val"
    )

    if st.button("💾 Salva parametri vitali"):
        parametri_vitali_utente[data_v_str] = {
            "press_sys_m": p_sys_m,
            "press_dia_m": p_dia_m,
            "puls_m": p_puls_m,
            "press_sys_s": p_sys_s,
            "press_dia_s": p_dia_s,
            "puls_s": p_puls_s,
            "saturazione": sat_val,
        }
        salva_dati(dati_app)
        st.success("Parametri vitali salvati!")

    if data_v_str in parametri_vitali_utente:
        v = parametri_vitali_utente[data_v_str]
        st.markdown("---")
        st.markdown(f"**Salvati per il {data_v_str}:**")
        sm, dm, pm = v.get("press_sys_m", 0), v.get("press_dia_m", 0), v.get("puls_m", 0)
        ss, ds, ps = v.get("press_sys_s", 0), v.get("press_dia_s", 0), v.get("puls_s", 0)
        sat = v.get("saturazione", 0)
        st.metric("Pressione mattina", f"{sm}/{dm} mmHg" if sm > 0 and dm > 0 else "Non registrata", f"{pm} BPM" if pm > 0 else "")
        st.metric("Pressione sera", f"{ss}/{ds} mmHg" if ss > 0 and ds > 0 else "Non registrata", f"{ps} BPM" if ps > 0 else "")
        st.metric("Saturazione SpO2", f"{sat}%" if sat > 0 else "Non registrata")
        if 0 < sat < 95:
            st.error("⚠️ Attenzione: saturazione sotto il 95%")

# ==========================================
# PAGINA: MEDIE
# ==========================================
elif pagina == "📈 Medie":
    st.subheader("Trend e medie")

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

    for giorni in (7, 30):
        media, conteggio = calcola_media_periodo(giorni)
        st.markdown(f"**Media {giorni} giorni** ({conteggio} giorni registrati)")
        if media:
            st.write(f"- Liquidi medi: **{media['acqua']:.0f} ml**")
            st.write(f"- Calorie medie: **{media['kcal']:.1f} kcal**")
            st.write(f"- Proteine medie: **{media['prot']:.1f} g**")
            st.write(f"- Potassio medio: **{media['potassio']:.1f} mg**")
        else:
            st.write(f"Dati insufficienti negli ultimi {giorni} giorni.")
        st.markdown("---")

# ==========================================
# PAGINA: ALIMENTI (DATABASE INGREDIENTI)
# ==========================================
elif pagina == "🥕 Alimenti":
    st.subheader("Database alimenti (condiviso)")

    if "msg_ing" in st.session_state:
        st.success(st.session_state.pop("msg_ing"))

    with st.expander("🔍 Elenco alimenti in ordine alfabetico"):
        for nome in ingredienti_ordinati:
            st.write(f"- {nome}")

    st.markdown("**Aggiungi un nuovo alimento** (valori per 100 g)")
    with st.form("form_ingrediente", clear_on_submit=True):
        nome_ing = st.text_input("Nome alimento")
        valori_ing = {}
        for chiave, etichetta, passo in CAMPI_INGREDIENTE:
            val = st.number_input(
                etichetta,
                value=None,
                min_value=0.0,
                step=passo,
                placeholder="0",
                key=f"ing_{chiave}",
            )
            valori_ing[chiave] = float(val) if val else 0.0
        invia_ing = st.form_submit_button("💾 Salva alimento")

    if invia_ing:
        if nome_ing.strip():
            dati_app["database"][nome_ing.strip()] = valori_ing
            salva_dati(dati_app)
            st.session_state["msg_ing"] = f"Alimento '{nome_ing.strip()}' salvato!"
            st.rerun()
        else:
            st.warning("Inserisci il nome dell'alimento.")

# ==========================================
# PAGINA: PROFILO
# ==========================================
elif pagina == "👤 Profilo":
    st.subheader(f"Profilo e target [{utente_selezionato}]")

    # Carico i widget con i dati del profilo (le chiavi si cancellano quando
    # si cambia pagina, quindi le ricreo ogni volta che entro qui)
    if st.session_state.get("profilo_caricato") != utente_selezionato or "anag_eta" not in st.session_state:
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

    st.markdown("**Dati anagrafici**")
    sesso_val = st.selectbox("Sesso", ["Donna", "Uomo"], key="anag_sesso", on_change=aggiorna_valori)
    eta_val = st.number_input("Età (anni)", step=1, key="anag_eta", on_change=aggiorna_valori)
    altezza_val = st.number_input("Altezza (cm)", step=1.0, key="anag_alt", on_change=aggiorna_valori)
    peso_val = st.number_input("Peso (kg)", step=0.5, key="anag_peso", on_change=aggiorna_valori)
    mobilita_val = st.selectbox("Stile di vita / Mobilità", MOBILITA_OPZIONI, key="anag_mob", on_change=aggiorna_valori)
    st.checkbox("🔄 Ricalcolo automatico dei target", key="anag_ricalc", on_change=aggiorna_valori)

    st.markdown("---")
    st.markdown("**Target giornalieri**")
    target_nuovi = {}
    for chiave, etichetta, passo in CAMPI_PRINCIPALI:
        target_nuovi[chiave] = st.number_input(etichetta, step=passo, key=f"t_{chiave}")

    with st.expander("Minerali e vitamine"):
        for chiave, etichetta, passo in CAMPI_TARGET:
            target_nuovi[chiave] = st.number_input(etichetta, step=passo, key=f"t_{chiave}")

    if st.button("💾 Salva profilo"):
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
        st.success("Profilo salvato!")

    st.markdown("---")
    st.markdown("**Nuovo profilo**")
    nuovo_nome_utente = st.text_input("Nome del nuovo profilo", key="txt_nuovo_profilo")
    if st.button("➕ Crea profilo"):
        nome = nuovo_nome_utente.strip()
        if nome and nome not in dati_app["utenti"]:
            dati_app["utenti"][nome] = nuovo_utente()
            salva_dati(dati_app)
            st.success(f"Profilo '{nome}' creato! Selezionalo in alto.")
        else:
            st.warning("Inserisci un nome non ancora usato.")

    st.markdown("---")
    auto = st.toggle(
        "🔄 Aggiornamento automatico ogni 30 s (solo nelle pagine Oggi e Medie)",
        value=st.session_state.get("auto_ref", False),
    )
    st.session_state["auto_ref"] = auto
