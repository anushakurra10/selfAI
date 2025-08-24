from .sanitizers import clean_reply 
import json
from src.utils import is_malicious,handle_exception
from .data_loader import system_prompt 

def process_chat(self, message, history, turn_count):
        if is_malicious(message):
            history.append((message, "🚫 Restricted input detected."))
            return "🚫 Restricted input detected.", history, turn_count

        try:
            turn_count += 1
            messages = [{"role": "system", "content": system_prompt(self)}] + [
                {"role": "user" if i % 2 == 0 else "assistant", "content": pair[0 if i % 2 == 0 else 1]}
                for i, pair in enumerate(history)
            ] + [{"role": "user", "content": message}]

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.tools
            )

            choice = response.choices[0]
            if choice.finish_reason == "tool_calls":
                messages.append(choice.message)
                messages += handle_tool_call(choice.message.tool_calls)
                reply = "Thanks — I've logged that as a follow‑up. If you’d like, share your email, and I can follow up offline."
                
            else:
                reply = clean_reply(choice.message.content)

            history.append((message, reply))
            return reply, history, turn_count

        except Exception as e:
            error_reply = handle_exception(self,e)
            history.append((message, error_reply))
            return error_reply, history, turn_count



def handle_tool_call( tool_calls):
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