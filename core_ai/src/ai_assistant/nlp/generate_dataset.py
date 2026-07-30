import csv
import os

# Define the intents and their corresponding commands in 3 languages
dataset = [
    # --- SYSTEM_SHUTDOWN ---
    {"text": "shut down the computer", "intent": "SYSTEM_SHUTDOWN", "lang": "English"},
    {"text": "turn off the pc", "intent": "SYSTEM_SHUTDOWN", "lang": "English"},
    {"text": "power off the system", "intent": "SYSTEM_SHUTDOWN", "lang": "English"},
    
    {"text": "computer band kar do", "intent": "SYSTEM_SHUTDOWN", "lang": "Hindi"},
    {"text": "pc off kar do", "intent": "SYSTEM_SHUTDOWN", "lang": "Hindi"},
    {"text": "system band kardo", "intent": "SYSTEM_SHUTDOWN", "lang": "Hindi"},
    
    {"text": "computerwa band kar da", "intent": "SYSTEM_SHUTDOWN", "lang": "Bhojpuri"},
    {"text": "systemwa off kar da", "intent": "SYSTEM_SHUTDOWN", "lang": "Bhojpuri"},
    {"text": "pc band kara", "intent": "SYSTEM_SHUTDOWN", "lang": "Bhojpuri"},

    # --- VOLUME_UP ---
    {"text": "increase the volume", "intent": "VOLUME_UP", "lang": "English"},
    {"text": "volume up", "intent": "VOLUME_UP", "lang": "English"},
    {"text": "make it louder", "intent": "VOLUME_UP", "lang": "English"},
    
    {"text": "awaaz badha do", "intent": "VOLUME_UP", "lang": "Hindi"},
    {"text": "volume tez karo", "intent": "VOLUME_UP", "lang": "Hindi"},
    {"text": "sound badhao", "intent": "VOLUME_UP", "lang": "Hindi"},
    
    {"text": "awaaz tej kara", "intent": "VOLUME_UP", "lang": "Bhojpuri"},
    {"text": "volume badha da", "intent": "VOLUME_UP", "lang": "Bhojpuri"},
    {"text": "josh me aawaz kara", "intent": "VOLUME_UP", "lang": "Bhojpuri"},

    # --- VOLUME_DOWN ---
    {"text": "decrease the volume", "intent": "VOLUME_DOWN", "lang": "English"},
    {"text": "volume down", "intent": "VOLUME_DOWN", "lang": "English"},
    {"text": "make it quieter", "intent": "VOLUME_DOWN", "lang": "English"},
    
    {"text": "awaaz kam karo", "intent": "VOLUME_DOWN", "lang": "Hindi"},
    {"text": "volume dheere karo", "intent": "VOLUME_DOWN", "lang": "Hindi"},
    {"text": "sound kam kar do", "intent": "VOLUME_DOWN", "lang": "Hindi"},
    
    {"text": "awaaz kam kara", "intent": "VOLUME_DOWN", "lang": "Bhojpuri"},
    {"text": "volume dheere kara", "intent": "VOLUME_DOWN", "lang": "Bhojpuri"},
    {"text": "soundwa kam kar da", "intent": "VOLUME_DOWN", "lang": "Bhojpuri"},

    # --- OPEN_BROWSER ---
    {"text": "open google chrome", "intent": "OPEN_BROWSER", "lang": "English"},
    {"text": "start the browser", "intent": "OPEN_BROWSER", "lang": "English"},
    {"text": "launch internet", "intent": "OPEN_BROWSER", "lang": "English"},
    
    {"text": "chrome kholo", "intent": "OPEN_BROWSER", "lang": "Hindi"},
    {"text": "browser start karo", "intent": "OPEN_BROWSER", "lang": "Hindi"},
    {"text": "internet kholo", "intent": "OPEN_BROWSER", "lang": "Hindi"},
    
    {"text": "chrome khol da", "intent": "OPEN_BROWSER", "lang": "Bhojpuri"},
    {"text": "browserwa chalu kara", "intent": "OPEN_BROWSER", "lang": "Bhojpuri"},
    {"text": "internetwa khol da", "intent": "OPEN_BROWSER", "lang": "Bhojpuri"},

    # --- GET_WEATHER ---
    {"text": "what is the weather like", "intent": "GET_WEATHER", "lang": "English"},
    {"text": "check the weather", "intent": "GET_WEATHER", "lang": "English"},
    {"text": "is it raining outside", "intent": "GET_WEATHER", "lang": "English"},
    
    {"text": "mausam kaisa hai", "intent": "GET_WEATHER", "lang": "Hindi"},
    {"text": "bahar ka mausam batao", "intent": "GET_WEATHER", "lang": "Hindi"},
    {"text": "kya barish ho rahi hai", "intent": "GET_WEATHER", "lang": "Hindi"},
    
    {"text": "mausam kaisan ba", "intent": "GET_WEATHER", "lang": "Bhojpuri"},
    {"text": "baharwa ke mausam batawa", "intent": "GET_WEATHER", "lang": "Bhojpuri"},
    {"text": "ka paani barsat ba", "intent": "GET_WEATHER", "lang": "Bhojpuri"},
]

def main():
    output_file = os.path.join(os.path.dirname(__file__), "commands_dataset.csv")
    
    # Write to CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["text", "intent", "lang"])
        writer.writeheader()
        writer.writerows(dataset)
        
    print(f"Dataset successfully generated at: {output_file}")
    print(f"Total commands generated: {len(dataset)}")

if __name__ == "__main__":
    main()
