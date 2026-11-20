#funkcja odpowiedzialna za weryfikacje peselu
def valid_pesel(pesel):

    # czy ma tylko cyfry
    if not pesel.isdigit():
        return False

    #weryfikacja, czy pesel ma 11 cyfr
    if len(pesel) != 11:
        return False

    #przypisanie odpowiedniego znaczenia cyfr do miejsc w peselu
    rok = int(pesel[0:2])
    miesiac = int(pesel[2:4])
    dzien = int(pesel[4:6])
    suma_kontrolna = int(pesel[10])

    #sprawdzam miesiąc
    if miesiac < 1 or miesiac > 12:
        return False

    #spr dzień
    dni_w_miesiacu = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if rok % 4 == 0 and (rok % 100 != 0 or rok % 400 == 0):
        dni_w_miesiacu[2] = 29  # Rok przestępny
    if dzien < 1 or dzien > dni_w_miesiacu[miesiac]:
        return False