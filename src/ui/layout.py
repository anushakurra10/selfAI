import gradio as gr
from src.ai.about_me import AboutMe
from .handlers import update_button_state, make_on_message_submit, make_on_contact_submit
import os


def build_ui():
    about_me = AboutMe()

    css_path = os.path.join(os.path.dirname(__file__), "theme.css")
    custom_css = open( 
        css_path
    ).read() if True else ""

    with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as app:
        turn_count = gr.State(0)
        details_recorded_state = gr.State(False)
        processing_state = gr.State(False)
        chatbot = gr.Chatbot(label=f"Chat with {about_me.name}",
        placeholder=f"<br>Please feel free to ask </br>.",
        show_copy_button=False)
        msg = gr.Textbox(placeholder="Ask something...", label="Your Message")
        send = gr.Button("SEND", interactive=False)

        email = gr.Textbox(label="Email", type="email", visible=False)
        phone = gr.Textbox(label="Phone", type="text", visible=False)
        notes = gr.Textbox(label="Notes (optional)", visible=False)
        submit_contact = gr.Button("Submit Contact Info", visible=False)

        # Bind handlers with ai captured via closures
        on_message_submit = make_on_message_submit(about_me)
        on_contact_submit = make_on_contact_submit(about_me)

        msg.change(fn=update_button_state, inputs=[msg, processing_state], outputs=send)


        # Generator-based submit for instant echo
        msg.submit(
            fn=on_message_submit,
            queue=True,
            inputs=[msg, chatbot, turn_count, details_recorded_state, processing_state],
            outputs=[email, phone, notes, submit_contact, msg, send, chatbot, turn_count, details_recorded_state, processing_state]
        )
        send.click(
            fn=on_message_submit,
            queue=True,
            inputs=[msg, chatbot, turn_count, details_recorded_state, processing_state],
            outputs=[email, phone, notes, submit_contact, msg, send, chatbot, turn_count, details_recorded_state, processing_state]
        )

        submit_contact.click(
            fn=on_contact_submit,
            inputs=[email, phone, notes, chatbot, turn_count, details_recorded_state],
            outputs=[email, phone, notes, submit_contact, chatbot, turn_count, details_recorded_state]
        )
    return app