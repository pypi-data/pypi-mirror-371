# ejercicios/crunch_abdominal.py
# -------------------------------
# Requierements
# -------------------------------
from trackerfit.ejercicios.ejercicio import Ejercicio

# -------------------------------
# Helpers
# -------------------------------

class CrunchAbdominal(Ejercicio):
    """
    Implementación del ejercicio 'Crunch Abdominal'.
    Calcula el ángulo entre cadera, abdomen y cabeza para validar la contracción abdominal.
    """
    def __init__(self,lado="derecho"):
        if(lado=="derecho"):
            puntos=(26,24,12) # Rodilla (der) = 26, # Cadera (der) = 24, Hombro (der) = 12
        else:
            puntos=(25,23,11) # Rodilla (der) = 25, # Cadera (der) = 23, Hombro (der) = 11
            
        super().__init__(angulo_min=110,angulo_max=150,puntos=puntos)
        self.umbral_validacion = self.angulo_min