import streamlit as st
import math
import time

# --- SEITEN-SETUP & GEDÄCHTNIS (SESSION STATE) ---
st.set_page_config(page_title="Feld-Assistent GW", page_icon="🛠️", layout="centered")

# Gedächtnis-Variablen anlegen, falls noch nicht vorhanden
if 'ziel_volumen' not in st.session_state:
    st.session_state.ziel_volumen = 0.0
if 'pumpen_leistung' not in st.session_state:
    st.session_state.pumpen_leistung = 0.0

st.title("🛠️ Grundwasser Feld-Assistent")
st.write("Wählen Sie das benötigte Werkzeug über die Reiter aus:")

# --- KARTEIREITER ---
tab1, tab2, tab3, tab4 = st.tabs(["💧 DIN-Rechner", "🪨 Filterkies", "⏱️ Förderstrom", "⏳ Live-Timer"])

# ==========================================
# WERKZEUG 1: DIN-RECHNER
# ==========================================
with tab1:
    st.subheader("Rohrvolumen nach DIN 38402-13")
    
    durchmesser_mm = st.number_input("Rohr-Durchmesser in mm", value=100.0, step=10.0, key="din_dn")
    tiefe_m = st.number_input("Gesamttiefe in m", value=22.5, step=0.1, key="din_tiefe")
    ruhewasser_m = st.number_input("Ruhewasserstand in m", value=14.2, step=0.1, key="din_rws")
    
    if st.button("DIN-Volumen berechnen", type="primary", key="btn_din"):
        radius_m = (durchmesser_mm / 2) / 1000
        wassersaeule_m = tiefe_m - ruhewasser_m
        
        if wassersaeule_m < 0:
            st.error("❌ Fehler: Ruhewasserstand tiefer als Gesamttiefe!")
        else:
            standwasser_volumen = math.pi * (radius_m ** 2) * wassersaeule_m * 1000
            abpump_volumen = 3 * standwasser_volumen
            
            # WERT IM GEDÄCHTNIS SPEICHERN FÜR DEN TIMER
            st.session_state.ziel_volumen = abpump_volumen
            
            st.success("✅ Berechnung erfolgreich! Wert wurde für den Timer gespeichert.")
            col1, col2, col3 = st.columns(3)
            col1.metric("Wassersäule", f"{wassersaeule_m:.2f} m")
            col2.metric("1-fach Volumen", f"{standwasser_volumen:.1f} L")
            col3.metric("3-fach Abpumpen", f"{abpump_volumen:.1f} L")


# ==========================================
# WERKZEUG 2: FILTERKIES-RECHNER
# ==========================================
with tab2:
    st.subheader("Volumen der Filterkiesschüttung")
    
    durchmesser_m = st.number_input("Bohrlochdurchmesser in Metern", min_value=0.0, value=0.15, step=0.01, key="kies_dn")
    maechtigkeit_m = st.number_input("Mächtigkeit der Schüttung in Metern", min_value=0.0, value=5.0, step=0.1, key="kies_h")
    
    if st.button("Kies-Volumen berechnen", type="primary", key="btn_kies"):
        if durchmesser_m <= 0 or maechtigkeit_m <= 0:
            st.error("❌ Fehler: Bitte Werte größer als 0 eingeben.")
        else:
            radius_m = durchmesser_m / 2
            zylinder_volumen_m3 = math.pi * (radius_m ** 2) * maechtigkeit_m
            ziel_volumen_l = (zylinder_volumen_m3 * 1.5) * 1000
            
            # WERT IM GEDÄCHTNIS SPEICHERN FÜR DEN TIMER
            st.session_state.ziel_volumen = ziel_volumen_l
            
            st.success("✅ Berechnung erfolgreich! Wert wurde für den Timer gespeichert.")
            col1, col2 = st.columns(2)
            col1.metric("1-fach Volumen (m³)", f"{zylinder_volumen_m3:.3f} m³")
            col2.metric("1,5-fach Abpumpen (L)", f"{ziel_volumen_l:.1f} L")


# ==========================================
# WERKZEUG 3: FÖRDERSTROM-UMRECHNER
# ==========================================
with tab3:
    st.subheader("Förderstrom ermitteln")
    
    auswahl = st.radio("Gemessener Wert:", ["Liter pro Minute (l/min)", "Liter pro Stunde (l/h)", "Zeit für 1 Liter (s/l)"], key="strom_radio")
    
    l_min = 0.0
    
    if auswahl == "Liter pro Minute (l/min)":
        wert = st.number_input("Wert in l/min:", min_value=0.001, value=12.0, step=0.5, key="strom_min")
        l_min = wert
    elif auswahl == "Liter pro Stunde (l/h)":
        wert = st.number_input("Wert in l/h:", min_value=0.001, value=720.0, step=10.0, key="strom_h")
        l_min = wert / 60
    elif auswahl == "Zeit für 1 Liter (s/l)":
        wert = st.number_input("Sekunden für 1 Liter:", min_value=0.001, value=5.0, step=0.5, key="strom_s")
        l_min = 60 / wert
        
    if st.button("Förderstrom bestätigen", type="primary", key="btn_strom"):
        # WERT IM GEDÄCHTNIS SPEICHERN FÜR DEN TIMER
        st.session_state.pumpen_leistung = l_min
        st.success(f"✅ Förderstrom von {l_min:.2f} l/min wurde für den Timer gespeichert.")


# ==========================================
# WERKZEUG 4: LIVE-TIMER
# ==========================================
with tab4:
    st.subheader("⏳ Abpump-Timer & Parameter-Erinnerung")
    
    vol = st.session_state.ziel_volumen
    flow = st.session_state.pumpen_leistung
    
    # Prüfen, ob schon Daten berechnet wurden
    if vol > 0 and flow > 0:
        total_minutes = vol / flow
        total_seconds = int(total_minutes * 60)
        
        st.info(f"**Aktuelle Daten:** Ziel-Volumen: {vol:.1f} L | Förderstrom: {flow:.2f} l/min\n\n**Berechnete Dauer:** {total_minutes:.1f} Minuten")
        
        if st.button("▶️ Pumpe & Timer starten", type="primary", key="btn_timer"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Die Timer-Schleife
            for i in range(total_seconds):
                verbleibend = total_seconds - i
                mins, secs = divmod(verbleibend, 60)
                
                # Anzeige aktualisieren
                status_text.markdown(f"### ⏳ {mins:02d}:{secs:02d} verbleibend")
                progress_bar.progress((i + 1) / total_seconds)
                
                # Erinnerung alle 5 Minuten (300 Sekunden)
                # i > 0 verhindert, dass der Alarm direkt bei Sekunde 0 losgeht
                if i > 0 and i % 300 == 0:
                    st.toast("🔔 **5 Minuten vergangen!** Bitte Vor-Ort-Parameter messen.", icon="⏱️")
                
                time.sleep(1) # 1 Sekunde warten
            
            # Wenn der Timer durch ist
            status_text.markdown("### ✅ Zielvolumen erreicht!")
            st.balloons()
            st.success("Das berechnete Wasservolumen wurde erfolgreich gefördert.")
            
    else:
        st.warning("⚠️ Bitte berechnen Sie zuerst das Abpumpvolumen (Reiter 1 oder 2) und bestätigen Sie den Förderstrom (Reiter 3).")
