import plotly.graph_objects as go
import plotly.express as px
import numpy as np


def generate_contour_plot():
    # Générer des données pour la démo
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(np.sqrt(X**2 + Y**2))

    # Créer la carte de contours
    fig = go.Figure(data=go.Contour(z=Z, x=x, y=y))

    # Renvoyer la figure pour un affichage ultérieur
    return fig
