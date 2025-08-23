import tkinter as tk
import webbrowser


def main():
    root = tk.Tk()
    root.title("Python Update Required")

    # Text instructions
    text = (
        "APSCALE has been updated to version 4\n\n"
        "Please update Python to Python 3.12\n\n"
        "Conda users: Upgrade the environment to APSCALE4\n\n"
        "Find more information here:"
    )
    label_text = tk.Label(root, text=text, justify="left")
    label_text.pack(padx=20, pady=(20, 5), anchor="w")

    # Clickable links
    links = [
        "https://github.com/TillMacher/apscale_gui",
        "https://github.com/TillMacher/apscale_installer"
    ]

    for link in links:
        lbl = tk.Label(root, text=link, fg="blue", cursor="hand2", justify="left")
        lbl.pack(padx=20, anchor="w")
        lbl.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))

    # OK button
    ok_btn = tk.Button(root, text="OK", command=root.destroy)
    ok_btn.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()