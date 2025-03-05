import streamlit as st
import yaml

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


# Typical pattern to run the Streamlit app
if __name__ == "__main__":
    app = SwissSkiApp("config.yml", "Swiss Ski Endurance App")
    app.run()