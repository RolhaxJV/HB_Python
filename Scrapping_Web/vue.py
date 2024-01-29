"""
Ce module contient les importations nécessaires pour le script.
"""
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pytest
from pytest_excel.plugin import xfail_strict
import pandas as pd
from scrap_jerome import FromageETL


class FromageUI:
    """
    Classe représentant l'interface utilisateur pour afficher des informations sur les fromages.
    """
    URL_FROMAGE = "https://www.laboitedufromager.com/liste-des-fromages-par-ordre-alphabetique/"
    DB_NAME = "fromages_bdd.sqlite"
    TABLE_NAME = "fromages_table"

    def __init__(self, master):
        """
        Initialisation de l'interface graphique de la classe FromageUI.
        """
        self.result1 = tk.StringVar()

        self.master = master
        master.title("Interface Fromage")

        # Ouvrir la fenêtre en plein écran
        master.attributes('-fullscreen', True)

        # Cadre principal
        self.main_frame = tk.Frame(master)
        self.main_frame.pack()

        # Bouton pour mettre à jour la BDD
        self.update_button = tk.Button(self.main_frame,
            text="Mettre à jour la BDD", command=self.update_database)
        self.update_button.pack()

        # Diagramme en camembert
        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack()

        self.label= tk.Label(self.main_frame, textvariable=result1)
        self.label.pack()

        # Bouton pour fermer la fenêtre
        self.close_button = tk.Button(self.main_frame, text="Fermer", command=self.close_window)
        self.close_button.pack()

    def update_database(self):
        """
        Met à jour la base de données (BDD) en extrayant,
        transformant et chargeant les données des fromages.
        """
        etl = FromageETL(url=self.URL_FROMAGE)
        etl.extract()
        etl.transform()
        data = etl.load(self.DB_NAME, self.TABLE_NAME)
        messagebox.showinfo("Mise à jour", "La base de données a été mise à jour avec succès.")

        # Mettre à jour le diagramme en camembert
        self.update_pie_chart(data)

    def update_pie_chart(self, data):
        """
        Met à jour les deux diagrammes en camembert avec les ratios de fromages par famille.
        """
        ratio = data['fromage_familles'].value_counts(normalize=True) * 100

        # Regrouper les données inférieures à 5% dans "Autres"
        mask = ratio < 5
        ratio['Autres'] = ratio[mask].sum()
        mask = mask.reindex(ratio.index, fill_value=False)
        ratio = ratio[~mask]

        # Créer les deux diagrammes en camembert côte à côte
        self.fig.clear()

        # Créer le premier diagramme en camembert
        ax1 = self.fig.add_axes([0, 0, 0.4, 1])  # [left, bottom, width, height]
        ax1.pie(ratio, labels=ratio.index, autopct='%1.1f%%')
        ax1.set_title("100% de la BDD")

        # Ajouter une légende pour le premier camembert
        legend_labels1 = [f"{label} : {ratio[label]:.1f}%" for label in ratio.index]
        legend1 = ax1.legend(legend_labels1, title="% BDD des 'Familles' > 5%")

        # Ajuster la position de la légende par rapport au camembert
        legend1.set_bbox_to_anchor((0.8, 0.82))  # Coordonnées relatives à l'axe du camembert
        legend1.get_title().set_fontsize('10')
        # Ajuster la taille de la légende (ajuster toutes les étiquettes)
        for text in legend1.get_texts():
            text.set_fontsize('8')


        # Créer un deuxième diagramme en camembert pour "Autres"
        if 'Autres' in ratio:
            other_data = data['fromage_familles'].value_counts(normalize=True)[mask] * 100
            ax2 = self.fig.add_axes([0.55, 0, 0.3, 1])
            ax2.pie(other_data, labels=other_data.index, autopct='%1.1f%%')
            ax2.set_title("100% des Autres", loc='center', pad=40)

            # Ajouter une légende pour le deuxième camembert
            legend_labels2 = [f"{label} : {other_data[label]:.1f}%" for label in other_data.index]
            legend2 = ax2.legend(legend_labels2, title="% BDD des 'Autres'")

            # Ajuster la position de la légende
            legend2.set_bbox_to_anchor((0.8, 0.80))
            legend2.get_title().set_fontsize('10')

            # Ajuster la taille des étiquettes
            for text in legend2.get_texts():
                text.set_fontsize('8')

        self.result1.set(str(self.pourcent_success()))
        self.canvas.draw()

    def close_window(self):
        """
        Fonction pour fermer la fenêtre.
        """
        self.master.destroy()

    def pourcent_success(self):
        """ Calcule le pourcentage de reussite des test pytest

        Returns:
            float: resultat du calcule pour affichage
        """
        # Configuration pour pytest-excel
        pytest.config.option.excel_report_file = "report.xlsx"
        pytest.config.pluginmanager.register(xfail_strict)

        # Exécutez les tests avec pytest
        pytest.main(["test_scrap.py"])

        # Charger les résultats du test à partir du fichier Excel
        test_result = pd.read_excel('report.xlsx')

        # Filtrer les résultats réussis (PASSED)
        mask = test_result['result'] == 'PASSED'

        # Calculer le pourcentage de tests réussis
        success_percentage = (test_result[mask].shape[0] / test_result.shape[0]) * 100

        return f"Test unitaire reussie a {success_percentage}%"

if __name__ == "__main__":
    root = tk.Tk()
    app = FromageUI(root)
    root.mainloop()
