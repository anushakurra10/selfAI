import gradio as gr
from src.ui.layout import build_ui

if __name__ == "__main__":
    app = build_ui()
    app.launch()

