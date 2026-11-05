
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="Traffic Data Visualizer",
    page_icon="🚦",
    layout="wide"
)

st.title("Traffic Data Visualizer")
st.write(
    "Upload a CSV file to find the busiest traffic hours "
    "and locations."
)

# Upload CSV file
uploaded_file = st.file_uploader(
    "Upload your traffic count CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Check required columns
        required = ["Hour", "Location", "Traffic_Count"]

        missing = [
            col for col in required
            if col not in df.columns
        ]

        if missing:
            st.error(
                "Missing columns: " + ", ".join(missing)
            )
            st.info(
                "Required columns: Hour, Location, Traffic_Count"
            )

        else:
            # Clean the data
            df["Traffic_Count"] = pd.to_numeric(
                df["Traffic_Count"], errors="coerce"
            )
            df["Hour"] = df["Hour"].astype(str).str.strip()
            df["Location"] = df["Location"].astype(str).str.strip()

            df = df.dropna(
                subset=["Hour", "Location", "Traffic_Count"]
            )
            df = df[
                (df["Hour"] != "") &
                (df["Location"] != "") &
                (df["Traffic_Count"] >= 0)
            ]

            if df.empty:
                st.error("No valid traffic records were found.")

            else:
                st.subheader("Uploaded Traffic Data")
                st.dataframe(df, use_container_width=True)

                # Summarize traffic by hour and location
                hourly = (
                    df.groupby("Hour")["Traffic_Count"]
                    .sum()
                    .reset_index()
                )

                # Sort hours numerically where possible
                hourly["_sort"] = pd.to_numeric(
                    hourly["Hour"], errors="coerce"
                )
                hourly = hourly.sort_values(
                    "_sort", na_position="last"
                )

                locations = (
                    df.groupby("Location")["Traffic_Count"]
                    .sum()
                    .sort_values(ascending=False)
                )

                # Dashboard metrics
                busiest_hour = hourly.loc[
                    hourly["Traffic_Count"].idxmax(), "Hour"
                ]
                busiest_location = locations.idxmax()
                total_traffic = df["Traffic_Count"].sum()

                st.subheader("Traffic Summary")
                c1, c2, c3 = st.columns(3)

                c1.metric("Total Traffic Count", f"{total_traffic:,.0f}")
                c2.metric("Busiest Hour", str(busiest_hour))
                c3.metric("Busiest Location", str(busiest_location))

                # Line chart: traffic by hour
                st.subheader("Traffic by Hour")

                fig1, ax1 = plt.subplots(figsize=(10, 4))
                ax1.plot(
                    hourly["Hour"],
                    hourly["Traffic_Count"],
                    marker="o",
                    linewidth=2
                )
                ax1.set_title("Traffic Count by Hour")
                ax1.set_xlabel("Hour of Day")
                ax1.set_ylabel("Vehicle Count")
                ax1.grid(True, alpha=0.3)
                fig1.tight_layout()
                st.pyplot(fig1)
                plt.close(fig1)

                # Bar chart: traffic by location
                st.subheader("Traffic by Location")

                fig2, ax2 = plt.subplots(figsize=(10, 4))
                locations.plot(kind="bar", ax=ax2)
                ax2.set_title("Total Traffic Count by Location")
                ax2.set_xlabel("Location")
                ax2.set_ylabel("Vehicle Count")
                ax2.tick_params(axis="x", rotation=45)
                fig2.tight_layout()
                st.pyplot(fig2)
                plt.close(fig2)

                # Top five busiest hours
                st.subheader("Top 5 Busiest Hours")
                top_hours = hourly.nlargest(
                    5, "Traffic_Count"
                )[["Hour", "Traffic_Count"]]
                st.dataframe(
                    top_hours, use_container_width=True
                )

                # Top five busiest locations
                st.subheader("Top 5 Busiest Locations")
                top_locations = (
                    locations.head(5)
                    .rename("Traffic_Count")
                    .reset_index()
                )
                st.dataframe(
                    top_locations, use_container_width=True
                )

                # Download analyzed data
                csv_output = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Cleaned Traffic Data",
                    data=csv_output,
                    file_name="cleaned_traffic_data.csv",
                    mime="text/csv"
                )

    except Exception as e:
        st.error(f"Could not read the file: {e}")

else:
    st.info("Upload a CSV file above to begin.")
