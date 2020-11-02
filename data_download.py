from astropy.io import fits
import numpy as np
import sys
from os import system
import os
import requests 
import statistics as s

# numer TIC (TESS Input Catalog) - numer konkretnej gwiazdy
TIC = sys.argv[1]

# daty i numery potrzebne do automatycznego pobierania danych
dates = ['2018206045859', '2018234235059', '2018263035959', '2018292075959', '2018319095959', '2018349182459', '2019006130736', '2019032160000',
         '2019058134432', '2019085135100', '2019112060037', '2019140104343', '2019169103026', '2019198215352', '2019226182529', '2019253231442',
         '2019279210107', '2019306063752', '2019331140908', '2019357164649', '2020020091053', '2020049080258', '2020078014623', '2020106103520', 
         '2020133194932', '2020160202036', '2020186164531', '2020212050318']

nrs = ['-0120','-0121','-0123','-0124','-0125','-0126','-0131','-0136','-0139','-0140','-0143','-0144','-0146','-0150','-0151','-0152','-0161',
      '-0162','-0164','-0165','-0167','-0174','-0177','-0180','-0182','-0188','-0189','-0190']

# sektory obserwacji satelity TESS (Transiting Exoplanet Survey Satellite)
sec = len(dates)
sectors = [i for i in range (1,sec+1)]

if len(sys.argv) == 3:
 sec = int(sys.argv[2])
 dates = [dates[sec-1]]
 nrs = [nrs[sec-1]]
 sectors = [sec]


# pobieranie pliku z danymi z MAST (Barbara A. Mikulski Archive for Space Telescopes)
for sector, date, nr, in zip(sectors, dates, nrs):
 s_flag = False
 try:
  if sector < 10:
   url='https://mast.stsci.edu/api/v0.1/Download/file/?uri=mast:TESS/product/tess' + str(date) + '-s000' + str(sector) + '-' + '0' * (16 - len(TIC)) + TIC + nr + '-s_lc.fits'
   r = requests.get(url, allow_redirects=True)
   fits_file = "TIC-s" + str(sector) + "-" + TIC + ".fits"
   open(fits_file, 'wb').write(r.content)
  if sector >= 10:
   url='https://mast.stsci.edu/api/v0.1/Download/file/?uri=mast:TESS/product/tess' + str(date) + '-s00' + str(sector) + '-' + '0' * (16 - len(TIC)) + TIC + nr + '-s_lc.fits'
   r = requests.get(url, allow_redirects=True)
   fits_file = "TIC-s" + str(sector) + "-" + TIC + ".fits"
  open(fits_file, 'wb').write(r.content)
  fits.getdata(fits_file, ext=1).columns
  try:
   fits_file.close()
  except:
   pass
  s_flag = True
 except IOError as error:
  pass

# jezeli plik zostal pobrany - odczytywanie danych z formatu FITS i zapisywanie do .dat
 if s_flag:
  with fits.open(fits_file, mode="readonly") as hdulist:
   tess_bjds = hdulist[1].data['TIME']
   pdcsap_fluxes = hdulist[1].data['PDCSAP_FLUX']
   pdcsap_fluxes_err = hdulist[1].data['PDCSAP_FLUX_ERR']
   qual_flag = hdulist[1].data['QUALITY']

   bad_data = (qual_flag > 0)
   ynan = np.isnan(pdcsap_fluxes_err)
   ynan = np.logical_or(ynan, bad_data)
   out = list(zip(tess_bjds[~ynan], 1000.*(pdcsap_fluxes[~ynan]-s.mean(pdcsap_fluxes[~ynan]))/s.mean(pdcsap_fluxes[~ynan]), pdcsap_fluxes_err[~ynan]/(s.mean(pdcsap_fluxes[~ynan])*1000.)))
   np.savetxt("TIC" + TIC + "-s" + str(sector) + ".dat", out, fmt=' %14.7f %14.7f %14.7f ')

# finalnie w pliku znajduja sie: czas, sygnal i blad sygnalu

     