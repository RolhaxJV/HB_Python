# En utilisant Tkinter, votre mission sera de réaliser une calculatrice.

# La contrainte à ce projet, est que la calculatrice ne possède qu’au maximum trois boutons.

# Livrables attendus :

# Un lien Github vers l’application

# Une feuille comportant 5 tests fonctionnels de sa propre application

# Une feuille comportant 5 tests fonctionnels d’une application concurrente.
import tkinter as tk

fenetre = tk.Tk()
fenetre.title("Calculatrice")
fenetre.geometry("640x480")
nbx = tk.Entry(fenetre)

nbx.pack()
fenetre.mainloop()

