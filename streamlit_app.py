import streamlit as st
import math
import time

# --- SEITEN-SETUP & GEDÄCHTNIS (SESSION STATE) ---
st.set_page_config(page_title="Feld-Assistent GW", page_icon="🛠️", layout="centered")

# Gedächtnis-Variablen initialisieren
if 'ziel_volumen' not in st.session_state:
    st.session_state.ziel_volumen = 0.0
if 'pumpen_leistung' not in st.session_state:
    st.session_state.pumpen_leistung = 0.0
if 'messungen' not in st.session_state:
    st.session_state.messungen = []
if 'pumpen_start' not in st.session_state:
    st.session_state.pumpen_start = None

st.title("🛠️ Grundwasser Feld-Assistent")
st.write("Wählen Sie das benötigte Werkzeug über die Reiter aus:")

# --- KARTEIREITER ---
tab1, tab2, tab3, tab4 = st.tabs(["💧 DIN-Rechner", "🪨 Filterkies", "⏱️ Förderstrom", "⏳ Protokoll & Timer"])

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
            st.session_state.ziel_volumen = ziel_volumen_l
            
            st.success("✅ Berechnung erfolgreich! Wert wurde für den Timer gespeichert.")
            col1, col2 = st.columns(2)
            col1.metric("1-fach Volumen (m³)", f"{zylinder_volumen_m3:.3f} m³")
            col2.metric("1,5-fach Abpumpen (L)", f"{ziel_volumen_l:.1f} L")


# ==========================================
# WERKZEUG 3: FÖRDERSTROM-UMRECHNER
# ==========================================
with tab3:
    st.subheader("Umrechnung von Pumpenleistung & Messzeit")
    
    auswahl = st.radio("Gemessener Wert:", ["Liter pro Minute (l/min)", "Liter pro Stunde (l/h)", "Zeit für 1 Liter (s/l)"], key="strom_radio")
    l_min, l_h, sek_pro_liter = 0.0, 0.0, 0.0
    
    if auswahl == "Liter pro Minute (l/min)":
        wert = st.number_input("Wert in l/min:", min_value=0.001, value=8.0, step=0.5, key="strom_min")
        l_min = wert
        l_h = wert * 60
        sek_pro_liter = 60 / wert
    elif auswahl == "Liter pro Stunde (l/h)":
        wert = st.number_input("Wert in l/h:", min_value=0.001, value=480.0, step=10.0, key="strom_h")
        l_h = wert
        l_min = wert / 60
        sek_pro_liter = 3600 / wert
    elif auswahl == "Zeit für 1 Liter (s/l)":
        wert = st.number_input("Sekunden für 1 Liter:", min_value=0.001, value=7.5, step=0.5, key="strom_s")
        sek_pro_liter = wert
        l_min = 60 / wert
        l_h = 3600 / wert
        
    st.write("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Liter pro Minute", f"{l_min:.2f} l/min")
    col2.metric("Liter pro Stunde", f"{l_h:.0f} l/h")
    col3.metric("Zeit für 1 Liter", f"{sek_pro_liter:.2f} s")
    
    st.write("---")
    if st.button("Förderstrom für den Timer übernehmen", type="primary", key="btn_strom"):
        st.session_state.pumpen_leistung = l_min
        st.success(f"✅ Förderstrom von {l_min:.2f} l/min gespeichert.")


# ==========================================
# WERKZEUG 4: LIVE-TIMER & PROTOKOLL
# ==========================================
with tab4:
    st.subheader("⏳ Protokoll & Abpump-Überwachung")
    
    vol = st.session_state.ziel_volumen
    flow = st.session_state.pumpen_leistung
    
    if vol > 0 and flow > 0:
        total_minutes = vol / flow
        total_seconds = int(total_minutes * 60)
        
        st.info(f"**Ziel-Volumen:** {vol:.1f} L | **Förderstrom:** {flow:.2f} l/min | **Dauer:** {total_minutes:.1f} Min.")
        
        # STATUS: PUMPE NOCH NICHT GESTARTET
        if st.session_state.pumpen_start is None:
            if st.button("▶️ Pumpe starten & Protokoll beginnen", type="primary"):
                st.session_state.pumpen_start = time.time()
                st.session_state.messungen = [] # Löscht alte Protokolle
                st.rerun() # Aktualisiert die Seite sofort
        
        # STATUS: PUMPE LÄUFT
        else:
            # Berechne vergangene und verbleibende Zeiten
            elapsed_seconds = int(time.time() - st.session_state.pumpen_start)
            remaining_total = max(0, total_seconds - elapsed_seconds)
            
            # 5-Minuten-Intervall-Logik (300 Sekunden)
            elapsed_in_cycle = elapsed_seconds % 300
            remaining_in_cycle = 300 - elapsed_in_cycle
            
            # --- DOPPEL-TIMER ANZEIGE ---
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.metric("Verbleibende Gesamtdauer", f"{remaining_total // 60:02d}:{remaining_total % 60:02d} Min")
                st.progress(min(1.0, elapsed_seconds / total_seconds))
            
            with col_t2:
                # Optische Warnung bei Ablauf der 5 Minuten
                if remaining_in_cycle < 15 or elapsed_in_cycle < 15:
                    st.error(f"🔔 JETZT MESSEN! ({remaining_in_cycle // 60:02d}:{remaining_in_cycle % 60:02d} Min)")
                else:
                    st.metric("Nächste Parameter-Messung in", f"{remaining_in_cycle // 60:02d}:{remaining_in_cycle % 60:02d} Min")
                st.progress(min(1.0, elapsed_in_cycle / 300))
                
            # Manueller Button, um die Anzeige zu aktualisieren (passiert auch automatisch bei Eingaben)
            if st.button("🔄 Timer-Anzeige aktualisieren"):
                st.rerun()
            
            st.write("---")
            
            # --- EINGABEMASKE FÜR VOR-ORT-PARAMETER ---
            st.markdown("### 📝 Parameter erfassen")
            
            # Drei Spalten für ein kompaktes Layout
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                temp = st.number_input("Temp. (°C)", value=11.0, step=0.1)
                ph = st.number_input("pH-Wert", value=7.00, step=0.01)
            with col_p2:
                lf = st.number_input("LF (µS/cm)", value=500.0, step=1.0)
                redox = st.number_input("Redox (mV)", value=150.0, step=1.0)
            with col_p3:
                o2 = st.number_input("Sauerstoff (mg/l)", value=5.0, step=0.1)
                
            # Speichern-Button
            if st.button("💾 Werte zum Protokoll hinzufügen", type="primary"):
                # Aktuellen Zeitstempel für die Messung formatieren
                zeitstempel = f"{elapsed_seconds // 60:02d}:{elapsed_seconds % 60:02d}"
                
                # Als Wörterbuch (Dictionary) in der Liste speichern
                neue_messung = {
                    "Zeit (Min)": zeitstempel,
                    "Temp (°C)": temp,
                    "pH": ph,
                    "LF (µS/cm)": lf,
                    "Redox (mV)": redox,
                    "O2 (mg/l)": o2
                }
                st.session_state.messungen.append(neue_messung)
                st.success(f"Messung bei Minute {zeitstempel} erfolgreich gespeichert!")
                
            # --- PROTOKOLL & EXPORT ---
            if len(st.session_state.messungen) > 0:
                st.write("---")
                st.markdown("### 📋 Ihr digitales Messprotokoll")
                
                # Zeigt die Daten zur Kontrolle als saubere Tabelle an
                st.dataframe(st.session_state.messungen)
                
                # --- EXPORT FÜR DIE ZWISCHENABLAGE BAUEN ---
                protokoll_text = "Protokoll Vor-Ort-Parameter (Grundwasser)\n"
                protokoll_text += "="*45 + "\n"
                protokoll_text += f"Ziel-Volumen:\t{vol:.1f} L\n"
                protokoll_text += f"Förderstrom:\t{flow:.2f} l/min\n"
                protokoll_text += "-"*45 + "\n"
                protokoll_text += "Zeit\tTemp\tpH\tLF\tRedox\tO2\n"
                
                # Alle gespeicherten Messungen als Text-Zeilen anfügen
                for m in st.session_state.messungen:
                    protokoll_text += f"{m['Zeit (Min)']}\t{m['Temp (°C)']}\t{m['pH']}\t{m['LF (µS/cm)']}\t{m['Redox (mV)']}\t{m['O2 (mg/l)']}\n"
                
                st.write("---")
                st.info("💡 **Tipp für den Export:** Klicken Sie in dem grauen Kasten unten auf das kleine **Kopieren-Symbol in der oberen rechten Ecke**. Danach können Sie die Werte per 'Einfügen' direkt in eine E-Mail, WhatsApp oder Ihr LIMS-System übertragen.")
                
                # Das st.code Element erzeugt automatisch den "Copy to Clipboard"-Button
                st.code(protokoll_text, language="markdown")
                
            # Abschlussmeldung
            if remaining_total == 0:
                st.balloons()
                st.success("🎉 Das berechnete Zielvolumen wurde vollständig abgepumpt!")
                
    else:
        st.warning("⚠️ Bitte berechnen Sie zuerst das Abpumpvolumen (Reiter 1 oder 2) und übernehmen Sie den Förderstrom (Reiter 3).")
