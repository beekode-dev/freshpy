import cohere
import quztools as qten
import os

IsAdmin = False

qten.decrypt_file("asst/quz/5d41402abc4b2a76b9719d911017c59e.quz", "z_tmp/cohere_key.txt", "beecode")
co = cohere.Client(open("z_tmp/cohere_key.txt", "r").readlines()[0].strip("\n"))
os.remove("z_tmp/cohere_key.txt")

chat_history = []
prem = str(open("asst/premables/regular", "r").read())

print("FreshPY ready. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "exit":
        break
    
    if user_input.startswith("command"):
        if user_input.endswith(" --dpass"):
            qten.decrypt_file("asst/quz/secrets.quz", "z_tmp/secret.txt", "beecode")
            tmpps = str(open("z_tmp/secret.txt", "r").readlines()[0].strip("\n"))
            conf = input("Password:\n>>> ")
            
            if conf == tmpps:
                print("Access granted. Welcome, Admin! [entry reason: dpass - 'beecode']")
                prem = str(open("asst/premables/admin", "r").read())
                
                if os.path.exists("z_tmp/secret.txt"):
                    os.remove("z_tmp/secret.txt")
                IsAdmin = True
                continue
            
            else:
                if os.path.exists("z_tmp/secret.txt"):
                    os.remove("z_tmp/secret.txt")
                IsAdmin = False
                continue
            
        elif user_input.endswith(" --clearhistory"):
            chat_history.clear()
            continue
        
    if os.path.exists("z_tmp/secret.txt"):
        os.remove("z_tmp/secret.txt")
        
    response = co.chat(
        model="command-a-03-2025",
        message=user_input,
        chat_history=chat_history,
        preamble=prem
    )
    
    if IsAdmin:
        print(response.tool_calls)
        print(response.generation_id)
        
        try:
            print(response.token_count)
        except AttributeError:
            print("Token count not available for this response.")
            
        print(response.meta.api_version)
        print(response.meta.billed_units)
        print(response.meta.tokens)
        print(response.meta.cached_tokens)
        print(response.meta.warnings)
        print(response.finish_reason)
        print(response.citations)
        print(response.documents)
        
    print("Bot:", response.text)
    
    chat_history.append({"role": "USER", "message": user_input})
    chat_history.append({"role": "CHATBOT", "message": response.text})

print("Thank you for using FreshPY. Goodbye!")