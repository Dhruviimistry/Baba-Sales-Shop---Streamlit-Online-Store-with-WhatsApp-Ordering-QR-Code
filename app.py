import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import urllib.parse

# -------------------- LOAD PRODUCTS --------------------
@st.cache_data
def load_products():
    return pd.read_csv("products.csv")

products = load_products()

# -------------------- SESSION STATE --------------------
if "cart" not in st.session_state:
    st.session_state["cart"] = pd.DataFrame(columns=["category","product","price","qty","subtotal"])

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Baba Product Shop", page_icon="🛍️", layout="wide")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
 <style>
* {
    box-sizing: border-box;
}
body {
    background-color: #f4f7fb;
    font-family: 'Segoe UI', sans-serif;
}
h1 {
    text-align:center;
    color:white;
    padding:18px;
    border-radius:15px;
    background: linear-gradient(90deg, #2196F3, #1565C0); /* blue gradient */
    box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
}
.product-card {
    border:1px solid #ddd;
    border-radius:12px;
    padding:12px;
    margin-bottom:10px;
    background:white;
    color: #222;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
}
button[kind="primary"] {
    background: linear-gradient(90deg,#43A047,#1B5E20) !important;
    color:white !important;
    border-radius:10px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🛍️ Baba Product - Online Shop</h1>", unsafe_allow_html=True)

# -------------------- PRODUCTS TABS --------------------
categories = list(products["category"].unique())
tabs = st.tabs(categories)

for i, category in enumerate(categories):
    with tabs[i]:
        df = products[products["category"] == category]

        st.write(f"### 📦 {category}")
        for _, row in df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3,1,1,1])
                with col1:
                    st.markdown(f"<div class='product-card'><b>{row['product']}</b></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='product-card'>₹{row['price']}</div>", unsafe_allow_html=True)
                with col3:
                    qty = st.number_input(f"Qty_{row['product']}_{i}", 0, 50, 0, key=f"qty_{row['product']}_{i}")
                with col4:
                    if st.button("➕ Add", key=f"add_{row['product']}_{i}"):
                        if qty > 0:
                            st.session_state["cart"] = pd.concat([
                                st.session_state["cart"],
                                pd.DataFrame([{
                                    "category": category,
                                    "product": row['product'],
                                    "price": row['price'],
                                    "qty": qty,
                                    "subtotal": qty * row['price']
                                }])
                            ], ignore_index=True)

# -------------------- CART & WHATSAPP --------------------
st.markdown("---")
st.subheader("🛒 Your Cart")

if not st.session_state["cart"].empty:
    st.dataframe(st.session_state["cart"], use_container_width=True)

    total = st.session_state["cart"]["subtotal"].sum()
    st.success(f"💰 Total: ₹{total}")

    customer_name = st.text_input("👤 Customer Name")
    customer_phone = st.text_input("📞 Customer Phone")

    if st.button("✅ Send Order on WhatsApp"):
        if customer_name and customer_phone:
            order_text = f"Customer: {customer_name} ({customer_phone})\nOrder:\n"
            for _, r in st.session_state["cart"].iterrows():
                order_text += f"- {r['product']} x {r['qty']} = ₹{r['subtotal']}\n"
            order_text += f"\nTotal = ₹{total}"

            wa_link = f"https://wa.me/917498765189?text={urllib.parse.quote(order_text)}"
            st.markdown(
                f"<a href='{wa_link}' target='_blank' style='background:#25D366; color:white; padding:10px 20px; border-radius:12px; text-decoration:none; font-weight:bold;'>📲 Send on WhatsApp</a>",
                unsafe_allow_html=True
            )

            # QR code
            qr_buf = BytesIO()
            img = qrcode.make(wa_link)
            img = img.resize((220, 220))
            img.save(qr_buf, format="PNG")
            st.image(qr_buf.getvalue(), caption="📱 Scan to send order on WhatsApp", width=220)
        else:
            st.error("⚠️ Please enter customer name and phone!")

    if st.button("🗑️ Clear cart"):
        st.session_state["cart"] = pd.DataFrame(columns=["category","product","price","qty","subtotal"])
        st.experimental_rerun()
else:
    st.info("Add products to the cart from the tabs above.")

st.caption("💡 Tip: Use Admin mode in the sidebar to update the product catalog CSV.")
