"""
    _summary_  The main application file for Colossus.
    Contains the main application class and page management.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import webbrowser
from colossus_ltsm.settings import settings, CL_CONFIG_PATH
from colossus_ltsm.font_viewer import FontViewer
from colossus_ltsm.font_converter import FontConverter
from colossus_ltsm import __version__

class ColossusApp(tk.Tk):
    """Main application class for Colossus
    This class initializes the main window and manages different pages.
    """

    def __init__(self):
        super().__init__()

        self.title("Colossus")
        self.geometry("800x600")

        # Container frame to hold pages
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to store pages
        self.frames = {}

        # Global button options
        self.option_add("*Button.Font", ("Arial", 18))
        self.option_add("*Button.Relief", "raised")
        self.option_add("*Button.BorderWidth", 5)

        # Pre-create pages that don't need extra arguments
        for F in (
                MainMenu, SettingsPage, AboutPage, FontConverter, FontViewer):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start on MainMenu
        self.show_frame(MainMenu)

    def show_frame(self, page_class):
        """ Raise the given frame to the top.
        Args:
            page_class (class): The class of the frame to show."""
        frame = self.frames[page_class]
        frame.tkraise()


class MainMenu(tk.Frame):
    """Main menu page with buttons to navigate to different functionalities."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Main Menu", font=("Arial", 24))
        label.pack(pady=20)
        btn_font_convert = tk.Button(
            self, text="Font tff to Data convert", command=self.open_convert)
        btn_font_convert.pack(pady=16)
        btn_font_horizontal = tk.Button(
            self, text="Font Data Viewer", command=self.open_font_viewer)
        btn_font_horizontal.pack(pady=16)
        btn_settings = tk.Button(self, text="Settings",
                                 command=self.open_settings)
        btn_settings.pack(pady=16)
        btn_about = tk.Button(self, text="About", command=self.open_about)
        btn_about.pack(pady=16)
        btn_exit = tk.Button(self, text="Exit", command=controller.quit)
        btn_exit.pack(pady=16)

    def open_font_viewer(self):
        """ Open the Font Viewer Page dynamically. """
        # Destroy any previous FontViewerPage (but keep MainMenu
        # and other static pages)
        for widget in self.controller.container.winfo_children():
            if isinstance(widget, FontViewerPage):
                widget.destroy()

        # Create new FontViewerPage dynamically
        frame = FontViewerPage(parent=self.controller.container,
                               controller=self.controller)
        frame.grid(row=0, column=0, sticky="nsew")
        self.controller.frames[FontViewerPage] = frame
        frame.tkraise()

    def open_settings(self):
        """ Open the Settings Page dynamically. """
        # Destroy old SettingsPage if exists
        for widget in self.controller.container.winfo_children():
            if isinstance(widget, SettingsPage):
                widget.destroy()
        # Create new SettingsPage dynamically
        frame = SettingsPage(parent=self.controller.container,
                             controller=self.controller)
        frame.grid(row=0, column=0, sticky="nsew")
        self.controller.frames[SettingsPage] = frame
        frame.tkraise()

    def open_convert(self):
        """ Open the Font Convert Page dynamically. """
        # Destroy old convertPage if exists
        for widget in self.controller.container.winfo_children():
            if isinstance(widget, ConvertPage):
                widget.destroy()
        # Create new ConvertPage dynamically
        frame = ConvertPage(parent=self.controller.container,
                            controller=self.controller)
        frame.grid(row=0, column=0, sticky="nsew")
        self.controller.frames[ConvertPage] = frame
        frame.tkraise()

    def open_about(self):
        """ Open the About Page dynamically. """
        # Destroy old aboutPage if exists
        for widget in self.controller.container.winfo_children():
            if isinstance(widget, AboutPage):
                widget.destroy()
        # Create new aboutPage dynamically
        frame = AboutPage(parent=self.controller.container,
                          controller=self.controller)
        frame.grid(row=0, column=0, sticky="nsew")
        self.controller.frames[AboutPage] = frame
        frame.tkraise()


class ConvertPage(tk.Frame):
    """ Page for converting TTF fonts to data format."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Embed the FontConverter inside this frame
        self.viewer = FontConverter(self, controller)
        self.viewer.pack(fill="both", expand=True)
        btn_back = tk.Button(
            self, text="Back to Menu",
            command=lambda: controller.show_frame(MainMenu)
        )
        btn_back.pack(pady=16)


class FontViewerPage(tk.Frame):
    """ Page for viewing font data in a horizontal or vertical layout."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Embed the FontViewer inside this frame
        self.viewer = FontViewer(self, controller)
        self.viewer.pack(fill="both", expand=True)
        btn_back = tk.Button(
            self, text="Back to Menu", relief='raised', borderwidth=5,
            command=lambda: controller.show_frame(MainMenu)
        )
        btn_back.pack(pady=16)


class SettingsPage(tk.Frame):
    """ Page for editing application settings."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # --- Text area with scrollbars ---
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.NONE,
            undo=True
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        # --- Buttons row at bottom ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        tk.Button(btn_frame, text="Save",
                  command=self.save).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Reload",
                  command=self.reload).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Back",
                  command=lambda:
                  controller.show_frame(MainMenu)).pack(side=tk.RIGHT,
                                                        padx=5)
        # Load current settings
        self.reload()

    def reload(self):
        """ Reload settings from the config file into the text area."""
        try:
            with open(CL_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = f.read()
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, data)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load settings:\n{e}")

    def save(self):
        """ Save the current text area content back to the config file."""
        try:
            with open(CL_CONFIG_PATH, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END).strip() + "\n")
            messagebox.showinfo("Saved", "Settings saved successfully.")
            settings.load()  # Reload settings to update in memory
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings:\n{e}")


class AboutPage(tk.Frame):
    """ Page displaying information about the application."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="About Colossus", font=("Arial", 24))
        label.pack(pady=20)
        # Selectable text widget
        text = tk.Text(self, wrap="word", height=6, width=60,
                       borderwidth=0, highlightthickness=0)
        text.insert(tk.END,
                    "Colossus\n"
                    "Version " + __version__ + "\n"
                    "Written by Gavin Lyons\n"
                    "URL: https://github.com/gavinlyonsrepo/Colossus_LTSM\n")
        text.config(state="disabled")  # make read-only
        text.pack(padx=10, pady=10, fill="both", expand=True)

        # Make URL clickable
        def open_url(event):
            webbrowser.open("https://github.com/gavinlyonsrepo/Colossus_LTSM")

        text.tag_add("link", "4.5", "4.end")  # line 4, chars 5 to end
        text.tag_config("link", foreground="blue", underline=True)
        text.tag_bind("link", "<Button-1>", open_url)
        # Back button
        btn_back = tk.Button(self, text="Back to Menu",
                             command=lambda: controller.show_frame(MainMenu))
        btn_back.pack(pady=10)

def main():
    """ Entry point for the Colossus application."""
    app = ColossusApp()
    app.mainloop()


if __name__ == "__main__":
    main()
else:
    print("Colossus script loaded as module, This is a script")
