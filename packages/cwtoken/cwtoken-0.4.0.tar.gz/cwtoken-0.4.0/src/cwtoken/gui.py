import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from .key_manager import cwapi
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
import json
import textwrap

# --- Tkinter root ---
root = tk.Tk()

# --- Shared state ---
logged_in = False
save_cred = tk.IntVar()
save_csv = tk.IntVar()
save_query = tk.IntVar()
clubcode_entry = None
token_entry = None
global_data_text = None
df = None
global_client = None

# --- Buttons ---

# --- Login check function ---
def try_login():
    global global_client
    clubcode = clubcode_entry.get()
    api_token = token_entry.get()
    save_credentials = save_cred.get()

    global_client = cwapi(api_token, clubcode=clubcode)
    if global_client.access_token is not None:
        logged_in = True

        if save_credentials == 1:
            config_dir = Path.home() / ".cwtoken"
            config_dir.mkdir(exist_ok=True)  # create directory if it doesn't exist
            cred_path = config_dir / "static_api.env"
            with open(cred_path, "w") as f:
                f.write(f"CLUBCODE={global_client.clubcode}\nAPI_TOKEN={global_client.api_token}\n")

        show_main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid clubcode or API token.")

# --- Save query function ---
def run_query():
    global df
    global global_data_text
    
    today = datetime.today().date()
    keywords = {
        "today": today,
        "tomorrow": today + timedelta(days=1),
        "yesterday": today - timedelta(days=1),
        "beginning_of_month": today.replace(day=1)
    }
    global_data_text = data_text.get("1.0", "end")
    query = data_text.get("1.0", "end").strip()
    query_keywords = query.format(**keywords)
    query_url_fmt = query_keywords.replace('\n', '').replace('\r', '')
    if not query_url_fmt:
        messagebox.showerror("Input Error", "Please enter a query URL.")
        return
    if not global_client.access_token:
        messagebox.showerror("Error", "Access token missing. Please login again.")
        return
    # TODO: fetch data and display or save
    print(f"Running query: {query_url_fmt}")
    df = global_client.raw_query(query_url_fmt).fetch()
    if df is None:
        messagebox.showerror("Error", "Invalid query")
        return
    if save_query.get():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            title="Save Query As"
        )
        dir_path = os.path.dirname(file_path)
        if not file_path:
            return  # user cancelled
        _, ext = os.path.splitext(file_path)

        if ext.lower() == ".json":
            # Save query + metadata as JSON
            data = {
                "query": query,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "club_code": global_client.clubcode,
                "last_run_at": datetime.now(timezone.utc).isoformat(),
                "load_count": 1,
            }
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Query + metadata saved to {file_path}")
        else:
            # Save only raw query string as plain text
            with open(file_path, "w") as f:
                f.write(query_str)
            print(f"Raw query saved to {file_path}")
    show_results()

def load_query():
    finish = 1
    while finish:
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            title="Open query file"
        )
        dir_path = os.path.dirname(file_path)
        
        if not file_path:
            return  # user cancelled
            
        _, ext = os.path.splitext(file_path) 
        if ext.lower() == ".json":
            if os.path.isdir(dir_path):
                finish = 0
                with open(file_path, 'r') as json_File:
                    load_file = json.load(json_File)
                file_content = load_file["query"]
                current_count = load_file["load_count"]
                load_file["load_count"] = current_count + 1
                
                load_file["last_run_at"] = datetime.now(timezone.utc).isoformat()

                with open(file_path, "w") as f:
                    json.dump(load_file, f, indent=4)

            else:
                print("Error: file path doesn't exist")
        else:
            if os.path.isdir(dir_path):
                finish = 0
                with open(file_path, 'r') as file:
                    file_content = file.read()
            else:
                print("Error: file path doesn't exist")
    data_text.insert('1.0', file_content)

def save_file():
    finish = 1
    while finish:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV As"
        )
        dir_path = os.path.dirname(file_path)
        if not file_path:
            return  # user cancelled
        if os.path.isdir(dir_path):
            df.to_csv(f"{file_path}")
            finish = 0
        else:
            print("Error: file path doesn't exist")

def generatepy():
    global global_data_text
    request = global_data_text.strip()
    request_fmt = request.replace('\n', '').replace('\r', '')
    if request:
        script_content = textwrap.dedent(f"""
            import cwtoken
            from datetime import datetime, timedelta

            today = datetime.today().date()
            keywords = {{
                "today": today,
                "tomorrow": today + timedelta(days=1),
                "yesterday": today - timedelta(days=1),
                "beginning_of_month": today.replace(day=1)
            }}

            clubcode = '{login_data["clubcode"]}'
            api_token = '{login_data["api_token"]}'
            raw_request = '{request_fmt}'
            request = raw_request.format(**keywords)
            
            df = cwtoken.fetch(request, api_token, clubcode=clubcode)
            print(df)
        """)

        finish = 1
        while finish:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("py files", "*.py")],
                title="Save PY As"
            )
            dir_path = os.path.dirname(file_path)
            if not file_path:
                return  # user cancelled
            if os.path.isdir(dir_path):
                with open(file_path, "w") as f:
                    f.write(script_content)
                finish = 0
                print(f"PY file saved to {file_path}")
            else:
                print("Error: file path doesn't exist")
    else:
        print("please enter query")
        return

# --- Pages ---

def show_results():
    for widget in root.winfo_children():
        widget.destroy()

    root.geometry("800x600")
    root.title("Query Results")

    if not df.empty:
        # Outer frame to hold everything
        container = tk.Frame(root)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Label frame to group the table visually
        display_df = tk.LabelFrame(container, text="Your query results")
        display_df.pack(fill="both", expand=True)

        # Treeview inside the label frame
        tv1 = ttk.Treeview(display_df)
        tv1.pack(side="left", fill="both", expand=True)

        # Scrollbars
        treescrolly = tk.Scrollbar(display_df, orient="vertical", command=tv1.yview)
        treescrollx = tk.Scrollbar(container, orient="horizontal", command=tv1.xview)
        tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        
        treescrolly.pack(side="right", fill="y")
        treescrollx.pack(side="bottom", fill="x")
        
        # Setup columns
        tv1["columns"] = list(df.columns)
        tv1["show"] = "headings"
        
        for column in tv1["columns"]:
            tv1.heading(column, text=column)
        
        # Insert rows
        df_rows = df.to_numpy().tolist()
        tv1["displaycolumns"] = ()
        for row in df_rows:
            tv1.insert("", "end", values=row)
        tv1["displaycolumns"] = list(df.columns)
    else:
        tk.Label(root, text="Query returned empty array!", font=("Arial", 14)).pack(pady=10, anchor="w", padx=10)


    # --- Bottom Buttons (Side-by-side)
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Save to CSV", command=save_file).pack(side="left", padx=20)
    tk.Button(button_frame, text="Generate PY file", command=generatepy).pack(side="left", padx=20)
    tk.Button(button_frame, text="Back to Query Creator", command=show_main_app).pack(side="left", padx=20)

            
def show_main_app():
    global data_text, save_csv, save_query
    for widget in root.winfo_children():
        widget.destroy()
    
    root.geometry("800x600")
    root.title("POSTGREST data request")

    # Configure root grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(3, weight=1)  # Make the Text widget row expandable

    tk.Label(root, text=f"Welcome! Clubcode: {global_client.clubcode}", font=("Arial", 14)).grid(row=0, column=0, pady=10, sticky="w", padx=10)

    desc_text = (
        "Enter your PostgREST API URL string below.\n"
        "This should be the endpoint you want to query, including any filters or parameters.\n\n"
        "Example:\n"
        "member?select=member_no,first_name,surname\n"
        "&first_name=eq.John\n\n"
        "Make sure your URL is valid and accessible with your API token."
    )
    tk.Label(root, text=desc_text, justify="left", wraplength=600).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

    # Row for checkbox + Load query button
    options_frame = tk.Frame(root)
    options_frame.grid(row=2, column=0, sticky="w", padx=10)

    save_query = tk.IntVar()
    tk.Checkbutton(options_frame, text="Save query?", variable=save_query).pack(side="left")

    tk.Button(options_frame, text="Load query!", command=load_query).pack(side="left", padx=10)

    # Text widget inside a Frame with Scrollbar (optional)
    text_frame = tk.Frame(root)
    text_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
    text_frame.columnconfigure(0, weight=1)
    text_frame.rowconfigure(0, weight=1)

    data_text = tk.Text(text_frame, wrap="word")
    data_text.grid(row=0, column=0, sticky="nsew")

    scroll = tk.Scrollbar(text_frame, command=data_text.yview)
    scroll.grid(row=0, column=1, sticky="ns")
    data_text.config(yscrollcommand=scroll.set)

    # Bottom button for running the query
    bottom_frame = tk.Frame(root)
    bottom_frame.grid(row=4, column=0, sticky="ew", pady=10)
    tk.Button(bottom_frame, text="Run query!", command=run_query).pack(side="left", padx=10)


def setup_login_screen():
    global clubcode_entry, token_entry
    root.title("Clubwise Login")
    root.geometry("300x220")
    
    tk.Label(root, text="Enter Clubcode:").pack(pady=5)
    clubcode_entry = tk.Entry(root)
    clubcode_entry.pack()
    
    tk.Label(root, text="Enter API Token:").pack(pady=5)
    token_entry = tk.Entry(root, show="*")
    token_entry.pack()
    
    tk.Checkbutton(root, text="Save credentials?", variable=save_cred).pack()
    config_dir = Path.home() / ".cwtoken"
    cred_path = config_dir / "static_api.env"

    if cred_path.exists():
        try:
            with open(cred_path, 'r') as f:
                load_dotenv(dotenv_path=cred_path)
                clubcode = os.getenv("CLUBCODE")
                api_token = os.getenv("API_TOKEN")

                clubcode_entry.insert(0, clubcode)
                token_entry.insert(0, api_token)
        except ValueError:
            print("Credential file format invalid.")

    tk.Button(root, text="Login", command=try_login).pack(pady=20)

# --- Initialise ---

def main():
    setup_login_screen()
    root.mainloop()

if __name__ == "__main__":
    main()
