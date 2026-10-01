"""
Fluent Cost Recovery Reconciliation App
Analyzes Account Transactions vs Sales for cost recovery matching
"""

import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
import re
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Fluent Reconciliation", layout="wide")

st.title("🏢 Fluent Cost Recovery Reconciliation App")
st.markdown("Match Account Transactions to Sales and identify unbilled costs")

# ============================================================================
# SIDEBAR - Configuration
# ============================================================================
st.sidebar.header("⚙️ Configuration")

# Building selection
building = st.sidebar.selectbox(
    "Select Building",
    ["EIGHTY2onM", "ONEHUNDREDonM", "SIXonN", "THREE43onB", "ONE46onM", "ONE26onM", "TenOnV"],
    help="Which property are you analyzing?"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏷️ Custom Triggers")

# Default triggers
triggers = {
    'Electricity': ['COCT UTILITIES', 'CCT UTILITIES', 'ELECTRICITY', 'ELECTRIS'],
    'Netflix': ['NETFLIX'],
}

# Add custom triggers
st.sidebar.markdown("**Built-in triggers:**")
for trigger_type, keywords in triggers.items():
    st.sidebar.caption(f"✓ {trigger_type}: {', '.join(keywords)}")

# Allow user to add custom triggers
st.sidebar.markdown("**Add custom triggers:**")
col1, col2 = st.sidebar.columns([2, 1])
with col1:
    custom_trigger_name = st.text_input("Trigger name (e.g., 'Water', 'Cleaning')", key="trigger_name")
with col2:
    add_trigger = st.button("Add", key="add_trigger_btn")

if add_trigger and custom_trigger_name:
    if 'custom_triggers' not in st.session_state:
        st.session_state.custom_triggers = {}
    keywords = st.text_input(f"Keywords for {custom_trigger_name} (comma-separated)", key=f"keywords_{custom_trigger_name}")
    if keywords:
        trigger_list = [k.strip().upper() for k in keywords.split(',')]
        st.session_state.custom_triggers[custom_trigger_name] = trigger_list
        st.sidebar.success(f"Added: {custom_trigger_name}")

if hasattr(st.session_state, 'custom_triggers'):
    st.sidebar.markdown("**Your custom triggers:**")
    for name, keywords in st.session_state.custom_triggers.items():
        st.sidebar.caption(f"• {name}: {', '.join(keywords)}")

# ============================================================================
# MAIN AREA - File Upload
# ============================================================================
st.header(f"📊 Reconciliation for {building}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Account Transactions")
    account_file = st.file_uploader(
        "Upload Account Transactions sheet",
        type=['xlsx', 'xls'],
        key="account_file",
        help="Excel file with Account Transactions data"
    )

with col2:
    st.subheader("2️⃣ Sales Data")
    sales_file = st.file_uploader(
        "Upload Sales sheet",
        type=['xlsx', 'xls'],
        key="sales_file",
        help="Excel file with Sales/Client Recoveries data"
    )

# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================

def extract_unit_number(desc):
    """Extract unit/room number from description"""
    if pd.isna(desc):
        return None
    desc_str = str(desc)
    patterns = [
        r'[Uu]nit\s+(\d+)',
        r'[Rr]oom\s+(\d+)',
        r'-\s*(\d{3})\s*[A-Z]',
        r'(?:100onM|100 on M|onM)\s*-\s*(\d+)',
        r'(?:UNIT|Unit)\s+(\d{3})\b',
        r'\(UNIT\s+(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, desc_str)
        if match:
            unit = match.group(1).lstrip('0') or match.group(1)
            return unit
    return None

def check_trigger(desc, trigger_keywords):
    """Check if description contains any trigger keywords"""
    if pd.isna(desc):
        return False
    desc_upper = str(desc).upper()
    return any(keyword in desc_upper for keyword in trigger_keywords)

def classify_item(desc, all_triggers):
    """Classify item based on triggers"""
    for trigger_type, keywords in all_triggers.items():
        if check_trigger(desc, keywords):
            return trigger_type
    return 'Other'

def process_reconciliation(account_data, sales_data, all_triggers):
    """Main reconciliation logic"""
    
    # Add classification columns
    account_data['Item_Type'] = account_data['Description'].apply(
        lambda x: classify_item(x, all_triggers)
    )
    account_data['Unit'] = account_data['Description'].apply(extract_unit_number)
    account_data['Is_Billed'] = False
    account_data['Billed_Amount'] = None
    account_data['Billed_Date'] = None
    account_data['Match_Status'] = 'Not Billed'
    account_data['Color'] = 'Red'
    
    # Process each transaction
    for at_idx, at_row in account_data.iterrows():
        at_type = at_row['Item_Type']
        at_unit = at_row['Unit']
        at_desc = str(at_row['Description']).upper()
        at_date = pd.to_datetime(at_row['Date']) if pd.notna(at_row['Date']) else None
        at_amount = float(at_row['Debit']) if pd.notna(at_row['Debit']) else 0
        
        # Netflix - always mark as billed
        if at_type == 'Netflix':
            account_data.at[at_idx, 'Is_Billed'] = True
            account_data.at[at_idx, 'Match_Status'] = 'Billed'
            account_data.at[at_idx, 'Color'] = 'Purple'
            continue
        
        # Find matching sales entry
        found_match = False
        for s_idx, s_row in sales_data.iterrows():
            s_unit = extract_unit_number(s_row['Description'])
            s_desc = str(s_row['Description']).upper()
            s_amount = float(s_row['Credit']) if pd.notna(s_row['Credit']) else 0
            s_date = pd.to_datetime(s_row['Date']) if pd.notna(s_row['Date']) else None
            
            if s_unit != at_unit:
                continue
            
            # For Electricity - match to "Electricity Cost Recovery"
            if at_type == 'Electricity' and 'ELECTRICITY COST RECOVERY' in s_desc:
                if at_date and s_date:
                    date_diff = (s_date - at_date).days
                    if -5 <= date_diff <= 30:
                        found_match = True
                        account_data.at[at_idx, 'Is_Billed'] = True
                        account_data.at[at_idx, 'Billed_Amount'] = s_amount
                        account_data.at[at_idx, 'Billed_Date'] = s_date
                        account_data.at[at_idx, 'Match_Status'] = 'Billed'
                        account_data.at[at_idx, 'Color'] = 'Green'
                        break
            
            # For custom triggers - match to general recovery items
            elif at_type != 'Other':
                trigger_upper = at_type.upper()
                if (trigger_upper in s_desc or 'COST RECOVERY' in s_desc or 'MAINTENANCE' in s_desc):
                    if at_date and s_date:
                        date_diff = (s_date - at_date).days
                        if -5 <= date_diff <= 60:
                            found_match = True
                            account_data.at[at_idx, 'Is_Billed'] = True
                            account_data.at[at_idx, 'Billed_Amount'] = s_amount
                            account_data.at[at_idx, 'Billed_Date'] = s_date
                            account_data.at[at_idx, 'Match_Status'] = 'Billed'
                            account_data.at[at_idx, 'Color'] = 'Green'
                            break
            
            # For Other items
            elif at_type == 'Other' and ('REPAIRS' in s_desc or 'MAINTENANCE' in s_desc):
                if at_date and s_date:
                    date_diff = (s_date - at_date).days
                    if -5 <= date_diff <= 60:
                        found_match = True
                        account_data.at[at_idx, 'Is_Billed'] = True
                        account_data.at[at_idx, 'Billed_Amount'] = s_amount
                        account_data.at[at_idx, 'Billed_Date'] = s_date
                        account_data.at[at_idx, 'Match_Status'] = 'Billed'
                        account_data.at[at_idx, 'Color'] = 'Green'
                        break
        
        # Set color for non-matched items
        if not found_match and at_type == 'Electricity':
            account_data.at[at_idx, 'Color'] = 'Light Blue'
    
    return account_data

def create_excel_output(account_data):
    """Create formatted Excel file with color coding"""
    
    color_map = {
        'Green': 'C6EFCE',
        'Red': 'FFC7CE',
        'Light Blue': 'ADD8E6',
        'Purple': 'E0B0E0'
    }
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reconciliation"
    
    # Headers
    headers = ['Date', 'Source', 'Description', 'Amount', 'Unit', 'Type', 'Status', 'Billed Amount', 'Billed Date']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Add data rows
    for row_num, (idx, row) in enumerate(account_data.iterrows(), 2):
        ws.cell(row=row_num, column=1).value = row['Date']
        ws.cell(row=row_num, column=2).value = row['Source']
        ws.cell(row=row_num, column=3).value = row['Description']
        ws.cell(row=row_num, column=4).value = row['Debit']
        ws.cell(row=row_num, column=5).value = row['Unit']
        ws.cell(row=row_num, column=6).value = row['Item_Type']
        ws.cell(row=row_num, column=7).value = row['Match_Status']
        ws.cell(row=row_num, column=8).value = row['Billed_Amount']
        ws.cell(row=row_num, column=9).value = row['Billed_Date']
        
        color_hex = color_map.get(row['Color'], 'FFC7CE')
        fill = PatternFill(start_color=color_hex, end_color=color_hex, fill_type="solid")
        
        for col in range(1, 10):
            cell = ws.cell(row=row_num, column=col)
            cell.fill = fill
            cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    
    # Set column widths
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 70
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 8
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 18
    ws.column_dimensions['H'].width = 13
    ws.column_dimensions['I'].width = 15
    
    return wb

# ============================================================================
# PROCESS FILES
# ============================================================================

if account_file and sales_file:
    st.markdown("---")
    
    try:
        # Read files
        with st.spinner("Reading files..."):
            # Account Transactions
            account_xls = pd.ExcelFile(account_file)
            account_raw = pd.read_excel(account_file, sheet_name="Account Transactions", header=None)
            
            # Find header row
            at_header = None
            for idx, row in account_raw.iterrows():
                if row[0] == 'Date':
                    at_header = idx
                    break
            
            if at_header is None:
                st.error("❌ Could not find Account Transactions header. Ensure 'Date' column exists.")
            else:
                account_data = account_raw.iloc[at_header+1:].reset_index(drop=True)
                account_data.columns = ['Date', 'Source', 'Description', 'Reference', 'Debit', 'Credit', 'Running Balance', 'Gross', 'Tax']
                account_data = account_data.dropna(subset=['Description'])
                account_data = account_data[account_data['Description'].astype(str).str.strip() != ''].reset_index(drop=True)
                
                # Sales
                sales_raw = pd.read_excel(sales_file, sheet_name=0, header=None)
                
                # Find header row
                s_header = None
                for idx, row in sales_raw.iterrows():
                    if row[1] in ['Receivable Credit Note', 'Spend Money', 'Receivable Invoice']:
                        s_header = idx
                        break
                
                if s_header is None:
                    st.error("❌ Could not find Sales header.")
                else:
                    sales_data = sales_raw.iloc[s_header:].reset_index(drop=True)
                    sales_data.columns = ['Date', 'Source', 'Description', 'Reference', 'Debit', 'Credit', 'Running Balance', 'Gross', 'Tax']
                    sales_data = sales_data.dropna(subset=['Description'])
                    
                    # Build all triggers
                    all_triggers = triggers.copy()
                    if hasattr(st.session_state, 'custom_triggers'):
                        all_triggers.update(st.session_state.custom_triggers)
                    
                    # Process
                    with st.spinner("Processing reconciliation..."):
                        result = process_reconciliation(account_data, sales_data, all_triggers)
                    
                    # Display summary
                    col1, col2, col3, col4 = st.columns(4)
                    
                    green_count = len(result[result['Color'] == 'Green'])
                    red_count = len(result[result['Color'] == 'Red'])
                    blue_count = len(result[result['Color'] == 'Light Blue'])
                    purple_count = len(result[result['Color'] == 'Purple'])
                    
                    with col1:
                        st.metric("🟢 Billed", green_count)
                    with col2:
                        st.metric("🔴 Not Billed", red_count)
                    with col3:
                        st.metric("🔵 Electricity Not Billed", blue_count)
                    with col4:
                        st.metric("🟣 Netflix", purple_count)
                    
                    st.markdown("---")
                    
                    # Show data
                    st.subheader("📋 Reconciliation Results")
                    
                    # Filter options
                    col1, col2 = st.columns(2)
                    with col1:
                        show_status = st.multiselect(
                            "Filter by Status",
                            ["Billed", "Not Billed", "Not Billed (Electricity)"],
                            default=["Billed", "Not Billed", "Not Billed (Electricity)"]
                        )
                    
                    with col2:
                        show_type = st.multiselect(
                            "Filter by Type",
                            result['Item_Type'].unique(),
                            default=result['Item_Type'].unique()
                        )
                    
                    filtered = result[
                        (result['Match_Status'].isin(show_status) | result['Match_Status'].str.contains('|'.join(show_status), case=False, na=False)) &
                        (result['Item_Type'].isin(show_type))
                    ]
                    
                    st.dataframe(
                        filtered[['Date', 'Description', 'Debit', 'Unit', 'Item_Type', 'Match_Status']].head(50),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    if len(filtered) > 50:
                        st.info(f"Showing 50 of {len(filtered)} results. Download full file to see all.")
                    
                    st.markdown("---")
                    
                    # Download button
                    st.subheader("⬇️ Download Results")
                    
                    wb = create_excel_output(result)
                    buffer = BytesIO()
                    wb.save(buffer)
                    buffer.seek(0)
                    
                    filename = f"{building}_Reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    
                    st.download_button(
                        label="📊 Download Excel File",
                        data=buffer,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    st.success("✓ Reconciliation complete! Download your file above.")
    
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")
        st.info("Make sure your files have the correct sheets: 'Account Transactions' and 'Sales' or similar.")

else:
    st.info("👆 Upload both files to get started. Your Account Transactions and Sales data will be matched and analyzed.")

