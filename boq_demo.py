import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from io import BytesIO

# Page configuration
st.set_page_config(page_title="BOQ Cost Analyzer - DEMO", layout="wide", initial_sidebar_state="expanded")
st.title("📊 BOQ Cost Analyzer - DEMO VERSION")
st.markdown("**Test Drive** - Sample BOQ Data (100% Local Processing)")

# Initialize session state
if "df" not in st.session_state:
    # Create sample BOQ data
    sample_data = {
        "MATERIALS": [
            "Structural Steel Grade 250",
            "Concrete Mix (M30)",
            "Reinforcement Steel (Fe500)",
            "Cement (OPC 53 Grade)",
            "Brick (1st Class Quality)",
            "Sand (Fine Quality)",
            "Coarse Aggregate (20mm)",
            "Plaster of Paris",
            "Paint (Emulsion - 20L)",
            "Electrical Wire (2.5mm)",
            "PVC Pipe (110mm)",
            "Granite Tiles (2x2)",
            "Timber (Teak Grade)",
            "Door Frame (Steel)",
            "Window Glass (4mm)"
        ],
        "CODE": [
            "SS-001", "CM-002", "RS-003", "CEM-004", "BRK-005",
            "SND-006", "AGG-007", "POP-008", "PNT-009", "ELW-010",
            "PVC-011", "GRN-012", "TMB-013", "DRF-014", "WGL-015"
        ],
        "UNIT": [
            "MT", "CUM", "MT", "Bags", "Nos",
            "CUM", "CUM", "Bags", "Bucket", "Roll",
            "MT", "SQM", "CFT", "Nos", "SQM"
        ],
        "QTY": [45, 120, 28, 850, 15000, 180, 140, 200, 85, 450, 85, 3500, 450, 250, 800],
        "ACT PRICE": [52000, 5500, 58000, 380, 7.5, 2200, 1800, 450, 1250, 350, 2800, 650, 6500, 8000, 280],
        "ACT VALUE": [2340000, 660000, 1624000, 323000, 112500, 396000, 252000, 90000, 106250, 157500, 238000, 2275000, 2925000, 2000000, 224000]
    }
    
    st.session_state.df = pd.DataFrame(sample_data)
    st.session_state.original_values = {
        "QTY": pd.Series(sample_data["QTY"]),
        "ACT PRICE": pd.Series(sample_data["ACT PRICE"]),
        "ACT VALUE": pd.Series(sample_data["ACT VALUE"])
    }

# Sidebar info
st.sidebar.header("📋 DEMO Information")
st.sidebar.markdown("""
### What is This?
Sample BOQ with 15 construction materials to test the analyzer.

### Try This:
1. Edit quantities in the table
2. Change unit rates
3. Watch totals update automatically
4. See critical cost factors highlighted

### Features to Test:
✅ Editable QTY & ACT PRICE  
✅ Auto-recalculation  
✅ Cost metrics  
✅ Critical factor alerts  
✅ Interactive charts  

🔒 **100% Local** - No data leaves your browser
""")

st.sidebar.divider()
st.sidebar.info("This is sample data for demonstration only!")

# Main content
st.subheader("📝 Edit Sample BOQ Data")
st.markdown("**Click cells in QTY or ACT PRICE columns to edit**")

df_edited = st.session_state.df.copy()

# Data Editor - Only QTY and ACT PRICE editable
col_config = {
    "MATERIALS": st.column_config.TextColumn("Materials", disabled=True),
    "CODE": st.column_config.TextColumn("Code", disabled=True),
    "UNIT": st.column_config.TextColumn("Unit", disabled=True),
    "QTY": st.column_config.NumberColumn("QTY", min_value=0),
    "ACT PRICE": st.column_config.NumberColumn("Act Price", min_value=0),
    "ACT VALUE": st.column_config.NumberColumn("Act Value", disabled=True),
}

edited_df = st.data_editor(
    df_edited,
    column_config=col_config,
    hide_index=False,
    use_container_width=True,
    key="boq_editor"
)

# Recalculate ACT VALUE based on edits
edited_df["ACT VALUE"] = edited_df["QTY"] * edited_df["ACT PRICE"]
st.session_state.df = edited_df

# Calculate totals
original_total = st.session_state.original_values["ACT VALUE"].sum()
new_total = edited_df["ACT VALUE"].sum()
cost_difference = new_total - original_total
percentage_change = (cost_difference / original_total * 100) if original_total != 0 else 0

# Display metrics
st.subheader("💰 Cost Summary")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric("Original Total", f"${original_total:,.2f}")

with metric_col2:
    st.metric("New Total", f"${new_total:,.2f}")

with metric_col3:
    delta_color = "inverse" if cost_difference > 0 else "normal"
    st.metric(
        "Cost Difference",
        f"${cost_difference:,.2f}",
        delta=f"{percentage_change:+.2f}%",
        delta_color=delta_color
    )

with metric_col4:
    st.metric("Number of Items", len(edited_df))

# Calculate cost impact per item
edited_df["Cost_Impact"] = edited_df["ACT VALUE"] - st.session_state.original_values["ACT VALUE"]
edited_df["Impact_Percentage"] = (edited_df["Cost_Impact"] / st.session_state.original_values["ACT VALUE"] * 100).replace([np.inf, -np.inf], 0).fillna(0)

# Identify critical items (items with significant changes)
st.subheader("🚨 Critical Cost Factors")

critical_items = edited_df[edited_df["Cost_Impact"].abs() > 0].copy()
critical_items = critical_items.sort_values("Cost_Impact", ascending=False, key=abs)

if len(critical_items) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Items with Increased Costs:**")
        increased = critical_items[critical_items["Cost_Impact"] > 0].head(5)
        if len(increased) > 0:
            for idx, row in increased.iterrows():
                st.warning(f"📈 {row['MATERIALS'][:40]} - **+${row['Cost_Impact']:,.2f}** ({row['Impact_Percentage']:+.1f}%)")
        else:
            st.info("No items with increased costs")
    
    with col2:
        st.write("**Items with Decreased Costs:**")
        decreased = critical_items[critical_items["Cost_Impact"] < 0].head(5)
        if len(decreased) > 0:
            for idx, row in decreased.iterrows():
                st.success(f"📉 {row['MATERIALS'][:40]} - **${row['Cost_Impact']:,.2f}** ({row['Impact_Percentage']:+.1f}%)")
        else:
            st.info("No items with decreased costs")
else:
    st.info("No changes detected - Edit quantities or prices to see impact")

# Top 10 Most Expensive Items with Cost Impact Visualization
st.subheader("📊 Top 10 Most Expensive Line Items (With Cost Impact)")

top_10 = edited_df.nlargest(10, "ACT VALUE").copy()
top_10 = top_10.sort_values("ACT VALUE", ascending=True)

# Determine color based on cost impact
colors = []
for impact in top_10["Cost_Impact"]:
    if impact > 0:
        colors.append("#EF553B")  # Red - increased cost
    elif impact < 0:
        colors.append("#00CC96")  # Green - decreased cost
    else:
        colors.append("#636EFA")  # Blue - no change

fig = go.Figure()

fig.add_trace(go.Bar(
    y=top_10["MATERIALS"].str[:30],
    x=top_10["ACT VALUE"],
    orientation='h',
    marker=dict(color=colors),
    text=[f"${val:,.0f}<br>Impact: ${impact:+,.0f}" 
          for val, impact in zip(top_10["ACT VALUE"], top_10["Cost_Impact"])],
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Total Value: $%{x:,.2f}<br>Cost Impact: %{text}<extra></extra>',
    showlegend=False
))

fig.update_layout(
    title="Top 10 Most Expensive Items (Color-coded by Cost Impact)",
    xaxis_title="Amount ($)",
    yaxis_title="Materials",
    height=500,
    hovermode='closest',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=10),
    margin=dict(l=200)
)

st.plotly_chart(fig, use_container_width=True)

# Add legend explanation
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🔴 **Red** = Cost Increased (high impact)")
with col2:
    st.markdown("🟢 **Green** = Cost Decreased (savings)")
with col3:
    st.markdown("🔵 **Blue** = No Change")

# Additional analysis: Sensitivity Analysis
st.subheader("📈 Sensitivity Analysis - Items Most Affected by Changes")

sensitivity_df = edited_df[edited_df["Cost_Impact"].abs() > 0].copy()
sensitivity_df = sensitivity_df.nlargest(8, "Cost_Impact", key=abs)
sensitivity_df = sensitivity_df.sort_values("Cost_Impact", ascending=True)

if len(sensitivity_df) > 0:
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        y=sensitivity_df["MATERIALS"].str[:30],
        x=sensitivity_df["Cost_Impact"],
        orientation='h',
        marker=dict(
            color=sensitivity_df["Cost_Impact"],
            colorscale='RdYlGn_r',
            showscale=False
        ),
        text=[f"${val:+,.0f}" for val in sensitivity_df["Cost_Impact"]],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Cost Change: $%{x:+,.2f}<extra></extra>',
        showlegend=False
    ))
    
    fig2.update_layout(
        title="Items with Highest Cost Changes (Sensitivity to Edits)",
        xaxis_title="Cost Change ($)",
        yaxis_title="Materials",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10),
        margin=dict(l=200)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No changes yet - Edit quantities or prices to see sensitivity analysis")

# Download button for updated BOQ
st.divider()
st.subheader("💾 Export Updated BOQ")
output_excel = BytesIO()
with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    edited_df.to_excel(writer, sheet_name='BOQ', index=False)
output_excel.seek(0)

st.download_button(
    label="📥 Download Sample BOQ (Excel)",
    data=output_excel,
    file_name="Sample_BOQ_Updated.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()
st.markdown("""
### 🎯 Ready to Use Your Own BOQ?
Download the **full version** from the files:
- `boq_analyzer.py` - Upload your own files
- Works with Excel & PDF
- 100% local processing
- All features available
""")
