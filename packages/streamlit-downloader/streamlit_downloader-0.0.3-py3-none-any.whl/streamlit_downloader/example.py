import time

import streamlit as st
from streamlit_downloader import downloader

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run downloader/example.py`

st.subheader("Download a file")

for i in range(10):
    time.sleep(1)
    # Could be a csv, or really anything.
    complete = downloader(
        (f'Hello world + {i}').encode('utf-8'),
        filename=F"hey{i}.txt",
        content_type="text/plain",
    )
