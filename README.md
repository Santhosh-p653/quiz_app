# 🎭 Who Is It? — Celebrity Quiz

A Dockerized Streamlit quiz app. Shows famous people images, accepts text answers with fuzzy matching.

## Structure

    quiz_app/
    ├── app.py
    ├── generate_dataset.py
    ├── requirements.txt
    ├── Dockerfile
    ├── README.md
    ├── dataset/
    │   ├── answers.json
    │   └── images/
    └── temp/

## Local Setup

    pip install -r requirements.txt
    python generate_dataset.py
    streamlit run app.py

Open http://localhost:8501

## Docker

    # Build
    docker build -t quiz-app .

    # Generate dataset on host first
    python generate_dataset.py

    # Run with mounted dataset
    docker run -p 8501:8501 -v "$(pwd)/dataset:/app/dataset" quiz-app

    # Or generate inside container, then run
    docker run -it --rm -v "$(pwd)/dataset:/app/dataset" \
      --entrypoint python quiz-app generate_dataset.py

    docker run -p 8501:8501 -v "$(pwd)/dataset:/app/dataset" quiz-app

## Notes

- Fuzzy threshold: 70 (change `FUZZY_THRESHOLD` in app.py)
- Add celebrities: edit `CELEBRITIES` list in generate_dataset.py, re-run it
- Dataset volume must be mounted so the container can read images
