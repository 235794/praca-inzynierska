# Małgorzata Pietras 235794
# Kierunek: Automatyka i Robotyka (AIR)
# Specjalność: Technologie informacyjne w systemach automatyki (ART)
# Praca inżynierska "Implementacja systemu identyfikacji rozbłysków gwiazdowych"
# Prowadzący pracę: Dr inż. Łukasz Jeleń, Katedra Informatyki Technicznej
# Politechnika Wrocławska 2020

# wymagane pakiety, które być może trzeba doinstalować: astropy, gatspy, sklearn

# Program do pobierania krzywych blasku gwiazd i ich analizy w celu wykrycia rozbłysków gwiazdowych
# W wersji podstawowej program:
#  - pobiera na wejściu numer TIC (TESS Input Catalog) gwiazdy lub plik z danymi
#  - zwraca użytkownikowi parametry rozbłysków: czas początku, końca i maksimum oraz amplitudę

from os import system
import glob, os
import subprocess
import time
from pathlib import Path 

# zdefiniowanie sposobu użycia
def usage():
 print("\n Użycie:", sys.argv[0],"[opcje] <pliki wejściowe>")
 print("Opcje:")
 print("-h, --help\t\t wyświetlenie sposobu użycia")
 print("-n, --points=<n>\t minimalna liczba punktów w rozbłysku (domyślnie: 5)")
 print("-l, --level=<l>\t poziom detekcji rozbłysków (domyślnie: 3.0)")
 print("-d, --download=<d>\t pobieranie danych dla gwiazdy o zadanym numerze")
 print("-s, --sector=<s>\t pobieranie danych dla gwiazdy z tylko jednego sektora")
 print("--save\t\t\t zapisywanie wyników do plików z końcówką '_out'")
 print("--noplot\t\t brak wykresów \n")
 print("Przykłady: \n python start.py TIC246891813-s3.dat \n python start.py -d 246891813 -s 3 \n python start.py -n 7 -l 2.0 --save --noplot -d 246891813 -s 3")
 sys.exit()

# start programu
if __name__ == "__main__":
 import getopt
 import sys

# zdefiniowanie parametrów startowych
 outfile = ""
 sector = "0"
 download = ""
 options = []

# pobieranie argumentów
 try:
  opts, args = getopt.getopt( sys.argv[1:], "h:n:l:d:s:",\
  ["help", "points=", "level=", "download=", "sector=", "noplot", "save"])

 except getopt.GetoptError as err:
  if sys.argv[1] != '-h':
   print('Error \n')
  usage()
  sys.exit()

# wyświetlenie instrukcji
 if opts == [] and args == []:
  print('\n Małgorzata Pietras 235794')
  print(' Kierunek: Automatyka i Robotyka (AIR)')
  print(' Specjalność: Technologie informacyjne w systemachautomatyki (ART)') 
  print(' Praca inżynierksa "Implementacja systemu identyfikacji rozbłysków gwiazdowych"')  
  print(' Dr inż. Łukasz Jeleń, Katedra Informatyki Technicznej')
  print(' Politechnika Wrocławska 2020 \n') 
  usage()
  sys.exit()

# obsługa argumentów
 for opt, arg in opts:
  if opt in ("-h", "--help"):
   usage()
   sys.exit()
  elif opt == "--noplot":
   options.append(opt)
  elif opt == "--save":
   options.append(opt)
  elif opt in ("-n", "--points"):
   options.append(opt)
   options.append(arg)
  elif opt in ("-l", "--level"):
   options.append(opt)
   options.append(arg)
  elif opt in ("-d", "--download"):
   download = arg
  elif opt in ("-s", "--sector"):
   sector = arg

# pobieranie danych z użyciem programu data_download.py 
 if download != "":
  if sector == "0": 
   process = subprocess.Popen(["python", "data_download.py"] + [download])
   process.wait()
   for file in glob.glob("TIC"+download+"*.dat"):
    args.append(file)
  if sector != "0": 
   process = subprocess.Popen(["python", "data_download.py"] + [download,sector])
   process.wait()
   args=["TIC"+download+"-s"+sector+".dat"]

# wyszukiwanie rozbłysków za pomocą programu find_flares.py
 process = subprocess.Popen(["python", "find_flares.py"] + options + args)
 process.wait()

# usuwanie zbędnych plików
 for file in glob.glob("*.fits"):
  os.remove(file)
