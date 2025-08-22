# ejercicios/tricep_dip.py
# -------------------------------
# Requierements
# -------------------------------
from trackerfit.ejercicios.ejercicio import Ejercicio

# -------------------------------
# Helpers
# -------------------------------

class DipTricep(Ejercicio):
    """
    Implementación del ejercicio 'Fondos de Tríceps (Tricep Dip)'.
    Calcula el ángulo entre hombro, codo y muñeca para identificar la flexión de los brazos al bajar el cuerpo.
    """
    def __init__(self,lado="derecho"):
        if(lado=="derecho"):
            puntos = (12,14,16) # Hombro (der) = 12 , Codo (der) = 14 y Muñeca (der) = 16
        else:
            puntos = (11,13,15) # Hombro (der) = 11 , Codo (der) = 13 y Muñeca (der) = 15
            
        super().__init__(angulo_min=90,angulo_max=160,puntos=puntos)
        self.umbral_validacion = self.angulo_min