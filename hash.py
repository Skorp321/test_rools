import streamlit_authenticator as stauth

hashed_password = stauth.Hasher(['user123']).generate()
print(hashed_password)