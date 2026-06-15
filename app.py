import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime
from num2words import num2words
from google import genai

# ================= 1. الإعدادات =================
st.set_page_config(page_title="ISO Marketing & Ventes", layout="wide", page_icon="🏢")

# ⚠️ تأكد من وضع مفتاحك الحقيقي هنا 
MY_API_KEY = "AQ.Ab8RN6KV1Tb2fp5B3p5AZtInWCk5UcWHsxwotG_gDMu1ySeDbw" 
client = genai.Client(api_key=MY_API_KEY)

CATALOG_DB = {
    "grille lineaire alu blanc 800x100": {"code": "04938", "des": "GRILLE LINEAIR ALU BLANC 800X100 ETM", "prix": 2559.04},
    "grille lineaire alu blanc 800x150": {"code": "04855", "des": "GRILLE LINEAIR ALU BLANC 800X150 ALU ETM", "prix": 2833.53},
    "grille de reprise alu blanc 600x600": {"code": "05243", "des": "GRILLE DE REPRISE ALU BLANC 600x600 ETM", "prix": 7563.03}
}

# ================= 2. القائمة الجانبية (Navigation) =================
st.sidebar.title("🏢 ISO Web System")
st.sidebar.caption("Plateforme Marketing & Ventes")
st.sidebar.markdown("---")
menu = st.sidebar.radio("📌 Navigation:", ["💬 Assistant Commercial (IA)", "📦 Cartographie Stock (WMS)"])
st.sidebar.markdown("---")
st.sidebar.success("🟢 En Ligne")

# ================= 3. شاشة المبيعات (AI Agent) =================
if menu == "💬 Assistant Commercial (IA)":
    st.title("🤖 Chatbot Commercial (Générateur de Devis)")
    st.markdown("---")

    SYSTEM_PROMPT = """
    أنت مساعد مبيعات ذكي. 
    1. رحب بالزبون.
    2. استخرج القياس والكمية.
    3. 🔴 لا تصدر الفاتورة قبل أن تسأل عن اسم الزبون: "À quel nom dois-je établir la facture proforma ?"
    4. 🟢 عندما تكتمل المعلومات، أصدر JSON حصرياً هكذا:
    {"status": "ready", "client_name": "NOM DU CLIENT", "items": [{"product": "grille lineaire alu blanc 800x100", "quantity": 33}]}
    """

    def num_to_words_dzd(amount):
        int_part = int(amount)
        words_int = num2words(int_part, lang='fr').capitalize()
        return f"{words_int} Dinars Algériens"

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "Bienvenue chez ISO Distribution, comment je peux vous aider aujourd'hui ?"}]

    col_chat, col_invoice = st.columns([1, 1.5])

    with col_chat:
        for msg in st.session_state.chat_history:
            if "invoice_html" not in msg:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if user_input := st.chat_input("Ex: Je veux des grilles..."):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"): 
                st.markdown(user_input)

            conversation = SYSTEM_PROMPT + "\n\n--- Historique ---\n"
            for msg in st.session_state.chat_history:
                if "invoice_html" not in msg: 
                    conversation += f"{msg['role']}: {msg['content']}\n"

            with st.chat_message("assistant"):
                with st.spinner("L'agent prépare le devis..."):
                    try:
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=conversation)
                        ai_reply = response.text.strip()

                        if '"status": "ready"' in ai_reply:
                            start_idx = ai_reply.find('{')
                            end_idx = ai_reply.rfind('}') + 1
                            order_data = json.loads(ai_reply[start_idx:end_idx])
                            
                            client_name = order_data.get("client_name", "CLIENT INCONNU")
                            bl_number = f"IA-{random.randint(100, 999)}/{datetime.now().year}"
                            
                            invoice_lines = ""
                            total_ht = 0
                            
                            for item in order_data.get("items", []):
                                prod_name = item.get("product", "").lower().strip()
                                qty = int(item.get("quantity", 1))
                                db_item = CATALOG_DB.get(prod_name, {"code": "00000", "des": prod_name.upper(), "prix": 2500.0})
                                montant = db_item["prix"] * qty
                                total_ht += montant
                                
                                invoice_lines += f"""
                                <tr>
                                    <td style="padding: 5px; border-bottom: 1px dotted #ccc;">{db_item['code']}</td>
                                    <td style="padding: 5px; border-bottom: 1px dotted #ccc; font-size: 10px;">{db_item['des']}</td>
                                    <td style="padding: 5px; border-bottom: 1px dotted #ccc; text-align: center;">UNITE</td>
                                    <td style="padding: 5px; border-bottom: 1px dotted #ccc; text-align: center;">{qty}</td>
                                    <td style="padding: 5px; border-bottom: 1px dotted #ccc; text-align: right;">{db_item['prix']:,.2f}</td>
                                    <td style="padding: 5px; border-bottom: 1px dotted #ccc; text-align: right;">{montant:,.2f}</td>
                                </tr>
                                """
                                
                            tva = total_ht * 0.19
                            total_ttc = total_ht + tva
                            words_amount = num_to_words_dzd(total_ttc)

                            # بناء الفاتورة المستنسخة من برنامجكم القديم
                            final_html = f"""
                            <div style="font-family: Arial, sans-serif; background: white; color: black; padding: 40px; font-size: 11px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                                <table style="width: 100%; border: none; margin-bottom: 30px;">
                                    <tr>
                                        <td style="width: 50%; vertical-align: top; line-height: 1.4;">
                                            <div style="color: #4b8bbe; font-weight: bold; font-size: 14px; margin-bottom: 10px;">ISO DISTRIBUTION CNE</div>
                                            <div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">SARL iso distribution cne</div>
                                            Constantine<br>NIF : 002325007397043
                                        </td>
                                        <td style="width: 50%; vertical-align: top; text-align: right;">
                                            <h2 style="margin: 0; font-size: 20px;">FACTURE PROFORMA</h2>
                                            <h3 style="margin: 5px 0 15px 0; font-size: 16px;">N° {bl_number}</h3>
                                            <div style="border-top: 2px solid black; padding-top: 5px; text-align: left;">
                                                <b>CLIENT :</b> <span style="text-transform: uppercase;">{client_name}</span>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                                <table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 20px;">
                                    <thead>
                                        <tr style="border-top: 2px solid black; border-bottom: 2px solid black;">
                                            <th style="padding: 5px; text-align: left;">Code</th>
                                            <th style="padding: 5px; text-align: left;">Désignation</th>
                                            <th style="padding: 5px; text-align: center;">U.M</th>
                                            <th style="padding: 5px; text-align: center;">Qté</th>
                                            <th style="padding: 5px; text-align: right;">Prix Unitaire HT</th>
                                            <th style="padding: 5px; text-align: right;">Montant HT</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {invoice_lines}
                                    </tbody>
                                </table>
                                <table style="width: 100%; border: none;">
                                    <tr>
                                        <td style="width: 55%; vertical-align: top; padding-right: 20px;">
                                            <b><u>Arrêter la somme de la présente facture :</u></b><br>
                                            <i style="font-size: 11.5px;">{words_amount}</i>
                                        </td>
                                        <td style="width: 45%; vertical-align: top;">
                                            <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                                                <tr><td style="padding: 3px;"><b>TOTAL HT</b></td><td style="padding: 3px; text-align: right;"><b>{total_ht:,.2f} DA</b></td></tr>
                                                <tr><td style="padding: 3px;">TOTAL TVA</td><td style="padding: 3px; text-align: right;">{tva:,.2f} DA</td></tr>
                                                <tr style="border-top: 2px solid black; border-bottom: 2px solid black;"><td style="padding: 5px;"><b>NET A PAYER</b></td><td style="padding: 5px; text-align: right; font-size: 12px;"><b>{total_ttc:,.2f} DA</b></td></tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                <div style="margin-top: 40px; font-size: 9px; color: #555; border-top: 1px solid #ccc; padding-top: 5px;">Logiciel : ISO Smart ERP (Généré par IA)</div>
                            </div>
                            """
                            
                            st.success("✅ Parfait ! Votre commande est validée. La facture est générée à droite 👉")
                            st.session_state.chat_history.append({"role": "assistant", "content": "Facture générée", "invoice_html": final_html})
                            st.rerun()

                        else:
                            clean_reply = ai_reply.replace("```json", "").replace("```", "").strip()
                            st.markdown(clean_reply)
                            st.session_state.chat_history.append({"role": "assistant", "content": clean_reply})
                    except Exception as e:
                        st.error("Erreur de connexion IA.")

    with col_invoice:
        st.subheader("📄 Facture Proforma Générée")
        last_invoice = next((msg["invoice_html"] for msg in reversed(st.session_state.chat_history) if "invoice_html" in msg), None)
        if last_invoice:
            st.components.v1.html(last_invoice, height=650, scrolling=True)
        else:
            st.caption("الورقة البيضاء للفاتورة ستظهر هنا بمجرد أن تعطي للبوت اسمك...")

# ================= 4. شاشة المخزون (WMS) =================
elif menu == "📦 Cartographie Stock (WMS)":
    st.title("📦 Cartographie du Stock (Marketing View)")
    
    data_stock = [
        {"Bâtiment": "Bâtiment 1", "Étage": "1er Étage", "Zone": "Zone A", "Article": "GRILLE LINEAIRE 800X100", "Quantité": 150, "Statut": "🟢 متوفر"},
        {"Bâtiment": "Bâtiment 1", "Étage": "1er Étage", "Zone": "Zone B", "Article": "GRILLE LINEAIRE 800X150", "Quantité": 12, "Statut": "🟠 ناقص"},
        {"Bâtiment": "Bâtiment 1", "Étage": "3ème Étage", "Zone": "Zone A", "Article": "DIFFUSEUR CARRE 600X600", "Quantité": 0, "Statut": "🔴 نفد"},
        {"Bâtiment": "Bâtiment 2", "Étage": "RDC", "Zone": "Zone Lourd", "Article": "MOTEUR VMC", "Quantité": 5, "Statut": "🟠 ناقص"},
    ]
    df_stock = pd.DataFrame(data_stock)
    
    search_query = st.text_input("🔍 Recherche rapide (ex: 800x100):")
    if search_query:
        result = df_stock[df_stock["Article"].str.contains(search_query.upper(), na=False)]
        if not result.empty:
            st.success("✅ Article trouvé :")
            st.dataframe(result, use_container_width=True, hide_index=True)
        else:
            st.error("Article non trouvé.")
            
    st.markdown("---")
    batiments = df_stock["Bâtiment"].unique()
    tabs = st.tabs(list(batiments))

    for i, tab in enumerate(tabs):
        with tab:
            df_bat = df_stock[df_stock["Bâtiment"] == batiments[i]]
            for etage in ["RDC", "1er Étage", "2ème Étage", "3ème Étage", "4ème Étage", "5ème Étage"]:
                df_etage = df_bat[df_bat["Étage"] == etage]
                if not df_etage.empty:
                    with st.expander(f"📶 {etage} - ({len(df_etage)} articles)", expanded=True):
                        st.dataframe(df_etage[["Zone", "Article", "Quantité", "Statut"]], use_container_width=True, hide_index=True)