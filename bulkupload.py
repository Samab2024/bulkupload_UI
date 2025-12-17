# bulkupload_ui_threaded.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC as VeracodeHMAC
from csv_in import csvIn
from new_api import veracode_api_call as api_call
import traceback
import threading

class BulkUploadUI:
    def __init__(self, root):
        self.root = root
        root.title("Veracode Bulk Upload Tool")

        # --- Credentials ---
        tk.Label(root, text="Region (US/EU):").grid(row=0, column=0, sticky='e')
        self.region_var = tk.StringVar()
        tk.Entry(root, textvariable=self.region_var).grid(row=0, column=1)

        tk.Label(root, text="API Key ID:").grid(row=1, column=0, sticky='e')
        self.api_id_var = tk.StringVar()
        tk.Entry(root, textvariable=self.api_id_var).grid(row=1, column=1)

        tk.Label(root, text="API Key Secret:").grid(row=2, column=0, sticky='e')
        self.api_secret_var = tk.StringVar()
        tk.Entry(root, textvariable=self.api_secret_var, show="*").grid(row=2, column=1)

        # --- CSV File ---
        tk.Label(root, text="CSV File:").grid(row=3, column=0, sticky='e')
        self.filename_var = tk.StringVar()
        tk.Entry(root, textvariable=self.filename_var, width=40).grid(row=3, column=1)
        tk.Button(root, text="Browse", command=self.browse_file).grid(row=3, column=2)

        # --- Run Button ---
        self.run_button = tk.Button(root, text="Start Upload", command=self.start_upload_thread)
        self.run_button.grid(row=4, column=1, pady=10)

        # --- Log Display ---
        self.log_display = scrolledtext.ScrolledText(root, width=80, height=20)
        self.log_display.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.filename_var.set(filename)

    def log(self, msg, error=False):
        # Update log in the UI
        self.log_display.insert(tk.END, msg + "\n")
        self.log_display.see(tk.END)
        if error:
            print(msg)

    def start_upload_thread(self):
        # Disable button to prevent multiple clicks
        self.run_button.config(state=tk.DISABLED)
        threading.Thread(target=self.start_upload, daemon=True).start()

    def start_upload(self):
        region = self.region_var.get().strip()
        api_id = self.api_id_var.get().strip()
        api_secret = self.api_secret_var.get().strip()
        filename = self.filename_var.get().strip()

        if not all([region, api_id, api_secret, filename]):
            self.run_button.config(state=tk.NORMAL)
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            creds = VeracodeHMAC(api_id, api_secret)
            myCSV = csvIn.fromFile(filename)

            # Credentials test
            try:
                params = {'rownum': 'CredentialsTest'}
                api_call(region=region, endpoint='getmaintenancescheduleinfo', creds=creds, logger=self, params=params)
            except Exception as e:
                self.log("Bad response from credentials test. Exiting...", error=True)
                traceback.print_exc()
                self.run_button.config(state=tk.NORMAL)
                return

            # Process CSV rows
            lineinfo = myCSV.next()
            while lineinfo:
                if 'apiaction' in lineinfo:
                    try:
                        endpoint = lineinfo.pop('apiaction')
                        api_call(region=region, endpoint=endpoint, creds=creds, logger=self, params=lineinfo)
                    except Exception as e:
                        self.log(f"Error on row {lineinfo.get('rownum')}: {e}", error=True)
                        traceback.print_exc()
                lineinfo = myCSV.next()

            self.log("CSV completed successfully!")
            messagebox.showinfo("Success", "Bulk upload completed!")

        except Exception as e:
            self.log(f"Unexpected error: {e}", error=True)
            traceback.print_exc()
            messagebox.showerror("Error", f"Unexpected error:\n{e}")

        finally:
            self.run_button.config(state=tk.NORMAL)  # Re-enable button

    # Logger interface for new_api
    def info(self, msg):
        self.log(msg)

    def error(self, msg):
        self.log(msg, error=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = BulkUploadUI(root)
    root.mainloop()