<p align="center">
  <img src="/img/cover.jpg" />
</p>

# I Made a Bounce Checker

## About

In today's digital environment, ensuring the integrity and deliverability of emails is paramount. Recognizing a need for an efficient method to scrutinize email addresses for potential bounces, I developed a sophisticated solution. This tool does not send any emails; rather, it meticulously examines lists, identifying key parameters that might influence bounce rates.

The system meticulously verifies email syntax, cross-references Mail Exchange (MX) records, and conducts several other vital checks. At its core, the solution is implemented as a Python script. However, I am in the process of augmenting its capabilities with an intuitive front-end interface to enhance user experience.

## Usage

1. Clone the repo:
```
git clone https://github.com/pyslarash/IMadeBounceChecker.git
```
2. Go to the "backend" directory
```
cd backend
```
3. Create a directory called **csv** inside the working directory and place your CSV (comma delimited) file there if needed. Name it **emails.csv** for ease of use.
4. Make sure that you have **pipenv** installed
```
pip install pipenv
```
5 Create a new virtual environment
```
pipenv shell
```
6. Install all of the dependencies
```
pipenv install
```
7. Run the main file (it will launch the API)
```
python app.py
````
8. If you need to go through a full email list, open **dataset.py** and change these lines if needed:
```
# Importing the file
data = "csv/emails.csv"

# Importing the name of the email column
col_name = "Email"
```
The first line is where you placed your CSV file and the second line is the name of your **email** column.
9. Run **dataset.py** while running **app.py** and follow prompts
```
python dataset.py
```
10. Get your file

## Technologies Used
<img height=50 src="https://user-images.githubusercontent.com/25181517/183423507-c056a6f9-1ba8-4312-a350-19bcbc5a8697.png" /><img height=50 src="https://user-images.githubusercontent.com/25181517/183423775-2276e25d-d43d-4e58-890b-edbc88e915f7.png" /></br>
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
