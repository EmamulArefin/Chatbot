#!/bin/bash

# Heroku setup script
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml

# Download Bengali language data
wget -O /app/.apt/usr/share/tesseract-ocr/4.00/tessdata/ben.traineddata \
    https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata
