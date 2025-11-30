# Global Research Analytics Dashboard  
### *An Interactive Scientometric Analysis Platform (Streamlit)*

This repository contains an advanced **Streamlit-based research analytics dashboard** designed for global scientometric evaluation, benchmarking, and insight generation.  
Inspired by dashboards used by **Leiden Ranking, OECD, Web of Science, Scopus**, and global policy organizations.

---

## Features

### Executive-Level Analytics
- Research productivity  
- Citation influence  
- Research quality (CNCI)  
- Excellence indicators (Top 1% & Top 10%)  
- Collaboration strength  

### Professionally Designed UI
- **Power BI Premium Dark theme**  
- KPI Cards  
- 2×2 analytic grid  
- Clean layout  

### Advanced Scientometric KPIs
- Citation Efficiency  
- Excellence Rate (Top 1%)  
- High-Impact Rate (Top 10%)  
- Citation Velocity  
- Citation Dominance  
- Collaboration Advantage  
- Quality Weighted Output  
- Citation Quality Index  
- Rank Efficiency  
- Impact per Excellence  

### Full Interactive Filtering
- Multi-country selection  
- Multi-year dropdown  
- Search country  

### Beautiful Visualizations
- Bar charts  
- Pie charts  
- Year-trend charts  
- Leaderboard tables  

### Drillthrough Dashboard
A dedicated country detail page including:
- KPIs  
- Trend charts  
- Excellence indicators  
- Pie charts  
- Interpretative insights  

---

## Dataset Summary

| Column | Description |
|--------|-------------|
| Name | Country |
| Web of Science Documents | Total publications |
| Times Cited | Total citations |
| Collab-CNCI | Collaboration CNCI |
| Rank | Global research rank |
| % Docs Cited | % of cited documents |
| Category Normalized Citation Impact | Field-adjusted citation impact |
| % Documents in Top 1% | Elite research output |
| % Documents in Top 10% | High-impact output |
| Documents in Top 1% | Count of Top 1% papers |
| Documents in Top 10% | Count of Top 10% papers |
| year | Reporting year |

---

## Project Structure

root/
│── app.py
│── requirements.txt
│── README.md
│── data/
│ └── publications.csv
│── src/
│ ├── load_data.py
│ ├── charts.py
│ └── eda_functions.py
│── .gitignore


---

## Installation Instructions

### 1️⃣ Clone this repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

## 💻 Installation Instructions

### 2️⃣ Create & activate virtual environment
```bash
python -m venv opsa
opsa\Scripts\activate     # Windows
```

```bash
pip install -r requirements.txt
```
```bash
streamlit run app.py
```

## Key Visuals Included

- Documents by Country  
- Citations by Country  
- CNCI Comparison  
- Quality Weighted Output  
- Citation Efficiency  
- Top 1% & Top 10% Outputs  
- Collaboration Advantage  
- Year-wise Trends  
- Pie Charts for Document Distribution  
- Correlation Heatmap  

---

## KPI Definitions

### **Citation Efficiency**  
**Times Cited / Documents**

### **Excellence Rate (Top 1%)**  
**Top 1% Docs / Total Docs**

### **High Impact Rate (Top 10%)**  
**Top 10% Docs / Total Docs**

### **Collaboration Advantage**  
**Collab-CNCI / CNCI**

### **Quality Weighted Output**  
**Documents × CNCI**

### **Citation Velocity**  
**Citations / (CurrentYear - year + 1)**

### **Citation Dominance**  
**Times Cited / TotalCitations**

### **Rank Efficiency**  
**Documents / Rank**

---

## Recommendations

- Expand **international collaborations** to boost citation impact.  
- Improve publication pipelines for **top-tier journals**.  
- Prioritize **quality over quantity** in national research output.  

