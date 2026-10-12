# Student Details & Performance Dashboard

An interactive Streamlit dashboard for exploring student information and academic performance. Sidebar filters update all charts, summary metrics, and the displayed data table.

## Dataset
Place `student_dropout_behavior_dataset.csv` in the same directory as `app.py`. The supplied dataset contains student ID, name, age, gender, quiz/exam marks, previous GPA, assignment data, and attendance data. It does **not** include father name, mother name, phone number, home address, or branch.

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```

## Upload to GitHub
Create a new GitHub repository and upload `app.py`, `requirements.txt`, `README.md`, and the CSV dataset. Do not upload real personal information such as private phone numbers or home addresses.

## Deploy on Streamlit Community Cloud
1. Push the files to a GitHub repository.
2. Open https://share.streamlit.io/
3. Sign in with GitHub and choose **Create app**.
4. Select the repository, branch, and `app.py`.
5. Deploy the app.
