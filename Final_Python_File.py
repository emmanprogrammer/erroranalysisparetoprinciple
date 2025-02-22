#download the following packages
#pip install pylint
#pip install pandas
#pip install matplotlib
#pip install customtkinter

import os
import subprocess
import re
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from tkinter.scrolledtext import ScrolledText
from matplotlib.ticker import PercentFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

filess = None

# Function to open file dialog and select files
def select_files():
    global filess
    file_paths = filedialog.askopenfilenames(title="Select Python Files", filetypes=[("Python Files", "*.py")])
    file_names = [os.path.basename(path) for path in file_paths]  # Extract filenames
    selected_files_text.delete("1.0", "end")  # Clear previous content
    selected_files_text.insert("end", "\n".join(file_names))  # Show only filenames
    filess = list(file_paths)
    show_selected_files()

def show_selected_files():
    selected_files_text.delete(1.0, ctk.END)
    if filess:
        for file in filess:
            selected_files_text.insert(ctk.END, file + "\n")
    else:
        selected_files_text.insert(ctk.END, "No files selected.")

def run_analysis():
    if not filess:
        print("No files selected. Exiting.")
        return

    python_files = filess

    # Run Pyright on the selected python files and write the output to a log file
    pyright_log_file = "pyright_log.txt"
    with open(pyright_log_file, 'w', encoding='utf-8') as f:
        for python_file in python_files:
            result = subprocess.run(["pyright", python_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
            f.write(result.stdout)
            f.write(result.stderr)
            

    # Run Pylint on the selected python files and write the output to a log file
    pylint_log_file = "pylint_log.txt"
    with open(pylint_log_file, 'w', encoding='utf-8') as f:
        for python_file in python_files:
            result = subprocess.run(["pylint", "--exit-zero", "--output-format=text", python_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
            f.write(result.stdout)
            f.write(result.stderr)

    # Error codes for Pylint
    pylint_error_codes = [
    "C0102", "C0103", "C0111", "C0112", "C0121", "C0202", "C0203", "C0204",
    "C0301", "C0302", "C0303", "C0304", "C0321", "C0322", "C0323", "C0324",
    "C0325", "C0326", "C1001",

    "F0001", "F0002", "F0003", "F0004", "F0010", "F0202", "F0220", "F0321",
    "F0401",

    "R0201", "R0401", "R0801", "R0901", "R0902", "R0903", "R0904", "R0911",
    "R0912", "R0913", "R0914", "R0915", "R0921", "R0922", "R0923",

    "W0101", "W0102", "W0104", "W0105", "W0106", "W0107", "W0108", "W0109",
    "W0110", "W0120", "W0121", "W0122", "W0141", "W0142", "W0150", "W0199",
    "W0201", "W0211", "W0212", "W0221", "W0222", "W0223", "W0231", "W0232",
    "W0233", "W0234", "W0301", "W0311", "W0312", "W0331", "W0332", "W0333",
    "W0401", "W0402", "W0403", "W0404", "W0406", "W0410", "W0511", "W0512",
    "W0601", "W0602", "W0603", "W0604", "W0611", "W0612", "W0613", "W0614",
    "W0621", "W0622", "W0623", "W0631", "W0632", "W0633", "W0701", "W0702",
    "W0703", "W0704", "W0710", "W0711", "W0712", "W1001", "W1111", "W1201",
    "W1300", "W1301", "W1401", "W1402", "W1501",
    ]

    pyright_error_codes = [ "reportGeneralTypeIssues", "reportFunctionMemberAccess",
    "reportMissingImports", "reportInvalidTypeForm", "reportAbstractUsage",
    "reportArgumentType", "reportAssertTypeFailure", "reportAssignmentType",
    "reportAttributeAccessIssue", "reportCallIssue", "reportInconsistentOverload",
    "reportIndexIssue", "reportInvalidTypeArguments", "reportNoOverloadImplementation",
    "reportOperatorIssue", "reportOptionalSubscript", "reportOptionalMemberAccess",
    "reportOptionalCall", "reportOptionalIterable", "reportOptionalContextManager",
    "reportOptionalOperand", "reportRedeclaration", "reportReturnType",
    "reportTypedDictNotRequiredAccess", "reportPrivateImportUsage", "reportIncompatibleMethodOverride",
    "reportIncompatibleVariableOverride", "reportOverlappingOverload", "reportPossiblyUnboundVariable",
    "reportUndefinedVariable", "reportUnboundVariable", "reportUnhashable",
    "reportUnusedCoroutine", "reportUnusedExcept",
    ]

    pylint_error_counts = {code: 0 for code in pylint_error_codes}
    pyright_error_counts = {code: 0 for code in pyright_error_codes}
    # Count the number of errors in each category by finding the error codes in the Pyright log file
    with open(pyright_log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
        for code in pyright_error_codes:
            count = len(re.findall(r'\b' + re.escape(code) + r'\b', log_content))
            pyright_error_counts[code] += count

    with open(pylint_log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
        for code in pylint_error_codes:
            count = len(re.findall(r'\b' + re.escape(code) + r'\b', log_content))
            pylint_error_counts[code] += count

    print("Pylint Error Counts:")
    for code, count in pylint_error_counts.items():                                #FOR DEBUGGIN PURPOSES
        print(f"{code}: {count}")

    print("\nPyright Error Counts:")
    for code, count in pyright_error_counts.items():
        print(f"{code}: {count}")
 
    # Dataframe of the error categories for the pareto chart
    # Filter the error counts to only include error codes with a count of 1 or more
    filtered_pylint_error_counts = {code: count for code, count in pylint_error_counts.items() if count >= 1}
    filtered_pyright_error_counts = {code: count for code, count in pyright_error_counts.items() if count >= 1}

# Combine the filtered error counts into a single dictionary for the DataFrame
    combined_error_counts = {**filtered_pylint_error_counts, **filtered_pyright_error_counts}

# Create a DataFrame of the error categories for the pareto chart
    df = pd.DataFrame(list(combined_error_counts.items()), columns=['Error Code', 'Count'])
    df = df.sort_values(by='Count', ascending=False)
    df["cumpercentage"] = df["Count"].cumsum() / df["Count"].sum() * 100
    print(df)
# Show the pareto chart
    def show_chart():
        fig, ax1 = plt.subplots()
        fig.patch.set_facecolor('#333333')  # Set the background color of the figure
        ax1.set_facecolor('#444444')  # Set the background color of the axes
        ax1.bar(df['Error Code'], df["Count"], color="C0")
        ax1.set_ylabel("Number of Errors", color="C0")
        ax1.tick_params(axis="y", colors="C0")
        ax1.set_xlabel("Error Code")
        ax1.set_xticklabels(df['Error Code'], rotation=45)
        ax1.set_title("Pareto Chart of Error Codes")
        ax2 = ax1.twinx()
        ax2.plot(df['Error Code'], df["cumpercentage"], color="C1", marker="D", ms=7)
        ax2.yaxis.set_major_formatter(PercentFormatter())
        ax2.tick_params(axis="y", colors="C1")
        # Add the chart to the chart frame
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
        
# Find the top errors contributing to 80% of the issues
    df_pareto = df[df["cumpercentage"] <= 80]

# If the dataframe is empty, use the first row
    if df_pareto.empty:
        df_pareto = df.iloc[:1]

# Display the top errors contributing to 80% of the issues
    df_pareto_category = df_pareto['Error Code'].tolist()
    final_analysis = [category for category in df_pareto_category]
    print("\nTop Errors Contributing to 80% of Issues:")
    print(final_analysis)

    # Display the feedback for the errors causing 80% of the issues
    relevant_errors = df_pareto['Error Code'].tolist()
    print("\nFeedbacks for errors causing 80% of the issues:")
    feedbacks_by_module = {}

    # Find the error codes in the log file and display the feedback
    for error in relevant_errors:
        if error.startswith('report'):
            with open(pyright_log_file, 'r', encoding='utf-8') as f:
                log_content = f.readlines()
                for line in log_content:
                    if error in line:
                        match = re.search(r'([\w.]+\.py):(\d+):\d+ - error: (.+) \((\w+)\)', line)
                        print(match)
                        if match:
                            module_name = match.group(1)
                            line_number = match.group(2)
                            error_code = match.group(4)
                            error_message = match.group(3)
                            if module_name not in feedbacks_by_module:
                                feedbacks_by_module[module_name] = {}
                            feedbacks_by_module[module_name].update({f"Line : {line_number} [{error_code}] - {error_message}":int(line_number)})
        else:
            with open(pylint_log_file, 'r', encoding='utf-8') as f:
                log_content = f.readlines()
                for line in log_content:
                    if error in line:
                        match = re.search(r'(\w+\.py):(\d+):\d+: (\w\d+): (.+)', line)
                    
                        if match:
                            module_name = match.group(1)
                            line_number = match.group(2)
                            error_code = match.group(3)
                            error_message = match.group(4)
                            if module_name not in feedbacks_by_module:
                                feedbacks_by_module[module_name] = {}
                            feedbacks_by_module[module_name].update({f"Line : {line_number} [{error_code}] - {error_message}":int(line_number)})

    sorted_feedbacks = sorted(feedbacks_by_module[module_name].items(), key=lambda x: x[1])
    feedbacks_by_module[module_name] = sorted_feedbacks
    
# Apply Pareto's principle to the feedback

    feedback_text = ""
    for module_name, feedbacks in feedbacks_by_module.items():
        feedback_text += f"\n({module_name})\n"
        for feedback in feedbacks:
            if isinstance(feedback, str):
                feedback_text += feedback + "\n\n"
            else:
                feedback_text += str(feedback[0]) + "\n\n"
# Update the GUI with the chart and feedbacks
    update_gui(feedback_text)
    show_chart()

def update_gui(feedback_text):
    # Clear previous content
    for widget in chart_frame.winfo_children():
        widget.destroy()
    for widget in feedback_frame.winfo_children():
        widget.destroy()

    # Add the feedbacks to the feedback frame
    feedback_label = ctk.CTkLabel(feedback_frame, text="Feedbacks", font=("Segoe UI", 20))
    feedback_label.pack(pady=10)
    feedback_text_widget = ScrolledText(feedback_frame, wrap=ctk.WORD, font=("Segoe UI", 12))
    feedback_text_widget.pack(fill=ctk.BOTH, expand=True)
    feedback_text_widget.insert(ctk.END, feedback_text)

# Create the main window
root = ctk.CTk()
root.geometry("1200x800")
root.configure(fg_color='#212121')
     

# Create a title label
title_label = ctk.CTkLabel(root, text="Pareto-Based Linter", font=("Segoe UI", 24), text_color='#FFFFFF', fg_color='#212121')
title_label.pack(pady=20)

# Create a frame for the buttons and selected files
control_frame = ctk.CTkFrame(root, border_color='#212121', fg_color='#212121')
control_frame.pack(anchor="nw", fill=ctk.X, padx=15, pady=15)

# Create a button to select files
select_files_button = ctk.CTkButton(master=control_frame, text="Select Files", fg_color='#e0569c', hover_color= '#86335d', font=("Arial", 16),hover=True, command=select_files, height=75, width=200, border_width=3, border_color='#FFFFFF')
select_files_button.grid(row=0, column=0, padx=10, pady=5, sticky="w")

# Create a button to run the analysis
run_analysis_button = ctk.CTkButton(master=control_frame, border_width=3, fg_color='#e0569c', hover_color= '#86335d', text="Run Analysis", font=("DM Sans", 16), border_color='#FFFFFF', height=75, width=200, command=lambda: threading.Thread(target=run_analysis).start())
run_analysis_button.grid(row=1, column=0, padx=10, pady=15, sticky="w")

# Create a frame to contain the textbox and scrollbar
text_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
text_frame.grid(row=0, column=1, rowspan=3, padx=5, pady=3, sticky="nsew")

# Create the CTkTextbox for selected files
selected_files_text = ctk.CTkTextbox(master=text_frame, font=("Arial", 12), height=10,
    width= 20,
    fg_color="#212121",
    text_color="white",
    border_color="#FFFFFF",
    border_width=3,
    wrap="word"  
)
selected_files_text.pack(side="left", fill="both", expand=True)

# Create a vertical scrollbar
text_scrollbar = ctk.CTkScrollbar(master=text_frame, command=selected_files_text.yview, button_color="#FFFFFF")
text_scrollbar.pack(side="right", fill="y")

# Link scrollbar to textbox
selected_files_text.configure(yscrollcommand=text_scrollbar.set)

# Configure grid weights to make the text widget expand
control_frame.grid_columnconfigure(1, weight=50)
control_frame.grid_rowconfigure(0, weight=50)
control_frame.grid_rowconfigure(1, weight=1)


# Create a frame for the chart
chart_frame = ctk.CTkFrame(root, fg_color='#212121')
chart_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

# Create a frame for the feedbacks
feedback_frame = ctk.CTkFrame(root, fg_color='#212121')
feedback_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

# Start the Tkinter main loop
root.mainloop()
