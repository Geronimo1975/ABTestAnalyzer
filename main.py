import streamlit as st
import plotly.graph_objects as go
from utils import (calculate_efficiency_rate, calculate_accuracy_rate,
                  calculate_confidence_interval, calculate_statistical_significance,
                  get_relative_improvement, calculate_utilization_rate)

def create_comparison_plot(control_rate, test_rate, 
                         control_ci, test_ci, p_value, metric_name):
    """Create a comparison plot with error bars and color coding"""
    # Determine colors based on statistical significance and improvement
    is_significant = p_value < 0.05
    is_improvement = test_rate > control_rate

    if not is_significant:
        bar_colors = ['lightgrey', 'lightgrey']
    else:
        if is_improvement:
            bar_colors = ['lightgrey', '#28a745']  # Green for significant improvement
        else:
            bar_colors = ['lightgrey', '#dc3545']  # Red for significant decline

    fig = go.Figure()

    # Add bars for control and test groups with hover text
    for i, (label, rate, ci, color) in enumerate([
        ('Current Process', control_rate, control_ci, bar_colors[0]),
        ('New Process', test_rate, test_ci, bar_colors[1])
    ]):
        fig.add_trace(go.Bar(
            name=label,
            x=[label],
            y=[rate * 100],
            width=[0.4],
            marker_color=color,
            error_y=dict(
                type='data',
                array=[(ci[1] - rate) * 100],
                arrayminus=[(rate - ci[0]) * 100],
                visible=True
            ),
            hovertemplate=(
                f"<b>{label}</b><br>" +
                f"{metric_name}: %{{y:.2f}}%<br>" +
                f"95% CI: [{ci[0]:.2%}, {ci[1]:.2%}]<br>" +
                "<extra></extra>"
            )
        ))

    # Add significance annotation
    significance_text = (
        "✓ Statistically Significant" if is_significant
        else "○ Not Statistically Significant"
    )

    fig.update_layout(
        title={
            'text': f'{metric_name} Comparison<br>' +
                   f'<sup>{significance_text}</sup>',
            'x': 0.5,
            'xanchor': 'center'
        },
        yaxis_title=f'{metric_name} (%)',
        showlegend=False,
        height=400,
        hovermode='closest'
    )

    return fig

def main():
    st.set_page_config(
        page_title="SAP WM Process Comparison",
        layout="wide"
    )

    st.title("SAP Warehouse Management Process Comparison")

    st.markdown("""
    This tool helps you analyze and compare warehouse management processes to determine if changes 
    are statistically significant. Select a metric and enter the data for both current and new processes.
    """)

    # Metric selection
    metric = st.selectbox(
        "Select Metric to Compare",
        ["Picking Efficiency", "Storage Utilization", "Inventory Accuracy", "Order Fulfillment"]
    )

    # Input section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Process")
        if metric in ["Picking Efficiency", "Order Fulfillment"]:
            control_success = st.number_input(
                "Successful Tasks/Orders",
                min_value=0,
                value=100,
                step=1
            )
            control_total = st.number_input(
                "Total Tasks/Orders",
                min_value=1,
                value=1000,
                step=1
            )
        else:  # Storage Utilization, Inventory Accuracy
            control_success = st.number_input(
                "Used Capacity/Correct Items",
                min_value=0,
                value=800,
                step=1
            )
            control_total = st.number_input(
                "Total Capacity/Items",
                min_value=1,
                value=1000,
                step=1
            )

    with col2:
        st.subheader("New Process")
        if metric in ["Picking Efficiency", "Order Fulfillment"]:
            test_success = st.number_input(
                "Successful Tasks/Orders (New)",
                min_value=0,
                value=120,
                step=1
            )
            test_total = st.number_input(
                "Total Tasks/Orders (New)",
                min_value=1,
                value=1000,
                step=1
            )
        else:  # Storage Utilization, Inventory Accuracy
            test_success = st.number_input(
                "Used Capacity/Correct Items (New)",
                min_value=0,
                value=850,
                step=1
            )
            test_total = st.number_input(
                "Total Capacity/Items (New)",
                min_value=1,
                value=1000,
                step=1
            )

    # Calculate metrics
    if metric in ["Picking Efficiency", "Order Fulfillment"]:
        control_rate = calculate_efficiency_rate(control_success, control_total)
        test_rate = calculate_efficiency_rate(test_success, test_total)
    else:  # Storage Utilization, Inventory Accuracy
        control_rate = calculate_accuracy_rate(control_success, control_total)
        test_rate = calculate_accuracy_rate(test_success, test_total)

    control_ci = calculate_confidence_interval(control_success, control_total)
    test_ci = calculate_confidence_interval(test_success, test_total)

    chi2, p_value = calculate_statistical_significance(
        control_success, control_total, test_success, test_total
    )

    relative_improvement = get_relative_improvement(control_rate, test_rate)

    # Results section
    st.header("Results")

    # Display rates
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Current Process Rate",
            f"{control_rate:.2%}",
            delta=None
        )

    with col2:
        st.metric(
            "New Process Rate",
            f"{test_rate:.2%}",
            delta=f"{relative_improvement:+.2f}%"
        )

    with col3:
        st.metric(
            "Statistical Significance",
            f"{(1 - p_value) * 100:.1f}%",
            delta=None
        )

    # Visualization
    fig = create_comparison_plot(
        control_rate, test_rate, control_ci, test_ci, p_value, metric
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed analysis
    st.subheader("Detailed Analysis")

    st.markdown(f"""
    - **Current Process Confidence Interval (95%)**: {control_ci[0]:.2%} to {control_ci[1]:.2%}
    - **New Process Confidence Interval (95%)**: {test_ci[0]:.2%} to {test_ci[1]:.2%}
    - **P-value**: {p_value:.4f}
    """)

    # Interpretation
    st.subheader("Interpretation")

    if p_value < 0.05:
        st.success(f"""
        **Statistically Significant Improvement**

        There is strong evidence (p < 0.05) that the difference between the current and new
        processes is not due to random chance. The new process shows a
        {abs(relative_improvement):.1f}% {'improvement' if relative_improvement > 0 else 'decline'}.
        """)
    else:
        st.warning("""
        **Not Statistically Significant**

        There isn't enough evidence to conclude that the difference between the processes
        is not due to random chance. Consider:
        - Collecting more data
        - Reviewing process changes
        - Analyzing other metrics
        """)

if __name__ == "__main__":
    main()