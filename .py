import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# New imports for PDF generation using Platypus
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)

# Set the base directory to the directory where this script resides.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Configure logging to store the log file in the same directory.
LOG_FILE = os.path.join(BASE_DIR, 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    filename=LOG_FILE,
    filemode='a'
)

@app.before_request
def log_request():
    app.logger.info("Request: %s %s from %s", request.method, request.path, request.remote_addr)

# Set the data file path to the same directory.
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

def load_data():
    """Load all records from the JSON file. If not found, return empty lists."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        app.logger.info("Data loaded from %s", DATA_FILE)
        return {
            "sales_records": data.get("sales_records", []),
            "purchase_records": data.get("purchase_records", []),
            "sale_return_records": data.get("sale_return_records", []),
            "purchase_return_records": data.get("purchase_return_records", [])
        }
    else:
        app.logger.info("No data file found; initializing empty data")
        return {
            "sales_records": [],
            "purchase_records": [],
            "sale_return_records": [],
            "purchase_return_records": []
        }

def save_data():
    """Save the global record lists to the JSON file."""
    data = {
        "sales_records": sales_records,
        "purchase_records": purchase_records,
        "sale_return_records": sale_return_records,
        "purchase_return_records": purchase_return_records
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    app.logger.info("Data saved to %s", DATA_FILE)

# Load data on startup
data = load_data()
sales_records = data["sales_records"]
purchase_records = data["purchase_records"]
sale_return_records = data["sale_return_records"]
purchase_return_records = data["purchase_return_records"]

@app.route("/")
def index():
    return render_template("index.html", sales=sales_records)

# ---------------- Sales Process ----------------
@app.route("/sale", methods=["GET", "POST"])
def sale():
    message = ""
    search_query = request.args.get("search", "").strip()

    if request.method == "POST":
        try:
            product_name = request.form.get("product_name", "").strip()
            sale_date = request.form.get("sale_date", "")
            unit_price = float(request.form.get("unit_price", 0))
            quantity = float(request.form.get("quantity", 0))
            total_sale = unit_price * quantity

            record = {
                "product_name": product_name,
                "sale_date": sale_date,
                "unit_price": unit_price,
                "quantity": quantity,
                "total_sale": total_sale
            }
            sales_records.append(record)
            save_data()
            message = "Sale record added successfully!"
            app.logger.info("Added sale record: %s", record)
        except ValueError:
            message = "Invalid input. Please enter numeric values for price and quantity."
            app.logger.error("Error adding sale record: Invalid numeric input")

    if search_query:
        filtered_records = [
            rec for rec in sales_records
            if search_query.lower() in rec.get("product_name", "").lower() or search_query in rec.get("sale_date", "")
        ]
    else:
        filtered_records = sales_records

    return render_template("sale.html", records=filtered_records, message=message, search_query=search_query)

# ---------------- Purchase Process ----------------
@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    message = ""
    search_query = request.args.get("search", "").strip()

    if request.method == "POST":
        try:
            supplier_name = request.form.get("supplier_name", "").strip()
            product_name = request.form.get("product_name", "").strip()
            purchase_date = request.form.get("purchase_date", "")
            unit_price = float(request.form.get("unit_price", 0))
            quantity = float(request.form.get("quantity", 0))
            total_purchase = unit_price * quantity

            record = {
                "supplier_name": supplier_name,
                "product_name": product_name,
                "purchase_date": purchase_date,
                "unit_price": unit_price,
                "quantity": quantity,
                "total_purchase": total_purchase
            }
            purchase_records.append(record)
            save_data()
            message = "Purchase record added successfully!"
            app.logger.info("Added purchase record: %s", record)
        except ValueError:
            message = "Invalid input. Please enter numeric values for price and quantity."
            app.logger.error("Error adding purchase record: Invalid numeric input")

    if search_query:
        filtered_records = [
            rec for rec in purchase_records
            if (search_query.lower() in rec.get("product_name", "").lower() or
                search_query.lower() in rec.get("supplier_name", "").lower() or
                search_query in rec.get("purchase_date", ""))
        ]
    else:
        filtered_records = purchase_records

    return render_template("purchase.html", records=filtered_records, message=message, search_query=search_query)

# ---------------- Sales Return Process ----------------
@app.route("/sale-return", methods=["GET", "POST"])
def sale_return():
    message = ""
    if request.method == "POST":
        try:
            product_name = request.form.get("product_name", "").strip()
            return_date = request.form.get("return_date", "")
            unit_price = float(request.form.get("unit_price", 0))
            quantity = float(request.form.get("quantity", 0))
            refund_amount = unit_price * quantity

            record = {
                "product_name": product_name,
                "return_date": return_date,
                "unit_price": unit_price,
                "quantity": quantity,
                "refund_amount": refund_amount
            }
            sale_return_records.append(record)
            save_data()
            message = "Sale return record added successfully!"
            app.logger.info("Added sale return record: %s", record)
        except ValueError:
            message = "Invalid input. Please enter numeric values for price and quantity."
            app.logger.error("Error adding sale return record: Invalid numeric input")
    return render_template("sale_return.html", records=sale_return_records, message=message)

# ---------------- Purchase Return Process ----------------
@app.route("/purchase-return", methods=["GET", "POST"])
def purchase_return():
    message = ""
    if request.method == "POST":
        try:
            supplier_name = request.form.get("supplier_name", "").strip()
            product_name = request.form.get("product_name", "").strip()
            return_date = request.form.get("return_date", "")
            unit_price = float(request.form.get("unit_price", 0))
            quantity = float(request.form.get("quantity", 0))
            total_return = unit_price * quantity

            record = {
                "supplier_name": supplier_name,
                "product_name": product_name,
                "return_date": return_date,
                "unit_price": unit_price,
                "quantity": quantity,
                "total_return": total_return
            }
            purchase_return_records.append(record)
            save_data()
            message = "Purchase return record added successfully!"
            app.logger.info("Added purchase return record: %s", record)
        except ValueError:
            message = "Invalid input. Please enter numeric values for price and quantity."
            app.logger.error("Error adding purchase return record: Invalid numeric input")
    return render_template("purchase_return.html", records=purchase_return_records, message=message)

# ---------------- Profit Calculation ----------------
@app.route("/profit", methods=["GET", "POST"])
def profit():
    message = ""
    operating_expenses = 0.0
    if request.method == "POST":
        try:
            operating_expenses = float(request.form.get("operating_expenses", 0))
        except ValueError:
            message = "Invalid input. Please enter numeric values for operating expenses."
            app.logger.error("Error in profit calculation: Invalid operating expenses input")

    total_sales = sum(record["total_sale"] for record in sales_records)
    total_sale_returns = sum(record["refund_amount"] for record in sale_return_records)
    net_sales = total_sales - total_sale_returns

    total_purchases = sum(record["total_purchase"] for record in purchase_records)
    total_purchase_returns = sum(record["total_return"] for record in purchase_return_records)
    net_purchases = total_purchases - total_purchase_returns

    gross_profit = net_sales - net_purchases
    net_profit = gross_profit - operating_expenses

    result = {
        "total_sales": total_sales,
        "total_sale_returns": total_sale_returns,
        "net_sales": net_sales,
        "total_purchases": total_purchases,
        "total_purchase_returns": total_purchase_returns,
        "net_purchases": net_purchases,
        "gross_profit": gross_profit,
        "operating_expenses": operating_expenses,
        "net_profit": net_profit
    }

    app.logger.info("Profit calculated: %s", result)
    return render_template("profit.html", result=result, message=message)

# ---------------- Cash Flow Calculation ----------------
@app.route("/cash-flow", methods=["GET", "POST"])
def cash_flow():
    message = ""
    opening_balance = 0.0
    additional_outflow = 0.0
    if request.method == "POST":
        try:
            opening_balance = float(request.form.get("opening_balance", 0))
            additional_outflow = float(request.form.get("additional_outflow", 0))
        except ValueError:
            message = "Invalid input. Please enter numeric values."
            app.logger.error("Error in cash flow calculation: Invalid numeric input")

    cash_inflow = sum(record["total_sale"] for record in sales_records) - sum(record["refund_amount"] for record in sale_return_records)
    cash_outflow = (sum(record["total_purchase"] for record in purchase_records) - sum(record["total_return"] for record in purchase_return_records)) + additional_outflow
    closing_balance = opening_balance + cash_inflow - cash_outflow

    result = {
        "opening_balance": opening_balance,
        "cash_inflow": cash_inflow,
        "cash_outflow": cash_outflow,
        "additional_outflow": additional_outflow,
        "closing_balance": closing_balance
    }
    app.logger.info("Cash flow calculated: %s", result)
    return render_template("cash_flow.html", result=result, message=message)

# ---------------- Cash Flow Report ----------------
@app.route("/cash-flow-report")
def cash_flow_report():
    daily_flow = {}
    # Process Sales (inflow)
    for rec in sales_records:
        date_str = rec.get("sale_date", "")
        if date_str:
            daily_flow.setdefault(date_str, {"inflow": 0, "outflow": 0})
            daily_flow[date_str]["inflow"] += rec.get("total_sale", 0)
    # Process Sale Returns (reduce inflow)
    for rec in sale_return_records:
        date_str = rec.get("return_date", "")
        if date_str:
            daily_flow.setdefault(date_str, {"inflow": 0, "outflow": 0})
            daily_flow[date_str]["inflow"] -= rec.get("refund_amount", 0)
    # Process Purchases (outflow)
    for rec in purchase_records:
        date_str = rec.get("purchase_date", "")
        if date_str:
            daily_flow.setdefault(date_str, {"inflow": 0, "outflow": 0})
            daily_flow[date_str]["outflow"] += rec.get("total_purchase", 0)
    # Process Purchase Returns (reduce outflow)
    for rec in purchase_return_records:
        date_str = rec.get("return_date", "")
        if date_str:
            daily_flow.setdefault(date_str, {"inflow": 0, "outflow": 0})
            daily_flow[date_str]["outflow"] -= rec.get("total_return", 0)

    # Convert daily_flow to a sorted list
    daily_flow_sorted = sorted(daily_flow.items(), key=lambda x: x[0])
    daily_flow_list = []
    for date_str, flow in daily_flow_sorted:
        net = flow["inflow"] - flow["outflow"]
        daily_flow_list.append({
            "date": date_str,
            "inflow": flow["inflow"],
            "outflow": flow["outflow"],
            "net": net
        })

    # Group by week (using ISO week)
    weekly_flow = {}
    for date_str, flow in daily_flow.items():
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        iso_year, iso_week, _ = dt.isocalendar()
        week_key = f"{iso_year}-W{iso_week}"
        weekly_flow.setdefault(week_key, {"inflow": 0, "outflow": 0})
        weekly_flow[week_key]["inflow"] += flow["inflow"]
        weekly_flow[week_key]["outflow"] += flow["outflow"]

    weekly_flow_sorted = sorted(weekly_flow.items(), key=lambda x: x[0])
    weekly_flow_list = []
    for week_key, flow in weekly_flow_sorted:
        net = flow["inflow"] - flow["outflow"]
        weekly_flow_list.append({
            "week": week_key,
            "inflow": flow["inflow"],
            "outflow": flow["outflow"],
            "net": net
        })

    app.logger.info("Cash flow report generated: Daily: %s, Weekly: %s", daily_flow_list, weekly_flow_list)
    return render_template("cash_flow_report.html", daily_flow=daily_flow_list, weekly_flow=weekly_flow_list)

# ---------------- Inventory ----------------
@app.route("/inventory")
def inventory():
    inventory_summary = {}

    for rec in purchase_records:
        product = rec.get("product_name", "")
        if product:
            inventory_summary.setdefault(product, {"purchased": 0, "purchase_returns": 0, "sold": 0, "sales_returns": 0})
            inventory_summary[product]["purchased"] += rec.get("quantity", 0)

    for rec in purchase_return_records:
        product = rec.get("product_name", "")
        if product:
            inventory_summary.setdefault(product, {"purchased": 0, "purchase_returns": 0, "sold": 0, "sales_returns": 0})
            inventory_summary[product]["purchase_returns"] += rec.get("quantity", 0)

    for rec in sales_records:
        product = rec.get("product_name", "")
        if product:
            inventory_summary.setdefault(product, {"purchased": 0, "purchase_returns": 0, "sold": 0, "sales_returns": 0})
            inventory_summary[product]["sold"] += rec.get("quantity", 0)

    for rec in sale_return_records:
        product = rec.get("product_name", "")
        if product:
            inventory_summary.setdefault(product, {"purchased": 0, "purchase_returns": 0, "sold": 0, "sales_returns": 0})
            inventory_summary[product]["sales_returns"] += rec.get("quantity", 0)

    for product, data in inventory_summary.items():
        data["current_inventory"] = data["purchased"] - data["purchase_returns"] - data["sold"] + data["sales_returns"]

    app.logger.info("Inventory report generated")
    return render_template("inventory.html", summary=inventory_summary)

# ---------------- Supplier Ledger ----------------
@app.route("/supplier-ledger")
def supplier_ledger():
    ledger = {}
    # Process purchase records
    for rec in purchase_records:
        supplier = rec.get("supplier_name", "").strip()
        if supplier:
            ledger.setdefault(supplier, {"purchases": [], "purchase_returns": []})
            ledger[supplier]["purchases"].append(rec)
    # Process purchase return records
    for rec in purchase_return_records:
        supplier = rec.get("supplier_name", "").strip()
        if supplier:
            ledger.setdefault(supplier, {"purchases": [], "purchase_returns": []})
            ledger[supplier]["purchase_returns"].append(rec)
    # Calculate sums for each supplier
    for supplier, data in ledger.items():
        total_purchase = sum(item["total_purchase"] for item in data["purchases"])
        total_return = sum(item["total_return"] for item in data["purchase_returns"])
        net = total_purchase - total_return
        data["total_purchase"] = total_purchase
        data["total_return"] = total_return
        data["net"] = net
    app.logger.info("Supplier ledger generated")
    return render_template("supplier_ledger.html", ledger=ledger)

# ---------------- Aggregated Supplier Ledger PDF ----------------
@app.route("/supplier-ledger/pdf")
def supplier_ledger_pdf():
    # Generate an aggregated ledger for all suppliers.
    ledger = {}
    for rec in purchase_records:
        supplier = rec.get("supplier_name", "").strip()
        if supplier:
            ledger.setdefault(supplier, {"purchases": [], "purchase_returns": []})
            ledger[supplier]["purchases"].append(rec)
    for rec in purchase_return_records:
        supplier = rec.get("supplier_name", "").strip()
        if supplier:
            ledger.setdefault(supplier, {"purchases": [], "purchase_returns": []})
            ledger[supplier]["purchase_returns"].append(rec)
    # Calculate sums for each supplier
    for supplier, data in ledger.items():
        total_purchase = sum(item["total_purchase"] for item in data["purchases"])
        total_return = sum(item["total_return"] for item in data["purchase_returns"])
        net = total_purchase - total_return
        data["total_purchase"] = total_purchase
        data["total_return"] = total_return
        data["net"] = net

    # Create the aggregated PDF using the canvas.
    pdf_path = os.path.join(BASE_DIR, "supplier_ledgers.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750
    c.drawString(50, y, "Supplier Ledgers")
    y -= 30
    for supplier, data in ledger.items():
        if y < 100:
            c.showPage()
            y = 750
            c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Supplier: {supplier}")
        y -= 20
        c.drawString(70, y, f"Total Purchases: {data['total_purchase']}")
        y -= 20
        c.drawString(70, y, f"Total Purchase Returns: {data['total_return']}")
        y -= 20
        c.drawString(70, y, f"Net Amount: {data['net']}")
        y -= 30
    c.save()
    app.logger.info("Aggregated Supplier ledger PDF generated")
    return send_file(pdf_path, as_attachment=True)

# ---------------- Supplier Ledger PDF for Separate Supplier Using create_pdf ----------------
def format_number(n):
    """Format a number with commas (without decimals)."""
    return "{:,.0f}".format(n) if n else ""

def create_pdf(transactions, filename):
    """
    Creates a PDF file with an Excel-like grid based on the transactions array.
    The PDF includes a large company header, a table with the transactions,
    and a footer header row.
    
    Each transaction should be a dict with keys:
      - date: string
      - product: string
      - quantity: numeric (0 if not applicable)
      - balance: numeric
      Optionally, a transaction may include:
      - credit: numeric (if applicable)
    """
    # Calculate totals
    total_quantity = sum(t.get("quantity", 0) for t in transactions)
    total_credit = sum(t.get("credit", 0) for t in transactions)

    # Build table data for the Excel-like grid
    table_data = []
    header = ["DATE", "PRODUCT", "QUANTITY", "UNITY\nPRICE", "TOTAL\nPURCHASE"]
    table_data.append(header)

    # Add transaction rows. If quantity is nonzero, calculate unit price.
    for t in transactions:
        qty = t.get("quantity", 0)
        if qty:
            unit_price = int(t["balance"] / qty)
        else:
            unit_price = ""
        row = [
            t.get("date", ""),
            t.get("product", ""),
            format_number(qty) if qty else "",
            format_number(unit_price) if unit_price != "" else "",
            format_number(t.get("balance", ""))
        ]
        table_data.append(row)

    # Totals row: merge the first two cells for "TOTAL"
    totals_row = ["TOTAL", "", format_number(total_quantity), format_number(total_credit), ""]
    table_data.append(totals_row)

    # Create the PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Define a larger style for the company header
    big_header_style = ParagraphStyle(
        name="BigHeader",
        parent=styles["Title"],
        fontSize=18,
        alignment=1,  # Centered
        spaceAfter=20
    )

    elements = []

    # 1. Add the company header at the top with a bigger font
    company_header = Paragraph("HANIF PACKAGES (PVT) LTD.<br/>PURE GOLD", big_header_style)
    elements.append(company_header)

    # 2. Create the transactions table with an Excel-like grid
    col_widths = [80, 150, 80, 80, 80]
    trans_table = Table(table_data, colWidths=col_widths)
    table_style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (-1,-2), 'CENTER'),
        ('ALIGN', (2,1), (4,-2), 'RIGHT'),
        ('ALIGN', (2,-1), (3,-1), 'RIGHT'),
        ('SPAN', (0, len(table_data)-1), (1, len(table_data)-1))
    ])
    trans_table.setStyle(table_style)
    elements.append(trans_table)
    elements.append(Spacer(1, 12))

    # 3. Add a footer header row for reference
    footer = Paragraph("DATE   PRODUCT   QUANTITY   UNITY-PRICE   TOTAL-PURCHASE", styles["Normal"])
    elements.append(footer)

    # Build the PDF
    doc.build(elements)
    print(f"PDF generated successfully as {filename}")

@app.route("/supplier-ledger/<supplier_name>/pdf")
def supplier_ledger_supplier_pdf(supplier_name):
    """
    Generates a PDF ledger for a specific supplier using the create_pdf function.
    It compiles purchase and purchase return transactions for the supplier,
    sorts them by date, and then generates an Excel-like PDF ledger.
    """
    supplier = supplier_name.strip()
    transactions = []
    # Add purchase transactions
    for rec in purchase_records:
        if rec.get("supplier_name", "").strip().lower() == supplier.lower():
            transactions.append({
                "date": rec.get("purchase_date", ""),
                "product": rec.get("product_name", ""),
                "quantity": rec.get("quantity", 0),
                "balance": rec.get("total_purchase", 0)
            })
    # Add purchase return transactions (as credits)
    for rec in purchase_return_records:
        if rec.get("supplier_name", "").strip().lower() == supplier.lower():
            transactions.append({
                "date": rec.get("return_date", ""),
                "product": rec.get("product_name", ""),
                "quantity": rec.get("quantity", 0),
                "balance": rec.get("total_return", 0),
                "credit": rec.get("total_return", 0)
            })
    if not transactions:
        app.logger.error("No ledger records found for supplier %s", supplier)
        return "No ledger records found for supplier", 404

    # Optionally, sort transactions by date (assuming YYYY-MM-DD format)
    try:
        transactions.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
    except Exception as e:
        app.logger.warning("Could not sort transactions by date: %s", e)

    pdf_path = os.path.join(BASE_DIR, f"supplier_ledger_{supplier.replace(' ', '_')}.pdf")
    create_pdf(transactions, pdf_path)
    app.logger.info("Supplier ledger PDF generated for supplier %s using create_pdf", supplier)
    return send_file(pdf_path, as_attachment=True)

# ---------------- Invoice Generation ----------------
@app.route("/invoice/<int:sale_id>")
def invoice(sale_id):
    if 0 <= sale_id < len(sales_records):
        sale = sales_records[sale_id]
        app.logger.info("Generating invoice for sale_id %s", sale_id)
        return render_template("invoice.html", sale=sale, sale_id=sale_id)
    app.logger.error("Invoice not found for sale_id %s", sale_id)
    return "Invoice not found", 404

@app.route("/invoice/<int:sale_id>/pdf")
def generate_invoice_pdf(sale_id):
    if 0 <= sale_id < len(sales_records):
        sale = sales_records[sale_id]
        pdf_path = os.path.join(BASE_DIR, f"invoice_{sale_id}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "INVOICE")
        c.drawString(100, 730, f"Invoice ID: {sale_id}")
        c.drawString(100, 710, f"Date: {sale['sale_date']}")
        c.drawString(100, 690, f"Product: {sale['product_name']}")
        c.drawString(100, 670, f"Quantity: {sale['quantity']}")
        c.drawString(100, 650, f"Unit Price: {sale['unit_price']}")
        c.drawString(100, 630, f"Total Amount: {sale['total_sale']}")
        c.save()
        app.logger.info("PDF invoice generated for sale_id %s", sale_id)
        return send_file(pdf_path, as_attachment=True)
    app.logger.error("Invoice PDF not found for sale_id %s", sale_id)
    return "Invoice not found", 404

# ---------------- For Deployment ----------------
if __name__ == "__main__":
    # For local testing only; on PythonAnywhere, the WSGI server will import the application.
    app.run(debug=True)