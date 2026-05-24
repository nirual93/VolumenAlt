import streamlit as st
import math

# --- DESIGN & TITEL ---
st.set_page_config(page_title="GW-Rechner", page_icon="💧")
st.title("💧 GW-Volumen Rechner")
st.subheader("Nach DIN 38402-13")
st.write("---")

# --- 1. EINGABEFELDER ---
# st.number_input sorgt dafür, dass Nutzer nur Zahlen tippen können
durchmesser_mm = st.number_input("Rohr-Durchmesser in mm", value=100.0, step=10.0)
tiefe_m = st.number_input("Gesamttiefe in m", value=22.5, step=0.1)
ruhewasser_m = st.number_input("Ruhewasserstand in m", value=14.2, step=0.1)

st.write("---")

# --- 2. BUTTON & BERECHNUNG ---
if st.button("Volumen berechnen", type="primary"):
    
    radius_m = (durchmesser_mm / 2) / 1000
    wassersaeule_m = tiefe_m - ruhewasser_m
    
    # Fehlerprüfung
    if wassersaeule_m < 0:
        st.error("❌ Fehler: Der Ruhewasserstand kann nicht tiefer sein als die Gesamttiefe!")
    else:
        # Die eigentliche Mathematik
        standwasser_volumen = math.pi * (radius_m ** 2) * wassersaeule_m * 1000
        abpump_volumen = 3 * standwasser_volumen
        
        # --- 3. ERGEBNIS-AUSGABE ---
        st.success("✅ Berechnung erfolgreich!")
        
        # Wir nutzen Columns, um die Daten schön nebeneinander darzustellen
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Wassersäule", value=f"{wassersaeule_m:.2f} m")
        col2.metric(label="1-fach Volumen", value=f"{standwasser_volumen:.1f} L")
        col3.metric(label="3-fach Abpumpen", value=f"{abpump_volumen:.1f} L")
        
        st.info(f"**Fazit:** Sie müssen mindestens **{abpump_volumen:.1f} Liter** abpumpen, bevor die chemische Konstanz geprüft werden darf.")
        
