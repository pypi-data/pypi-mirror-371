# Streamlit Downloader

A Streamlit component that triggers an automatic download of one or more files without requiring user interaction.

## Installation

```bash
pip install streamlit-downloader
```
# Usage

Use the downloader function to initiate a download. The component will automatically trigger the browser's download dialog when the page loads or when the component is rendered.

### Downloading a Single File

```python
import streamlit as st
from streamlit_downloader import downloader

# The `downloader` function returns True when the download is complete.
st.subheader("Download a single file")

data_to_download = b'Hello, this is the content of the file.'
filename = "my_text_file.txt"
content_type = "text/plain"

if st.button("Start Download"):
    download_complete = downloader(
        data=data_to_download,
        filename=filename,
        content_type=content_type
    )

    if download_complete:
        st.success(f"File '{filename}' has been downloaded!")
```

### Downloading Multiple Files

The downloader component can handle multiple files by being called multiple times.

```python
import streamlit as st
from streamlit_downloader import downloader

st.subheader("Download multiple files")

# File 1 details
data_file1 = b"This is the first file."
filename_file1 = "file1.txt"
content_type_file1 = "text/plain"

# File 2 details
data_file2 = b"This is the second file."
filename_file2 = "file2.csv"
content_type_file2 = "text/csv"

if st.button("Download Both Files"):
    # The component must be called for each file you want to download.
    download_complete_1 = downloader(
        data=data_file1,
        filename=filename_file1,
        content_type=content_type_file1,
    )
    
    download_complete_2 = downloader(
        data=data_file2,
        filename=filename_file2,
        content_type=content_type_file2,
    )

    if download_complete_1 and download_complete_2:
        st.success("All files have been downloaded!")
```


### Parameters

The `downloader` function accepts the following parameters:

* `data`: The raw data of the file to be downloaded. This can be a string, bytes, or a similar data type.
* `filename`: The name the downloaded file will have.
* `content_type`: The MIME type of the file (e.g., `text/csv`, `application/pdf`).
* `key`: (Optional) A unique key for the component, required when you have multiple downloaders on the same page.

---

## How It Works

The component leverages the browser's ability to trigger downloads using a hidden link element. When the Streamlit component is rendered, it uses JavaScript to create a `Blob` from the data, creates a temporary `<a>` element, sets its `href` to a URL created from the Blob, and simulates a click to initiate the download. The component is visually hidden to provide a seamless user experience.

---

## Development

To run the example app and test changes:

1.  Navigate to the `streamlit_downloader` directory.
2.  Run `streamlit run example.py`.