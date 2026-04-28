# ⚡ GridSense: Smart Grid Energy AI

Hello! This is my capstone project. I built **GridSense** to help manage smart grids using AI. It basically looks at how much energy we are using and helps decide the best way to supply it while keeping costs low and the environment clean.

## 🚀 What does this project do?
In simple words, it does three main things:
1.  **Data Cleaning:** It takes messy energy data (like Excel files) and organizes it. It also calculates how much CO2 is being produced by different energy sources like Coal or Gas.
2.  **AI Forecasting:** I used a model called **Prophet** to look at past energy trends and predict what the demand will be in the future.
3.  **Smart Optimization:** It uses math (Linear Programming) to figure out the perfect "mix." For example, if we have a lot of solar power available, the system will prioritize that over expensive and dirty fossil fuels.

## 🛠️ How I built it
* **Language:** Python 🐍
* **Dashboard:** Streamlit (to make it look like a real website)
* **AI Model:** Meta Prophet (for time-series forecasting)
* **Optimization:** PuLP (to solve the energy distribution math)
* **Charts:** Plotly (for the interactive graphs)

## 📁 What's in this folder?
* `app.py`: The main code for the website.
* `test.py`: A script I wrote to verify that all the math and AI logic is working 100% correctly.
* `requirements.txt`: A list of libraries needed to run this project.
* `packages.txt`: System settings for the AI model to work on the cloud.
* `*.xlsx`: Sample energy datasets I used for testing (specifically for Maharashtra/India).

## 🚦 How to run it
If you want to run this on your own computer:
1.  Install the requirements: `pip install -r requirements.txt`
2.  Run the app: `streamlit run app.py`
3.  To check if the logic is correct, run the tests: `python -m pytest test.py`
