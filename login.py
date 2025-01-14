
import streamlit as st

users = {
    'dinesh': 'redrock',
    'rizlan': 'redrockadminfamily',
    'sameena': 'redrockadminfamily',
    'haneefa': 'redrockadminfamily',
    'sulaiha': 'redrockadminfamily'
    
}


# Function for handling login
def login():
    # Input fields for username and password
    username = st.text_input('Username').lower()
    password = st.text_input('Password', type='password')
    
    if st.button('Login'):
        # Check if credentials are correct
        if username in users and users[username] == password:
            # Set session state to logged in
            st.session_state['logged_in'] = True
            st.session_state['user'] = username
            st.success('Logged in successfully!')
        else:
            st.error('Invalid username or password')


# Function to handle logout
def logout():
    del st.session_state['logged_in']
    del st.session_state['user']
    st.experimental_rerun()