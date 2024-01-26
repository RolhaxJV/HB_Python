""" View of scrap_jerome """
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pytest
import pandas as pd
from scrap_jerome import FromageETL


class FromageApp:
    """ View Class of scrap_jerome """
    def __init__(self, master):
        self.master = master
        self.master.title("Interface Fromage")
        self.etl = FromageETL("https://www.laboitedufromager.com/liste-des-fromages-par-ordre-alphabetique/")
        self.load_data_button = tk.Button(master, text="Mettre à jour la BDD", command=self.update_database)
        self.load_data_button.pack(pady=10)

        self.pie_chart_frame = ttk.Frame(master)
        self.pie_chart_frame.pack(pady=10)

        self.accuracy_label = tk.Label(master, text="Taux de fiabilité des résultats: ")
        self.accuracy_label.pack(pady=10)

    def update_database(self):
        """ Upadate the database with the url data """
        self.etl.extract()
        self.etl.transform()
        self.etl.load('fromages_bdd.sqlite', 'fromages_table')
        self.plot_pie_chart()
        accuracy = self.calculate_accuracy()
        self.accuracy_label.config(text=f"Taux de fiabilité des résultats: {accuracy:.2%}")

    def plot_pie_chart(self):
        """ Create a pie chart """
        data_from_db = self.etl.read_from_database('fromages_bdd.sqlite', 'fromages_table')
        famille_counts = data_from_db['familles'].value_counts()

        fig, ax = plt.subplots()
        ax.pie(famille_counts, labels=famille_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        canvas = FigureCanvasTkAgg(fig, master=self.pie_chart_frame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas.draw()

    def run_tests(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        result = pytest.main(["--excel_report=report.xlsx", "test_scrap.py"])
        return result

    def calculate_accuracy(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        test_result = pd.read_excel('report.xlsx')

        mask = test_result['result'] == 'PASSED'
        
        return str((test_result[mask].shape[0] / test_result.shape[0]) * 100) + " %"

def main():
    root = tk.Tk()
    app = FromageApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
