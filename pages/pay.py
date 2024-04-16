import razorpay
import streamlit as st
import streamlit.components.v1 as components
from streamlit.components.v1 import html
client = razorpay.Client(auth=("rzp_live_ccdgxUrjuwvI5O", "lHxlvFXCwt8qz6StKedTMab2"))

def payment_page(bill_amount):
    st.markdown("**Payment**")
    order = client.order.create({"amount": int(bill_amount), "currency": "INR"})
    payment_id = order['id']
    return payment_id