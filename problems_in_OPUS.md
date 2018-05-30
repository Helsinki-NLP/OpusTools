# Problems in OPUS

## Books

* `/proj/nlpl/data/OPUS/Books/latest/xml/en-es.xml.gz` contains line `<link xtargets="s1241;" id="SL1241"/>` under `<linkGrp targType="s" fromDoc="en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.x
ml.gz" toDoc="es/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml.gz" >`
* Sentence with id `s1241` does not exist in file `Books/xml/en/Doyle_Arthur_Conan-Hound_of_the_Baskervilles.xml` in `/proj/nlpl/data/OPUS/Books/latest/xml/en.zip`

## GNOME

* Error message: `xml.parsers.expat.ExpatError: not well-formed (invalid token): line 1, column 3234`
* Probably caused by not having closing tags for `<no description>`.
* `<no description>` -tags in `GNOME/xml/en/accerciser.gnome-2-30/accerciser.gnome-2-30.xml`
* `<ei kuvausta>` in `GNOME/xml/fi/accerciser.gnome-2-30/accerciser.gnome-2-30.xml`
* `<keine Beschreibung>` in `GNOME/xml/de/accerciser.gnome-2-30/accerciser.gnome-2-30.xml`
* `<sin descripciÃ<U+0083>Â³n>` in `GNOME/xml/es/accerciser.gnome-2-30/accerciser.gnome-2-30.xml`
* `<Ð½ÐµÐ¼Ð° Ð¾Ð¿Ð¸Ñ<U+0081>>` in `GNOME/xml/mk/accerciser.gnome-2-30/accerciser.gnome-2-30.xml`
* Same problem possibly in all languages

## MPC1
 
* Error message: `xml.parsers.expat.ExpatError: not well-formed (invalid token): line 1, column 122657`
* A paragraph beginning with "He considered the version" has no `<p>` but does have `</p>` in `MPC1/xml/en/Jersild_Barnenso.xml`
* A paragraph beginning with "Il finit son" in `MPC1/xml/fr/MFredriksson.xml` 
* A paragraph beginning with "BREVET SER KONSTIGT UT" in `MPC1/xml/sv/MajgullAxelsson_Aprilhaxan1997.xml`
* A paragraph at the beginning of `MPC1/cml/fi/MajgullAxelsson_Aprilhaxan1997.xml` 

## OpenSubtitles

* Sentence ids are not always in sequential order.
* In en-fi.xml.gz the second document pair:
```
...
fromDoc="en/0/3808640/5878190.xml.gz" toDoc="fi/0/3808640/6350206.xml.gz" 
    <link id="SL286" xtargets="318 320;292" overlap="0.775" />
    <link id="SL287" xtargets="319;" />
...
```
* In en-es.xml.gz  the first document pair:
```
fromDoc="en/0/1084944/3377035.xml.gz" toDoc="es/0/1084944/4103721.xml.gz"
...
    <link id="SL149" xtargets="153;149" overlap="0.960" />
    <link id="SL150" xtargets="152;148" overlap="0.710" />
...
```
* In de-en.xml.gz the first document pair:
```
fromDoc="de/0/1467474/6453495.xml.gz" toDoc="en/0/1467474/6185069.xml.gz" 
...
    <link id="SL249" xtargets="268 266;231" overlap="0.932" />
    <link id="SL250" xtargets="267;232" overlap="0.271" />
...
``` 
