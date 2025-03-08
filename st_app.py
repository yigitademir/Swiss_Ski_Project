import numpy as np
import pandas as pd
import streamlit as st
import yaml
import json
import math

class YamlManager:
    def __init__(self, file_path):
        """Initialize with a path to the YAML config file."""
        self.file_path = file_path
        self.data = self.load_yaml()  # Load data right away
    
    def load_yaml(self):
        """Load the YAML file and return its data as a dictionary."""
        with open(self.file_path, "r") as config_file:
            return yaml.safe_load(config_file)
        
    def update_yaml(self, option, new_option):
        """
        Update the YAML file with a new option under the specified key.
        Also ensures 'Other' is always at the end of the list.
        """
        if new_option:
            data = self.load_yaml()

            # Get the options except "Other"
            other_option = "Other"
            options = [opt for opt in data[option] if opt != other_option]

            # Add new option to the list if not already present
            if new_option not in options:
                options.append(new_option)

            # Put "Other" back at the end
            options.append(other_option)
            data[option] = options

            # Write updated data to the YAML file
            with open(self.file_path, "w") as config_file:
                yaml.safe_dump(data, config_file, default_flow_style=False)
            
            # Update the in-memory data so it stays in sync
            self.data = data

class SwissSkiApp:
    def __init__(self, config_path: str, app_name: str):
        """
        Initialize the Swiss Ski App with a path to a config file and an app name.
        """
        self.app_name = app_name
        self.config_manager = YamlManager(config_path)
        self.config_data = self.config_manager.data 

    def run(self):
        """
        Main method that orchestrates the entire Streamlit app.
        """
        st.set_page_config(page_title=self.app_name)
        st.title(self.app_name)

        # Render each section of the app
        self.show_personal_data()
        self.show_test_conditions()
        self.show_protocol()
        self.upload_files()

    def show_personal_data(self):
        """
        Render the 'Personal Data' section of the app (name, BMI calc, etc.).
        """
        st.subheader("Personal Data")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Surname")
        with col2:
            st.text_input("First name")
        with col3:
            st.text_input("Date of Birth")

        col4, col5, col6 = st.columns(3)
        with col4:
            height = st.text_input("Height (cm)", value="")
        with col5:
            weight = st.text_input("Weight (kg)", value="")
        with col6:
            if height and weight:
                try:
                    h_val = float(height)
                    w_val = float(weight)
                    bmi = w_val / ((h_val / 100) ** 2)
                    st.metric(label="BMI", value=f"{bmi:.2f}")
                except ValueError:
                    st.text("Please enter valid numeric values.")

        col7, col8 = st.columns(2)
        with col7:
            st.text_input("Type of sport")
        with col8:
            st.text_input("Squad")

        col9, col10 = st.columns(2)
        with col9:
            st.selectbox(
                "Motivation",
                range(
                    self.config_data['state_of_mind']['start'],
                    self.config_data['state_of_mind']['end'] + 1
                )
            )
        with col10:
            st.selectbox(
                "State of Mind",
                range(
                    self.config_data['training']['start'],
                    self.config_data['training']['end'] + 1
                )
            )

        col11, col12 = st.columns(2)
        with col11:
            st.text_input("Training")
        with col12:
            st.text_input("Comments")

    
    def show_technical_data(self):
        """
        Render the 'Technical Data' section (Test By, Gear Check, etc.).
        """
        st.subheader("Technical Data")

    def show_test_conditions(self):
        """
        Render the 'Test Conditions' section (Test By, Gear Check, etc.).
        """
        st.subheader("Test Conditions")

        # Test By
        test_by_options = self.config_data.get('test_by', [])
        test_selected_option = st.selectbox("Test By:", test_by_options)
        if test_selected_option == "Other":
            test_manual_entry = st.text_input("Enter Person")
            if st.button("Save"):
                if test_manual_entry:
                    # Update the config (YAML)
                    self.config_manager.update_yaml("test_by", test_manual_entry)
                    st.success(f"'{test_manual_entry}' saved!")
                else:
                    st.warning("Please enter a name")

        # Other dropdowns
        st.selectbox("Test Conditions", self.config_data['test_conditions'])
        st.selectbox("Gear Check", self.config_data['gear_check'])
        st.selectbox("SRM Zero-Offset", self.config_data['srm_offset'])

    def show_protocol(self):
        """
        Render the 'Protocol' section (Protocol, Lactate Analyser, etc.).
        """
        st.subheader("Protocol")

        #Protocol
        protocol_options = self.config_data.get("protocol", [])
        protocol_selected_option = st.selectbox("Protocol:", protocol_options)
        if protocol_selected_option == "Other":
            protocol_manual_entry = st.text_input("Enter Protocol")
            if st.button("Save"):
                if protocol_manual_entry:
                    # Update the config (YAML) with this new name
                    self.config_manager.update_yaml("protocol", protocol_manual_entry)
                    st.success(f"'{protocol_manual_entry}' saved!")
                else:
                    st.warning("Please enter a protocol name")
        
        
        
        st.selectbox("Lactate Analyser", self.config_data['lactate_analyser'])
        st.selectbox("Sampling Point", self.config_data['sampling_point'])
        st.selectbox("Ergometer", self.config_data['ergometer'])

    def upload_files(self):

        st.subheader("Endurance Test Files")

        # HR Data
        heart_rate_file = st.file_uploader("HR Data to upload", type="csv")

        if heart_rate_file is not None:
            # read the csv file into a pandas DataFrame
            df_hr = pd.read_csv(heart_rate_file, header=None)
            # Access HR measurements
            hr_data = df_hr.iloc[20:, 0]  # Heart rate values starting from row 21
            hr_data_relevant = hr_data[440:]  # Skip first 7 minutes - 420 sec
            hr_data_relevant_list = hr_data_relevant.tolist()  # converting series to list
            hr_data_relevant_list = [float(value.strip(';')) for value in hr_data_relevant_list]  # removing ;
            print(hr_data_relevant_list)

            duration = len(hr_data_relevant_list)  # duration of the measurements
            window_size = 30  # Last 30 seconds of each 3-min interval
            interval_size = 180  # length of 3-min interval
            no_of_levels = math.ceil(duration / interval_size)  # rounding up
            hr_test_values = []

            for i in range(0, no_of_levels):
                # Calculate the start and end index for the last 30 sec of the current 3-min interval
                start_index = (i + 1) * interval_size - window_size
                end_index = (i + 1) * interval_size

                # Ensure that the slice doesn't go beyond the length of the data
                if end_index > len(hr_data_relevant_list):
                    end_index = len(hr_data_relevant_list)
                    start_index = max(0, end_index - window_size)

                last_30_sec = hr_data[start_index:end_index]
                print(last_30_sec)
                last_30_sec_list = last_30_sec.tolist()  # converting to list
                last_30_sec_list = [float(value.strip(';')) for value in last_30_sec_list]  # removing ;
                avg_hr = np.mean(last_30_sec_list)
                hr_test_values.append({
                    "Level": i + 1,
                    "Average HR": round(avg_hr, 2),
                })

            hr_data_json = json.dumps(hr_test_values)
            st.write(hr_data_json)

        # Spiro Data
        spiro_file = st.file_uploader("Spiro Data to upload", type="xls")




# Typical pattern to run the Streamlit app
if __name__ == "__main__":
    app = SwissSkiApp("config.yml", "Swiss Ski Endurance App")
    app.run()