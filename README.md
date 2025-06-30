1) usa text-converter-cleaner-v3.py per caricare EPUB, PDF e convertirli in TXT e togliere i caratteri speciali che potrebbero dare fastidio al sintetizzatore vocale
2) sistema ulteriormente il txt togliendo le parti inutili, ringraziamenti etc.. (usa VisualCode)
3) splitta il txt in 10 / 20 quante vuoi parti con txt-book-splitter.py (così da poter dividere il lavoro in più tempi se necessario)
4) usa audiobook-v9-light.py per lanciare la creazione degli mp3 selezionando le parti del libro splittate precedentemente (ogni txt viene diviso in sottoparti da 5000 parole e crea un mp3 di ognuno, alla fine li unisce)
5) unisci tutte le parti con concatena-mp3.py
6) comprimi il tutto a 32 kbps con mp3-bitrates-converter.py (serve ffmpeg da scaricare e inserire il percorso di ffmpeg.exe)

suggerimento: usare Giuseppe Multilingual per l'ITALIANO
