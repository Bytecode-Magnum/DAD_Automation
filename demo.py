import streamlit as st
import polars as pl
import pandas as pd
import os
import time

st.set_page_config(
    layout='wide'
)


@st.dialog("No file provided", width='small')
def no_file_provided():
    st.error('No file provided, please provide the Raw/Base Invoice Data to consolidate first!', icon='🥲')


@st.dialog('No mapping provided', width='small')
def no_mapping_provided():
    st.error("No Mapping provide, please provide the mapping.", icon='😭')


def about_common_schema():
    st.subheader(
        "Hi! We Help You Consolidate data from multiple businesses Of Client to a Unified Simfoni Format, providing "
        "you more transparency and control Over data")
    st.markdown("""<h4>Key Features of Data Consolidation and Assessment Automation</h4 >""",
                unsafe_allow_html=True)

    # List of key features
    st.markdown("""
                - **Multiple File Upload**: Clients and analysts can upload multiple files, including multiple raw/base invoice data.
                - **Master File Creation**: Using automation scripts, the module consolidates data from various sources into a single master file by mapping headers of raw/data to Unified Headers.
                - **Userdefined Column For Unmapped Headers**: In Case client or analyst want to create a user defined header for unmapped headers, they can do it as step 2.
                - **Automated Header Creation for Unmapped Raw Headers**:At the Last step where we are left with few unmapped headers, we create Automated Header for those headers, same as raw header.
            """)
    st.write("Please Nagivate to Next Page to Begin the Conslidation Process😊")


def upload_file_common_schema():
    st.session_state.all_raw_invoice_path = None
    st.subheader("Hi! As the first step of Consolidation, please provide all the raw invoice data you have.")
    all_raw_invoice_path = st.file_uploader('Select the Invoice Data', type=['xlsx', 'csv'], accept_multiple_files=True)
    st.session_state.all_raw_invoice_path = all_raw_invoice_path


def header_mapping_common_schema():
    st.session_state.file_names = [str(file.name).split(".")[0] for file in st.session_state.all_raw_invoice_path]
    st.session_state.mapping_df = pd.DataFrame(columns=st.session_state.file_names,
                                               index=st.session_state.unified_headers)
    if len(st.session_state.all_raw_invoice_path) == 0 or st.session_state.all_raw_invoice_path is None:
        no_file_provided()
    else:
        st.subheader(
            "Hi! As second step of Consolidation we will be mapping the headers of raw invoice data to Unified Simfoni Headers.")
        for i, file_path in enumerate(st.session_state.all_raw_invoice_path):
            st.session_state.file_info_dict[f'invoice_data_{i}'] = {}
            st.session_state.file_info_dict[f'invoice_data_{i}']['name'] = str(file_path.name).split(".")[0]
            if file_path.name.endswith('csv'):
                try:
                    df = pl.read_csv(file_path, infer_schema_length=0)
                    df = df.to_pandas()
                    st.session_state.file_info_dict[f'invoice_data_{i}']['df'] = df
                    st.session_state.file_load_status = True
                except Exception as e:
                    st.error(
                        f"Unexpected {e} Error Occured While Opening Invoice Data {str(file_path.name).split('.')[0]}")
                    st.session_state.file_load_status = False
            elif file_path.name.endswith('xlsx'):
                try:
                    df = pl.read_excel(file_path, infer_schema_length=0)
                    df = df.to_pandas()
                    st.session_state.file_info_dict[f'invoice_data_{i}']['df'] = df
                    st.session_state.file_load_status = True
                except Exception as e:
                    st.error(
                        f"Unexpected {e} Error Occured While Opening Invoice Data {str(file_path.name).split('.')[0]}")
                    st.session_state.file_load_status = False
        if st.session_state.file_load_status:
            st.markdown("""
                <style>
                /* Style for the column group container */
                .column-group {
                    border: 2px solid #4a4a4a;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                    background-color: rgba(255, 255, 255, 0.05);
                }

                /* Style for the column header */
                .column-header {
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    padding: 5px;
                    border-bottom: 1px solid #666;
                    color: black;
                }

                /* Style for individual selectboxes */
                .stSelectbox > div {
                    margin-bottom: 10px;
                }
                </style>
            """, unsafe_allow_html=True)
            for column in st.session_state.mapping_df.index:
                st.markdown(f"""
                    <div class='column-group'>
                        <div class='column-header'>Unified Header: {column}</div>
                    </div>
                """, unsafe_allow_html=True)
                cols = st.columns(len(st.session_state.file_info_dict))
                for idx, (key, value) in enumerate(st.session_state.file_info_dict.items()):
                    with cols[idx]:
                        if column != 'File Name':
                            choice = st.selectbox(
                                f"From {value['name']}",
                                options=value['df'].columns.tolist() + ['None'],
                                index=None,
                                key=f"{column}_{value['name']}_select",
                                placeholder=f"{column}"
                            )
                            st.session_state.mapping_df.loc[column, value['name']] = choice
                        else:
                            choice = st.selectbox(
                                f"From {value['name']}",
                                options=st.session_state.file_names,
                                index=None,
                                key=f"{column}_{value['name']}_select",
                                placeholder=f"{column}",
                            )
                            st.session_state.mapping_df.loc[column, value['name']] = choice


def map_unmapped_header_userdefined_header():
    st.markdown("""
                    <style>
                    /* Style for the column group container */
                    .column-group {
                        border: 2px solid #4a4a4a;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 15px 0;
                        background-color: rgba(255, 255, 255, 0.05);
                    }

                    /* Style for the column header */
                    .column-header {
                        font-size: 16px;
                        font-weight: bold;
                        margin-bottom: 10px;
                        padding: 5px;
                        border-bottom: 1px solid #666;
                        color: black;
                    }

                    /* Style for individual selectboxes */
                    .stSelectbox > div {
                        margin-bottom: 10px;
                    }
                    </style>
                """, unsafe_allow_html=True)
    unmapped_dict = {}
    st.subheader("Creating Analyst or Client defined column name for unmapped headers")
    for each in st.session_state.file_info_dict:
        raw_data_columns = st.session_state.file_info_dict[each]['df'].columns
        mapping_df_columns = list(st.session_state.mapping_df[st.session_state.file_info_dict[each]['name']])
        unmapped_dict[f'{st.session_state.file_info_dict[each]["name"]}'] = []
        for column in raw_data_columns:
            if column not in mapping_df_columns:
                unmapped_dict[f'{st.session_state.file_info_dict[each]["name"]}'].append(column)
    st.markdown("""<h5>Following are the unmapped header details.</h5>""", unsafe_allow_html=True)
    st.write(unmapped_dict)
    st.markdown("""<h5>Provide New Head Name For Unmapped columns.</h5>""", unsafe_allow_html=True)
    user_defined_column_names = st.text_input('Provide Column Name for Unmapped headers')
    user_defined_column_names = [each.strip() for each in user_defined_column_names.split(",")]
    if user_defined_column_names:
        for column in user_defined_column_names:
            st.markdown(f"""
                <div class='column-group'>
                    <div class='column-header'>Unified Header: {column}</div>
                </div>
            """, unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.file_info_dict))
            for idx, (key, value) in enumerate(st.session_state.file_info_dict.items()):
                with cols[idx]:
                    if column != 'File Name':
                        choice = st.selectbox(
                            f"From {value['name']}",
                            options=value['df'].columns.tolist() + ['None'],
                            index=None,
                            key=f"{column}_{value['name']}_select",
                            placeholder=f"{column}"
                        )
                        st.session_state.mapping_df.loc[column, value['name']] = choice


def autocreate_unmapped_headers_common():
    if 'autocreate_header_dict' not in st.session_state:
        st.session_state.autocreate_header_dict = {}
    st.subheader('In this last step, we can create header same as Raw Header which are still unmapped.')
    unmapped_dict = {}
    for each in st.session_state.file_info_dict:
        raw_data_columns = st.session_state.file_info_dict[each]['df'].columns
        mapping_df_columns = list(st.session_state.mapping_df[st.session_state.file_info_dict[each]['name']])
        unmapped_dict[f'{st.session_state.file_info_dict[each]["name"]}'] = []
        for column in raw_data_columns:
            if column not in mapping_df_columns:
                unmapped_dict[f'{st.session_state.file_info_dict[each]["name"]}'].append(column)
    st.markdown("<h5>Following are the list of unmapped Headers</h5>", unsafe_allow_html=True)
    st.write(unmapped_dict)
    st.markdown("<h5>Select Header For Appending at end of Master File.</h5>", unsafe_allow_html=True)
    for each in unmapped_dict:
        st.session_state.autocreate_header_dict[each] = []
        st.session_state.autocreate_header_dict[each] = st.multiselect(
            f'Select the Column from {each} for Appending at end', options=unmapped_dict[each])

    for each in st.session_state.autocreate_header_dict:
        columns = st.session_state.autocreate_header_dict[each]
        for column in columns:
            st.session_state.mapping_df.loc[column, each] = column


def common_schema():
    subpages = [about_common_schema, upload_file_common_schema, header_mapping_common_schema,
                map_unmapped_header_userdefined_header, autocreate_unmapped_headers_common]
    current_index = st.session_state.page_index
    subpages[current_index]()
    col1, col3, col2 = st.columns([6, 8, 6])
    with col1:
        if current_index != 0:
            if st.button("Previous", use_container_width=True) and current_index > 0:
                st.session_state.page_index -= 1
                st.rerun()
    with col2:
        if current_index != 4:
            if st.button("Next", use_container_width=True):
                if st.session_state.page_index == 1 and (
                        len(st.session_state.all_raw_invoice_path) == 0 or st.session_state.all_raw_invoice_path is None):
                    no_file_provided()
                elif st.session_state.page_index == 2 and (st.session_state.mapping_df.isnull().all().any()):
                    no_mapping_provided()
                elif st.session_state.page_index == 4:
                    no_mapping_provided()
                else:
                    if st.session_state.page_index < len(subpages) - 1:
                        st.session_state.page_index += 1
                        st.rerun()
        else:
            if st.button('Save Mapping and Create Master File.', use_container_width=True):
                st.session_state.master_df = create_master_file()


@st.dialog('Saving Master File')
def create_master_file():
    file_name = st.text_input('Provide a file name to save the file')
    if file_name:
        with st.spinner('Creating the Master file'):
            columns = list(st.session_state.mapping_df.index)
            appended_df = pd.DataFrame(columns=columns)  # Initialize empty DataFrame for final result
            files = list(st.session_state.mapping_df.columns)
            for i, file in enumerate(files):
                master_df = pd.DataFrame(columns=columns)
                df = st.session_state.file_info_dict[f'invoice_data_{i}']['df']
                for key in columns:
                    if key == 'File Name':
                        print("key found")
                        master_df[key] = [file] * len(df)  # Assign file name for the current DataFrame
                    else:
                        value = st.session_state.mapping_df.loc[key][file]
                        if value != 'None' and value is not None:
                            master_df[key] = df[value].copy()
                appended_df = pd.concat([appended_df, master_df], axis=0, ignore_index=True)
            time.sleep(10)
            st.success('Master File Created', icon='😁')
            directory = 'Master DF'
            file_path = directory + '/' + f'{file_name}.xlsx'
            if not os.path.exists(directory):
                os.makedirs(directory)
            else:
                appended_df.to_excel(file_path,index=False)
                st.success(f'Master File Saved Successfully at location {file_path}')
        return appended_df


def About():
    st.title("Hi! Welcome to Simfoni Auto DAD Module.")


if __name__ == "__main__":
    if 'file_info_dict' not in st.session_state:
        st.session_state.file_info_dict = {}
    if 'mapping_df' not in st.session_state:
        st.session_state.mapping_df = pd.DataFrame()
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0
    if 'all_raw_invoice_path' not in st.session_state:
        st.session_state.all_raw_invoice_path = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'About'
    if 'file_load_status' not in st.session_state:
        st.session_state.file_load_status = None
    if 'master_df' not in st.session_state:
        st.session_state.master_df = pd.DataFrame(columns=st.session_state.unified_headers)

    if 'unified_headers' not in st.session_state:
        st.session_state.unified_headers = [
            "SrNo",
            "ActualSrNo",
            "Data Source",
            "File Name",
            "Source System",
            "Entity Code",
            "Entity Name",
            "Entity City",
            "Entity State",
            "Entity Country",
            "Entity Region",
            "Document Number",
            "Document Line Number",
            "Document Date",
            "Document Header Description",
            "Document Line Description",
            # "Buyer Name",
            # "Payment Terms Code",
            # "Payment Terms Description",
            # "Supplier Document Number",
            # "Supplier Code",
            # "Supplier Name",
            # "Supplier Name (Normalized)",
            # "Supplier City",
            # "Supplier State",
            # "Supplier Country",
            # "Supplier Region",
            # "Supplier Tax ID",
            # "Document Unit price",
            # "Document Quantity",
            # "Document UOM",
            # "Document Currency",
            # "Amount in Document Currency",
            # "FX Rate",
            # "Spend",
            # "Cost Center Code",
            # "Cost Center Description",
            # "General Ledger Code",
            # "General Ledger Description",
            # "Material Code",
            # "Material Description",
            # "Material Group Code",
            # "Material Group Description",
            # "Contract Flag",
            # "Intercompany Flag",
            # "Scope",
            # "Supplier Commonality",
            # "Supplier Group",
            # "Invoice Group",
            # "Transaction Group",
            # "Addressability Flag",
            # "Category Level 0",
            # "Category Level 1",
            # "Category Level 2",
            # "Category Level 3",
            # "Category Level 4",
            # "Category Level 5",
            # "Category Level 6",
            # "Employee Last Name",
            # "cl_qa_flag",
            # "cl_training_set_flag",
            # "cl_cluster_id",
            # "source_name",
            # "custom_field1",
            # "custom_field2",
            # "custom_field3",
            # "custom_field4",
            # "custom_field5",
            # "QA flag",
            # "Posted Date",
            # "Sent for Payment Date",
            # "Detail",
            # "Batch ID",
            # "Sequence",
            # "Employee ID",
            # "Employee First Name",
            # "Expense Group ID",
            # "Operating Department Code",
            # "Company Name",
            # "Company Code",
            # "Division/Branch Name",
            # "Division/Branch Code",
            # "Department Name",
            # "Department Code",
            # "Report Name",
            # "Total Approved Amount",
            # "Reimbursement Currency",
            # "Payment Type",
            # "Project #",
            # "Name on Card",
            # "Last Four Account Digits",
            # "Merchant Code",
            # "Transaction Date"
        ]
    st.sidebar.title("Nagivation")
    page = st.sidebar.radio('Go To', ['About', 'Common Schema'])
    st.session_state.current_page = page

    if st.session_state.current_page == 'About':
        About()
    elif st.session_state.current_page == 'Common Schema':
        common_schema()
