import streamlit as st

# HTML content for Razorpay payment form
html_content = """
<!DOCTYPE html>
<html>
<head></head>
<body>
    <div id="paymentId"></div>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const myParam = urlParams.get('order_id');
        var options = {
            "key": "rzp_test_W4imizM9wdSgfj",
            "amount": "{{amount}}",
            "currency": "INR",
            "name": "Parking Management System",
            "description": "Test Transaction",
            "order_id": myParam,
            "handler": function (response){
                document.getElementById('paymentId').innerHTML = response.razorpay_payment_id;
                alert('Payment Successful');
                localStorage.setItem("status", "success");
                localStorage.setItem("paymentId", response.razorpay_payment_id);
                urlParams.append('order_id', response.razorpay_payment_id);
            },
            "prefill": {
                "name": "",
                "contact": ""
            },
            "notes": {
                "address": "Razorpay Corporate Office"
            },
            "theme": {
                "color": "#3399cc"
            }
        };
        var rzp1 = new Razorpay(options);
        rzp1.on('payment.failed', function (response){
            alert('Payment Failed');
            urlParams.append('order_id', 'failed');
        });
        rzp1.open();
        e.preventDefault();
    </script>
</body>
</html>
"""

# Generate dynamic link for HTML content
def generate_html_file(html_content):
    with open("payment.html", "w") as html_file:
        html_file.write(html_content)

# Display link to download the HTML file
if st.button("Download Payment Page"):
    generate_html_file(html_content)
    st.markdown(get_binary_file_downloader_html("payment.html", "HTML"), unsafe_allow_html=True)
