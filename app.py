import streamlit as st
import pandas as pd
import os
import polars as pl
import re
import time
st.set_page_config(page_title="DAD conslidation Automation",
                   layout='wide')


def append_files():
     st.markdown("<h4>Append Files to Create a single master file</h4>",unsafe_allow_html=True)
     uploaded_file = st.file_uploader('Select the file you want to Append to create a single master file', accept_multiple_files=True, type=['XLSX','XLS','xls','xlsx'])

     appended_df = []
     if uploaded_file:
          for path in uploaded_file:
                try:
                    df = pl.read_excel(path,infer_schema_length=0)
                    df = df.to_pandas()
                    st.toast(f"{os.path.basename(path.name)} Read successfully!")
                    appended_df.append(df)
                
                except Exception as e:
                    st.error(f"{e} Error Raised While Opening File Path: {path}")
                
          st.toast("All Files to be appended read successfully!",icon='😍')
          if appended_df:
            master_df = pd.DataFrame(columns=appended_df[0].columns)
            for df in appended_df:
                master_df = pd.concat([master_df, df], axis=0)
              
            if master_df.shape[0]!=0:
                file_path = "./Appended Data"
                file_name = st.text_input("Provide a file name to Save the Appended files. ")
                file_name = file_path +"/" + file_name
                if file_name:
                    if st.button("Save File"):
                        try:
                            master_df.to_excel(f"{file_name}.xlsx",index=False)
                            st.toast(f'{file_name} Saved Successfully')
                            st.success("File Saved Successfully")

                        except Exception as e:
                            st.error(f"{e} Error Raised While Saving the Master File!",icon='😭')             
                elif not file_name:
                    st.error("Please Provide the File Name!!")

     


def data_consolidation_page():
    st.title('Data Consolidation and Assessment Automation')

    # Introduction to the module
    st.write("""
        Welcome to the Data Consolidation and Assessment Automation module. This feature is designed to streamline the process of data integration and analysis, enabling clients and analysts to efficiently manage their procurement data.
    """)

    # Key Features section
    st.subheader("Key Features of Data Consolidation and Assessment Automation")

    # List of key features
    st.markdown("""
        - **Multiple File Upload**: Clients and analysts can upload multiple files, including a main file and several mapping files, allowing for comprehensive data integration.
        - **Master File Creation**: Using automation scripts, the module consolidates data from various sources into a single master file. This master file serves as the foundation for further analysis.
        - **Single Master File Usage**: If a client has a single master file, it can be directly utilized for in-depth analysis across various metrics without additional processing.
        - **Appending Multiple Master Files**: In cases where multiple master files are provided, the system seamlessly appends these files to create a unified master file for analysis.
        - **Data Mapping and Enrichment**: Mapping files allow for the extraction and integration of useful fields from multiple sources, enhancing the main file with relevant data for more robust insights.
    """)

    # Analysis Overview section
    st.subheader("Data Analysis Capabilities")

    # Explanation of analysis process
    st.write("""
        The data analysis component of this module offers a range of analytical capabilities, including:
        
        - **Population Statistics**: Analyze key columns to assess data completeness and quality, ensuring critical fields are populated effectively.
        - **Outlier Detection**: For date columns, the system checks for outliers, helping identify data entry errors or unusual patterns that may require further investigation.
        - **Spend Analysis**: Examine spending patterns by identifying negative and positive expenditures, facilitating better financial oversight and strategic decision-making.
        - **Custom Metrics**: Additional analytical measures can be implemented to meet specific client needs, providing tailored insights that drive informed procurement decisions.
    """)

    # Closing paragraph
    st.write("""
        This module not only simplifies the data consolidation process but also empowers organizations to derive actionable insights from their procurement data. By leveraging automation and robust analytical capabilities, clients can optimize their procurement strategies and uncover significant opportunities for cost savings and efficiency.
    """)


def analyse_file():
    st.markdown("<h4>Provide the File DAD Analysis</h4>", unsafe_allow_html=True)
    main_file_path = st.file_uploader('Select the File to Analyse', type=['XLSX', 'XLS', 'xls', 'xlsx'])

    if main_file_path:
        try:
            main_df = pl.read_excel(main_file_path, infer_schema_length=0)
            main_df = main_df.to_pandas()
            st.session_state.main_df = main_df
        except Exception as e:
            st.error(f"Error raised while opening the file: {e}", icon='😭')
            return

        columns = list(main_df.columns)
        columns.append("NONE")
        st.markdown("<h4>Provide the following necessary information</h4>", unsafe_allow_html=True)

        date_col = st.selectbox("Select the Date Column", options=columns, index=None, placeholder="Date Column", help="Select NONE if No Mapping Column Available")
        spend_col = st.selectbox("Select the Spend Column", options=columns, index=None, placeholder="Spend Column", help="Select NONE if No Mapping Column Available")
        currency_col = st.selectbox("Select the Currency Column", options=columns, index=None, placeholder="Currency Column" ,help="Select NONE if No Mapping Column Available")
        invoice_number_col = st.selectbox("Select the Invoice Number Column", options=columns, index=None, placeholder="Invoice Number Column",help="Select NONE if No Mapping Column Available")
        invoice_line_number_col = st.selectbox("Select the Invoice Line Number Column", options=columns, index=None, placeholder="Invoice Line Number Column",help="Select NONE if No Mapping Column Available")
        supplier_name_col = st.selectbox("Select the Supplier Name Column", options=columns, index=None, placeholder="Supplier Name Column",help="Select NONE if No Mapping Column Available")
        all_description_col = st.multiselect('Select all the Description Columns', options=columns, placeholder='Description Columns',help="Select NONE if No Mapping Column Available")

        # Store button state in session state to manage form submission
        if st.button("Begin Analysis!"):
            # Check if all necessary fields are filled
            if all([date_col, spend_col, currency_col, invoice_number_col, invoice_line_number_col, supplier_name_col]) and all_description_col:
                st.session_state.mapping_dict = {
                    'Date': date_col,
                    "Spend": spend_col,
                    "Currency": currency_col,
                    'Invoice Number': invoice_number_col,
                    'Invoice Line Number': invoice_line_number_col,
                    'Supplier Name': supplier_name_col,
                    'All Description': all_description_col
                }
                began_analysis()
            
                # Proceed with analysis here
            else:
                # Display warning if any fields are not filled
                st.warning('Please fill all the necessary fields!', icon='😒')

              
def began_analysis():
    def check_content(value):
        if isinstance(value, str):
            # Check if the string is purely numeric
            if value.isdigit():
                return None
            # Check if the string contains only special characters
            if re.fullmatch(r'[^a-zA-Z0-9]+', value):
                return None
            # Check if the string is alphanumeric (contains numbers and symbols)
            if re.search(r'[0-9]', value) and re.search(r'[^a-zA-Z0-9]', value):
                return None
        return value        
            
    result = {}
    df= st.session_state.main_df.copy()
    total_transaction = df.shape[0]
    invalids = ["#N/A", 'N/A', 'NA', 'NULL', 'NONE', 'NOT ASSIGNED', 'NOT AVAILABLE', " ", '0',' ','']
    for key in st.session_state.mapping_dict:

        #: analysis of the description columns
        if key == 'All Description':
            desc_cols = st.session_state.mapping_dict[key]
            for column in  desc_cols:
                df[column] = df[column].apply(
                    lambda x: x.upper() if isinstance(x, str) else x
                )
                df[column] = df[column].replace(invalids,None)
                df[column] = df[column].apply(check_content)
                na_count = df[column].isna().sum()
                percentage_na = ((total_transaction-na_count)/total_transaction)*100
                result[column]={'Percentage Population':percentage_na,'Comment':None, 'Blank Rows Count' : na_count,
                               'Column Type':'Important'}
   
        #: analysis of the date column
        elif key == "Date":
            upper_range = 2024
            lower_range = 2024
            date_col = st.session_state.mapping_dict[key]
            # Handle "NONE" case for the date column
            if result.get(date_col) == "NONE":
                result[key] = {
                    'Percentage Population': None,
                    'Comment': 'No mapping column for this column',
                    'Blank Rows Count': None,
                    'Column Type': 'Important'
                }
            else:
                df[date_col] = pd.to_datetime(df[date_col], infer_datetime_format=True)
                df['year'] = df[date_col].dt.year
                out_of_range = df[(df['year'] > upper_range) | (df['year'] < lower_range)].shape[0]
                out_of_range_percent = ((total_transaction - out_of_range) / total_transaction) * 100
                result[date_col] = {
                    'Percentage Population': out_of_range_percent,
                    'Comment': f'Total {out_of_range} Outlier Document Dates found in Data',
                    'Blank Rows Count': out_of_range,
                    'Column Type': 'Important'
                }

        #: analysis of the Spend column
        elif key == 'Spend':
            spend_col = st.session_state.mapping_dict[key]
            # Handle "NONE" case for the spend column
            if result.get(spend_col) == "NONE":
                result[key] = {
                    'Percentage Population': None,
                    'Comment': 'No mapping column for this column',
                    'Blank Rows Count': None,
                    'Column Type': 'Important'
                }
            else:
                df[spend_col] = df[spend_col].astype(float)
                Q1 = df[spend_col].quantile(0.25)
                Q3 = df[spend_col].quantile(0.75)
                IQR = Q3 - Q1
                # Define outliers as values outside of 1.5 * IQR
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = df[(df[spend_col] < lower_bound) | (df[spend_col] > upper_bound)][spend_col]
                total_outlier_spend = outliers.sum()
                no_spend = df[spend_col].isna().sum()
                negative_spend = df[df[spend_col] < 0][spend_col].sum()
                positive_spend = df[df[spend_col] > 0][spend_col].sum()
                percentage_spend_na = ((total_transaction - no_spend) / total_transaction) * 100
                result[key] = {
                    'Percentage Population': percentage_spend_na,
                    'Comment': f'Total negative Spend {negative_spend} and Positive Spend {positive_spend} and Total Outliers Spend is {total_outlier_spend}',
                    'Blank Rows Count': no_spend,
                    'Column Type': 'Important'
                }

        #: analysing the currency column
        elif key == "Currency":
            currency_col = st.session_state.mapping_dict[key]
            # Handle "NONE" case for the currency column
            if result.get(currency_col) == "NONE":
                result[key] = {
                    'Percentage Population': None,
                    'Comment': 'No mapping column for this column',
                    'Blank Rows Count': None,
                    'Column Type': 'Important'
                }
            else:
                currency_count_result_dict = {}
                null_currency = df[currency_col].isna().sum()
                value_counts = df[currency_col].value_counts().reset_index()
                for i, j in value_counts.iterrows():
                    currency_count_result_dict[j[currency_col]] = j['count']
                percentage_na = ((total_transaction - null_currency) / total_transaction) * 100
                result[key] = {
                    'Percentage Population': percentage_na,
                    'Comment': str(currency_count_result_dict),
                    'Blank Rows Count': null_currency,
                    'Column Type': 'Important'
                }
             
        #: analysis of the rest of the columns
        else:
            value=st.session_state.mapping_dict[key]
            nas=df[value].isna().sum()
            percentage=((total_transaction-nas)/total_transaction)*100
            result[key]={'Percentage Population':percentage,'Comment':None,
                            'Blank Rows Count' :nas,
                            'Column Type':'Important'}
            
    #: analysis of columns other than important, ie good to have columns
    for column in df.columns:
        if column not in list(st.session_state.mapping_dict.values()):
            nas=df[column].isna().sum()
            percentage=((total_transaction-nas)/total_transaction)*100
            result[column]={'Percentage Population':percentage,'Comment':None,
                            'Blank Rows Count' :nas,
                            'Column Type':'Good to have'}
    st.session_state.result_df = pd.DataFrame.from_records(result)
    st.session_state.result_df = st.session_state.result_df.transpose()
    st.session_state.result_df.reset_index(inplace=True)
    try:
        st.session_state.result_df.to_excel("Analysis_results.xlsx", index=False)
        st.success("Analysis Results saved successfully!",icon='😁')
    except Exception as e:
            st.error(f"Error saving file: {e}")



def conslidate_data():
    st.markdown("<h4>Hi ! Welcome to DAD Consolidation Module</h4>", unsafe_allow_html=True)
    st.write('Provide the Main File and Mapping File for the consolidation of data')

    # File uploaders
    main_file_path = st.file_uploader('Select the Main File', type=['XLSX', 'xls', 'XLS', 'xlsx'])
    mapping_file_path = st.file_uploader('Select the Mapping File', type=['XLSX', 'xls', 'XLS', 'xlsx'])

    # Read files if not already in session state
    if main_file_path and mapping_file_path:
        if 'main_file_df' not in st.session_state or 'mapping_df' not in st.session_state:
            try:
                main_file_df = pl.read_excel(main_file_path, infer_schema_length=0).to_pandas()
                mapping_df = pl.read_excel(mapping_file_path, infer_schema_length=0).to_pandas()
                st.session_state.main_file_df = main_file_df
                st.session_state.mapping_df = mapping_df
                st.session_state.file_read = True
            except Exception as e:
                st.error(f"{e} Error Occurred While Opening the files")
                st.session_state.file_read = False

    # Work with files already loaded in session state
    if st.session_state.get('file_read'):
        main_file_df = st.session_state.main_file_df
        mapping_df = st.session_state.mapping_df
        
        # Select keys
        st.session_state.main_df_key = st.selectbox('Provide the Key from Main file', options=list(main_file_df.columns), index=None, placeholder='Main file Key')
        st.session_state.mapping_df_key = st.selectbox('Provide the Key from Mapping file', options=list(mapping_df.columns), index=None, placeholder='Mapping file Key')

        # Select columns to map
        if st.session_state.main_df_key and st.session_state.mapping_df_key:
            st.markdown("<h5>Please Select the Lookup Information!!</h5>", unsafe_allow_html=True)
            st.session_state.main_column = st.selectbox("Select the Main file Column", options=list(main_file_df.columns), index=None, placeholder='Main file Column Name')
            st.session_state.mapping_column = st.selectbox("Select the Mapping file Column", options=list(mapping_df.columns), index=None, placeholder='Mapping file Column Name')
            
            col1, col2, col3 = st.columns([1, 1, 1])

            if st.session_state.main_column and st.session_state.mapping_column:
                with col1:
                    if st.button('Map Details', use_container_width=True):
                        # Perform mapping and update the DataFrame
                        main_file_df[st.session_state.main_column] = main_file_df[st.session_state.main_df_key].map(
                            mapping_df.set_index(st.session_state.mapping_df_key)[st.session_state.mapping_column]
                        )
                        
                        # Store updated DataFrame in session state
                        st.session_state.main_file_df = main_file_df
                        
                        time.sleep(2)
                        st.toast(f"{st.session_state.main_column} Mapped Successfully", icon='😁')

                with col2:
                    if st.button('Clear Mapping', use_container_width=True):
                        st.session_state.main_column = None
                        st.session_state.mapping_column = None
                        st.rerun()

                with col3:
                    if st.button('Clear Keys', use_container_width=True):
                        st.session_state.main_df_key = None
                        st.session_state.mapping_df_key = None
                        st.rerun()

                # Show consolidated DataFrame and download button (full-width display)
                if st.button('Show Consolidated File', use_container_width=True):
                    st.write("### Consolidated File")
                    st.dataframe(main_file_df, use_container_width=True)
                    st.download_button("Download Updated File", main_file_df.to_csv(index=False), "updated_main_file.csv")




if __name__=="__main__":
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

    st.sidebar.title("Navigate")
    page = st.sidebar.radio( 
        "Selection Task" , ["Home","Append File","Consolidate Data","Analyse File"]
    )
    st.session_state.current_page = page

    

    if st.session_state.current_page == 'Home':
        data_consolidation_page()
    elif st.session_state.current_page =="Append File":
        append_files()
    elif st.session_state.current_page == "Analyse File":
        analyse_file()
    elif st.session_state.current_page == "Consolidate Data":
        conslidate_data()
    
