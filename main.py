import streamlit as st
import plotly.graph_objects as go
from utils import (calculate_conversion_rate, calculate_confidence_interval,
                  calculate_statistical_significance, get_relative_improvement)

def create_conversion_comparison_plot(control_rate, test_rate, 
                                    control_ci, test_ci):
    """Create a comparison plot with error bars"""
    fig = go.Figure()
    
    # Add bars for control and test groups
    fig.add_trace(go.Bar(
        x=['Control', 'Test'],
        y=[control_rate * 100, test_rate * 100],
        width=[0.4, 0.4],
        error_y=dict(
            type='data',
            array=[
                (control_ci[1] - control_rate) * 100,
                (test_ci[1] - test_rate) * 100
            ],
            arrayminus=[
                (control_rate - control_ci[0]) * 100,
                (test_rate - test_ci[0]) * 100
            ],
            visible=True
        )
    ))
    
    fig.update_layout(
        title='Conversion Rate Comparison',
        yaxis_title='Conversion Rate (%)',
        showlegend=False,
        height=400
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="A/B Test Calculator",
        layout="wide"
    )
    
    st.title("A/B Test Statistical Significance Calculator")
    
    st.markdown("""
    This calculator helps you determine if your A/B test results are statistically significant.
    Enter the number of conversions and total visitors for both your control and test groups.
    """)
    
    # Input section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Control Group (A)")
        control_conv = st.number_input(
            "Control Group Conversions",
            min_value=0,
            value=100,
            step=1
        )
        control_size = st.number_input(
            "Control Group Total Size",
            min_value=1,
            value=1000,
            step=1
        )
    
    with col2:
        st.subheader("Test Group (B)")
        test_conv = st.number_input(
            "Test Group Conversions",
            min_value=0,
            value=120,
            step=1
        )
        test_size = st.number_input(
            "Test Group Total Size",
            min_value=1,
            value=1000,
            step=1
        )
    
    # Calculate metrics
    control_rate = calculate_conversion_rate(control_conv, control_size)
    test_rate = calculate_conversion_rate(test_conv, test_size)
    
    control_ci = calculate_confidence_interval(control_conv, control_size)
    test_ci = calculate_confidence_interval(test_conv, test_size)
    
    chi2, p_value = calculate_statistical_significance(
        control_conv, control_size, test_conv, test_size
    )
    
    relative_improvement = get_relative_improvement(control_rate, test_rate)
    
    # Results section
    st.header("Results")
    
    # Display conversion rates
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Control Conversion Rate",
            f"{control_rate:.2%}",
            delta=None
        )
    
    with col2:
        st.metric(
            "Test Conversion Rate",
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
    fig = create_conversion_comparison_plot(
        control_rate, test_rate, control_ci, test_ci
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results
    st.subheader("Detailed Analysis")
    
    st.markdown(f"""
    - **Control Group Confidence Interval (95%)**: {control_ci[0]:.2%} to {control_ci[1]:.2%}
    - **Test Group Confidence Interval (95%)**: {test_ci[0]:.2%} to {test_ci[1]:.2%}
    - **P-value**: {p_value:.4f}
    """)
    
    # Interpretation
    st.subheader("Interpretation")
    
    if p_value < 0.05:
        st.success("""
        **Statistically Significant Result**
        
        There is strong evidence (p < 0.05) that the difference between the control and test
        groups is not due to random chance.
        """)
    else:
        st.warning("""
        **Not Statistically Significant**
        
        There isn't enough evidence to conclude that the difference between the control and
        test groups is not due to random chance. Consider:
        - Running the test longer
        - Increasing sample sizes
        - Reviewing your test setup
        """)

if __name__ == "__main__":
    main()
