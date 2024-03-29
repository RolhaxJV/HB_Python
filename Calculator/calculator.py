""" Calculator Tkinter """

import tkinter as tk
from tkinter import ttk
import pandas as pd

def save(dataframe):
    """ Save the dataframe in operation.csv
    Args:
        dataframe (DataFrame): contain the operation log
    Returns:
        str: information message
    """
    dataframe.to_csv('operation.csv', mode='a', index=False, header=False)
    return "Add in csv file made"

def perf_ope():
    """ Performs the calculated selection in the checkbox
    """
    try:
        num1 = float(entry1.get().replace(',','.'))
        num2 = float(entry2.get().replace(',','.'))
        selected_operation = operation_var.get()

        match selected_operation:
            case "+":
                result1.set(num1 + num2)

            case "-":
                result1.set(num1 - num2)

            case "*":
                result1.set(num1 * num2)

            case "**":
                result1.set(num1 ** num2)

            case "/":
                result1.set(num1 / num2)

            case "//":
                result1.set(num1 // num2)

            case "%":
                result1.set(num1 % num2)
        result2.set(save(pd.DataFrame({'Numero 1': [num1],
                                    'Numero 2': [num2],
                                    'Operation': [f"{num1} {selected_operation} {num2}"],
                                    'Resultat': [result1.get()]})))
    except ValueError as e:
        result1.set(f"Input error: {e}")
    except ZeroDivisionError:
        result1.set("Division by zero impossible")

def view_log():
    """Permit to see the operation log
    """
    fenetre = tk.Tk()
    fenetre.title("Operation Log")
    text = tk.Text(fenetre)
    text.insert(tk.END,str(pd.read_csv('operation.csv')))
    text.grid(row=0, column=0, padx=10, pady=10)

window = tk.Tk()
window.title("Calculatrice")

result1 = tk.StringVar()
result2 = tk.StringVar()

# Entry One
entry1 = tk.Entry(window, width=15)
entry1.grid(row=0, column=0, padx=10, pady=10)

# Entry Two
entry2 = tk.Entry(window, width=15)
entry2.grid(row=0, column=2, padx=10, pady=10)

# List of operations
operations = ["+", "*", "**", "-", "/", "//", "%"]
operation_var = tk.StringVar()
operation_dropdown = ttk.Combobox(window, textvariable=operation_var, values=operations, width=5)
operation_dropdown.grid(row=0, column=1, padx=10, pady=10)
operation_dropdown.set("+")

# Operation button
calculate_button = tk.Button(window, text="Calculate", command=perf_ope)
calculate_button.grid(row=2, column=0, pady=10)

# View operation logs button
log_button = tk.Button(window, text="Operation logs", command=view_log)
log_button.grid(row=2, column=2, pady=10)

result_label1 = tk.Label(window, textvariable=result1)
result_label1.grid(row=3, column=1, pady=10)

result_label2 = tk.Label(window, textvariable=result2)
result_label2.grid(row=4, column=1,pady=10)

window.mainloop()
