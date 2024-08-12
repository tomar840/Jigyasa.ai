# Jigyasa (जिज्ञासा)
This repository contains ollama based logic for open source AI-powered search engine.

## Table of Contents

- [Installation](#Installation)
- [Usage](#Usage)
- [To-Do](#To-Do)
- [Contributing](#contributing)

## Installation
To use this implementation, you will need to have Python >= 3.10 installed on your system, as well as the following Python libraries:

```
git clone https://github.com/tomar840/Jigyasa.git
cd Jigyasa.ai
pip install -r requirements.txt
```

To install ollama, follow instructions from this [repo](https://github.com/ollama/ollama).

## Usage
You can start the ollama inference server using instructions from this [repo](https://github.com/ollama/ollama).

In a standalone terminal, run ollama inference server for your model
```
ollama run llama3:8b-instruct-q8_0
```

Run the below command to run the streamlit app
```
streamlit run app.py
```
then go to `http://localhost:8501/`

## TODO
- Restructure the code into modules

## Contributing
Contributions to improve the project are welcome. Please follow these steps to contribute:

Fork the repository.\
Create a new branch for each feature or improvement.\
Submit a pull request with a comprehensive description of changes.