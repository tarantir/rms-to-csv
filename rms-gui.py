import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import sys
from pathlib import Path

class RmsConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RMS Message to CSV Converter")
        self.root.geometry("600x400")
        
        # Variables
        self.messages_path = tk.StringVar()
        self.data_path = tk.StringVar()
        self.selected_folder = tk.StringVar()
        self.output_file = tk.StringVar()
        self.detailed_output = tk.BooleanVar()
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create and place widgets
        self._create_path_section(main_frame)
        self._create_folder_section(main_frame)
        self._create_output_section(main_frame)
        self._create_buttons(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_bar.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Configure grid
        for i in range(3):
            main_frame.columnconfigure(i, weight=1)
    
    def _create_path_section(self, parent):
        # Messages folder section
        ttk.Label(parent, text="Messages Folder:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(parent, textvariable=self.messages_path).grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(parent, text="Browse", command=lambda: self._browse_directory(self.messages_path)).grid(row=0, column=2, padx=5)
        
        # Data folder section
        ttk.Label(parent, text="Data Folder:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(parent, textvariable=self.data_path).grid(row=1, column=1, sticky=(tk.W, tk.E))
        ttk.Button(parent, text="Browse", command=lambda: self._browse_directory(self.data_path)).grid(row=1, column=2, padx=5)
    
    def _create_folder_section(self, parent):
        ttk.Label(parent, text="RMS Folder:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        folders = ["InBox", "Sent Items", "Deleted Items", "Archive", "Outbox"]
        folder_combo = ttk.Combobox(parent, textvariable=self.selected_folder, values=folders)
        folder_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        folder_combo.set("InBox")
    
    def _create_output_section(self, parent):
        # Output file section
        ttk.Label(parent, text="Output CSV:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(parent, textvariable=self.output_file).grid(row=3, column=1, sticky=(tk.W, tk.E))
        ttk.Button(parent, text="Browse", command=self._browse_save_file).grid(row=3, column=2, padx=5)
        
        # Detailed output checkbox
        ttk.Checkbutton(parent, text="Include detailed output", variable=self.detailed_output).grid(row=4, column=0, columnspan=2, sticky=tk.W)
    
    def _create_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Convert", command=self._convert).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)
    
    def _browse_directory(self, path_var):
        directory = filedialog.askdirectory()
        if directory:
            path_var.set(directory)
    
    def _browse_save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.output_file.set(file_path)
    
    def _validate_inputs(self):
        if not self.messages_path.get() or not os.path.exists(self.messages_path.get()):
            messagebox.showerror("Error", "Invalid Messages folder path")
            return False
        if not self.data_path.get() or not os.path.exists(self.data_path.get()):
            messagebox.showerror("Error", "Invalid Data folder path")
            return False
        if not self.selected_folder.get():
            messagebox.showerror("Error", "Please select an RMS folder")
            return False
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify output CSV file")
            return False
        return True
    
    def _convert(self):
        if not self._validate_inputs():
            return
        
        try:
            # Update the paths in the original script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            rmsmsg2csv_path = os.path.join(script_dir, "rmsmsg2csv.py")
            
            # Build command
            cmd = [sys.executable, rmsmsg2csv_path, 
                  self.selected_folder.get(), 
                  self.output_file.get()]
            
            if self.detailed_output.get():
                cmd.append('-d')
            
            # Set environment variables for paths
            env = os.environ.copy()
            env['P_MSG_PATH'] = str(Path(self.messages_path.get()) / '')  # Ensure trailing slash
            env['P_DATA_PATH'] = str(Path(self.data_path.get()) / '')     # Ensure trailing slash
            
            # Run conversion
            self.status_var.set("Converting messages...")
            self.root.update()
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.status_var.set(result.stdout.strip())
                messagebox.showinfo("Success", "Conversion completed successfully!")
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            self.status_var.set("Error occurred during conversion")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

def main():
    root = tk.Tk()
    app = RmsConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
