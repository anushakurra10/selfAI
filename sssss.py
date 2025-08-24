import os
import json
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import html

load_dotenv(override=True)

TURN_LIMIT = int(os.getenv("TURN_LIMIT", 5))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(SCRIPT_DIR, "knowledge_base", "me.pdf")

# === Push Notification ===
def push(message: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"[{timestamp}] {message}"
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_TOKEN"),
                "user": os.getenv("PUSHOVER_USER"),
                "message": message,
            }, timeout=6
        )
    except Exception as err:
        print("Don't crash UI if push fails",err);
        # Don't crash UI if push fails
        pass

# === Tool Functions ===
def record_user_details(email, phone, notes=""):
    push(f"Recording user: Email: {email} | Phone: {phone} | Notes: {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Unanswered question recorded: {question}")
    return {"recorded": "ok"}

# === Validators ===
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def is_valid_phone(phone):
    return re.match(r"^\+?\d[\d\- ]{7,15}$", phone) is not None

# === Output sanitizers ===
BLOCKED_PHRASES = {
    "If you’re open to connecting further, feel free to share your email or phone number, and I’ll reach out to you.🙂",
}

def clean_reply(text: str) -> str:
    if not text:
        return text
    for p in BLOCKED_PHRASES:
        if p in text:
            text = text.replace(p, "")
    # Hide internal tool names from user-visible text
    text = re.sub(r"record_user_details|record_unknown_question", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text).strip()

# === Tool Schemas ===
record_user_details_json = {
    "name": "record_user_details",
    "description": "Record an interested user's contact information.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "User's email address"},
            "phone": {"type": "string", "description": "User's phone number"},
            "notes": {"type": "string", "description": "Additional context"}
        },
        "required": ["email", "phone"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Record any question that couldn't be answered.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "Unanswered question"}
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

TOOLS = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]

class AboutMe:
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("API_KEY"),
        )
        self.name = os.getenv("ME", "Someone Mysterious")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4")
        self.about_me_text = self.load_profile()
        self.details_recorded = False
        self.error_contact = False

    def load_profile(self):
        if not os.path.exists(PDF_PATH):
            print(f"PDF not found at {PDF_PATH}")
            return ""
        reader = PdfReader(PDF_PATH)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def system_prompt(self):
        return (
        f"You are {self.name}. Speak ONLY in first person (I, me, my) about your own work and experience. Never refer to yourself as '{self.name}' or 'they'."
        f"Always answer using 'I', 'me', and 'my' (never 'they' or '{self.name}' to refer to yourself). "
        f"Keep a professional, warm tone as if speaking with a hiring manager.\n\n"
        f"You are answering questions on {self.name}'s profile, "
        f"specifically those related to their career, background, skills, and experience.\n\n"
        
        f"Your role is to represent {self.name} authentically and professionally to help them get hired. "
        f"Assume you are speaking directly to a hiring manager or prospective client who is evaluating {self.name} "
        f"for a job or opportunity. Your tone should be confident, warm, and professional.\n\n"
        
        f"Below is {self.name}'s profile information, which you should use to answer relevant questions:\n\n"
        f"## Profile:\n{self.about_me_text}\n\n"
        "Do not invent personal details; if a question is unrelated to professional profile, call record_unknown_question"
        "Be honest.If you are unsure on how to answer any question, use your record_unknown_question tool to record the question that you couldn't answerr — even if it seems minor or unrelated to career topics.\n\n"
        
        "If a user begins a conversation, guide them toward sharing their email so they can be contacted directly. "
        "Ask for their email address politely and record it using your record_user_details tool for future use.\n\n"
        
        "Do not reference internal tools or systems when requesting contact information — just ask in a natural and professional manner.\n\n"
        
        "Decline any requests involving unethical actions, malicious code, or unauthorized access. Make it clear that you cannot assist with such queries.\n\n"
        
        "Always stay in character. Represent {self.name} with professionalism, and politely reject any unethical or inappropriate questions."
    )

    def system_prompt444(self):
        return (
            f"You are {self.name}. Speak ONLY in first person (I, me, my). "
            f"Never refer to yourself as '{self.name}' or 'they'. Keep a professional, warm tone as if speaking with a hiring manager.\n\n"
            f"You are answering questions about my career, background, skills, and experience.\n\n"
            f"Use ONLY the profile below to answer:\n\n## Profile:\n{self.about_me_text}\n\n"
            "If you are unsure how to answer a question, silently log it with the unknown-question tool; "
            "do not mention tools in your reply. Ask for contact details naturally when appropriate, "
            "without referencing internal tools or systems. Politely decline unethical or malicious requests."
        )


    def handle_tool_call(self, tool_calls):
        responses = []
        for call in tool_calls:
            tool_name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"Tool call received: {tool_name}")
            tool_func = globals().get(tool_name)
            if tool_func:
                result = tool_func(**args)
                responses.append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": call.id
                })
        return responses

    def handle_exception(self, e):
        print("Error in chat function:", e)
        
        # If we don't have contact recorded yet, ask the UI to open the form
        if not self.details_recorded:
            self.error_contact = True

        if isinstance(e, requests.exceptions.Timeout):
            return "⏱️ Server timeout. Please try again later."

        if isinstance(e, requests.exceptions.ConnectionError):
            return "🔌 I’m having trouble connecting. Please try again later."

        try:
            error_message = e.args[0]
            match = re.search(r"'X-RateLimit-Reset': '(\d+)'", error_message)
            if match:
                reset_ts = int(match.group(1)) / 1000
                reset_time = datetime.fromtimestamp(reset_ts).strftime("%Y-%m-%d %H:%M:%S")
                return (
                    f"🚫 I’m on a break. Please be back after {reset_time}."
                )
        except Exception:
            pass

        return "⚠️ Something went wrong. Please try again later."

    def is_malicious(self, text):
        return any(bad in text.lower() for bad in ["eval", "exec", "subprocess", "os.system", "rm -rf", "curl", "wget"])

    def chat_fn(self, message, history, turn_count):
        if self.is_malicious(message):
            history.append((message, "🚫 Restricted input detected."))
            return "🚫 Restricted input detected.", history, turn_count

        try:
            turn_count += 1
            messages = [{"role": "system", "content": self.system_prompt()}] + [
                {"role": "user" if i % 2 == 0 else "assistant", "content": pair[0 if i % 2 == 0 else 1]}
                for i, pair in enumerate(history)
            ] + [{"role": "user", "content": message}]

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=TOOLS
            )

            choice = response.choices[0]
            if choice.finish_reason == "tool_calls":
                messages.append(choice.message)
                messages += self.handle_tool_call(choice.message.tool_calls)
                reply = "Thanks — I've logged that as a follow‑up. If you’d like, share your email, and I can follow up offline."
                
            else:
                reply = clean_reply(choice.message.content)

            history.append((message, reply))
            return reply, history, turn_count

        except Exception as e:
            error_reply = self.handle_exception(e)
            history.append((message, error_reply))
            return error_reply, history, turn_count


if __name__ == "__main__":
    ai = AboutMe()

    custom_css = """
        /* Global look & feel */
        .gradio-container { 
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, \"Apple Color Emoji\", \"Segoe UI Emoji\" !important;
            background: linear-gradient(180deg, #fafaff 0%, #f5f7fb 100%);
        }
        .gradio-container .prose, .gradio-container .prose * { font-family: inherit !important; }

        /* Chatbot card */
         .gradio-container .bubble-wrap { 
            background: #ffffff !important; 
            border: 2px solid var(--border-color-accent-subdued) !important; 
            border-radius: 18px !important; 
            box-shadow: 0 6px 20px rgba(43, 55, 91, 0.08) !important;
        }

        /* Assistant bubble */
        .gradio-container .assistant .message, 
        .gradio-container .bot .message, 
        .gradio-container .bubble.assistant { 
            background: #ffffff !important; 
        }
        /* User bubble */
        .gradio-container .user .message, 
        .gradio-container .self .message, 
        .gradio-container .bubble.user { 
            background: #eef2ff !important; 
            border-color: #c7d2fe !important; 
        }

        /* Input area */
        .gradio-container textarea, .gradio-container input[type=text], .gradio-container input[type=email] { 
            border-radius: 12px !important; 
            border: 2px solid var(--border-color-accent-subdued) !important; 
            box-shadow: 0 1px 0 rgba(20,20,20,0.03) inset; 
        }
        .gradio-container button { 
            border-radius: 12px !important; 
            box-shadow: 0 4px 14px rgba(109, 99, 255, 0.15) !important;
            border: 2px solid var(--border-color-accent-subdued) !important; 
            color: #362ebb !important;
            background-color: var(--border-color-accent-subdued) !important;
        }

        /* Hide footer */
        footer {display:none !important;}

        /* Hide message action icons (delete/undo/retry/copy) – several selectors to cover variants */
        button[aria-label="Clear"],
        button[aria-label*="Clear"],
        button[aria-label="Undo"],
        button[aria-label*="Undo"],
        button[aria-label="Retry"],
        button[aria-label*="Retry"],
        button[aria-label="Copy"],
        button[aria-label*="Copy"],
        .copy-btn, .retry-btn, .delete-btn,
        .message-actions, .actions, .message-buttons,
        .chatbot .actions, .chat .actions { display: none !important; }

        /* Slightly tighten spacing */
        .gradio-container .chatbot .wrap { padding: 10px 14px !important; }

        /* Ellipsis (typing) message: show only big dots, no bubble */
        .bot div:has(.pending-ellipsis) {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }

   

/* Animated dots */
.pending-ellipsis {
    display: inline-flex;
    gap: 4px;
    font-size: 28px;
    line-height: 1.2;
    font-weight: 800;
    color: #6b6f76;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.pending-ellipsis span {
    animation: blink 1.4s infinite both;
}

.pending-ellipsis span:nth-child(2) {
    animation-delay: 0.2s;
}
.pending-ellipsis span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes blink {
    0% { opacity: 0.2; transform: translateY(0); }
    20% { opacity: 1; transform: translateY(-3px); }
    100% { opacity: 0.2; transform: translateY(0); }
}



    
    """

    with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
        turn_count = gr.State(0)
        details_recorded_state = gr.State(False)
        processing_state = gr.State(False)
        chatbot = gr.Chatbot(label=f"Chat with {ai.name}",
        placeholder=f"<br>Please feel free to ask </br>.",
        show_copy_button=False)
        msg = gr.Textbox(placeholder="Ask something...", label="Your Message")
        send = gr.Button("SEND", interactive=False)

        email = gr.Textbox(label="Email", type="email", visible=False)
        phone = gr.Textbox(label="Phone", type="text", visible=False)
        notes = gr.Textbox(label="Notes (optional)", visible=False)
        submit_contact = gr.Button("Submit Contact Info", visible=False)


        def update_button_state(text, is_processing):
            return gr.update(interactive=bool(text.strip()) and not is_processing)


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
            if turn_count >= TURN_LIMIT and not (details_recorded or ai.details_recorded):
                history[-1] = (user_msg, "✉️ Please share your contact details to continue.\n\n📧 Email\n📞 Phone\n📝 Notes (optional)")
                processing = False
                yield (gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                       gr.update(value="", interactive=True), gr.update(interactive=False), history, turn_count, details_recorded, processing)
                return

            # 4) Get model reply and replace placeholder
            reply, updated_history, updated_turn = ai.chat_fn(user_msg, history[:-1], turn_count)
            updated_history[-1] = (user_msg, reply)

            # If error handler asked to show contact, pop the form now
            if ai.error_contact and not (details_recorded or ai.details_recorded):
                ai.error_contact = False  # reset so it doesn't keep popping
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

        def on_contact_submit(email_val, phone_val, notes_val, history, turn_count, details_recorded):
            history = list(history or [])
            if not is_valid_email(email_val):
                history.append(("Contact submission", "❌ Invalid email format."))
                return (gr.update(), gr.update(), gr.update(), gr.update(), history, turn_count, details_recorded)
            if not is_valid_phone(phone_val):
                history.append(("Contact submission", "❌ Invalid phone number format."))
                return (gr.update(), gr.update(), gr.update(), gr.update(), history, turn_count, details_recorded)

            record_user_details(email=email_val, phone=phone_val, notes=notes_val)
            ai.details_recorded = True
            details_recorded = True
            history.append(("Contact details submitted", "✅ Your contact details have been saved, will reach out to you in case needed."))
            return (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                    history, turn_count, details_recorded)

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

    demo.launch()
