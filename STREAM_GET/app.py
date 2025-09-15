import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Getaround – Dashboard Analyse", layout="wide")

st.title("🚗 Dashboard Analyse – Getaround")
st.markdown("""
Bienvenue sur le dashboard interactif de l’étude Getaround.  
Vous avez 3 onglets pour naviguer sur les themes suivant :  
1. Analyse Retards  
2. Analyse Pricing 
3. Prédiction API 
""")

tab1, tab2, tab3 = st.tabs(["📊 Analyse Retards", "💰 Analyse Pricing", "🤖 Prédiction API"])

with tab1:
    st.header("Analyse des retards")

    df = pd.read_csv("data/get_around_delay_analysis.csv")
    df_pricing = pd.read_csv("data/pricing_clean.csv")

    loc_moyenne = df_pricing["rental_price_per_day"].mean()

    # EDA SUR LES RETARDS 
    st.header("📊 Analyse des retards et annulations")


    fig_state = px.pie(df, names="state", title="Répartition par état des locations")
    st.plotly_chart(fig_state, use_container_width=True)

    annulation = (df["state"] == "canceled").sum()
    st.metric("Nombre total d'annulations", annulation)

    st.markdown("""
    👉 Environ **15 % des transactions sont annulées**.  
    La proportion est légèrement plus élevée via **Connect** que via Mobile.
    """)


    fig_delay = px.histogram(
        df.query("-150 <= delay_at_checkout_in_minutes <= 150"),
        x="delay_at_checkout_in_minutes",
        nbins=60,
        title="Distribution des retards (fenêtre -150 à 150 min)"
    )
    st.plotly_chart(fig_delay, use_container_width=True)

    st.markdown("""
    👉 La majorité des retards est **courte** :  
    - 50 % ≤ 9 min  
    - 75 % ≤ 67 min  
    Mais certains cas extrêmes dépassent plusieurs jours.
    """)

    # ANALYSE DES ANNULATIONS 
    st.header("❌ Analyse des annulations liées aux retards")

    mask = df['previous_ended_rental_id'] > 0
    df_nan = df[mask]
    st.metric("Le nombre d'annulations du au retard du véhicule liées à un location précendente est de", (df_nan["state"] == "canceled").sum())
    annulation = (df_nan["state"] == "canceled").sum() 
    st.metric("La location moyenne d'un véhicule par jour est de ", df_pricing['rental_price_per_day'].mean().round(2))
    st.metric("La perte du aux annulations s'élève a :", (annulation * loc_moyenne).round(2))

    canceled = df[df["state"] == "canceled"][["rental_id", "car_id", "previous_ended_rental_id", "checkin_type","time_delta_with_previous_rental_in_minutes"]]

    merged = canceled.merge(
        df[["rental_id", "car_id", "delay_at_checkout_in_minutes", "checkin_type"]],
        left_on="previous_ended_rental_id",   
        right_on="rental_id",                 
        suffixes=("_canceled", "_previous")
    )

    conflict_strict = merged[
        merged["delay_at_checkout_in_minutes"] > merged["time_delta_with_previous_rental_in_minutes"]
    ]
    st.metric("Conflits stricts :", len(conflict_strict))
    st.metric("Moyenne retard précédent (conflits seulement) :", conflict_strict["delay_at_checkout_in_minutes"].mean().round(2))

    st.markdown("""
    👉 Parmi les **229 annulations liées à une location précédente**,  
    **37** sont dues à un retard allant au delà de l'heure de début de la prochaine location.  
    Ces retards sont très longs (~4h15 en moyenne).
    """)

    conflict_minus30 = merged[
        merged["delay_at_checkout_in_minutes"] > merged["time_delta_with_previous_rental_in_minutes"] - 30
    ]

    conflict_minus60 = merged[
        merged["delay_at_checkout_in_minutes"] > merged["time_delta_with_previous_rental_in_minutes"] - 60
    ]

    conflict_minus90 = merged[
        merged["delay_at_checkout_in_minutes"] > merged["time_delta_with_previous_rental_in_minutes"] - 90
    ]

    conflict_minus180 = merged[
        merged["delay_at_checkout_in_minutes"] > merged["time_delta_with_previous_rental_in_minutes"] - 180
    ]


    results = [
        {"Buffer": "-30 min", "Conflits": (len(conflict_minus30)-len(conflict_strict)), "Moyenne retard (min)": conflict_minus30["delay_at_checkout_in_minutes"].mean()},
        {"Buffer": "-60 min", "Conflits": (len(conflict_minus60)-len(conflict_strict)), "Moyenne retard (min)": conflict_minus60["delay_at_checkout_in_minutes"].mean()},
        {"Buffer": "-90 min", "Conflits": (len(conflict_minus90)-len(conflict_strict)), "Moyenne retard (min)": conflict_minus90["delay_at_checkout_in_minutes"].mean()},
        {"Buffer": "-180 min", "Conflits": (len(conflict_minus180)-len(conflict_strict)), "Moyenne retard (min)": conflict_minus180["delay_at_checkout_in_minutes"].mean()},
    ]
    df_conflicts = pd.DataFrame(results)
    df_conflicts['lost_value'] = df_conflicts["Conflits"]*loc_moyenne
    st.dataframe(df_conflicts)

    st.markdown("""Si on regarde 30 miniutes avant le début de la location du véhicule combien ont été annulé (buffer de 30 minutes), on détecte 10 annulations supplémentaires : ces cas correspondent à des locations rendues trop proches de la suivante (<30 min de marge).
    Avec un buffer de 60 minutes, seulement 3 cas en plus → ce sont donc des situations rares mais critiques.
    En élargissant à 90 minutes, on ajoute encore 7 cas.""")


    fig_type = px.histogram(
        df.query("-150 <= delay_at_checkout_in_minutes <= 150"),
        x="delay_at_checkout_in_minutes",
        color="checkin_type",
        nbins=int((150 - (-150)) / 10),  
        opacity=0.2,
        title="Distribution des retards par type de check-in",
        labels={"delay_at_checkout_in_minutes": "Retard (minutes)"},
        range_x=[-150, 150],
        width=1200, height=600,
    )
    fig_type.update_layout(barmode="overlay")
    fig_type.update_yaxes(title="Nombre de locations")
    #
    st.plotly_chart(fig_type, use_container_width=True)


    st.markdown(""" ANALYSE SUR MOBILE """)

    mask = merged["checkin_type_canceled"] == "mobile"
    merged_mob = merged[mask]
    conflict_strict1= merged_mob[
        merged_mob["delay_at_checkout_in_minutes"] > merged_mob["time_delta_with_previous_rental_in_minutes"]
    ]
    st.metric("Conflits stricts :", len(conflict_strict1))
    st.metric("Moyenne retard précédent (conflits seulement) :", conflict_strict1["delay_at_checkout_in_minutes"].mean().round(2))

    conflict_1minus30 = merged_mob[
        merged_mob["delay_at_checkout_in_minutes"] > merged_mob["time_delta_with_previous_rental_in_minutes"] - 30
    ]

    conflict_1minus60 = merged_mob[
        merged_mob["delay_at_checkout_in_minutes"] > merged_mob["time_delta_with_previous_rental_in_minutes"] - 60
    ]

    conflict_1minus90 = merged_mob[
        merged_mob["delay_at_checkout_in_minutes"] > merged_mob["time_delta_with_previous_rental_in_minutes"] - 90
    ]

    conflict_1minus180 = merged_mob[
        merged_mob["delay_at_checkout_in_minutes"] > merged_mob["time_delta_with_previous_rental_in_minutes"] - 180
    ]


    results = [
        {"Buffer": "-30 min", "Conflits": (len(conflict_1minus30)-len(conflict_strict1)), "Moyenne retard (min)": conflict_1minus30["delay_at_checkout_in_minutes"].mean()},
        {"Buffer": "-60 min", "Conflits": (len(conflict_1minus60)-len(conflict_strict1)), "Moyenne retard (min)": conflict_1minus60["delay_at_checkout_in_minutes"].mean()},
        {"Buffer": "-90 min", "Conflits": (len(conflict_1minus90)-len(conflict_strict1)), "Moyenne retard (min)": conflict_1minus90["delay_at_checkout_in_minutes"].mean()},
        {"Buffer": "-180 min", "Conflits": (len(conflict_1minus180)-len(conflict_strict1)), "Moyenne retard (min)": conflict_1minus180["delay_at_checkout_in_minutes"].mean()},
    ]
    df_conflicts_mob = pd.DataFrame(results)
    df_conflicts_mob['lost_value'] = df_conflicts_mob["Conflits"]*loc_moyenne
    st.dataframe(df_conflicts_mob)

    st.markdown(""" ANALYSE SUR CONNECT """)

    mask = merged["checkin_type_canceled"] == "connect"
    merged_connect = merged[mask]
    conflict_strict2 = merged_connect[
        merged_connect["delay_at_checkout_in_minutes"] > merged_connect["time_delta_with_previous_rental_in_minutes"]
    ]
    st.metric("Conflits stricts :", len(conflict_strict2))
    st.metric("Moyenne retard précédent (conflits seulement) :", conflict_strict2["delay_at_checkout_in_minutes"].mean().round(2))


    conflict_2minus30 = merged_connect[
        merged_connect["delay_at_checkout_in_minutes"] > merged_connect["time_delta_with_previous_rental_in_minutes"] - 30
    ]


    conflict_2minus60 = merged_connect[
        merged_connect["delay_at_checkout_in_minutes"] > merged_connect["time_delta_with_previous_rental_in_minutes"] - 60
    ]

    conflict_2minus90 = merged_connect[
        merged_connect["delay_at_checkout_in_minutes"] > merged_connect["time_delta_with_previous_rental_in_minutes"] - 90
    ]

    conflict_2minus180 = merged_connect[
        merged_connect["delay_at_checkout_in_minutes"] > merged_connect["time_delta_with_previous_rental_in_minutes"] - 180
    ]


    results = [
        {"Buffer": "-30 min", "Conflits": (len(conflict_2minus30)-len(conflict_strict2)), "Moyenne retard (min)": conflict_2minus30["delay_at_checkout_in_minutes"].mean()},
        {"Buffer": "-60 min", "Conflits": (len(conflict_2minus60)-len(conflict_strict2)), "Moyenne retard (min)": conflict_2minus60["delay_at_checkout_in_minutes"].mean()},
        {"Buffer": "-90 min", "Conflits": (len(conflict_2minus90)-len(conflict_strict2)), "Moyenne retard (min)": conflict_2minus90["delay_at_checkout_in_minutes"].mean()},
        {"Buffer": "-180 min", "Conflits": (len(conflict_2minus180)-len(conflict_strict2)), "Moyenne retard (min)": conflict_2minus180["delay_at_checkout_in_minutes"].mean()},
    ]
    df_conflicts_con = pd.DataFrame(results)

    df_conflicts_con['lost_value'] = df_conflicts_con["Conflits"]*loc_moyenne

    st.dataframe(df_conflicts_con)

    st.markdown("""Les deux systèmes subissent des annulations liées aux délais courts.
    Connect est plus fréquent en volume absolu, mais ses retards sont légèrement moins sévères.
    Mobile présente moins de cas mais avec des retards plus longs → donc plus difficiles à absorber sans impact client.
    Les deux méthodes sont exposées aux retards, mais Connect encaisse plus de cas tandis que Mobile concentre les retards les plus importants.
    """ )

    # IMPACT DES BUFFERS 
    st.header("⏳ Simulation de buffer entre locations")
    st.markdown(""" Afin d'analyser l'impact d'un buffer nous prenons cette fois ci que les locations qui ont eu lieu et filtrons toutes les locations ayant débutées dans les 30 minutes qui suit la précéddentes.
    Ces locations sont celle qui risquent d'etre impactées par ce delai """)

    loc_moyenne = df_pricing["rental_price_per_day"].mean()
    CA_total = (df['state'] == 'ended').sum() * loc_moyenne


    df_valid = df[df["state"] == "ended"].copy()
    df_valid["ecart"] = df_valid["time_delta_with_previous_rental_in_minutes"] - df_valid["delay_at_checkout_in_minutes"]

    def count_blocked(df, buffer):
        return (df["ecart"] < buffer).sum()

    results = []
    for b in [30, 60, 90, 180]:
        blocked = count_blocked(df_valid, b)
        perte_estimee = blocked * loc_moyenne
        results.append({"Buffer (min)": b, "Locations bloquées": blocked, "Perte estimée ($)": round(perte_estimee, 2)})

    df_results = pd.DataFrame(results)
    st.dataframe(df_results)


    st.markdown(""" MOBILE UNIQUEMENT""")

    df_valid_mob = df[(df["state"] == "ended") & (df["checkin_type"] == "mobile")].copy()
    df_valid_mob["ecart"] = df_valid_mob["time_delta_with_previous_rental_in_minutes"] - df_valid_mob["delay_at_checkout_in_minutes"]

    def count_blocked(df, buffer):
        return (df["ecart"] < buffer).sum()

    results2 = []
    for b in [30, 60, 90, 180]:
        blocked = count_blocked(df_valid_mob, b)
        perte_estimee = blocked * loc_moyenne
        results2.append({"Buffer (min)": b, "Locations bloquées": blocked, "Perte estimée ($)": round(perte_estimee, 2)})

    df_results_mob = pd.DataFrame(results2)
    st.dataframe(df_results_mob)


    st.markdown(""" CONNECT UNIQUEMENT""")

    df_valid_con = df[(df["state"] == "ended") & (df["checkin_type"] == "connect")].copy()
    df_valid_con["ecart"] = df_valid_con["time_delta_with_previous_rental_in_minutes"] - df_valid_con["delay_at_checkout_in_minutes"]

    def count_blocked(df, buffer):
        return (df["ecart"] < buffer).sum()

    results3 = []
    for b in [30, 60, 90, 180]:
        blocked = count_blocked(df_valid_con, b)
        perte_estimee = blocked * loc_moyenne
        results3.append({"Buffer (min)": b, "Locations bloquées": blocked, "Perte estimée ($)": round(perte_estimee, 2)})

    df_results_con = pd.DataFrame(results3)
    st.dataframe(df_results_con)

    st.markdown("""
    👉 Un buffer **de 30 min bloque ~340 locations** → pertes supérieures aux gains.  
    👉 Un buffer de **180 min réduit beaucoup les annulations** mais fait perdre trop de CA. 
    
    Les utilisateurs connect sont ceux qui annulent le plus 30 min avant la location comme nous l'avons vu juste avant, mais se sont ceux où l'impact business serait le plus faible. 
    dans le cas où l'on met un buffer à 30 min. Néanmoins le gain vs cout sera toujours négatif.
    **Conclusion : un buffer global n’est pas viable.**
    """)

    # CONCLUSION BUSINESS
    st.header("📌 Conclusion business")

    st.markdown("""
    Nos analyses montrent :  
    - Les retards courts sont fréquents, mais les **annulations sont rares (229 cas)**.  
    - Les retards extrêmes sont à l’origine de la majorité des conflits.  
    - Un buffer global **réduit les annulations mais détruit plus de revenu** qu’il n’en sauve.  

    ✅ **Recommandations** :  
    - Pas de buffer global.  
    - Buffer ciblé (<1h) sur cas à risque, zone chaude.  
    - Notifications pour inciter à rendre le véhicule en avance.  
    - Eventuellement pénalités pour retards répétés.(=> mais c'est anticommercial )

    👉 L’impact économique du buffer est donc limité,  
    mais des mesures ciblées peuvent réduire la friction sans perte majeure de CA.
    """)
    

# ANALYSE DU PRICING
with tab2:
    st.header("Analyse Pricing")
    
    df_pricing = pd.read_csv("data/pricing_clean.csv")

    fig_price = px.histogram(df_pricing, x="rental_price_per_day", nbins=50,
                            title="Distribution des prix de location par jour")
    st.plotly_chart(fig_price, use_container_width=True)


    fig_car_typ = px.box(df_pricing, x="car_type", y="rental_price_per_day",
                title="Prix par type de véhicule")
    st.plotly_chart(fig_car_typ, use_container_width=True)


    st.markdown("""
    👉 Le marché est concentré autour de **100–140 $/jour**.  
    Les **SUV, coupés, cabriolets** sont plus chers.  
    Les **citadines** et **hatchbacks** moins chers.
    """)


    df_corr = df_pricing.copy()
    bool_cols = df_corr.select_dtypes(include="bool").columns
    df_corr[bool_cols] = df_corr[bool_cols].astype(int)

    num_df = df_corr.select_dtypes(include=["int64", "float64"])

    corr = num_df.corr()

    fig_cor = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Matrice de corrélation",
        height=800,
        width=1000
    )
    st.plotly_chart(fig_cor, use_container_width=True)

    st.markdown(""" 
    + corrélation prix ↔ puissance moteur
                
    – corrélation prix ↔ kilométrage
                
    Transmission automatique = + valeur ajoutée
                
    Présence de GPS = + valeur ajoutée """)
    
with tab3:
    st.header("🔧 Prédiction API")

    # Sélection des valeurs
    model_key = st.selectbox("Marque", ["Audi", "BMW", "Peugeot", "Renault", "Citroën"])
    mileage = st.number_input("Kilométrage", min_value=0, max_value=300000, value=50000, step=1000)
    engine_power = st.number_input("Puissance moteur (ch)", min_value=50, max_value=300, value=110)
    fuel = st.selectbox("Carburant", ["diesel", "petrol", "hybrid_petrol", "electro"])
    paint_color = st.selectbox("Couleur", ["black", "grey", "white", "red", "silver", "blue", "orange", "beige", "brown", "green"])
    car_type = st.selectbox("Type de voiture", ["estate", "hatchback", "sedan", "suv", "convertible", "coupe", "van"])

    private_parking_available = st.checkbox("Parking privé disponible")
    has_gps = st.checkbox("GPS")
    has_air_conditioning = st.checkbox("Climatisation")
    automatic_car = st.checkbox("Automatique")
    has_getaround_connect = st.checkbox("Getaround Connect")
    has_speed_regulator = st.checkbox("Régulateur de vitesse")
    winter_tires = st.checkbox("Pneus hiver")

    # Construire le JSON attendu
    payload = {
        "model_key": model_key,
        "mileage": mileage,
        "engine_power": engine_power,
        "fuel": fuel,
        "paint_color": paint_color,
        "car_type": car_type,
        "private_parking_available": private_parking_available,
        "has_gps": has_gps,
        "has_air_conditioning": has_air_conditioning,
        "automatic_car": automatic_car,
        "has_getaround_connect": has_getaround_connect,
        "has_speed_regulator": has_speed_regulator,
        "winter_tires": winter_tires
    }

    if st.button("🔮 Prédire le prix"):
        try:
            response = requests.post("https://gdleds-api-get.hf.space/predict", json=payload)
            if response.status_code == 200:
                result = response.json()
                st.success(f"💰 Prix estimé : {result['predicted_price_per_day'][0]} $/jour")
            else:
                st.error(f"Erreur API ({response.status_code}) : {response.text}")
        except Exception as e:
            st.error(f"⚠️ Impossible d'appeler l'API : {e}")
