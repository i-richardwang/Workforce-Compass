"""
Workforce Compass - Application Entry Point

This application (Workforce Compass / 人才金字塔预测) predicts multi-year trends in
organizational talent flow and structure. It forecasts 1-5 year changes based on current
personnel data and key parameters, helping HR and management with strategic talent planning.
"""
import streamlit as st
from ui.layouts import AppLayout


def main() -> None:
    """
    Application main entry function

    Initialize application layout and render the entire UI
    """
    # Create application layout instance
    layout = AppLayout()
    # Render application interface
    layout.render()


if __name__ == "__main__":
    main()
