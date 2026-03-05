#!/bin/sh

echo "Waiting for database..."
sleep 5

echo "Running table creation..."
python db/create_tables.py

echo "Running data insertion..."
python db/insert_data.py

echo "Starting Streamlit..."
streamlit run dashboard/Dashboard.py