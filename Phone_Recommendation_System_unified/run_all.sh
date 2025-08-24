#!/bin/bash
# Start all module Flask apps in background. Run from project root (Phone Recommendation System).
echo "Starting modules..."
(cd phonefinder && python app.py) &
(cd salesprediction && python app.py) &
(cd buyandsell && python app.py) &
(cd comparephone && python app.py) &
(cd upcomingphone && python app.py) &
(cd reviews && python app.py) &
echo "All modules started. Open main/index.html or visit the URLs:"
echo "Phone Finder: http://127.0.0.1:5000/"
echo "Sales: http://127.0.0.1:5001/"
echo "Buy & Sell: http://127.0.0.1:5002/"
echo "Compare: http://127.0.0.1:5003/"
echo "Upcoming: http://127.0.0.1:5004/"
echo "Reviews: http://127.0.0.1:5005/"
