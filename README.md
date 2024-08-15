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

In a standalone terminal, run ollama inference server for your model. We are using Llama3.1-Instruct model at the moment.
```
ollama run llama3:8b-instruct-q8_0
```

[![Watch the video](https://drive.google.com/uc?export=view&id=1zTXL4TTe_ilhKOotBBajJcPRlV9YBf5Z)](https://drive.google.com/file/d/1neo_H1jrsQXm1lnxp5kKM2oXw9kQ4set/view?usp=sharing)

Run the below commands to run the streamlit app
```
python libs/modules/route/answer.py 
streamlit run ./libs/modules/route/app.py 
```
then go to `http://localhost:8501/`

## TODO
- Tuning prompts for Llama-3.1-Instruct

## Contributing
Contributions to improve the project are welcome. Please follow these steps to contribute:

Fork the repository.\
Create a new branch for each feature or improvement.\
Submit a pull request with a comprehensive description of changes.
