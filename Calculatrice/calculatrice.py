# En utilisant Tkinter, votre mission sera de réaliser une calculatrice.

# La contrainte à ce projet, est que la calculatrice ne possède qu’au maximum trois boutons.

# Livrables attendus :

# Un lien Github vers l’application

# Une feuille comportant 5 tests fonctionnels de sa propre application

# Une feuille comportant 5 tests fonctionnels d’une application concurrente.
import tkinter as tk

def addition():
    """ Sum of the two entries
    """

def subtraction():
    """ Subtraction of the two entries
    """

def multiplication():
    """ Product of the two entries
    """

def division():
    """ Division of the two entries
    """



window = tk.Tk()
window.title("Calculatrice")

result = tk.StringVar()

# Entry One
entry1 = tk.Entry(window, width=15)
entry1.grid(row=0, column=0, padx=10, pady=10)

# Entry Two
entry2 = tk.Entry(window, width=15)
entry2.grid(row=0, column=1, padx=10, pady=10)

# Button call addition function
add_button = tk.Button(window, text="+", command=addition)
add_button.grid(row=1, column=0, padx=5, pady=5)

# Button call subtraction function
subtract_button = tk.Button(window, text="-", command=subtraction)
subtract_button.grid(row=1, column=1, padx=5, pady=5)

# Button call multiplication function
multiply_button = tk.Button(window, text="*", command=multiplication)
multiply_button.grid(row=2, column=0, padx=5, pady=5)

divide_button = tk.Button(window, text="/", command=division)
divide_button.grid(row=2, column=1, padx=5, pady=5)

result_label = tk.Label(window, textvariable=result)
result_label.grid(row=3, column=0, columnspan=2, pady=10)

window.mainloop()
