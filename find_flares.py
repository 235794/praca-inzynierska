import sys
import os
import getopt
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from matplotlib import pyplot as plt
from gatspy.periodic import LombScargleFast
from sklearn import linear_model
from sklearn import preprocessing
from sklearn.base import BaseEstimator
from sklearn.model_selection import KFold, GridSearchCV

def Flares(time, signal, period, sigma=3., n_points=5):

# Funkcja do detekcji rozbłysków gwiazdowych

# parametry wejściowe: 
#  - time: czas
#  - signal: sygnał
#  - period: okres zmian jasności gwiazdy
#  - sigma: próg detekcji (domyślnie 3.0)
#  - n_points: minimaalna liczba punktów w rozbłysku (domyślnie 5) 

# parametry wyjściowe:
#  - tablice zawierające indeksy czasu startu i końca rozbłysków


# wykorzystywany będzie algorytm RANSAC (scikit learn)
 reg = linear_model.RANSACRegressor(random_state=0)

# krzywa blasku analizowana jest przedziałami o długości 1.5 okresu zmian jasności gwiady
 box = 1.5 * period
 shift = 0.25 * box 

# flaga zawierająca detekcje rozbłysków
 flag = np.zeros_like( time )

# pętla po analizowanych przedziałach czasu
 start = np.min(time) - box + shift
 i = 0
 while start < np.max(time):
  ii = np.where( (time > start) * (time < start+box) )
  x = time[ii]
  y = signal[ii]

# normalizacja
  x_norm = (x - np.mean(x)) / np.std(x)

# dopasowanie modelu do danych treningowych i docelowych wartości
  reg.fit( np.vander(x_norm, N=9), y )
# wektor wartości oczekiwanych
  prediction = reg.predict( np.vander(x_norm, N=9) )

# Detekcja rozbłysków 
# Warunkiem jest wartość w punkcie większa od modelu o sigma*odchylenie standardowe po odrzuceniu punktów odstających
  flare_detection =  y > prediction + sigma*np.std( (y - prediction)[reg.inlier_mask_] ) 

# Zliczanie detekcji w kolejnych analizowanych przedziałach czasu
  flag[ii[0][0] : ii[0][-1]+1] += flare_detection 

  i += 1
  start += shift

# analizowane są tylko detekcje, które co najmniej 2 razy zostały zaklasyfikowane jako rozbłysk

 detections_index = np.zeros_like(signal)
 detections_index[np.where( flag >= 3 )] = 1

# definiowanie zmiennych z indeksami początków i końców rozbłysków
 startt=[]
 stopp=[]
 j=0

# odrzucenie zjawisk trwających któcej niż założony czas (domyślnie 5 puktów)
 while j < (len(detections_index)-(int(n_points)+1)): 
  if detections_index[j] == 1:
   if np.sum(detections_index[j:j+int(n_points)]) == n_points:
    startt.append(j)
    stopp.append(j+np.where(detections_index[j:] == 0.0)[0][0])
    j=stopp[-1]
  j += 1

# procedura zwraca punkty początku i końca każdego z rozbłysków
 return startt, stopp

def Result(time,signal,tstart,tstop, fileout=""):

# Funkcja wyświetlająca i zapisująca wyniki obliczeń 

# parametry wejściowe: 
#  - time: czas
#  - signal: sygnał
#  - tstart: indeks początków rozbłysków
#  - tstop: indeks końća rozbłysków
#  - fileout: nazwa pliku, do którego zapisywane są dane (domyślnie *_out)


# definiowanie wykresu
 if not noplot:
  figure = plt.figure(num=1)
  figure.clf()
  ax = plt.subplot()
  ax.scatter(time, signal, c="k", s=0.1)
  ax.set_xlabel('czas [dni]')
  ax.set_ylabel('sygnał')
  ax.set_title('Krzywa blasku gwiazdy')

# jeżeli wybrano zapisywanie do pliku
 if fileout:
  fil = open(fileout, "w")
 
# nagłówek 
 header = "{:14}{:14}{:14}{:14}".format("#t_start","t_end","t_max","lc_amp")
 
 if fileout:
  fil.write(header+"\n")
 else:
  print(header)

# wyznaczenie czasów startu, maksimum i końca rozbłysku oraz amplitudy rozbłysku
 for i in range(len(tstart)):
  t_start = time[ tstart[i] ]
  t_stop = time[ tstop[i]+1 ]
  tmax = tstart[i] + np.argmax(signal[ tstart[i]:tstop[i]+1 ])
  t_max = time[ tmax ]  
  amp = signal[tmax]-np.median(signal[tmax-20:tmax+20])

  line="{:<14.4f}".format(t_start)+"{:<14.4f}".format(t_stop)+"{:<14.4f}".format(t_max)+"{:<14.4f}".format(amp)
  if not noplot:
   ax.scatter(time[ tstart[i]:tstop[i]+1 ], signal[ tstart[i]:tstop[i]+1 ], c="r", s=3) 

# wypisanie parematrów rozbłysku
  if fileout:
   fil.write(line+"\n")
  else:
   print(line)

 if fileout: 
  fil.close()

# wyświetlenie lub zapisanie wykresu do pliku
 if not noplot:
  if fileout:
   plt.savefig(os.path.splitext(files)[0]+"_out.pdf")
  plt.show()
  plt.ion()


# początek programu
if __name__ == "__main__":

# definiowane parametrow startowych
 save = False
 noplot = False
 file_out = ""
 points = 5
 level = 3.0

 try:
  opts, args = getopt.getopt( sys.argv[1:], "n:l:", ["points=","level=","noplot", "save"])

 except getopt.GetoptError as err:
  print('Error')
  sys.exit()

# wczytywanie parametrow opcjonalnych
 for opt, arg in opts:
  if opt == "--noplot":
   noplot = True
  if opt == "--save":
   save = True
  if opt in ("-n", "--points"):
   points = float(arg)
  if opt in ("-l", "--level"):
   level = float(arg)

# wczytywanie danych z pliku: czasu i sygnału
 for files in args:
  data = np.genfromtxt(files)
  time = data[:,0]
  signal = data[:,1]

# okreslanie okresu rotacji gwiazdy za pomocą metody Lomb-Scargle - pakiet gatspy
# założony zakres okresu rotacji zawiera się w 0.1-30 dniach (obserwacje z jednego sektora to ok. 27 dni)
  ls = LombScargleFast(fit_period=True,optimizer_kwds={"quiet": True})
  ls.optimizer.period_range = (0.1, 20.0)
  ls.fit(time,signal)
  period = ls.best_period

# procedura szukania rozblyskow
  tstart, tstop = Flares(time, signal, period, n_points=points, sigma=level)

# zdefiniowanie pliku z wynikami
  if save:
   file_out = os.path.splitext(files)[0]+"_out.dat"
   
# wypisanie wyników na ekran lub do plików
  Result(time,signal,tstart,tstop,fileout=file_out)

# jezeli jest wiele plikow do analizy - wszytsko zaczyna się od nowa
  file_out = ""

