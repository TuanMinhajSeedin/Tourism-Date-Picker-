import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_toggle import st_toggle_switch
from login import login,logout


st.set_page_config(
    page_title="RedRock Data Entry",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    div.stButton > button {
        background-color: #4CAF50; /* Green */
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()  # Call the login function

else:
    col1, col2 = st.columns((0.3, 0.7))

    guest_rooms = {
        'Red Rock Guest': [f'Room {no}' for no in range(100, 114) if not no in (106, 112)],
        'Lake View': ['Room 106', 'Room 112'],
        'Red Rock Home Stay': ['Full House']
    }

    data = {
        'Date': ['2025-01-01', '2025-01-01', '2025-01-03'],
        'Guest': ['Red Rock Guest', 'Lake View', 'Red Rock Home Stay'],
        'Rooms': ['Room 100', 'Room 106', 'Full House']
    }


    try:
        df = pd.read_csv('guest_records.csv')
    except FileNotFoundError:
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date']).dt.date # Ensure Date is datetime.date type


    with col1:
        delete_record = st_toggle_switch(
        label="Delete Record",
        key="delete_toggle",
        default_value=False,
        label_after=True)

    col1, col2 = st.columns((0.3, 0.7))
    with col1:
        
        user = st.session_state['user']
        new_date = st.date_input("Select a pickup date:", value=datetime.now().date())
        
        if user != 'dinesh':
            new_guest = st.selectbox("Enter Guest Name", options=['Red Rock Guest', 'Lake View', 'Red Rock Home Stay'])
        else:
            new_guest = 'Red Rock Guest'
            
        # available_rooms = []
        # for guest in new_guest:
        #     available_rooms.extend(guest_rooms.get(guest, []))
        available_rooms = guest_rooms[new_guest]
        new_rooms = st.multiselect("Enter Rooms", options=available_rooms, default=['Full House'] if 'Red Rock Home Stay' in new_guest else [])


        
    def insert(df):
        with col1:
            if st.button("Add Record", key="add_record", type="primary"):
                if user == 'Select a User':
                    st.warning("Please select a valid user before submitting.")
                else:
                    if new_date and new_guest and new_rooms:
                        # Create a new record
                        new_record = pd.DataFrame({'Date': [new_date], 'Guest': new_guest, 'Rooms': [', '.join(new_rooms)], 'Booked by': [st.session_state['user']], 'Booked Time': datetime.now()})
                        
                        # Check if an exact record already exists
                        if not df[
                            (df['Date'].astype(str) == str(new_date)) & 
                            (df['Guest'] == new_guest) & 
                            (df['Rooms'] == ', '.join(new_rooms))
                        ].empty:
                            st.warning("This record already exists.")
                        
                        # Check if there is a conflict with the same date and guest having overlapping rooms
                        else:
                            existing_record = df[
                                (df['Date'].astype(str) == str(new_date)) & 
                                (df['Guest'] == new_guest)
                            ]
                            
                            if not existing_record.empty:
                                # Get existing rooms for the same date and guest
                                existing_rooms = set(', '.join(existing_record['Rooms'].values).split(', '))
                                new_rooms_set = set(new_rooms)
                                
                                # Check for overlapping rooms
                                if existing_rooms & new_rooms_set:
                                    st.warning(
                                        f"{new_guest} already Booked "
                                        f"({', '.join(existing_rooms & new_rooms_set)}) on {str(new_date)}."
                                    )
                                else:
                                    # Append the new record if no conflict
                                    df = pd.concat([df, new_record], ignore_index=True)
                                    df = df.drop_duplicates(subset=['Date', 'Guest', 'Rooms'], keep='first').reset_index(drop=True)
                                    # df['Booked by'] = user
                                    df.to_csv('guest_records.csv', index=False)
                                    st.success("Record added successfully!")
                            else:
                                # Append the new record if no conflict
                                df = pd.concat([df, new_record], ignore_index=True)
                                df = df.drop_duplicates(subset=['Date', 'Guest', 'Rooms'], keep='first').reset_index(drop=True)
                                df.to_csv('guest_records.csv', index=False)
                                st.success("Record added successfully!")
                    else:
                        st.warning("Please fill in all fields before adding a record.")

        # Display the updated DataFrame
        with col2:
            if user != 'dinesh':
                st.dataframe(df.fillna("").set_index('Date'), width=900)
            else:
                st.dataframe(df[df['Booked by']=='dinesh'].fillna("").set_index('Date'), width=900)
                
                


    def delete(df):
        
        matching_rows = df[
            (df['Date'] == str(new_date)) & 
            (df['Guest'] == (new_guest))
        ]
        with col2:
            st.dataframe(matching_rows.set_index('Date'),width=800)
        
        if not matching_rows.empty:
            
            delete_confirm = st.button("Delete Selected Record")
            
            if delete_confirm:
                df = df.drop(matching_rows.index)
                df = df.reset_index(drop=True)  
                
                df.to_csv('guest_records.csv', index=False)
                st.success(f"Record deleted successfully! ")
                
        else:
            st.warning(f"No matching records found for {new_date} and {new_guest}.")



    if delete_record:   
        delete(df)
    else:
        insert(df)


