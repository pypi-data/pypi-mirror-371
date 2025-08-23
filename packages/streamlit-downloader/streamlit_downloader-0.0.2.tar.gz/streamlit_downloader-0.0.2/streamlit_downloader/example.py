import streamlit as st
from streamlit_downloader import downloader

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run downloader/example.py`

st.subheader("Download a file")

# Could be a csv, or really anything.
complete = downloader(
    b'Hello world',
    filename="hey.txt",
    content_type="text/plain",
)
if complete:
    st.write(complete)

# Could be a csv, or really anything.
complete2 = downloader(
    b'Hello world2',
    filename="hey.txt",
    content_type="text/plain",
)
if complete2:
    st.write(complete2)
