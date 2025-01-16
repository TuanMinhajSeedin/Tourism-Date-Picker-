import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_toggle import st_toggle_switch
from login import login,logout

st.set_page_config(
    page_title="RedRock",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main_page():
    guest_rooms = {
        'Red Rock Guest': [f'Room {no}' for no in range(101, 114) if not no in (106, 112)],
        'Lake View': ['Room 106', 'Room 107','Room 108','Room 109'],
        'Red Rock Home Stay': ['Full House']}
    all_rooms = [room for rooms in guest_rooms.values() for room in rooms]

    df = pd.read_csv('guest_records.csv')
    search_date = st.date_input("Search date:", value=datetime.now().date())
    matching_rows = df[
        (df['Date'] == str(search_date)) 
    ].drop(columns=['Booked Time','Booked by'],axis=1)

    booked_rooms = matching_rows.Rooms.tolist()
    booked_rooms = [room.strip() for sublist in booked_rooms for room in sublist.split(',')]

    non_intersection = list(set(all_rooms) ^ set(booked_rooms))

    available_data = []
    for guest, rooms in guest_rooms.items():
        available_rooms = list(set(rooms) & set(non_intersection))  # Get available rooms for each guest and ensure uniqueness
        if not available_rooms:  # Check if the list is empty
            continue  # Skip this iteration if no available rooms
        if len(available_rooms) == len(rooms) and guest == 'Red Rock Guest':  # If all rooms are available, set 'All'
            available_rooms = ['All']  # All rooms available for this guest
        else:
            available_rooms = sorted(available_rooms)  # Otherwise, show the available rooms in sorted order
        
        available_data.append({
            'Date': search_date,
            'Guest': guest,
            'Available Rooms': ', '.join(available_rooms)  # Join rooms into a string for display
    })


    available_df = pd.DataFrame(available_data).set_index('Date')
    st.markdown("""
        <style>
        .streamlit-expanderHeader {
            font-size: 20px;
        }
        .stDataFrame td, .stDataFrame th {
            text-align: center;
        }
        .stDataFrame .column-Available_Rooms {
            max-width: 900px;
            word-wrap: break-word;
        }
        </style>
    """, unsafe_allow_html=True)

    # st.dataframe(available_df, width=2000)
    user = st.session_state['user']
    
    if user != 'dinesh':
        st.dataframe(available_df.fillna(""), width=2000)
    else:
        st.dataframe(available_df[available_df['Guest']=='Red Rock Guest'].fillna(""), width=2000)
    


# Check if the user is logged in
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    main_page()
else:
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()  # Call the login function
