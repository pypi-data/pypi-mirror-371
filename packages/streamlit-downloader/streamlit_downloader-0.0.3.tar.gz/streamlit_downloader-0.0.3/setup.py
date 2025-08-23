from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-downloader",
    version="0.0.3",
    author="Gaspard Merten",
    author_email="gaspard@norse.be",
    description="Streamlit component to download a file programmatically, without user input.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/streamlit-downloader", # Added a placeholder URL
    packages=setuptools.find_packages(),
    include_package_data=True,
    # This is the key change to include the build directory
    package_data={
        "streamlit_downloader": ["template/build/**"]
    },
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.48.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    }
)