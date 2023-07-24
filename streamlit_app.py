import streamlit as st
from utils import NASA_APIConnection
from datetime import date as date_function
from dotenv import load_dotenv
import os

load_dotenv()
# Assuming you have already obtained your NASA API key
NASA_API_KEY = os.getenv('NASA_API_KEY')

# Create the NASA API connection
nasa_conn = st.experimental_connection("nasa", type=NASA_APIConnection, api_key=NASA_API_KEY)

# Streamlit app
def main():
    st.title("🚀NASA API Connection with Streamlit")
    st.markdown(
    """
    This app is an official submission to the Streamlit Connections Hackathon.
     - [Hackathon Link](https://discuss.streamlit.io/t/connections-hackathon/47574)
     - [GitHub Repo](https://github.com/pramitbhatia25/NASA_OpenAPI-Connector)
     - [NASA API's](https://api.nasa.gov/)
    """)


    st.sidebar.markdown(
        """
🚀 Explore Space with NASA APIs! 🌌

Welcome to our NASA API Streamlit connector! Discover awe-inspiring space imagery, delve into space weather events, browse Mars rover photos, track near-Earth objects, and explore a vast collection of exoplanet data, all at your fingertips!

🛰️ What NASA APIs do we support? 🌠

Astronomy Picture of the Day (APOD): Witness captivating daily images and learn from professional astronomers' insights about the universe's wonders.

Mars Rover Photos: Explore the Red Planet through the lens of NASA's rovers and immerse yourself in the Martian landscape.

Near-Earth Object Web Service (NEOWS): Stay informed about close-approaching asteroids and comets, safeguarding our home planet.

DONKI: Space Weather Database: Discover various space weather events and related information, from solar flares to geomagnetic storms.

Exoplanet Archive: Dive into the fascinating world of exoplanets, distant planets beyond our solar system, with a wealth of data to explore.

🌠 What our app offers? 🚀

Our app provides a user-friendly interface to interact with these powerful NASA APIs. With just a few clicks, you can access real-time and historical space data, customize queries, and visualize intriguing celestial phenomena.

🌌 How to use our app? 🌟

Simply select your preferred NASA API from the menu and follow the intuitive instructions. You can input dates, filter conditions, and choose data tables to retrieve the most relevant and captivating information.

Join us on this cosmic adventure, where the wonders of space await! 🚀✨        """
    )
    # Sidebar menu to select NASA API
    selected_api = st.selectbox("Select a NASA API", ["APOD", "Near-Earth Object Web Service (NEOWS)", "Mars Rover Photos", "DONKI: Space Weather Database", "Exoplanet"])

    if selected_api == "APOD":
        today = date_function.today()
        d1 = today.strftime("%b %d, %Y")


        st.subheader("Astronomy Picture of the Day (APOD)")
        st.markdown(
            """
            **Astronomy Picture of the Day (APOD)**
            The Astronomy Picture of the Day (APOD) is a website provided by NASA that features
            a new and different image or photograph of the universe every day, along with a brief
            explanation written by a professional astronomer.
            """
        )

        st.write('**Date must be between Jun 16, 1995 and {}.**'.format(d1))
        date = st.text_input("Enter a date in the format 'YYYY-MM-DD' or 'latest' for the latest APOD:")
 
        if st.button("Get APOD"):
            if date:
                apod_data = nasa_conn.query_apod(date)

                if apod_data is not None:
                    st.write(f"Date: {apod_data['date'].values[0]}")
                    st.write(f"Title: {apod_data['title'].values[0]}")
                    st.image(apod_data['url'].values[0], caption=apod_data['title'].values[0])
                    st.write(f"Explanation: {apod_data['explanation'].values[0]}")
                else:
                    st.error("Failed to fetch APOD data")

    elif selected_api == "Mars Rover Photos":
        st.subheader("Mars Rover Photos")
        st.markdown(
            """
            **Mars Rover Photos**
            The Mars Rover Photos API allows you to explore the photos taken by NASA's rovers on Mars.
            You can select a rover (Curiosity, Opportunity, or Spirit) and enter a Martian sol (a Martian day)
            to view the corresponding photos captured by the selected rover on that sol.

            Select a rover from the dropdown menu, enter a Martian sol, and click the 'Get Photos' button
            to view the images taken on the specified sol.

            Only the top 100 photos are retrieved.
            """
        )
        rover_name = st.selectbox("Select a rover", ["Curiosity", "Opportunity", "Spirit"])
        sol = st.text_input("Enter a Martian sol (e.g., 1000):")

        if st.button("Get Photos"):
            if sol:
                mars_rover_photos = nasa_conn.query_mars_rover_photos(rover_name, sol)

                if mars_rover_photos is not None:
                    st.write(f"Rover: {rover_name}")
                    st.write(f"Number of Photos: 100")

                    st.write(mars_rover_photos)
                    df = mars_rover_photos
                    num_images = len(df)
                    rows = (num_images // 3) + 1

                    for i in range(rows):
                        cols = min(3, num_images - i * 3)

                        for j in range(cols):
                            idx = i * 3 + j
                            img_url = df.iloc[idx]["img_src"]
                            st.image(img_url, caption=f"Earth Date: {df.iloc[idx]['earth_date']}", width=300)

                else:
                    st.error("Failed to fetch Mars rover photos")
    elif selected_api == "Near-Earth Object Web Service (NEOWS)":

        st.subheader("Near-Earth Object Web Service (NEOWS)")
        st.markdown(
            """
            **Near-Earth Object Web Service (NEOWS)**
            The Near-Earth Object Web Service (NEOWS) API provides information about near-Earth asteroids and comets.
            You can use this API to get a list of close-approaching objects for a given date range or lookup specific
            objects by their IDs.

            Enter a date range (start_date and end_date) and click the 'Get Close-Approaching Objects' button to view
            a list of near-Earth objects for the specified date range.
            """
        )
        st.write('**Date range must be within 7 days.**')
        st.write('Eg. startDate=2022-07-01, endDate= 2022-07-08 is valid.')
        st.write('Eg. startDate=2022-07-01, endDate= 2022-07-09 is invalid.')
        start_date = st.text_input("Enter the start date in the format 'YYYY-MM-DD':")
        end_date = st.text_input("Enter the end date in the format 'YYYY-MM-DD':")

        if st.button("Get Close-Approaching Objects"):
            if start_date and end_date:
                neows_data = nasa_conn.query_neows(start_date, end_date)

                if neows_data is not None:
                    st.write(f"Start Date: {start_date}")
                    st.write(f"End Date: {end_date}")

                    st.write(neows_data)
                else:
                    st.error("Failed to fetch NEOWS data")                    
    elif selected_api == "DONKI: Space Weather Database":
        st.subheader("NASA DONKI Database Query")
        st.markdown(
            """
            **DONKI: Space Weather Database**
            This app lets you query the NASA DONKI (Space Weather Database Of Notifications, Knowledge, Information) 
            to find various space weather events and related information. You can search for events based on different 
            parameters. Happy space weather exploration!
            """
        )

        st.write("**Please allow the date range gap to be atleast 30 days.**")
        st.write("**Please limit the date range gap to be a maximum of 60 days for fastest API CALL Times.**")

        # Event types supported by DONKI
        donki_event_types = [
            "Coronal Mass Ejection (CME)",
            "Geomagnetic Storm (GST)",
            "Solar Flare (FLR)",
            "Solar Energetic Particle (SEP)",
            "Magnetopause Crossing (MPC)",
            "Radiation Belt Enhancement (RBE)",
            "High-Speed Stream (HSS)",
            "Notifications"
        ]

        # Sidebar menu to select DONKI event type
        selected_donki_event = st.selectbox("Select a DONKI Event Type", donki_event_types)

        if selected_donki_event == "Coronal Mass Ejection (CME)":
            start_date = st.text_input("Enter the start date in the format 'YYYY-MM-DD':")
            end_date = st.text_input("Enter the end date in the format 'YYYY-MM-DD':")

            if st.button("Get CME Data"):
                if start_date and end_date:
                    cme_data = nasa_conn.query_donki(start_date, end_date, type="CME")
                    st.write(cme_data)

        elif selected_donki_event == "Geomagnetic Storm (GST)":
            start_date = st.text_input("Enter the start date in the format 'YYYY-MM-DD':")
            end_date = st.text_input("Enter the end date in the format 'YYYY-MM-DD':")

            if st.button("Get GST Data"):
                if start_date and end_date:
                    gst_data = nasa_conn.query_donki(start_date, end_date, type="GST")
                    st.write(gst_data)

        elif selected_donki_event == "Solar Flare (FLR)":
            start_date = st.text_input("Enter the start date in the format 'YYYY-MM-DD':")
            end_date = st.text_input("Enter the end date in the format 'YYYY-MM-DD':")

            if st.button("Get FLR Data"):
                if start_date and end_date:
                    flr_data = nasa_conn.query_donki(start_date, end_date, type="FLR")
                    st.write(flr_data)

        elif selected_donki_event == "Solar Energetic Particle (SEP)":
            start_date = st.text_input("Enter the start date in the format 'YYYY-MM-DD':")
            end_date = st.text_input("Enter the end date in the format 'YYYY-MM-DD':")

            if st.button("Get SEP Data"):
                if start_date and end_date:
                    sep_data = nasa_conn.query_donki(start_date, end_date, type="SEP")
                    st.write(sep_data)

        elif selected_donki_event == "Magnetopause Crossing (MPC)":
            start_date = st.text_input("Enter the start date in the format 'YYYY-MM-DD':")
            end_date = st.text_input("Enter the end date in the format 'YYYY-MM-DD':")

            if st.button("Get MPC Data"):
                if start_date and end_date:
                    mpc_data = nasa_conn.query_donki(start_date, end_date, type="MPC")
                    st.write(mpc_data)

        elif selected_donki_event == "Radiation Belt Enhancement (RBE)":
            start_date = st.text_input("Enter the start date in the format 'YYYY-MM-DD':")
            end_date = st.text_input("Enter the end date in the format 'YYYY-MM-DD':")

            if st.button("Get RBE Data"):
                if start_date and end_date:
                    rbe_data = nasa_conn.query_donki(start_date, end_date, type="RBE")
                    st.write(rbe_data)

        elif selected_donki_event == "High-Speed Stream (HSS)":
            start_date = st.text_input("Enter the start date in the format 'YYYY-MM-DD':")
            end_date = st.text_input("Enter the end date in the format 'YYYY-MM-DD':")

            if st.button("Get HSS Data"):
                if start_date and end_date:
                    hss_data = nasa_conn.query_donki(start_date, end_date, type="HSS")
                    st.write(hss_data)

        elif selected_donki_event == "Notifications":
            start_date = st.text_input("Enter the start date in the format 'YYYY-MM-DD':")
            end_date = st.text_input("Enter the end date in the format 'YYYY-MM-DD':")

            if st.button("Get Notifications Data"):
                if start_date and end_date:
                    not_data = nasa_conn.query_donki(start_date, end_date, type="notifications")
                    st.write(not_data)

    elif selected_api == "Exoplanet":
        st.subheader("NASA Exoplanet Archive Query")
        st.markdown(
            """
            **Exoplanet Archive**
            The Exoplanet Archive API allows programmatic access to NASA's Exoplanet Archive database.
            Enter the query to retrieve data from the database of all confirmed planets (and hosts) in the archive with parameters derived from a single, published reference that are designated as the archive's default parameter set.
            Happy planet hunting!
            """
        )

        # Examples to add custom queries for Exoplanet Archive
        st.write("Example 1: Query the Kepler Objects of Interest (KOI) Cumulative Table for exoplanets with a Kepler disposition of 'CANDIDATE', an orbital period (koi_period) more than 300 days, and a planet radius (koi_prad) less than 2.")
        exo_where_example1 = "koi_disposition like 'CANDIDATE' and koi_period > 300 and koi_prad < 2"
        st.write("Query:")
        st.write("select *  from cumulative where koi_disposition like 'CANDIDATE' and koi_period > 300 and koi_prad < 2")
        if st.button("Get Exoplanet Data - Example 1"):
            exo_data_example1 = nasa_conn.query_exoplanet_data(table="cumulative", where=exo_where_example1)
            st.write(exo_data_example1)

        # Custom query input fields
        st.subheader("Custom Query")
        select = st.text_input("Enter the 'select' clause to specify columns to return (optional):", value ="*")
        where = st.text_input("Enter the 'where' clause to specify filtering conditions (optional):", value ="koi_disposition like 'CANDIDATE' and koi_period > 300 and koi_prad < 2")
        order = st.text_input("Enter the 'order' clause to specify the order of rows (optional):", value ="kepid")

        if st.button("Run Query"):
            exoplanet_data = nasa_conn.query_exoplanet_data(
                table="cumulative",
                where=where,
                select=select,
                order=order,
            )

            if exoplanet_data is not None:
                st.write(exoplanet_data)
            else:
                st.error("Failed to fetch Exoplanet Archive data")

if __name__ == "__main__":
    main()
