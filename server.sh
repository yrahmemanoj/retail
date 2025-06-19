 #!/bin/bash
echo "Running EDA analysis..."
python3 eda/run.py
if [ $? -ne 0 ]; then
    echo "EDA analysis failed. Exiting."
    exit 1
fi
echo "EDA analysis completed successfully!"
echo "Starting Python HTTP Server..."
open http://localhost:8000/dashboard/ 2>/dev/null || xdg-open http://localhost:8000/dashboard/
python3 -m http.server 8000