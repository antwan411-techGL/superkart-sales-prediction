
import streamlit as st
import pandas as pd
import requests

# Flask backend address within the Docker network
BACKEND_URL = "http://backend:7860"

# Configure Streamlit page
st.set_page_config(
    page_title="SuperKart Sales Prediction",
    page_icon="🛒",
    layout="wide"
)

# Page title
st.title("🛒 SuperKart System")

st.write(
    "Enter the product and store details below "
    "to predict the total sales."
)

st.divider()

# Product details
st.subheader("Product Information")

col1, col2 = st.columns(2)

with col1:
    Product_Weight = st.number_input(
        "Product Weight",
        min_value=0.0,
        value=12.66
    )

    Product_Sugar_Content = st.selectbox(
        "Product Sugar Content",
        ["Low Sugar", "Regular", "No Sugar"]
    )

    Product_Allocated_Area = st.number_input(
        "Product Allocated Area",
        min_value=0.0,
        value=0.027,
        format="%.3f"
    )

with col2:
    Product_MRP = st.number_input(
        "Product MRP",
        min_value=0.0,
        value=117.08
    )

    Product_Id_char = st.selectbox(
        "Product ID Character",
        ["FD", "DR", "NC"]
    )

    Product_Type_Category = st.selectbox(
        "Product Type Category",
        ["Perishables", "Non Perishables"]
    )

st.divider()

# Store details
st.subheader("Store Information")

col3, col4 = st.columns(2)

with col3:
    Store_Size = st.selectbox(
        "Store Size",
        ["Small", "Medium", "High"]
    )

    Store_Location_City_Type = st.selectbox(
        "Store Location City Type",
        ["Tier 1", "Tier 2", "Tier 3"]
    )

with col4:
    Store_Type = st.selectbox(
        "Store Type",
        [
            "Supermarket Type1",
            "Supermarket Type2",
            "Supermarket Type3",
            "Departmental Store",
            "Food Mart"
        ]
    )

    Store_Age_Years = st.number_input(
        "Store Age (Years)",
        min_value=0,
        value=16
    )

# Create JSON payload
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category
}

st.divider()

# Single product prediction
st.subheader("Single Product Sales Prediction")

if st.button("Predict Sales", type="primary"):

    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/predict",
            json=product_data,
            timeout=30
        )

        if response.status_code == 200:

            result = response.json()
            predicted_sales = result["Sales"]

            st.success("Prediction completed successfully!")

            st.metric(
                label="Predicted Product Store Sales Total",
                value=f"₹{predicted_sales:,.2f}"
            )

        else:
            st.error(
                f"Prediction failed: {response.text}"
            )

    except requests.exceptions.RequestException as e:
        st.error(
            f"Unable to connect to the Flask backend: {e}"
        )

st.divider()

# Batch prediction
st.subheader("Batch Prediction")

st.write(
    "Upload a CSV file containing product and store "
    "information to predict sales for multiple products."
)

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    if st.button("Predict for Batch", type="primary"):

        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "text/csv"
                    )
                },
                timeout=120
            )

            if response.status_code == 200:

                results = response.json()

                # Convert indexed prediction results to DataFrame
                if isinstance(results, dict):
                    df = pd.DataFrame(
                        [
                            {
                                "Row": int(k),
                                "Predicted Sales": v
                            }
                            for k, v in results.items()
                        ]
                    )

                    df = df.sort_values("Row")
                    df["Row"] = df["Row"] + 1

                elif isinstance(results, list):
                    df = pd.DataFrame(results)

                else:
                    df = pd.DataFrame(
                        {"Prediction": [results]}
                    )

                st.success(
                    "Batch predictions completed successfully!"
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

                # Download predictions
                csv_data = df.to_csv(index=False)

                st.download_button(
                    label="Download Predictions CSV",
                    data=csv_data,
                    file_name="superkart_predictions.csv",
                    mime="text/csv"
                )

            else:
                st.error(
                    f"Batch prediction failed: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            st.error(
                f"Unable to connect to the Flask backend: {e}"
            )
