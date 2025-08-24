import gradio as gr
from src.utils import is_valid_email,is_valid_phone
from src.notifications import record_user_details
from src import config
from src.ai import process_chat
import html



def update_button_state(text, is_processing):
            return gr.update(interactive=bool(text.strip()) and not is_processing)

def make_on_message_submit(self):

    def on_message_submit(user_msg, history, turn_count, details_recorded, processing):

        # 1) Guard empty
        if processing or not user_msg or not user_msg.strip():
            yield (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                    gr.update(value="", interactive=True), gr.update(interactive=False), history, turn_count, details_recorded, processing)
            return

        # 2) Immediately show user's message with placeholder
        processing = True
        history = list(history or [])
        history.append((html.escape(user_msg), "<div class='pending-ellipsis'><span>.</span><span>.</span><span>.</span></div>"))

        yield (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                gr.update(value="", interactive=False), gr.update(interactive=False), history, turn_count, details_recorded, processing)

        # 3) Contact gating
        if turn_count >= config.TURN_LIMIT and not (details_recorded or self.details_recorded):
            history[-1] = (user_msg, "✉️ Please share your contact details to continue.\n\n📧 Email\n📞 Phone\n📝 Notes (optional)")
            processing = False
            yield (gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                    gr.update(value="", interactive=True), gr.update(interactive=False), history, turn_count, details_recorded, processing)
            return

        # 4) Get model reply and replace placeholder
        reply, updated_history, updated_turn = process_chat(self, user_msg, history[:-1], turn_count)
        updated_history[-1] = (user_msg, reply)

        # If error handler asked to show contact, pop the form now
        if self.error_contact and not (details_recorded or self.details_recorded):
            self.error_contact = False  # reset so it doesn't keep popping
            processing = False
            yield (
                gr.update(visible=True),   # email
                gr.update(visible=True),   # phone
                gr.update(visible=True),   # notes
                gr.update(visible=True),   # submit_contact
                gr.update(value="", interactive=True),   # msg box enabled (or False if you want to force form)
                gr.update(interactive=False),            # send disabled (submit via form)
                updated_history, updated_turn, details_recorded, processing
            )
            return
        
        processing = False
        yield (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                gr.update(value="", interactive=True), gr.update(interactive=False), updated_history, updated_turn, details_recorded, processing)

    return on_message_submit

def make_on_contact_submit(self):
        def on_contact_submit(email_val, phone_val, notes_val, history, turn_count, details_recorded):
            history = list(history or [])
            if not is_valid_email(email_val):
                history.append(("Contact submission", "❌ Invalid email format."))
                return (gr.update(), gr.update(), gr.update(), gr.update(), history, turn_count, details_recorded)
            if not is_valid_phone(phone_val):
                history.append(("Contact submission", "❌ Invalid phone number format."))
                return (gr.update(), gr.update(), gr.update(), gr.update(), history, turn_count, details_recorded)

            record_user_details(email=email_val, phone=phone_val, notes=notes_val)
            self.details_recorded = True
            details_recorded = True
            history.append(("Contact details submitted", "✅ Your contact details have been saved, will reach out to you in case needed."))
            return (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                    history, turn_count, details_recorded)
        return on_contact_submit