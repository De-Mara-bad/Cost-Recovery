# 🏢 Fluent Cost Recovery Reconciliation App

An online tool for matching Account Transactions to Sales and identifying unbilled costs across Fluent properties.

**Access the app:** Open the link when deployed to Streamlit Cloud (see Setup Guide)

---

## Features

✅ **All Fluent Buildings Supported**
- EIGHTY2onM
- ONEHUNDREDonM
- SIXonN
- THREE43onB
- ONE46onM
- ONE26onM
- TenOnV

✅ **Automatic Cost Matching**
- Matches Account Transactions to Sales entries
- Identifies unbilled costs
- Extracts unit numbers automatically

✅ **Color-Coded Results**
- 🟢 **GREEN** = Billed items (matched to sales)
- 🔴 **RED** = Items NOT billed
- 🔵 **LIGHT BLUE** = Electricity not billed
- 🟣 **PURPLE** = Netflix (always marked as billed)

✅ **Custom Triggers**
- Built-in: Electricity, Netflix
- Add your own: Water, Cleaning, Maintenance, etc.

✅ **Professional Excel Output**
- Color-coded rows
- Summary metrics
- Ready to share with owners

---

## How to Use

1. **Select your building** from the dropdown
2. **Configure triggers** (optional—add custom cost types)
3. **Upload files:**
   - Account Transactions Excel file
   - Sales Excel file
4. **Review results** in the browser
5. **Download Excel file** with all color coding

---

## File Requirements

### Account Transactions File
Excel file with a sheet named "Account Transactions" containing:
- Date
- Source
- Description
- Reference
- Debit
- Credit
- Running Balance (optional)
- Gross (optional)
- Tax (optional)

### Sales File
Excel file with columns like:
- Date
- Source (e.g., "Receivable Credit Note")
- Description
- Reference
- Debit
- Credit
- Running Balance (optional)
- Gross (optional)
- Tax (optional)

---

## Installation (Local Development)

If you want to run this locally:

```bash
pip install -r requirements.txt
streamlit run fluent_reconciliation_app.py
```

---

## Deployment

Deployed on **Streamlit Cloud** for free online access. See `GITHUB_SETUP.md` for deployment instructions.

---

## Technology Stack

- **Python 3.9+**
- **Streamlit** - Web app framework
- **Pandas** - Data processing
- **OpenPyXL** - Excel file handling

---

## Support

For questions or feature requests, contact the development team.

---

## License

Internal Fluent tool. All rights reserved.

---

**Made for Fluent Living** 🏠
